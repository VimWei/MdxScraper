from __future__ import annotations

from pathlib import Path
from typing import Optional

from mdxscraper.services.settings_service import SettingsService
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.utils import path_utils


class ConfigCoordinator:
    """Coordinate config sync/import/export/validation around services and UI."""

    def __init__(self, settings: SettingsService, presets: PresetsService) -> None:
        self.settings = settings
        self.presets = presets

    # --- sync ---
    def sync_all_from_config(self, mw) -> None:
        basic_config = self.settings.get_basic_config()
        mw.tab_basic.set_config(basic_config)

        image_config = self.settings.get_image_config()
        mw.tab_image.set_config(image_config)

        advanced_config = self.settings.get_advanced_config()
        mw.tab_advanced.set_config(advanced_config)

        pdf_config = self.settings.get_pdf_config()
        mw.tab_pdf.set_config(pdf_config)

        css_config = self.settings.get_css_config()
        mw.tab_css.set_config(css_config)

    def sync_all_to_config(self, mw) -> None:
        self.settings.update_basic_config(mw.tab_basic.get_config())
        try:
            self.settings.update_image_config(mw.tab_image.get_config())
        except (ValueError, TypeError):
            pass
        self.settings.update_advanced_config(mw.tab_advanced.get_config())
        self.settings.update_pdf_config(mw.tab_pdf.get_config())
        self.settings.update_css_config(mw.tab_css.get_config())

    # --- import/export ---
    def import_config(self, mw, file_path: Path) -> None:
        try:
            import tomllib as _tomllib
            with open(file_path, "rb") as f:
                cfg = _tomllib.load(f)
            # autosave Untitled before overwrite
            mw.preset_coordinator.autosave_untitled_if_needed(mw)
            self.settings.replace_config(cfg)
            info = self.settings.get_normalize_info_once()
            # reload presets then sync UI
            mw.preset_coordinator.reload_presets(mw, auto_select_default=False)
            self.sync_all_from_config(mw)
            mw.log_panel.appendLog(f"✅ Imported config applied: {self.settings.to_relative(str(file_path))}")
            if info.get("changed"):
                removed, added, type_fixed = info.get("removed", 0), info.get("added", 0), info.get("type_fixed", 0)
                mw.log_panel.appendLog(f"⚙️ Config normalized after import (removed: {removed}, added: {added}, type fixed: {type_fixed}). Please save to persist.")
        except Exception as e:
            mw.log_panel.appendLog(f"❌ Failed to import config: {e}")

    def export_config(self, mw, file_path: Path) -> None:
        # sync pages to settings first
        self.sync_all_to_config(mw)
        # then autosave any Untitled dirty state
        mw.preset_coordinator.autosave_untitled_if_needed(mw)

        # validate and log, but proceed
        result = self.settings.validate()
        if not result.is_valid:
            problems = "\n".join(result.errors)
            mw.log_panel.appendLog("⚠️ Config validation issues before export:\n" + problems)

        from mdxscraper.config import config_manager as _cm
        data = self.settings.get_config_dict()

        # freeze Untitled to snapshots when needed
        new_pdf_label, new_css_label = mw.preset_coordinator.create_snapshots_if_needed_on_export(mw)
        if new_pdf_label:
            data.setdefault('pdf', {})['preset_label'] = new_pdf_label
            mw.log_panel.appendLog(f"📌 Frozen PDF Untitled to: {self.settings.to_relative(self.presets.user_pdf_dir() / (new_pdf_label + '.toml'))}")
        if new_css_label:
            data.setdefault('css', {})['preset_label'] = new_css_label
            mw.log_panel.appendLog(f"📌 Frozen CSS Untitled to: {self.settings.to_relative(self.presets.user_css_dir() / (new_css_label + '.toml'))}")

        content = _cm.tomli_w.dumps(data)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        mw.log_panel.appendLog(f"✅ Exported config to: {self.settings.to_relative(str(file_path))}")

        # if snapshots were created, reload and select
        if new_pdf_label or new_css_label:
            mw.preset_coordinator.reload_presets(mw, auto_select_default=False)
            if new_pdf_label:
                mw.preset_coordinator.select_label_and_load(mw, 'pdf', new_pdf_label)
                mw.pdf_dirty = False
                mw.tab_pdf.show_dirty(False)
            if new_css_label:
                mw.preset_coordinator.select_label_and_load(mw, 'css', new_css_label)
                mw.css_dirty = False
                mw.tab_css.show_dirty(False)

    # --- Advanced helpers ---
    def validate_wkhtmltopdf(self, path: str, force_redetect: bool = False) -> tuple[bool, str, str]:
        """Validate or auto-detect wkhtmltopdf.

        Returns: (is_valid, resolved_path, message)
        - resolved_path 为空字符串表示未找到或保留 auto 状态
        """
        try:
            if not path or path in ("auto", ""):
                if force_redetect:
                    ok, detected, msg = path_utils.force_auto_detect()
                else:
                    ok, detected, msg = path_utils.get_auto_detect_status()
                return ok, detected if ok else "", msg
            ok, msg = path_utils.validate_wkhtmltopdf_path(path)
            return ok, path if ok else "", msg
        except Exception as e:
            return False, "", f"validation error: {e}"


