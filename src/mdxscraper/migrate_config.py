from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import tomli_w


def migrate_from_settings_py(project_root: Path | None = None) -> Path | None:
    """One-shot migration from settings.py to data/configs/config_latest.toml.

    Returns the path to the created TOML config, or None if settings.py not found.
    """
    root = project_root or Path(__file__).resolve().parents[1]
    settings_path = root / "settings.py"
    if not settings_path.is_file():
        return None

    # Import settings dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location("_legacy_settings", str(settings_path))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[arg-type]

    # Build new config dict
    config: Dict[str, Any] = {
        "input": {"file": str(Path(mod.INPUT_PATH) / mod.INPUT_NAME)},
        "dictionary": {"file": str(Path(mod.DICTIONARY_PATH) / mod.DICTIONARY_NAME)},
        "output": {"file": str(Path(mod.OUTPUT_PATH) / (mod.OUTPUT_NAME or "lookup_results.html")), "with_toc": True},
        "processing": {"invalid_action": "collect_warning", "parallel": False, "max_workers": 4},
        "advanced": {"wkhtmltopdf_path": "auto"},
    }

    dest_dir = root / "data" / "configs"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "config_latest.toml"
    with open(dest, "w", encoding="utf-8") as f:
        tomli_w.dump(config, f)
    # rename legacy settings.py to settings.py.bak to avoid confusion
    try:
        settings_path.rename(settings_path.with_suffix(settings_path.suffix + ".bak"))
    except Exception:
        pass
    return dest


