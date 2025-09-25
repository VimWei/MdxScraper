from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, Union

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.gui.models.config_models import (
    BasicConfig, ImageConfig, AdvancedConfig, PdfConfig, CssConfig
)

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
            self.cm.set('pdf.preset_text', pdf_text)
            self.cm.set('pdf.preset_label', pdf_label)
            self.cm.set('css.preset_text', css_text)
            self.cm.set('css.preset_label', css_label)
        except Exception:
            pass

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

    # Unified configuration access methods
    def get_basic_config(self) -> BasicConfig:
        """Get Basic page configuration as data class"""
        # Read exclusively from new [basic] section
        return BasicConfig(
            input_file=str(self.get("basic.input_file", "")),
            dictionary_file=str(self.get("basic.dictionary_file", "")),
            output_file=str(self.get("basic.output_file", "")),
            output_add_timestamp=self.get_output_add_timestamp(),
            backup_input=self.get_backup_input(),
            save_invalid_words=self.get_save_invalid_words(),
            with_toc=bool(self.get("basic.with_toc", True))
        )

    def update_basic_config(self, config: BasicConfig) -> None:
        """Update Basic page configuration from data class"""
        # Write only to new [basic] section
        self.set("basic.input_file", config.input_file)
        self.set("basic.dictionary_file", config.dictionary_file)
        self.set("basic.output_file", config.output_file)
        self.set_output_add_timestamp(config.output_add_timestamp)
        self.set_backup_input(config.backup_input)
        self.set_save_invalid_words(config.save_invalid_words)
        # Persist with_toc only in new [basic] section
        with_toc_val = bool(getattr(config, 'with_toc', True))
        self.set("basic.with_toc", with_toc_val)

    def get_image_config(self) -> ImageConfig:
        """Get Image page configuration as data class"""
        return ImageConfig(
            width=int(self.get("image.width", 0) or 0),
            zoom=float(self.get("image.zoom", 1.0) or 1.0),
            background=bool(self.get("image.background", True)),
            jpg_quality=int(self.get("image.jpg.quality", 85) or 85),
            png_optimize=bool(self.get("image.png.optimize", True)),
            png_compress_level=int(self.get("image.png.compress_level", 9) or 9),
            png_transparent_bg=bool(self.get("image.png.transparent_bg", False)),
            webp_quality=int(self.get("image.webp.quality", 80) or 80),
            webp_lossless=bool(self.get("image.webp.lossless", False)),
            webp_transparent_bg=bool(self.get("image.webp.transparent_bg", False))
        )

    def update_image_config(self, config: ImageConfig) -> None:
        """Update Image page configuration from data class"""
        self.set("image.width", config.width)
        self.set("image.zoom", config.zoom)
        self.set("image.background", config.background)
        self.set("image.jpg.quality", config.jpg_quality)
        self.set("image.png.optimize", config.png_optimize)
        self.set("image.png.compress_level", config.png_compress_level)
        self.set("image.png.transparent_bg", config.png_transparent_bg)
        self.set("image.webp.quality", config.webp_quality)
        self.set("image.webp.lossless", config.webp_lossless)
        self.set("image.webp.transparent_bg", config.webp_transparent_bg)

    def get_advanced_config(self) -> AdvancedConfig:
        """Get Advanced page configuration as data class"""
        return AdvancedConfig(
            wkhtmltopdf_path=str(self.get("advanced.wkhtmltopdf_path", "auto"))
        )

    def update_advanced_config(self, config: AdvancedConfig) -> None:
        """Update Advanced page configuration from data class"""
        self.set("advanced.wkhtmltopdf_path", config.wkhtmltopdf_path)

    def get_pdf_config(self) -> PdfConfig:
        """Get PDF page configuration as data class"""
        return PdfConfig(
            preset_text=str(self.get("pdf.preset_text", "")),
            preset_label=str(self.get("pdf.preset_label", ""))
        )

    def update_pdf_config(self, config: PdfConfig) -> None:
        """Update PDF page configuration from data class"""
        self.set("pdf.preset_text", config.preset_text)
        self.set("pdf.preset_label", config.preset_label)

    def get_css_config(self) -> CssConfig:
        """Get CSS page configuration as data class"""
        return CssConfig(
            preset_text=str(self.get("css.preset_text", "")),
            preset_label=str(self.get("css.preset_label", ""))
        )

    def update_css_config(self, config: CssConfig) -> None:
        """Update CSS page configuration from data class"""
        self.set("css.preset_text", config.preset_text)
        self.set("css.preset_label", config.preset_label)
