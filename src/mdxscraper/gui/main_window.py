from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.coordinators import (
    ConfigCoordinator,
    ConversionCoordinator,
    FileCoordinator,
    PresetCoordinator,
)
from mdxscraper.gui.components.command_panel import CommandPanel
from mdxscraper.gui.components.log_panel import LogPanel
from mdxscraper.gui.pages.about_page import AboutPage
from mdxscraper.gui.pages.advanced_page import AdvancedPage
from mdxscraper.gui.pages.basic_page import BasicPage
from mdxscraper.gui.pages.css_page import CssPage
from mdxscraper.gui.pages.image_page import ImagePage
from mdxscraper.gui.pages.pdf_page import PdfPage
from mdxscraper.gui.styles.theme_loader import ThemeLoader
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.version import get_app_title


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        self.setWindowTitle(get_app_title())
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
        # Coordinators (incremental adoption)
        self.preset_coordinator = PresetCoordinator(self.presets, self.settings)
        self.filec = FileCoordinator(self.settings, project_root)
        self.cfgc = ConfigCoordinator(self.settings, self.presets)
        self.convc = ConversionCoordinator(self.settings, self.presets, project_root, self.cm)
        # Announce normalization result once
        info = self.settings.get_normalize_info_once()
        if info.get("changed"):
            removed, added, type_fixed = (
                info.get("removed", 0),
                info.get("added", 0),
                info.get("type_fixed", 0),
            )
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
        self.tabs.setMinimumHeight(200)
        # Basic Tab -> BasicPage
        self.tab_basic = BasicPage(self)
        # Initialize with configuration
        basic_config = self.settings.get_basic_config()
        self.tab_basic.set_config(basic_config)
        # Connect signals to existing handlers
        self.tab_basic.edit_input.editingFinished.connect(self.on_input_edited)
        self.tab_basic.btn_input.clicked.connect(lambda: self.filec.choose_input(self))
        self.tab_basic.edit_dict.editingFinished.connect(self.on_dictionary_edited)
        self.tab_basic.btn_dict.clicked.connect(lambda: self.filec.choose_dictionary(self))
        self.tab_basic.edit_output.editingFinished.connect(self.on_output_edited)
        self.tab_basic.btn_output.clicked.connect(lambda: self.filec.choose_output(self))
        self.tab_basic.check_timestamp.stateChanged.connect(
            lambda: self.cfgc.sync_all_to_config(self)
        )
        self.tab_basic.check_backup.stateChanged.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_basic.check_save_invalid.stateChanged.connect(
            lambda: self.cfgc.sync_all_to_config(self)
        )
        # new with_toc checkbox in Basic
        if hasattr(self.tab_basic, "check_with_toc"):
            self.tab_basic.check_with_toc.stateChanged.connect(
                lambda: self.cfgc.sync_all_to_config(self)
            )
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

        # Wire preset-related signals EARLY (before reload_presets) so initial selection loads editor
        self.pdf_dirty = False
        self.css_dirty = False
        self._updating_pdf_editor = False
        self._updating_css_editor = False
        self.last_pdf_label = ""
        self.last_css_label = ""
        self.tab_pdf.preset_changed.connect(self.on_pdf_preset_changed)
        self.tab_pdf.text_changed.connect(self.on_pdf_text_changed)
        self.tab_css.preset_changed.connect(self.on_css_preset_changed)
        self.tab_css.text_changed.connect(self.on_css_text_changed)

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

        # Create splitter for tabs and log areas with button panel in between
        self.splitter = QSplitter(Qt.Vertical, self)

        # Add tabs to splitter (top)
        self.splitter.addWidget(self.tabs)

        # Create command panel (middle, fixed height)
        self.command_panel = CommandPanel(self)
        self.command_panel.restoreRequested.connect(self.restore_last_config)
        self.command_panel.importRequested.connect(self.import_config)
        self.command_panel.exportRequested.connect(self.export_config)
        self.command_panel.scrapeRequested.connect(self.run_conversion)

        # Create log panel (bottom)
        self.log_panel = LogPanel(self)

        # Add command panel and log panel to splitter
        self.splitter.addWidget(self.command_panel)
        self.splitter.addWidget(self.log_panel)

        # Configure splitter behavior
        self.splitter.setSizes([220, 120, 260])  # Initial proportions - command panel is 120px
        self.splitter.setStretchFactor(0, 0)  # Tab area fixed height (not stretchable)
        self.splitter.setStretchFactor(1, 0)  # Command panel fixed
        self.splitter.setStretchFactor(2, 1)  # Log area stretchable
        self.splitter.setChildrenCollapsible(False)  # Prevent collapse
        self.splitter.splitterMoved.connect(self.on_splitter_moved)

        # Prefer showing Basic tab first
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tab_basic))

        # Add splitter to main layout
        root.addWidget(self.splitter)

        self.setMinimumSize(800, 520)
        self.setCentralWidget(central)

        # Override showEvent to force splitter behavior after window is shown
        self.showEvent = self._on_show_event

        # Load presets (delegated) - handlers already connected, so selection will load editor
        self.reload_presets(auto_select_default=False)
        # Sync all pages from configuration using unified methods
        self.cfgc.sync_all_from_config(self)
        # Wire Image Tab controls to sync changes to config
        self.tab_image.width_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.zoom_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.background_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.jpg_quality_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.png_optimize_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.png_compress_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.png_transparent_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.webp_quality_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.webp_lossless_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
        self.tab_image.webp_transparent_changed.connect(lambda: self.cfgc.sync_all_to_config(self))

        # Wire remaining PDF/CSS controls (save/refresh)
        self.tab_pdf.save_clicked.connect(self.on_pdf_save_clicked)
        self.tab_pdf.refresh_clicked.connect(self.on_pdf_refresh_clicked)
        self.tab_css.save_clicked.connect(self.on_css_save_clicked)
        self.tab_css.refresh_clicked.connect(self.on_css_refresh_clicked)

        # Wire Advanced Tab controls
        self.tab_advanced.wkhtmltopdf_path_changed.connect(
            lambda: self.cfgc.sync_all_to_config(self)
        )
        # Open user data directory
        self.tab_advanced.open_user_data_requested.connect(
            lambda: self.filec.open_user_data_dir(self)
        )
        # Restore default config
        self.tab_advanced.restore_default_config_requested.connect(
            lambda: self.cfgc.restore_default_config(self)
        )

        # After UI ready, show normalization log if any
        if hasattr(self, "log_message_later") and self.log_message_later:
            self.log_panel.appendLog(self.log_message_later)
            self.log_message_later = None

    def apply_modern_styling(self):
        """Apply modern PySide6 styling using built-in styles"""
        from PySide6.QtWidgets import QApplication

        # Apply styling through theme system
        theme_loader = ThemeLoader(self.project_root)
        theme_name = "default"

        # Apply base style (configurable per theme)
        app = QApplication.instance()
        theme_loader.apply_base_style(app, theme_name)

        # Load theme from external QSS file
        self.setStyleSheet(theme_loader.load_theme(theme_name))

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
            self,
            "Select input file",
            start_dir,
            "Text/Markdown files (*.txt *.md);;JSON files (*.json);;Excel files (*.xlsx);;All files (*.*)",
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
            self,
            "Select output file",
            str(Path(start_dir) / (default_filename + ".html" if default_filename else "")),
            "HTML files (*.html);;PDF files (*.pdf);;JPG files (*.jpg);;PNG files (*.png);;WEBP files (*.webp);;All files (*.*)",
        )
        if file:
            self.settings.set_output_file(file)
            self.edit_output.setText(self.settings.get("basic.output_file"))

    def closeEvent(self, event):
        """Handle application close event - save config before closing"""
        # Sync all page configurations to settings before saving
        try:
            # Sync all page configurations to settings before saving
            self.cfgc.sync_all_to_config(self)
            # Autosave Untitled when dirty
            self.autosave_untitled_if_needed()
        except Exception:
            pass

        # Save all configuration to disk
        self.settings.save()
        event.accept()

    def run_conversion(self):
        self.convc.run(self)

    def on_run_finished(self, message: str):
        self.convc.on_finished(self, message)

    def on_run_error(self, message: str):
        self.convc.on_error(self, message)

    def on_progress_update(self, progress: int, message: str):
        self.convc.on_progress(self, progress, message)

    def on_splitter_moved(self, pos: int, index: int):
        """Enforce minimum sizes when splitter is moved"""
        sizes = self.splitter.sizes()
        min_sizes = [200, 120, 150]  # Tab, Button, Log minimum heights

        # Check if any area needs adjustment
        if any(sizes[i] < min_sizes[i] for i in range(3)):
            # Temporarily disconnect to avoid recursion
            self.splitter.splitterMoved.disconnect(self.on_splitter_moved)
            # Apply minimum sizes
            adjusted_sizes = [max(sizes[i], min_sizes[i]) for i in range(3)]
            self.splitter.setSizes(adjusted_sizes)
            # Reconnect signal
            self.splitter.splitterMoved.connect(self.on_splitter_moved)

    def _on_show_event(self, event):
        """Handle window show event to force correct splitter behavior"""
        super().showEvent(event)

        # Force splitter to behave correctly by setting sizes explicitly
        # This ensures tab area stays fixed and only log area stretches
        from PySide6.QtCore import QTimer

        QTimer.singleShot(50, self._force_splitter_config)

    def _force_splitter_config(self):
        """Force splitter configuration after window is shown"""
        # Get current splitter sizes to capture the actual tab height
        current_sizes = self.splitter.sizes()
        current_tab_height = current_sizes[0]  # Capture current tab height

        # Store this as the "remembered" tab height
        self.remembered_tab_height = current_tab_height

        # Get current window height
        window_height = self.height()

        # Calculate desired sizes: use current tab height, command fixed, log gets the rest
        tab_height = current_tab_height  # Use current tab height as the "remembered" height
        command_height = 120  # Fixed command height (matches CommandPanel.setFixedHeight(120))
        log_height = window_height - tab_height - command_height - 32  # 32 for margins

        # Ensure minimum log height
        if log_height < 150:
            log_height = 150

        # Force set the sizes - this "teaches" the splitter to remember the current tab height
        self.splitter.setSizes([tab_height, command_height, log_height])

        # Reconfigure stretch factors to ensure they stick
        self.splitter.setStretchFactor(0, 0)  # Tab area fixed
        self.splitter.setStretchFactor(1, 0)  # Command panel fixed
        self.splitter.setStretchFactor(2, 1)  # Log area stretchable

        # Force the splitter to "remember" these sizes by triggering a resize
        # This ensures the splitter's internal memory is set correctly
        from PySide6.QtCore import QTimer

        QTimer.singleShot(10, self._reinforce_splitter_memory)

    def _reinforce_splitter_memory(self):
        """Reinforce the splitter's memory of correct sizes"""
        # Get current sizes
        current_sizes = self.splitter.sizes()

        # If tab area is not at the remembered height, force it back
        if (
            hasattr(self, "remembered_tab_height")
            and current_sizes[0] != self.remembered_tab_height
        ):
            # Recalculate with remembered tab height
            window_height = self.height()
            tab_height = self.remembered_tab_height
            command_height = 120  # Fixed command height (matches CommandPanel.setFixedHeight(120))
            log_height = window_height - tab_height - command_height - 32

            if log_height < 150:
                log_height = 150

            # Force set the sizes again to reinforce the memory
            self.splitter.setSizes([tab_height, command_height, log_height])

            # Reapply stretch factors
            self.splitter.setStretchFactor(0, 0)  # Tab area fixed
            self.splitter.setStretchFactor(1, 0)  # Command panel fixed
            self.splitter.setStretchFactor(2, 1)  # Log area stretchable

    def on_log(self, text: str):
        # Skip progress messages as they're redundant with progress bar
        if not text.startswith("Progress:"):
            self.log_panel.appendLog(text)

    # --- Config buttons ---
    def restore_last_config(self):
        """Restore last saved configuration from disk"""
        self.cfgc.restore_last_config(self)

    def import_config(self):
        start_dir = str((self.project_root / "data" / "configs").resolve())
        file, _ = QFileDialog.getOpenFileName(
            self, "Import config (TOML)", start_dir, "TOML files (*.toml)"
        )
        if not file:
            return
        self.cfgc.import_config(self, Path(file))

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
            self,
            "Export config as (TOML)",
            str(Path(start_dir) / (default_filename + ".toml" if default_filename else "")),
            "TOML files (*.toml)",
        )
        if not file:
            return
        self.cfgc.export_config(self, Path(file))

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
        # Deprecated: replaced by cfgc.sync_all_from_config(self)
        self.cfgc.sync_all_from_config(self)

    # ---- Presets loading/saving ----
    def reload_presets(self, auto_select_default: bool = True):
        self.preset_coordinator.reload_presets(self, auto_select_default=auto_select_default)

    def _iter_presets(self, kind: str):
        # Deprecated shim
        yield from self.presets.iter_presets(kind)

    def on_pdf_preset_changed(self, label: str):
        self.preset_coordinator.on_pdf_preset_changed(self, label)

    def on_css_preset_changed(self, label: str):
        self.preset_coordinator.on_css_preset_changed(self, label)

    def on_pdf_save_clicked(self):
        user_dir = (self.project_root / "data" / "configs" / "pdf").resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(
            self, "Save PDF preset as", str(user_dir), "TOML files (*.toml)"
        )
        if not file:
            return
        try:
            text = self.tab_pdf.pdf_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set("pdf.preset_label", Path(file).stem)
            self.log_panel.appendLog(f"✅ Saved PDF preset: {file}")
            # Reload presets and select the saved label via unified method
            saved_label = Path(file).stem
            self.reload_presets(auto_select_default=False)
            self.preset_coordinator.select_label_and_load(self, "pdf", saved_label)
            self.settings.set("pdf.preset_label", saved_label)
            # settings already updated by set('pdf.preset_label')
            self.pdf_dirty = False
            self.last_pdf_label = saved_label
            self.tab_pdf.show_dirty(False)
        except Exception as e:
            self.log_panel.appendLog(f"❌ Failed to save PDF preset: {e}")

    def on_css_save_clicked(self):
        user_dir = (self.project_root / "data" / "configs" / "css").resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(
            self, "Save CSS preset as", str(user_dir), "TOML files (*.toml)"
        )
        if not file:
            return
        try:
            text = self.tab_css.css_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set("css.preset_label", Path(file).stem)
            self.log_panel.appendLog(f"✅ Saved CSS preset: {file}")
            # Reload presets and select the saved label via unified method
            saved_label = Path(file).stem
            self.reload_presets(auto_select_default=False)
            self.preset_coordinator.select_label_and_load(self, "css", saved_label)
            self.settings.set("css.preset_label", saved_label)
            # settings already updated by set('css.preset_label')
            self.css_dirty = False
            self.last_css_label = saved_label
            self.tab_css.show_dirty(False)
        except Exception as e:
            self.log_panel.appendLog(f"❌ Failed to save CSS preset: {e}")

    def on_pdf_text_changed(self):
        self.preset_coordinator.on_pdf_text_changed(self)

    def on_css_text_changed(self):
        self.preset_coordinator.on_css_text_changed(self)

    def on_pdf_refresh_clicked(self):
        self.reload_presets(auto_select_default=False)

    def on_css_refresh_clicked(self):
        self.reload_presets(auto_select_default=False)

    def autosave_untitled_if_needed(self):
        self.preset_coordinator.autosave_untitled_if_needed(self)

    def autosave_untitled(self, kind: str):
        # Backward-compat shim: delegate to coordinator
        if kind in ("pdf", "css"):
            self.preset_coordinator._autosave_untitled(self, kind)

    # --- Unified preset selection and * Untitled state helpers ---
    def _enter_untitled_state(self, kind: str, clear_editor: bool = True) -> None:
        self.preset_coordinator.enter_untitled_state(self, kind, clear_editor)

    def select_label_and_load(self, kind: str, label: str) -> None:
        self.preset_coordinator.select_label_and_load(self, kind, label)

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
    w.resize(800, 600)
    w.show()
    sys.exit(app.exec())
