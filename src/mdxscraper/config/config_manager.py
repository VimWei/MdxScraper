from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib
import tomli_w


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


class ConfigManager:
    """Manage default config, user config, and schemes.

    GUI-facing API:
    - load(), save()
    - get(path), set(path, value)
    - list_schemes(), apply_scheme(name)
    - validate()
    - backup(file_path)
    - path helpers: get_input_file(), set_input_file(...), etc.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or Path(__file__).resolve().parents[3]
        self.data_dir = self.project_root / "data"
        self.configs_dir = self.data_dir / "configs"
        self.default_config_path = (
            self.project_root / "src" / "mdxscraper" / "config" / "default_config.toml"
        )
        self.latest_config_path = self.configs_dir / "config_latest.toml"
        self._config: Dict[str, Any] = {}
        # Normalization reporting state (consumed once by GUI)
        self._norm_changed: bool = False
        self._norm_counts: Dict[str, int] = {"removed": 0, "added": 0, "type_fixed": 0}

    # ---------- Public API ----------
    def load(self) -> Dict[str, Any]:
        if self.latest_config_path.is_file():
            self._config = self._read_toml(self.latest_config_path)
        else:
            self._config = self._read_toml(self.default_config_path)
            self.configs_dir.mkdir(parents=True, exist_ok=True)
            self._atomic_write(self.latest_config_path, self._config)
        # Normalize in-memory config against current defaults
        self._normalize_config()
        return self._config

    def save(self) -> None:
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        # Ensure config is normalized before persisting
        self._normalize_config()
        self._atomic_write(self.latest_config_path, self._config)

    def get(self, dotted_path: str, default: Any = None) -> Any:
        node: Any = self._config
        for key in dotted_path.split("."):
            if not isinstance(node, dict) or key not in node:
                return default
            node = node[key]
        return node

    def set(self, dotted_path: str, value: Any) -> None:
        node = self._config
        keys = dotted_path.split(".")
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value

    def list_schemes(self) -> list[str]:
        if not self.configs_dir.exists():
            return []
        return [p.name for p in self.configs_dir.glob("*.toml") if p.name != "config_latest.toml"]

    def apply_scheme(self, name: str) -> None:
        scheme_path = self.configs_dir / name
        if not scheme_path.is_file():
            raise FileNotFoundError(f"Scheme not found: {scheme_path}")
        self._config = self._read_toml(scheme_path)
        self.save()

    def validate(self) -> ValidationResult:
        errors: list[str] = []

        # Required keys
        required = ["input.file", "dictionary.file", "output.file"]
        for key in required:
            if self.get(key) in (None, ""):
                errors.append(f"Missing required field: {key}")

        # Paths existence checks (best-effort)
        input_file = self.get("input.file")
        if input_file and not self._resolve_path(input_file).exists():
            errors.append(f"Input file not found: {input_file}")

        dict_file = self.get("dictionary.file")
        if dict_file and not self._resolve_path(dict_file).exists():
            errors.append(f"Dictionary file not found: {dict_file}")

        output_file = self.get("output.file")
        if output_file:
            out_path = self._resolve_path(output_file)
            out_dir = out_path.parent
            if not out_dir.exists():
                try:
                    out_dir.mkdir(parents=True, exist_ok=True)
                except Exception:
                    errors.append(f"Cannot create output directory: {out_dir}")

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def backup(self, suffix: str = "bak") -> Path:
        backup_path = self.latest_config_path.with_suffix(self.latest_config_path.suffix + f".{suffix}")
        if self.latest_config_path.is_file():
            data = self._read_toml(self.latest_config_path)
            self._atomic_write(backup_path, data)
        return backup_path

    # Field helpers for GUI
    def get_input_file(self) -> Optional[str]:
        return self.get("input.file")

    def set_input_file(self, path: str) -> None:
        self.set("input.file", self._to_external_path(path))

    def get_dictionary_file(self) -> Optional[str]:
        return self.get("dictionary.file")

    def set_dictionary_file(self, path: str) -> None:
        self.set("dictionary.file", self._to_external_path(path))

    def get_output_file(self) -> Optional[str]:
        return self.get("output.file")

    def set_output_file(self, path: str) -> None:
        self.set("output.file", self._to_external_path(path))

    def get_output_add_timestamp(self) -> bool:
        return self.get("output.add_timestamp", True)

    def set_output_add_timestamp(self, value: bool) -> None:
        self.set("output.add_timestamp", value)

    def get_backup_input(self) -> bool:
        return self.get("output.backup_input", True)

    def set_backup_input(self, value: bool) -> None:
        self.set("output.backup_input", value)

    def get_save_invalid_words(self) -> bool:
        return bool(self.get("output.save_invalid_words", True))

    def set_save_invalid_words(self, value: bool) -> None:
        self.set("output.save_invalid_words", bool(value))

    # ---------- Internal helpers ----------
    def _read_toml(self, path: Path) -> Dict[str, Any]:
        with open(path, "rb") as f:
            return tomllib.load(f)

    def _atomic_write(self, path: Path, data: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        content = tomli_w.dumps(data)
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp_path, path)

    def _resolve_path(self, external_path: str) -> Path:
        # Treat external path as relative to project_root
        p = Path(external_path)
        if not p.is_absolute():
            return (self.project_root / p).resolve()
        return p

    def _to_external_path(self, any_path: str | Path) -> str:
        p = Path(any_path)
        try:
            return str(p.resolve().relative_to(self.project_root))
        except Exception:
            return str(p)

    def _normalize_config(self) -> None:
        """Normalize in-memory config to the latest schema.

        Strategy:
        - Reconcile strictly against default_config.toml:
          • remove unknown keys
          • add missing keys with defaults
          • if type mismatch, replace with default
        - Record a one-time summary (counts) for GUI to announce.
        """
        self._norm_changed = False
        self._norm_counts = {"removed": 0, "added": 0, "type_fixed": 0}

        cfg: Dict[str, Any] = self._config if isinstance(self._config, dict) else {}

        # --- Reconcile with defaults ---
        try:
            defaults: Dict[str, Any] = self._read_toml(self.default_config_path)
        except Exception:
            defaults = {}

        def reconcile(current: Any, default: Any, path: str = "") -> Any:
            # If default is not a dict, enforce type by replacing mismatched values
            if not isinstance(default, dict):
                if (default is None) or isinstance(current, type(default)):
                    return current if current is not None else default
                # type mismatch → replace
                self._norm_changed = True
                self._norm_counts["type_fixed"] += 1
                return default

            # default is a dict: current must be a dict, otherwise replace whole node
            if not isinstance(current, dict):
                self._norm_changed = True
                # Count as type fix
                self._norm_counts["type_fixed"] += 1
                # return a deep copy-like structure based on default
                return reconcile({}, default, path)

            # remove unknown keys
            for k in list(current.keys()):
                if k not in default:
                    current.pop(k, None)
                    self._norm_changed = True
                    self._norm_counts["removed"] += 1

            # add missing keys and recurse existing keys
            for k, dv in default.items():
                if k in current:
                    current[k] = reconcile(current[k], dv, f"{path}.{k}" if path else k)
                else:
                    # add missing from defaults
                    current[k] = dv
                    self._norm_changed = True
                    self._norm_counts["added"] += 1

            return current

        self._config = reconcile(cfg, defaults)

    def get_normalize_info_once(self) -> dict:
        """Return and reset one-time normalization summary for GUI logging."""
        info = {
            "changed": self._norm_changed,
            "removed": self._norm_counts.get("removed", 0),
            "added": self._norm_counts.get("added", 0),
            "type_fixed": self._norm_counts.get("type_fixed", 0),
        }
        # reset after consumption
        self._norm_changed = False
        self._norm_counts = {"removed": 0, "added": 0, "type_fixed": 0}
        return info


