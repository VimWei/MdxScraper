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
        info = self.settings.get_normalize_info_once()
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
        # Initialize with configuration
        basic_config = self.settings.get_basic_config()
        self.tab_basic.set_config(basic_config)
        # Connect signals to existing handlers
        self.tab_basic.edit_input.editingFinished.connect(self.on_input_edited)
        self.tab_basic.btn_input.clicked.connect(self.choose_input)
        self.tab_basic.edit_dict.editingFinished.connect(self.on_dictionary_edited)
        self.tab_basic.btn_dict.clicked.connect(self.choose_dictionary)
        self.tab_basic.edit_output.editingFinished.connect(self.on_output_edited)
        self.tab_basic.btn_output.clicked.connect(self.choose_output)
        self.tab_basic.check_timestamp.stateChanged.connect(self.sync_basic_to_config)
        self.tab_basic.check_backup.stateChanged.connect(self.sync_basic_to_config)
        self.tab_basic.check_save_invalid.stateChanged.connect(self.sync_basic_to_config)
        # new with_toc checkbox in Basic
        if hasattr(self.tab_basic, 'check_with_toc'):
            self.tab_basic.check_with_toc.stateChanged.connect(self.sync_basic_to_config)
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

        # Load presets
        self.reload_presets(auto_select_default=False)
        # Sync all pages from configuration using unified methods
        self.sync_from_config()
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
        self.pdf_dirty = False
        self.css_dirty = False
        # Guards to avoid treating programmatic editor updates as user edits
        self._updating_pdf_editor = False
        self._updating_css_editor = False
        self.last_pdf_label = ''
        self.last_css_label = ''
        self.tab_pdf.preset_changed.connect(self.on_pdf_preset_changed)
        self.tab_pdf.save_clicked.connect(self.on_pdf_save_clicked)
        self.tab_pdf.refresh_clicked.connect(self.on_pdf_refresh_clicked)
        self.tab_pdf.text_changed.connect(self.on_pdf_text_changed)

        # Wire CSS Tab controls
        self.tab_css.preset_changed.connect(self.on_css_preset_changed)
        self.tab_css.save_clicked.connect(self.on_css_save_clicked)
        self.tab_css.refresh_clicked.connect(self.on_css_refresh_clicked)
        self.tab_css.text_changed.connect(self.on_css_text_changed)

        # Wire Advanced Tab controls
        self.tab_advanced.wkhtmltopdf_path_changed.connect(self.sync_advanced_to_config)

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
            self.settings.set_input_file(file)
            self.edit_input.setText(self.settings.get("basic.input_file"))
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
            self.settings.set_dictionary_file(file)
            self.edit_dict.setText(self.settings.get("basic.dictionary_file"))

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
            self.settings.set_output_file(file)
            self.edit_output.setText(self.settings.get("basic.output_file"))

    def closeEvent(self, event):
        """Handle application close event - save config before closing"""
        # Sync all page configurations to settings before saving
        try:
            # Sync all page configurations to settings before saving
            self.sync_basic_to_config()
            self.sync_image_to_config()
            self.sync_advanced_to_config()
            # Autosave Untitled when dirty
            self.autosave_untitled_if_needed()
            # Only labels persisted
            self.sync_pdf_to_config()
            self.sync_css_to_config()
        except Exception:
            pass

        # Save all configuration to disk
        self.settings.save()
        event.accept()

    def run_conversion(self):
        # Sync all page configurations to settings before running conversion
        self.sync_basic_to_config()
        self.sync_image_to_config()
        self.sync_advanced_to_config()
        # Autosave Untitled when dirty before running
        self.autosave_untitled_if_needed()
        self.sync_pdf_to_config()
        self.sync_css_to_config()

        output = self.settings.get("basic.output_file")
        if not output:
            QMessageBox.warning(self, "Run", "Please set output file first.")
            return
        self.command_panel.btn_scrape.setEnabled(False)
        # Collect current preset editor contents
        pdf_text = self.resolve_effective_preset_text('pdf')
        css_text = self.resolve_effective_preset_text('css')
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
            # Reload presets first, then sync from config to preserve preset selection
            self.reload_presets(auto_select_default=False)
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
            # Before import: autosave Untitled if dirty
            try:
                self.autosave_untitled_if_needed()
            except Exception:
                pass
            # Replace in-memory config only; normalize in-memory; persist on app close
            self.settings.replace_config(cfg)
            info = self.settings.get_normalize_info_once()
            # Reload presets first, then sync from config to preserve preset selection
            # 统一机制：reload_presets 会通过 select_label_and_load 触发信号加载内容
            self.reload_presets(auto_select_default=False)
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
            # Sync all page configurations to settings before export
            self.sync_basic_to_config()
            self.sync_image_to_config()
            self.sync_advanced_to_config()
            # First sync current combo selections -> config
            self.sync_pdf_to_config()
            self.sync_css_to_config()
            # Then autosave Untitled if dirty, which will also set label to 'Untitled'
            self.autosave_untitled_if_needed()
            # Validate before export; log issues but proceed
            result = self.settings.validate()
            if not result.is_valid:
                problems = "\n".join(result.errors)
                self.command_panel.appendLog("⚠️ Config validation issues before export:\n" + problems)
            # Write selected path
            from pathlib import Path as _P
            from mdxscraper.config import config_manager as _cm
            data = self.settings.get_config_dict()
            # Freeze Untitled: if label is 'Untitled' OR current tab is dirty, create a timestamped snapshot and point label to it
            try:
                # Reload labels from settings after potential autosave
                pdf_label = str(self.settings.get('pdf.preset_label', '') or '')
                css_label = str(self.settings.get('css.preset_label', '') or '')
                new_pdf_label = None
                new_css_label = None
                if self.pdf_dirty or pdf_label.strip().lower() == 'untitled':
                    pdf_text = self.tab_pdf.pdf_editor.toPlainText()
                    snap = self.presets.create_untitled_snapshot('pdf', pdf_text)
                    # point label to snapshot stem
                    self.settings.set('pdf.preset_label', snap.stem)
                    data.setdefault('pdf', {})['preset_label'] = snap.stem
                    self.command_panel.appendLog(f"📌 Frozen PDF Untitled to: {self.settings.to_relative(snap)}")
                    new_pdf_label = snap.stem
                if self.css_dirty or css_label.strip().lower() == 'untitled':
                    css_text = self.tab_css.css_editor.toPlainText()
                    snap = self.presets.create_untitled_snapshot('css', css_text)
                    self.settings.set('css.preset_label', snap.stem)
                    data.setdefault('css', {})['preset_label'] = snap.stem
                    self.command_panel.appendLog(f"📌 Frozen CSS Untitled to: {self.settings.to_relative(snap)}")
                    new_css_label = snap.stem
            except Exception as fe:
                self.command_panel.appendLog(f"⚠️ Failed to freeze Untitled: {fe}")
            content = _cm.tomli_w.dumps(data)
            p = _P(file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.command_panel.appendLog(f"✅ Exported config to: {file}")
            # If we created snapshots, reload presets and select the new labels via unified method
            try:
                if (locals().get('new_pdf_label') or locals().get('new_css_label')):
                    self.reload_presets(auto_select_default=False)
                    if locals().get('new_pdf_label'):
                        self.select_label_and_load('pdf', new_pdf_label)
                        self.pdf_dirty = False
                        self.tab_pdf.show_dirty(False)
                    if locals().get('new_css_label'):
                        self.select_label_and_load('css', new_css_label)
                        self.css_dirty = False
                        self.tab_css.show_dirty(False)
            except Exception:
                pass
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to export config: {e}")

    # --- Field edit handlers ---
    def on_input_edited(self):
        text = self.edit_input.text().strip()
        if text:
            self.settings.set_input_file(text)
            # Auto-adjust output filename base to match input base, keeping path and suffix
            current_output = self.settings.get("basic.output_file")
            if current_output:
                out_path = Path(current_output)
                new_base = Path(text).stem
                new_name = new_base + out_path.suffix
                new_output_path = out_path.with_name(new_name)
                self.settings.set_output_file(str(new_output_path))
                # Reflect change in UI
                self.edit_output.setText(self.settings.get("basic.output_file"))

    def on_dictionary_edited(self):
        text = self.edit_dict.text().strip()
        if text:
            self.settings.set_dictionary_file(text)

    def on_output_edited(self):
        text = self.edit_output.text().strip()
        if text:
            self.settings.set_output_file(text)

    def sync_from_config(self):
        """Sync all pages from configuration using unified methods"""
        # Sync Basic page
        basic_config = self.settings.get_basic_config()
        self.tab_basic.set_config(basic_config)

        # Sync Image page
        self.sync_image_from_config()

        # Sync Advanced page
        self.sync_advanced_from_config()

        # Sync PDF page
        pdf_config = self.settings.get_pdf_config()
        self.tab_pdf.set_config(pdf_config)

        # Sync CSS page
        css_config = self.settings.get_css_config()
        self.tab_css.set_config(css_config)

        # Post-check: if configured labels are not present, enter * Untitled with empty editor
        try:
            # PDF label existence check (full label or base-name)
            cfg_pdf_label = (pdf_config.preset_label or '').strip()
            found_pdf = False
            for i in range(self.tab_pdf.pdf_combo.count()):
                item = self.tab_pdf.pdf_combo.itemText(i)
                base = item.split(' [', 1)[0]
                if item == cfg_pdf_label or base == cfg_pdf_label:
                    found_pdf = True
                    break
            if not found_pdf and cfg_pdf_label:
                self._enter_untitled_state('pdf', clear_editor=True)
                try:
                    self.settings.set('pdf.preset_label', '')
                except Exception:
                    pass
            # CSS label existence check (full label or base-name)
            cfg_css_label = (css_config.preset_label or '').strip()
            found_css = False
            for i in range(self.tab_css.css_combo.count()):
                item = self.tab_css.css_combo.itemText(i)
                base = item.split(' [', 1)[0]
                if item == cfg_css_label or base == cfg_css_label:
                    found_css = True
                    break
            if not found_css and cfg_css_label:
                self._enter_untitled_state('css', clear_editor=True)
                try:
                    self.settings.set('css.preset_label', '')
                except Exception:
                    pass
        except Exception:
            pass

        # Ensure initial load: if label is set and editor is empty, load from current selection
        try:
            if (self.settings.get('pdf.preset_label') or '').strip():
                if not self.tab_pdf.pdf_editor.toPlainText().strip():
                    idx = self.tab_pdf.pdf_combo.currentIndex()
                    path = self.tab_pdf.pdf_combo.itemData(idx)
                    if path:
                        text = self.presets.load_preset_text(Path(path))
                        self._updating_pdf_editor = True
                        try:
                            self.tab_pdf.pdf_editor.setPlainText(text)
                        finally:
                            self._updating_pdf_editor = False
                        self.pdf_dirty = False
                        self.tab_pdf.show_dirty(False)
            if (self.settings.get('css.preset_label') or '').strip():
                if not self.tab_css.css_editor.toPlainText().strip():
                    idx = self.tab_css.css_combo.currentIndex()
                    path = self.tab_css.css_combo.itemData(idx)
                    if path:
                        text = self.presets.load_preset_text(Path(path))
                        self._updating_css_editor = True
                        try:
                            self.tab_css.css_editor.setPlainText(text)
                        finally:
                            self._updating_css_editor = False
                        self.css_dirty = False
                        self.tab_css.show_dirty(False)
        except Exception:
            pass

    def sync_image_from_config(self):
        """Sync Image page from configuration using unified method"""
        image_config = self.settings.get_image_config()
        self.tab_image.set_config(image_config)

    def sync_image_to_config(self):
        """Sync Image page to configuration using unified method"""
        try:
            image_config = self.tab_image.get_config()
            self.settings.update_image_config(image_config)
        except (ValueError, TypeError) as e:
            # Ignore invalid values during typing, they'll be handled on export
            pass

    def sync_advanced_from_config(self):
        """Sync Advanced page from configuration using unified method"""
        advanced_config = self.settings.get_advanced_config()
        self.tab_advanced.set_config(advanced_config)

    def sync_advanced_to_config(self):
        """Sync Advanced page to configuration using unified method"""
        advanced_config = self.tab_advanced.get_config()
        self.settings.update_advanced_config(advanced_config)

    def sync_basic_to_config(self):
        """Sync Basic page to configuration using unified method"""
        basic_config = self.tab_basic.get_config()
        self.settings.update_basic_config(basic_config)

    def sync_pdf_to_config(self):
        """Sync PDF page to configuration using unified method"""
        pdf_config = self.tab_pdf.get_config()
        self.settings.update_pdf_config(pdf_config)

    def sync_css_to_config(self):
        """Sync CSS page to configuration using unified method"""
        css_config = self.tab_css.get_config()
        self.settings.update_css_config(css_config)

    # ---- Presets loading/saving ----
    def reload_presets(self, auto_select_default: bool = True):
        # Preserve currently configured labels
        current_pdf_label = str(self.settings.get('pdf.preset_label', '') or '')
        current_css_label = str(self.settings.get('css.preset_label', '') or '')

        # PDF presets - 使用统一方法选择，让信号自然触发
        self.tab_pdf.pdf_combo.clear()
        for label, path in self.presets.iter_presets('pdf'):
            self.tab_pdf.pdf_combo.addItem(label, userData=str(path))
        
        # 使用统一方法选择预设，避免手动信号阻断
        if current_pdf_label:
            self.select_label_and_load('pdf', current_pdf_label)
        elif self.tab_pdf.pdf_combo.count() > 0 and auto_select_default:
            # 可选默认选择（保留时通常不使用）
            preferred_label = None
            for i in range(self.tab_pdf.pdf_combo.count()):
                txt = self.tab_pdf.pdf_combo.itemText(i).lower()
                if txt.startswith('default'):
                    preferred_label = self.tab_pdf.pdf_combo.itemText(i)
                    break
            if preferred_label:
                self.select_label_and_load('pdf', preferred_label)

        # CSS presets - 使用统一方法选择，让信号自然触发
        self.tab_css.css_combo.clear()
        for label, path in self.presets.iter_presets('css'):
            self.tab_css.css_combo.addItem(label, userData=str(path))
        
        # 使用统一方法选择预设，避免手动信号阻断
        if current_css_label:
            self.select_label_and_load('css', current_css_label)
        elif self.tab_css.css_combo.count() > 0 and auto_select_default:
            preferred_label = None
            for i in range(self.tab_css.css_combo.count()):
                txt = self.tab_css.css_combo.itemText(i).lower()
                if txt.startswith('original'):
                    preferred_label = self.tab_css.css_combo.itemText(i)
                    break
            if preferred_label:
                self.select_label_and_load('css', preferred_label)

    def _iter_presets(self, kind: str):
        # Backward compatibility shim if needed elsewhere
        yield from self.presets.iter_presets(kind)

    def on_pdf_preset_changed(self, label: str):
        idx = self.tab_pdf.pdf_combo.currentIndex()
        if idx < 0:
            # No selection -> * Untitled state: ignore load
            return
        path = self.tab_pdf.pdf_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                # Programmatic update: suppress text_changed side effects
                self._updating_pdf_editor = True
                try:
                    self.tab_pdf.pdf_editor.setPlainText(text)
                finally:
                    self._updating_pdf_editor = False
                # Persist selection label only
                self.settings.set('pdf.preset_label', label)
                self.pdf_dirty = False
                self.last_pdf_label = label
                self.tab_pdf.show_dirty(False)
            except Exception as e:
                # Enter * Untitled state with empty editor per spec
                self.command_panel.appendLog(f"❌ Failed to load PDF preset: {e}. Switched to * Untitled.")
                self._enter_untitled_state('pdf', clear_editor=True)
                # Clear invalid label from settings to avoid repeated failures
                try:
                    self.settings.set('pdf.preset_label', '')
                except Exception:
                    pass

    def on_css_preset_changed(self, label: str):
        idx = self.tab_css.css_combo.currentIndex()
        if idx < 0:
            # No selection -> * Untitled state: ignore load
            return
        path = self.tab_css.css_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                self._updating_css_editor = True
                try:
                    self.tab_css.css_editor.setPlainText(text)
                finally:
                    self._updating_css_editor = False
                # Persist selection label only
                self.settings.set('css.preset_label', label)
                self.css_dirty = False
                self.last_css_label = label
                self.tab_css.show_dirty(False)
            except Exception as e:
                # Enter * Untitled state with empty editor per spec
                self.command_panel.appendLog(f"❌ Failed to load CSS preset: {e}. Switched to * Untitled.")
                self._enter_untitled_state('css', clear_editor=True)
                try:
                    self.settings.set('css.preset_label', '')
                except Exception:
                    pass

    def on_pdf_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'pdf').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save PDF preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            text = self.tab_pdf.pdf_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set('pdf.preset_label', Path(file).stem)
            self.command_panel.appendLog(f"✅ Saved PDF preset: {file}")
            # Reload presets and select the saved label via unified method
            saved_label = Path(file).stem
            self.reload_presets(auto_select_default=False)
            self.select_label_and_load('pdf', saved_label)
            self.settings.set('pdf.preset_label', saved_label)
            self.sync_pdf_to_config()
            self.pdf_dirty = False
            self.last_pdf_label = saved_label
            self.tab_pdf.show_dirty(False)
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
            self.settings.set('css.preset_label', Path(file).stem)
            self.command_panel.appendLog(f"✅ Saved CSS preset: {file}")
            # Reload presets and select the saved label via unified method
            saved_label = Path(file).stem
            self.reload_presets(auto_select_default=False)
            self.select_label_and_load('css', saved_label)
            self.settings.set('css.preset_label', saved_label)
            self.sync_css_to_config()
            self.css_dirty = False
            self.last_css_label = saved_label
            self.tab_css.show_dirty(False)
        except Exception as e:
            self.command_panel.appendLog(f"❌ Failed to save CSS preset: {e}")

    def on_pdf_text_changed(self):
        if self._updating_pdf_editor:
            return
        # Enter * Untitled state due to user edit, keep editor content
        self._enter_untitled_state('pdf', clear_editor=False)

    def on_css_text_changed(self):
        if self._updating_css_editor:
            return
        # Enter * Untitled state due to user edit, keep editor content
        self._enter_untitled_state('css', clear_editor=False)

    def on_pdf_refresh_clicked(self):
        self.reload_presets(auto_select_default=False)

    def on_css_refresh_clicked(self):
        self.reload_presets(auto_select_default=False)

    def resolve_effective_preset_text(self, kind: str) -> str:
        """Per spec: Scrape uses editor content directly (autosave handled by caller)."""
        try:
            if kind == 'pdf':
                return self.tab_pdf.pdf_editor.toPlainText()
            else:
                return self.tab_css.css_editor.toPlainText()
        except Exception:
            return ''


    def autosave_untitled_if_needed(self):
        if self.pdf_dirty:
            self.autosave_untitled('pdf')
        if self.css_dirty:
            self.autosave_untitled('css')

    def autosave_untitled(self, kind: str):
        try:
            if kind == 'pdf':
                text = self.tab_pdf.pdf_editor.toPlainText()
                out = (self.project_root / 'data' / 'configs' / 'pdf' / 'Untitled.toml')
                self.presets.save_preset_text(out, text)
                self.settings.set('pdf.preset_label', 'Untitled')
                self.pdf_dirty = False
                self.tab_pdf.show_dirty(False)
                # Ensure combo shows 'Untitled' after autosave
                self.reload_presets(auto_select_default=False)
                self.select_label_and_load('pdf', 'Untitled')
            else:
                text = self.tab_css.css_editor.toPlainText()
                out = (self.project_root / 'data' / 'configs' / 'css' / 'Untitled.toml')
                self.presets.save_preset_text(out, text)
                self.settings.set('css.preset_label', 'Untitled')
                self.css_dirty = False
                self.tab_css.show_dirty(False)
                # Ensure combo shows 'Untitled' after autosave
                self.reload_presets(auto_select_default=False)
                self.select_label_and_load('css', 'Untitled')
        except Exception as e:
            self.command_panel.appendLog(f"⚠️ Failed to autosave Untitled: {e}")

    # --- Unified preset selection and * Untitled state helpers ---
    def _enter_untitled_state(self, kind: str, clear_editor: bool = True) -> None:
        """Enter * Untitled state: combo shows no selection (-1), dirty shown.

        If clear_editor is True, editor is cleared (e.g., load failure). If False,
        keep current editor content (e.g., user edits).
        """
        if kind == 'pdf':
            combo = self.tab_pdf.pdf_combo
            editor = self.tab_pdf.pdf_editor
            show_dirty = self.tab_pdf.show_dirty
            if clear_editor:
                self._updating_pdf_editor = True
                try:
                    editor.setPlainText("")
                finally:
                    self._updating_pdf_editor = False
            combo.setCurrentIndex(-1)
            self.pdf_dirty = True
            show_dirty(True)
        else:
            combo = self.tab_css.css_combo
            editor = self.tab_css.css_editor
            show_dirty = self.tab_css.show_dirty
            if clear_editor:
                self._updating_css_editor = True
                try:
                    editor.setPlainText("")
                finally:
                    self._updating_css_editor = False
            combo.setCurrentIndex(-1)
            self.css_dirty = True
            show_dirty(True)

    def select_label_and_load(self, kind: str, label: str) -> None:
        """Unified entry to select a preset by label and trigger load via signal."""
        combo = self.tab_pdf.pdf_combo if kind == 'pdf' else self.tab_css.css_combo
        matched_index = -1
        for i in range(combo.count()):
            if combo.itemText(i) == label:
                matched_index = i
                break
        if matched_index >= 0:
            combo.setCurrentIndex(matched_index)
            return
        # Not found: enter * Untitled state (keep content) and clear invalid config label
        self._enter_untitled_state(kind, clear_editor=False)
        try:
            if kind == 'pdf':
                self.settings.set('pdf.preset_label', '')
            else:
                self.settings.set('css.preset_label', '')
        except Exception:
            pass

    # update_tab_enablement removed: tabs are always enabled now

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
