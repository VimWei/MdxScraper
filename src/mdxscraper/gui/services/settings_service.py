from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Union

from mdxscraper.config.config_manager import ConfigManager


class SettingsService:
    def __init__(self, project_root: Path, cm: ConfigManager | None = None):
        self.project_root = project_root
        if cm is None:
            self.cm = ConfigManager(project_root)
            self.cm.load()
        else:
            self.cm = cm

    # Facade to ConfigManager common operations
    def get(self, key: str, default: Any = None) -> Any:
        return self.cm.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.cm.set(key, value)

    def save(self) -> None:
        self.cm.save()

    def validate(self) -> Any:
        return self.cm.validate()

    def load(self) -> None:
        self.cm.load()

    # Config replacements and normalization
    def replace_config(self, cfg: Dict[str, Any]) -> None:
        self.cm._config = cfg
        self.cm._normalize_config()

    def get_normalize_info_once(self) -> Dict[str, Any]:
        return self.cm.get_normalize_info_once()

    def get_config_dict(self) -> Dict[str, Any]:
        return self.cm._config

    # Specific helpers mentioned in the refactor doc
    def persist_session_state(self, pdf_text: str, pdf_label: str, css_text: str, css_label: str) -> None:
        try:
            self.cm.set('output.pdf.preset_text', pdf_text)
            self.cm.set('output.pdf.preset_label', pdf_label)
            self.cm.set('output.css.preset_text', css_text)
            self.cm.set('output.css.preset_label', css_label)
        except Exception:
            pass

    def get_tab_enablement(self, output_path: str) -> Dict[str, bool]:
        suffix = Path(output_path).suffix.lower() if output_path else ''
        return {
            'pdf': suffix == '.pdf',
            'image': suffix in ('.jpg', '.jpeg', '.png', '.webp'),
            'css': True,
        }

    def resolve_path(self, maybe_path: Union[str, Path]) -> Path:
        return self.cm._resolve_path(maybe_path)

    # Checkbox helpers
    def get_output_add_timestamp(self) -> bool:
        return self.cm.get_output_add_timestamp()

    def set_output_add_timestamp(self, value: bool) -> None:
        self.cm.set_output_add_timestamp(value)

    def get_backup_input(self) -> bool:
        return self.cm.get_backup_input()

    def set_backup_input(self, value: bool) -> None:
        self.cm.set_backup_input(value)

    def get_save_invalid_words(self) -> bool:
        return self.cm.get_save_invalid_words()

    def set_save_invalid_words(self, value: bool) -> None:
        self.cm.set_save_invalid_words(value)

    # File path setters (UI wrappers)
    def set_input_file(self, path: str) -> None:
        self.cm.set_input_file(path)

    def set_dictionary_file(self, path: str) -> None:
        self.cm.set_dictionary_file(path)

    def set_output_file(self, path: str) -> None:
        self.cm.set_output_file(path)

    # Paths helpers
    def to_relative(self, p: Union[Path, str]) -> str:
        try:
            root = self.project_root.resolve()
            return str(Path(p).resolve().relative_to(root))
        except Exception:
            # Rule B: if outside project root (or on different drive), keep absolute
            return str(Path(p).resolve())


