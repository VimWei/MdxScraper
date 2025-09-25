from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTextEdit, QHBoxLayout, QLineEdit, QProgressBar,
    QGridLayout, QSizePolicy, QSpacerItem, QCheckBox, QTabWidget, QComboBox, QSlider
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QIcon

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.gui.workers.conversion_worker import ConversionWorker
from mdxscraper.gui.services.settings_service import SettingsService
from mdxscraper.gui.services.presets_service import PresetsService
from mdxscraper.gui.components.command_panel import CommandPanel
from mdxscraper.gui.pages.basic_page import BasicPage
from mdxscraper.gui.pages.image_page import ImagePage
from mdxscraper.gui.pages.pdf_page import PdfPage
from mdxscraper.gui.pages.css_page import CssPage
from mdxscraper.gui.pages.advanced_page import AdvancedPage
from mdxscraper.gui.pages.about_page import AboutPage


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        self.setWindowTitle("MdxScraper")
        self.project_root = project_root
        
        # Set window icon
        icon_path = project_root / "src" / "mdxscraper" / "gui" / "assets" / "app_icon.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        # Services (temporary: cm kept for incremental migration)
        self.cm = ConfigManager(project_root)
        self.cm.load()
        # Ensure SettingsService shares the same ConfigManager instance
        self.settings = SettingsService(project_root, self.cm)
        self.presets = PresetsService(project_root)
        # Announce normalization result once
        info = self.cm.get_normalize_info_once()
        if info.get("changed"):
            removed, added, type_fixed = info.get("removed", 0), info.get("added", 0), info.get("type_fixed", 0)
            self.log_message_later = f"⚙️ Config normalized (removed: {removed}, added: {added}, type fixed: {type_fixed}). Please save to persist."
        else:
            self.log_message_later = None

        central = QWidget(self)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Apply modern styling
        self.apply_modern_styling()

        # Tabs: Basic / Image / PDF / CSS
        self.tabs = QTabWidget(self)
        # Basic Tab -> BasicPage
        self.tab_basic = BasicPage(self)
        # Wire initial values
        self.tab_basic.edit_input.setText(self.settings.get("input.file", ""))
        self.tab_basic.edit_dict.setText(self.settings.get("dictionary.file", ""))
        self.tab_basic.edit_output.setText(self.settings.get("output.file", ""))
        self.tab_basic.check_timestamp.setChecked(self.settings.get_output_add_timestamp())
        self.tab_basic.check_backup.setChecked(self.settings.get_backup_input())
        self.tab_basic.check_save_invalid.setChecked(self.settings.get_save_invalid_words())
        # Connect signals to existing handlers
        self.tab_basic.edit_input.editingFinished.connect(self.on_input_edited)
        self.tab_basic.btn_input.clicked.connect(self.choose_input)
        self.tab_basic.edit_dict.editingFinished.connect(self.on_dictionary_edited)
        self.tab_basic.btn_dict.clicked.connect(self.choose_dictionary)
        self.tab_basic.edit_output.editingFinished.connect(self.on_output_edited)
        self.tab_basic.btn_output.clicked.connect(self.choose_output)
        self.tab_basic.check_timestamp.stateChanged.connect(self.on_timestamp_changed)
        self.tab_basic.check_backup.stateChanged.connect(self.on_backup_changed)
        self.tab_basic.check_save_invalid.stateChanged.connect(self.on_save_invalid_changed)
        # Keep references consistent
        self.edit_input = self.tab_basic.edit_input
        self.edit_dict = self.tab_basic.edit_dict
        self.edit_output = self.tab_basic.edit_output
        self.check_timestamp = self.tab_basic.check_timestamp
        self.check_backup = self.tab_basic.check_backup
        self.check_save_invalid = self.tab_basic.check_save_invalid
        self.tabs.addTab(self.tab_basic, "Basic")
        # Image Tab -> ImagePage
        self.tab_image = ImagePage(self)
        self.tabs.addTab(self.tab_image, "Image")

        # PDF Tab -> PdfPage
        self.tab_pdf = PdfPage(self)
        self.tabs.addTab(self.tab_pdf, "PDF")

        # CSS Tab -> CssPage
        self.tab_css = CssPage(self)
        self.tabs.addTab(self.tab_css, "CSS")

        # Advanced Tab -> AdvancedPage
        self.tab_advanced = AdvancedPage(self)
        self.tabs.addTab(self.tab_advanced, "Advanced")

        # About Tab
        self.tab_about = AboutPage(self)
        self.tabs.addTab(self.tab_about, "About")

        # Reorder tabs to: Basic, CSS, Image, PDF, Advanced, About
        try:
            desired_order = [
                (self.tab_basic, "Basic"),
                (self.tab_css, "CSS"),
                (self.tab_image, "Image"),
                (self.tab_pdf, "PDF"),
                (self.tab_advanced, "Advanced"),
                (self.tab_about, "About"),
            ]
            # Remove all existing tabs
            while self.tabs.count() > 0:
                self.tabs.removeTab(0)
            # Add back in the desired order
            for widget, label in desired_order:
                self.tabs.addTab(widget, label)
        except Exception:
            # If anything goes wrong, fallback silently keeping existing order
            pass

        root.addWidget(self.tabs)
        # Prefer showing Basic tab first
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tab_basic))
        # Replace bottom controls with CommandPanel
        self.command_panel = CommandPanel(self)
        self.command_panel.restoreRequested.connect(self.restore_last_config)
        self.command_panel.importRequested.connect(self.import_config)
        self.command_panel.exportRequested.connect(self.export_config)
        self.command_panel.scrapeRequested.connect(self.run_conversion)
        root.addWidget(self.command_panel)

        self.setMinimumSize(800, 520)
        self.setCentralWidget(central)
        
        # Load presets and set tab enablement
        self.reload_presets()
        self.update_tab_enablement()
        # Sync tab inputs from config
        self.sync_image_from_config()
        self.sync_advanced_from_config()
        # Restore last PDF/CSS editor contents if present
        last_pdf_text = self.settings.get('output.pdf.preset_text', '')
        if last_pdf_text:
            self.tab_pdf.pdf_editor.setPlainText(last_pdf_text)
        last_css_text = self.settings.get('output.css.preset_text', '')
        if last_css_text:
            self.tab_css.css_editor.setPlainText(last_css_text)
        # Wire Image Tab controls to sync changes to config
        self.tab_image.width_changed.connect(self.sync_image_to_config)
        self.tab_image.zoom_changed.connect(self.sync_image_to_config)
        self.tab_image.background_changed.connect(self.sync_image_to_config)
        self.tab_image.jpg_quality_changed.connect(self.sync_image_to_config)
        self.tab_image.png_optimize_changed.connect(self.sync_image_to_config)
        self.tab_image.png_compress_changed.connect(self.sync_image_to_config)
        self.tab_image.png_transparent_changed.connect(self.sync_image_to_config)
        self.tab_image.webp_quality_changed.connect(self.sync_image_to_config)
        self.tab_image.webp_lossless_changed.connect(self.sync_image_to_config)
        self.tab_image.webp_transparent_changed.connect(self.sync_image_to_config)
        
        # Wire PDF Tab controls
        self.tab_pdf.preset_changed.connect(self.on_pdf_preset_changed)
        self.tab_pdf.save_clicked.connect(self.on_pdf_save_clicked)
        
        # Wire CSS Tab controls
        self.tab_css.preset_changed.connect(self.on_css_preset_changed)
        self.tab_css.save_clicked.connect(self.on_css_save_clicked)
        
        # Wire Advanced Tab controls
        self.tab_advanced.with_toc_changed.connect(self.on_with_toc_changed)
        self.tab_advanced.wkhtmltopdf_path_changed.connect(self.on_wkhtmltopdf_path_changed)
        
        # After UI ready, show normalization log if any
        if hasattr(self, 'log_message_later') and self.log_message_later:
            self.command_panel.appendLog(self.log_message_later)
            self.log_message_later = None

    def apply_modern_styling(self):
        """Apply modern PySide6 styling using built-in styles"""
        from PySide6.QtWidgets import QApplication
        
        # Use modern built-in style
        app = QApplication.instance()
        if app:
            app.setStyle('Fusion')  # Modern, cross-platform style
        
        # Only apply minimal custom styling for specific needs
        self.setStyleSheet("""
            QLabel[class="field-label"] {
                font-weight: bold;
            }
            
            QPushButton#scrape-button {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 12px 24px;
            }
            
            QPushButton#scrape-button:hover {
                background-color: #106ebe;
            }
            
            QPushButton#scrape-button:pressed {
                background-color: #005a9e;
            }
            
            QPushButton#scrape-button:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            /* Make progress bar visually distinct from Scrape button */
            QProgressBar {
                border: 1px solid #bdbdbd;
                border-radius: 6px;
                background-color: #e6e6e6;
                text-align: center;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #4caf50; /* green */
                border-radius: 6px;
            }
            
            QTextEdit {
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)

    def choose_input(self):
        current = self.edit_input.text()
        if current:
            # Try to resolve the current path (could be relative or absolute)
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    start_dir = str(self.project_root)
            except Exception:
                start_dir = str(self.project_root)
        else:
            start_dir = str(self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            self, "Select input file", start_dir,
            "Text/Markdown files (*.txt *.md);;JSON files (*.json);;Excel files (*.xlsx);;All files (*.*)"
        )
        if file:
            self.cm.set_input_file(file)
            self.edit_input.setText(self.settings.get("input.file"))
            # Also update output base name to match input base
            self.on_input_edited()

    def choose_dictionary(self):
        current = self.edit_dict.text()
        if current:
            # Try to resolve the current path (could be relative or absolute)
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    start_dir = str(self.project_root)
            except Exception:
                start_dir = str(self.project_root)
        else:
            start_dir = str(self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            self, "Select MDX dictionary", start_dir, "MDX Files (*.mdx)"
        )
        if file:
            self.cm.set_dictionary_file(file)
            self.edit_dict.setText(self.settings.get("dictionary.file"))

    def choose_output(self):
        current = self.edit_output.text()
        if current:
            # Try to resolve the current path (could be relative or absolute)
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    # Default to output directory from config
                    output_dir = self.settings.get("output.directory", "data/output")
                    if Path(output_dir).exists():
                        start_dir = str(Path(output_dir).resolve())
                    else:
                        start_dir = str(self.project_root / "data" / "output")
            except Exception:
                # Default to output directory from config
                output_dir = self.settings.get("output.directory", "data/output")
                if Path(output_dir).exists():
                    start_dir = str(Path(output_dir).resolve())
                else:
                    start_dir = str(self.project_root / "data" / "output")
        else:
            # Default to output directory from config
            output_dir = self.settings.get("output.directory", "data/output")
            if Path(output_dir).exists():
                start_dir = str(Path(output_dir).resolve())
            else:
                start_dir = str(self.project_root / "data" / "output")
        # Generate default filename based on input file
        default_filename = ""
        input_file = self.edit_input.text().strip()
        if input_file:
            try:
                input_path = self.settings.resolve_path(input_file)
                default_filename = input_path.stem  # Get filename without extension
            except Exception:
                pass
        
        file, _ = QFileDialog.getSaveFileName(
            self, "Select output file", 
            str(Path(start_dir) / (default_filename + ".html" if default_filename else "")),
            "HTML files (*.html);;PDF files (*.pdf);;JPG files (*.jpg);;PNG files (*.png);;WEBP files (*.webp);;All files (*.*)"
        )
        if file:
            self.cm.set_output_file(file)
            self.edit_output.setText(self.settings.get("output.file"))
            self.update_tab_enablement()

    def on_timestamp_changed(self, state):
        """Handle timestamp checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.settings.set_output_add_timestamp(is_checked)
    
    def on_backup_changed(self, state):
        """Handle backup checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.settings.set_backup_input(is_checked)
    
    def on_save_invalid_changed(self, state):
        """Handle save invalid words checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.settings.set_save_invalid_words(is_checked)
    
    def on_with_toc_changed(self):
        """Handle with_toc checkbox state change"""
        is_checked = self.tab_advanced.check_with_toc.isChecked()
        self.settings.set("advanced.with_toc", is_checked)
    
    def on_wkhtmltopdf_path_changed(self):
        """Handle wkhtmltopdf path change"""
        path_value = self.tab_advanced.get_wkhtmltopdf_path()
        self.settings.set("advanced.wkhtmltopdf_path", path_value or "auto")
    
    def closeEvent(self, event):
        """Handle application close event - save config before closing"""
        # Persist live PDF/CSS editor content on exit via SettingsService
        try:
            pdf_text = self.tab_pdf.pdf_editor.toPlainText()
            pdf_label = self.tab_pdf.pdf_combo.currentText()
            css_text = self.tab_css.css_editor.toPlainText()
            css_label = self.tab_css.css_combo.currentText()
            self.settings.persist_session_state(pdf_text, pdf_label, css_text, css_label)
        except Exception:
            pass
        self.settings.save()
        event.accept()

    def run_conversion(self):
        # Ensure latest values from inputs are synced to config before running
        # Avoid calling on_input_edited() here to prevent unintended renaming of output
        input_text = self.edit_input.text().strip()
        if input_text:
            self.settings.set_input_file(input_text)
        dict_text = self.edit_dict.text().strip()
        if dict_text:
            self.settings.set_dictionary_file(dict_text)
        output_text = self.edit_output.text().strip()
        if output_text:
            self.settings.set_output_file(output_text)
        # Persist Image tab values to config
        try:
            width = int(self.tab_image.img_width.text().strip() or '0')
            zoom = float(self.tab_image.img_zoom_value.text().strip() or '1.0')
            self.settings.set('output.image.width', width)
            self.settings.set('output.image.zoom', zoom)
        except Exception:
            pass
        self.settings.set('output.image.background', bool(self.tab_image.img_background.isChecked()))
        try:
            self.settings.set('output.image.jpg.quality', int(self.tab_image.jpg_quality_value.text().strip() or '85'))
        except Exception:
            pass
        self.settings.set('output.image.png.optimize', bool(self.tab_image.png_optimize.isChecked()))
        try:
            self.settings.set('output.image.png.compress_level', int(self.tab_image.png_compress_value.text().strip() or '9'))
        except Exception:
            pass
        self.settings.set('output.image.png.transparent_bg', bool(self.tab_image.png_transparent.isChecked()))
        try:
            self.settings.set('output.image.webp.quality', int(self.tab_image.webp_quality_value.text().strip() or '80'))
        except Exception:
            pass
        self.settings.set('output.image.webp.lossless', bool(self.tab_image.webp_lossless.isChecked()))
        self.settings.set('output.image.webp.transparent_bg', bool(self.tab_image.webp_transparent.isChecked()))

        output = self.settings.get("output.file")
        if not output:
            QMessageBox.warning(self, "Run", "Please set output file first.")
            return
        self.command_panel.btn_scrape.setEnabled(False)
        # Collect current preset editor contents
        pdf_text = self.tab_pdf.pdf_editor.toPlainText()
        css_text = self.tab_css.css_editor.toPlainText()
        self.worker = ConversionWorker(self.project_root, self.cm, pdf_text=pdf_text, css_text=css_text)
        self.worker.finished_sig.connect(self.on_run_finished)
        self.worker.error_sig.connect(self.on_run_error)
        self.worker.log_sig.connect(self.on_log)
        self.command_panel.setProgress(0)
        self.worker.start()

    def on_run_finished(self, message: str):
        self.command_panel.btn_scrape.setEnabled(True)
        self.command_panel.setProgress(100)
        self.command_panel.appendLog(f"✅ {message}")

    def on_run_error(self, message: str):
        self.command_panel.btn_scrape.setEnabled(True)
        self.command_panel.setProgress(0)
        self.command_panel.appendLog(f"❌ Error: {message}")

    def on_log(self, text: str):
        # Skip progress messages as they're redundant with progress bar
        if not text.startswith("Progress:"):
            self.command_panel.appendLog(text)

    # --- Config buttons ---
    def restore_last_config(self):
        try:
            # Reload latest config from disk and refresh GUI
            self.settings.load()
            self.sync_from_config()
            self.command_panel.appendLog("ℹ️ Restored last saved config.")
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to restore config: {e}")

    def import_config(self):
        start_dir = str((self.project_root / "data" / "configs").resolve())
        file, _ = QFileDialog.getOpenFileName(
            self, "Import config (TOML)", start_dir, "TOML files (*.toml)"
        )
        if not file:
            return
        try:
            from pathlib import Path as _P
            import tomllib as _tomllib
            with open(_P(file), "rb") as f:
                cfg = _tomllib.load(f)
            # Replace in-memory config only; normalize in-memory; persist on app close
            self.settings.replace_config(cfg)
            info = self.settings.get_normalize_info_once()
            self.sync_from_config()
            self.command_panel.appendLog(f"✅ Imported config applied: {file}")
            if info.get("changed"):
                removed, added, type_fixed = info.get("removed", 0), info.get("added", 0), info.get("type_fixed", 0)
                self.command_panel.appendLog(f"⚙️ Config normalized after import (removed: {removed}, added: {added}, type fixed: {type_fixed}). Please save to persist.")
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to import config: {e}")

    def export_config(self):
        start_dir = str((self.project_root / "data" / "configs").resolve())
        
        # Generate default filename based on input file
        default_filename = ""
        input_file = self.edit_input.text().strip()
        if input_file:
            try:
                input_path = self.settings.resolve_path(input_file)
                default_filename = input_path.stem  # Get filename without extension
            except Exception:
                pass
        
        file, _ = QFileDialog.getSaveFileName(
            self, "Export config as (TOML)", 
            str(Path(start_dir) / (default_filename + ".toml" if default_filename else "")),
            "TOML files (*.toml)"
        )
        if not file:
            return
        try:
            # Ensure current GUI edits are reflected to config
            input_text = self.edit_input.text().strip()
            if input_text:
                self.cm.set_input_file(input_text)
            dict_text = self.edit_dict.text().strip()
            if dict_text:
                self.cm.set_dictionary_file(dict_text)
            output_text = self.edit_output.text().strip()
            if output_text:
                self.cm.set_output_file(output_text)
            # Sync current PDF/CSS editors into config before export
            self.settings.set('output.pdf.preset_text', self.tab_pdf.pdf_editor.toPlainText())
            self.settings.set('output.pdf.preset_label', self.tab_pdf.pdf_combo.currentText())
            self.settings.set('output.css.preset_text', self.tab_css.css_editor.toPlainText())
            self.settings.set('output.css.preset_label', self.tab_css.css_combo.currentText())
            # Sync current Image Tab settings into config before export
            self.sync_image_to_config()
            # Sync checkbox states to ensure consistency
            self.settings.set_output_add_timestamp(self.check_timestamp.isChecked())
            self.settings.set_backup_input(self.check_backup.isChecked())
            self.settings.set_save_invalid_words(self.check_save_invalid.isChecked())
            # Validate before export; log issues but proceed
            result = self.cm.validate()
            if not result.is_valid:
                problems = "\n".join(result.errors)
                self.command_panel.appendLog("⚠️ Config validation issues before export:\n" + problems)
            # Write selected path
            from pathlib import Path as _P
            from mdxscraper.config import config_manager as _cm
            data = self.settings.get_config_dict()
            content = _cm.tomli_w.dumps(data)
            p = _P(file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.command_panel.appendLog(f"✅ Exported config to: {file}")
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to export config: {e}")

    # --- Field edit handlers ---
    def on_input_edited(self):
        text = self.edit_input.text().strip()
        if text:
            self.settings.set_input_file(text)
            # Auto-adjust output filename base to match input base, keeping path and suffix
            current_output = self.settings.get("output.file")
            if current_output:
                out_path = Path(current_output)
                new_base = Path(text).stem
                new_name = new_base + out_path.suffix
                new_output_path = out_path.with_name(new_name)
                self.settings.set_output_file(str(new_output_path))
                # Reflect change in UI
                self.edit_output.setText(self.settings.get("output.file"))

    def on_dictionary_edited(self):
        text = self.edit_dict.text().strip()
        if text:
            self.settings.set_dictionary_file(text)

    def on_output_edited(self):
        text = self.edit_output.text().strip()
        if text:
            self.settings.set_output_file(text)
        self.update_tab_enablement()

    def sync_from_config(self):
        # Refresh GUI fields from in-memory config
        self.edit_input.setText(self.settings.get("input.file", ""))
        self.edit_dict.setText(self.settings.get("dictionary.file", ""))
        self.edit_output.setText(self.settings.get("output.file", ""))
        self.check_timestamp.setChecked(self.settings.get_output_add_timestamp())
        self.check_backup.setChecked(self.settings.get_backup_input())
        self.check_save_invalid.setChecked(self.settings.get_save_invalid_words())
        self.update_tab_enablement()
        self.sync_image_from_config()
        self.sync_advanced_from_config()
        # Sync PDF/CSS editors and preset labels from config
        try:
            pdf_text = self.settings.get('output.pdf.preset_text', '') or ''
            self.tab_pdf.pdf_editor.setPlainText(pdf_text)
            pdf_label = self.settings.get('output.pdf.preset_label', '') or ''
            if pdf_label:
                for i in range(self.tab_pdf.pdf_combo.count()):
                    if self.tab_pdf.pdf_combo.itemText(i) == pdf_label:
                        self.tab_pdf.pdf_combo.setCurrentIndex(i)
                        break
            css_text = self.settings.get('output.css.preset_text', '') or ''
            self.tab_css.css_editor.setPlainText(css_text)
            css_label = self.settings.get('output.css.preset_label', '') or ''
            if css_label:
                for i in range(self.tab_css.css_combo.count()):
                    if self.tab_css.css_combo.itemText(i) == css_label:
                        self.tab_css.css_combo.setCurrentIndex(i)
                        break
        except Exception:
            # Non-fatal: keep going if presets cannot be synced
            pass

    def sync_image_from_config(self):
        # Populate image fields from config defaults
        get = self.cm.get
        self.tab_image.img_width.setText(str(get("output.image.width", 0)))
        zoom = float(get("output.image.zoom", 1.0))
        self.tab_image.img_zoom_slider.setValue(int(round(zoom * 10)))
        self.tab_image.img_zoom_value.setText(f"{zoom:.1f}")
        self.tab_image.img_background.setChecked(bool(get("output.image.background", True)))
        jpg_q = int(get("output.image.jpg.quality", 85))
        self.tab_image.jpg_quality_slider.setValue(jpg_q)
        self.tab_image.jpg_quality_value.setText(str(jpg_q))
        self.tab_image.png_optimize.setChecked(bool(get("output.image.png.optimize", True)))
        png_c = int(get("output.image.png.compress_level", 9))
        self.tab_image.png_compress_slider.setValue(png_c)
        self.tab_image.png_compress_value.setText(str(png_c))
        self.tab_image.png_transparent.setChecked(bool(get("output.image.png.transparent_bg", False)))
        webp_q = int(get("output.image.webp.quality", 80))
        self.tab_image.webp_quality_slider.setValue(webp_q)
        self.tab_image.webp_quality_value.setText(str(webp_q))
        self.tab_image.webp_lossless.setChecked(bool(get("output.image.webp.lossless", False)))
        self.tab_image.webp_transparent.setChecked(bool(get("output.image.webp.transparent_bg", False)))

    def sync_image_to_config(self):
        # Sync current Image Tab GUI values to config
        try:
            # General settings
            width_text = self.tab_image.img_width.text().strip()
            if width_text:
                width = int(width_text)
                self.settings.set("output.image.width", width)
            else:
                self.settings.set("output.image.width", 0)
            
            zoom = self.tab_image.img_zoom_slider.value() / 10.0
            self.settings.set("output.image.zoom", zoom)
            
            self.settings.set("output.image.background", self.tab_image.img_background.isChecked())
            
            # JPG settings
            jpg_quality = self.tab_image.jpg_quality_slider.value()
            self.settings.set("output.image.jpg.quality", jpg_quality)
            
            # PNG settings
            self.settings.set("output.image.png.optimize", self.tab_image.png_optimize.isChecked())
            png_compress = self.tab_image.png_compress_slider.value()
            self.settings.set("output.image.png.compress_level", png_compress)
            self.settings.set("output.image.png.transparent_bg", self.tab_image.png_transparent.isChecked())
            
            # WEBP settings
            webp_quality = self.tab_image.webp_quality_slider.value()
            self.settings.set("output.image.webp.quality", webp_quality)
            self.settings.set("output.image.webp.lossless", self.tab_image.webp_lossless.isChecked())
            self.settings.set("output.image.webp.transparent_bg", self.tab_image.webp_transparent.isChecked())
            
        except (ValueError, TypeError) as e:
            # Ignore invalid values during typing, they'll be handled on export
            pass

    def sync_advanced_from_config(self):
        """Populate advanced fields from config defaults"""
        get = self.cm.get
        self.tab_advanced.check_with_toc.setChecked(bool(get("advanced.with_toc", True)))
        self.tab_advanced.set_wkhtmltopdf_path(str(get("advanced.wkhtmltopdf_path", "auto")))


    # ---- Presets loading/saving ----
    def reload_presets(self):
        # PDF presets
        self.tab_pdf.pdf_combo.blockSignals(True)
        self.tab_pdf.pdf_combo.clear()
        for label, path in self.presets.iter_presets('pdf'):
            self.tab_pdf.pdf_combo.addItem(label, userData=str(path))
        self.tab_pdf.pdf_combo.blockSignals(False)
        if self.tab_pdf.pdf_combo.count() > 0:
            # Prefer 'default' built-in if present, else first
            preferred_idx = 0
            for i in range(self.tab_pdf.pdf_combo.count()):
                txt = self.tab_pdf.pdf_combo.itemText(i).lower()
                if txt.startswith('default'):
                    preferred_idx = i
                    break
            self.tab_pdf.pdf_combo.setCurrentIndex(preferred_idx)
            self.on_pdf_preset_changed(self.tab_pdf.pdf_combo.currentText())
        # CSS presets
        self.tab_css.css_combo.blockSignals(True)
        self.tab_css.css_combo.clear()
        for label, path in self.presets.iter_presets('css'):
            self.tab_css.css_combo.addItem(label, userData=str(path))
        self.tab_css.css_combo.blockSignals(False)
        if self.tab_css.css_combo.count() > 0:
            # Prefer 'original' built-in if present, else first
            preferred_idx = 0
            for i in range(self.tab_css.css_combo.count()):
                txt = self.tab_css.css_combo.itemText(i).lower()
                if txt.startswith('original'):
                    preferred_idx = i
                    break
            self.tab_css.css_combo.setCurrentIndex(preferred_idx)
            self.on_css_preset_changed(self.tab_css.css_combo.currentText())

    def _iter_presets(self, kind: str):
        # Backward compatibility shim if needed elsewhere
        yield from self.presets.iter_presets(kind)

    def on_pdf_preset_changed(self, label: str):
        idx = self.tab_pdf.pdf_combo.currentIndex()
        path = self.tab_pdf.pdf_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                self.tab_pdf.pdf_editor.setPlainText(text)
                    # Persist selection and text in config
                self.settings.set('output.pdf.preset_label', label)
                self.settings.set('output.pdf.preset_text', text)
            except Exception as e:
                self.command_panel.appendLog(f"❌ Failed to load PDF preset: {e}")

    def on_css_preset_changed(self, label: str):
        idx = self.tab_css.css_combo.currentIndex()
        path = self.tab_css.css_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                self.tab_css.css_editor.setPlainText(text)
                    # Persist selection and text in config
                self.settings.set('output.css.preset_label', label)
                self.settings.set('output.css.preset_text', text)
            except Exception as e:
                self.command_panel.appendLog(f"❌ Failed to load CSS preset: {e}")

    def on_pdf_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'pdf').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save PDF preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            text = self.tab_pdf.pdf_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set('output.pdf.preset_label', Path(file).stem)
            self.settings.set('output.pdf.preset_text', text)
            self.command_panel.appendLog(f"✅ Saved PDF preset: {file}")
            self.reload_presets()
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to save PDF preset: {e}")

    def on_css_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'css').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save CSS preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            text = self.tab_css.css_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set('output.css.preset_label', Path(file).stem)
            self.settings.set('output.css.preset_text', text)
            self.command_panel.appendLog(f"✅ Saved CSS preset: {file}")
            self.reload_presets()
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to save CSS preset: {e}")

    def update_tab_enablement(self):
        out = self.settings.get("output.file", "")
        enable = self.settings.get_tab_enablement(out)
        self.tabs.setTabEnabled(self.tabs.indexOf(self.tab_pdf), enable.get('pdf', False))
        self.tabs.setTabEnabled(self.tabs.indexOf(self.tab_image), enable.get('image', False))
        # CSS always enabled by service contract

def run_gui():
    import sys
    app = QApplication(sys.argv)
    
    # Set application icon
    root = Path(__file__).resolve().parents[3]
    icon_path = root / "src" / "mdxscraper" / "gui" / "assets" / "app_icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    w = MainWindow(root)
    w.resize(640, 360)
    w.show()
    sys.exit(app.exec())
