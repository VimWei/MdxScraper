from __future__ import annotations

from pathlib import Path
from typing import Optional

from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


class PresetCoordinator:
    """Coordinate preset list, selection, editor loading, dirty state and snapshots.

    This extracts duplicated logic from MainWindow to improve maintainability.
    """

    def __init__(self, presets: PresetsService, settings: SettingsService) -> None:
        self.presets = presets
        self.settings = settings

    # --- public API ---
    def reload_presets(self, mw, auto_select_default: bool = False) -> None:
        # Preserve configured labels
        current_pdf_label = str(self.settings.get("pdf.preset_label", "") or "")
        current_css_label = str(self.settings.get("css.preset_label", "") or "")

        # PDF list
        mw.tab_pdf.pdf_combo.clear()
        for label, path in self.presets.iter_presets("pdf"):
            mw.tab_pdf.pdf_combo.addItem(label, userData=str(path))

        if current_pdf_label:
            self.select_label_and_load(mw, "pdf", current_pdf_label)
        elif mw.tab_pdf.pdf_combo.count() > 0 and auto_select_default:
            preferred = None
            for i in range(mw.tab_pdf.pdf_combo.count()):
                txt = mw.tab_pdf.pdf_combo.itemText(i).lower()
                if txt.startswith("default"):
                    preferred = mw.tab_pdf.pdf_combo.itemText(i)
                    break
            if preferred:
                self.select_label_and_load(mw, "pdf", preferred)

        # CSS list
        mw.tab_css.css_combo.clear()
        for label, path in self.presets.iter_presets("css"):
            mw.tab_css.css_combo.addItem(label, userData=str(path))

        if current_css_label:
            self.select_label_and_load(mw, "css", current_css_label)
        elif mw.tab_css.css_combo.count() > 0 and auto_select_default:
            preferred = None
            for i in range(mw.tab_css.css_combo.count()):
                txt = mw.tab_css.css_combo.itemText(i).lower()
                if txt.startswith("original"):
                    preferred = mw.tab_css.css_combo.itemText(i)
                    break
            if preferred:
                self.select_label_and_load(mw, "css", preferred)

    def select_label_and_load(self, mw, kind: str, label: str) -> None:
        combo = mw.tab_pdf.pdf_combo if kind == "pdf" else mw.tab_css.css_combo
        matched = -1
        for i in range(combo.count()):
            if combo.itemText(i) == label:
                matched = i
                break
        if matched >= 0:
            combo.setCurrentIndex(matched)
            return
        # Not found → * Untitled state (keep editor content)
        self.enter_untitled_state(mw, kind, clear_editor=False)
        try:
            if kind == "pdf":
                self.settings.set("pdf.preset_label", "")
            else:
                self.settings.set("css.preset_label", "")
        except Exception:
            pass

    def enter_untitled_state(self, mw, kind: str, clear_editor: bool) -> None:
        if kind == "pdf":
            combo = mw.tab_pdf.pdf_combo
            editor = mw.tab_pdf.pdf_editor
            show_dirty = mw.tab_pdf.show_dirty
            if clear_editor:
                mw._updating_pdf_editor = True
                try:
                    editor.setPlainText("")
                finally:
                    mw._updating_pdf_editor = False
            combo.setCurrentIndex(-1)
            mw.pdf_dirty = True
            show_dirty(True)
        else:
            combo = mw.tab_css.css_combo
            editor = mw.tab_css.css_editor
            show_dirty = mw.tab_css.show_dirty
            if clear_editor:
                mw._updating_css_editor = True
                try:
                    editor.setPlainText("")
                finally:
                    mw._updating_css_editor = False
            combo.setCurrentIndex(-1)
            mw.css_dirty = True
            show_dirty(True)

    # --- signal handlers ---
    def on_pdf_preset_changed(self, mw, label: str) -> None:
        idx = mw.tab_pdf.pdf_combo.currentIndex()
        if idx < 0:
            return
        path = mw.tab_pdf.pdf_combo.itemData(idx)
        if not path:
            return
        try:
            text = self.presets.load_preset_text(Path(path))
            mw._updating_pdf_editor = True
            try:
                mw.tab_pdf.pdf_editor.setPlainText(text)
            finally:
                mw._updating_pdf_editor = False
            self.settings.set("pdf.preset_label", label)
            mw.pdf_dirty = False
            mw.last_pdf_label = label
            mw.tab_pdf.show_dirty(False)
        except Exception as e:
            mw.log_panel.appendLog(f"❌ Failed to load PDF preset: {e}. Switched to * Untitled.")
            self.enter_untitled_state(mw, "pdf", clear_editor=True)
            try:
                self.settings.set("pdf.preset_label", "")
            except Exception:
                pass

    def on_css_preset_changed(self, mw, label: str) -> None:
        idx = mw.tab_css.css_combo.currentIndex()
        if idx < 0:
            return
        path = mw.tab_css.css_combo.itemData(idx)
        if not path:
            return
        try:
            text = self.presets.load_preset_text(Path(path))
            mw._updating_css_editor = True
            try:
                mw.tab_css.css_editor.setPlainText(text)
            finally:
                mw._updating_css_editor = False
            self.settings.set("css.preset_label", label)
            mw.css_dirty = False
            mw.last_css_label = label
            mw.tab_css.show_dirty(False)
        except Exception as e:
            mw.log_panel.appendLog(f"❌ Failed to load CSS preset: {e}. Switched to * Untitled.")
            self.enter_untitled_state(mw, "css", clear_editor=True)
            try:
                self.settings.set("css.preset_label", "")
            except Exception:
                pass

    def on_pdf_text_changed(self, mw) -> None:
        if mw._updating_pdf_editor:
            return
        self.enter_untitled_state(mw, "pdf", clear_editor=False)

    def on_css_text_changed(self, mw) -> None:
        if mw._updating_css_editor:
            return
        self.enter_untitled_state(mw, "css", clear_editor=False)

    # --- autosave / snapshot ---
    def autosave_untitled_if_needed(self, mw) -> None:
        if mw.pdf_dirty:
            self._autosave_untitled(mw, "pdf")
        if mw.css_dirty:
            self._autosave_untitled(mw, "css")

    def _autosave_untitled(self, mw, kind: str) -> None:
        try:
            if kind == "pdf":
                text = mw.tab_pdf.pdf_editor.toPlainText()
                out = mw.project_root / "data" / "configs" / "pdf" / "Untitled.toml"
                self.presets.save_preset_text(out, text)
                self.settings.set("pdf.preset_label", "Untitled")
                mw.pdf_dirty = False
                mw.tab_pdf.show_dirty(False)
                self.reload_presets(mw, auto_select_default=False)
                self.select_label_and_load(mw, "pdf", "Untitled")
            else:
                text = mw.tab_css.css_editor.toPlainText()
                out = mw.project_root / "data" / "configs" / "css" / "Untitled.toml"
                self.presets.save_preset_text(out, text)
                self.settings.set("css.preset_label", "Untitled")
                mw.css_dirty = False
                mw.tab_css.show_dirty(False)
                self.reload_presets(mw, auto_select_default=False)
                self.select_label_and_load(mw, "css", "Untitled")
        except Exception as e:
            mw.log_panel.appendLog(f"⚠️ Failed to autosave Untitled: {e}")

    def create_snapshots_if_needed_on_export(self, mw) -> tuple[Optional[str], Optional[str]]:
        new_pdf_label: Optional[str] = None
        new_css_label: Optional[str] = None
        try:
            pdf_label = str(self.settings.get("pdf.preset_label", "") or "")
            css_label = str(self.settings.get("css.preset_label", "") or "")
            if mw.pdf_dirty or pdf_label.strip().lower() == "untitled":
                pdf_text = mw.tab_pdf.pdf_editor.toPlainText()
                snap = self.presets.create_untitled_snapshot("pdf", pdf_text)
                self.settings.set("pdf.preset_label", snap.stem)
                new_pdf_label = snap.stem
            if mw.css_dirty or css_label.strip().lower() == "untitled":
                css_text = mw.tab_css.css_editor.toPlainText()
                snap = self.presets.create_untitled_snapshot("css", css_text)
                self.settings.set("css.preset_label", snap.stem)
                new_css_label = snap.stem
        except Exception as e:
            mw.log_panel.appendLog(f"⚠️ Failed to freeze Untitled: {e}")
        return new_pdf_label, new_css_label
