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

        # Form grid for aligned elements
        form = QGridLayout()
        # Reduce horizontal spacing to bring labels, inputs and buttons closer
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(8)

        # Slightly narrow label width to reduce gap before inputs
        label_w = 80
        btn_w = 90

        lbl_in = QLabel("Input:")
        lbl_in.setFixedWidth(label_w)
        lbl_in.setProperty("class", "field-label")
        self.edit_input = QLineEdit(self.settings.get("input.file", ""), self)
        self.edit_input.editingFinished.connect(self.on_input_edited)
        btn_input = QPushButton("Choose...", self)
        btn_input.setFixedWidth(btn_w)
        btn_input.clicked.connect(self.choose_input)
        form.addWidget(lbl_in, 0, 0)
        form.addWidget(self.edit_input, 0, 1)
        form.addWidget(btn_input, 0, 2)

        lbl_dict = QLabel("Dictionary:")
        lbl_dict.setFixedWidth(label_w)
        lbl_dict.setProperty("class", "field-label")
        self.edit_dict = QLineEdit(self.settings.get("dictionary.file", ""), self)
        self.edit_dict.editingFinished.connect(self.on_dictionary_edited)
        btn_dict = QPushButton("Choose...", self)
        btn_dict.setFixedWidth(btn_w)
        btn_dict.clicked.connect(self.choose_dictionary)
        form.addWidget(lbl_dict, 1, 0)
        form.addWidget(self.edit_dict, 1, 1)
        form.addWidget(btn_dict, 1, 2)

        lbl_out = QLabel("Output:")
        lbl_out.setFixedWidth(label_w)
        lbl_out.setProperty("class", "field-label")
        self.edit_output = QLineEdit(self.settings.get("output.file", ""), self)
        self.edit_output.editingFinished.connect(self.on_output_edited)
        btn_output = QPushButton("Choose...", self)
        btn_output.setFixedWidth(btn_w)
        btn_output.clicked.connect(self.choose_output)
        form.addWidget(lbl_out, 2, 0)
        form.addWidget(self.edit_output, 2, 1)
        form.addWidget(btn_output, 2, 2)

        # Add timestamp and backup options in one row under the output field, left-aligned together
        self.check_timestamp = QCheckBox("Add timestamp to output filename", self)
        self.check_timestamp.setChecked(self.settings.get_output_add_timestamp())
        self.check_timestamp.stateChanged.connect(self.on_timestamp_changed)

        self.check_backup = QCheckBox("Backup input file", self)
        self.check_backup.setChecked(self.settings.get_backup_input())
        self.check_backup.stateChanged.connect(self.on_backup_changed)

        self.check_save_invalid = QCheckBox("Save invalid words file", self)
        self.check_save_invalid.setChecked(self.settings.get_save_invalid_words())
        self.check_save_invalid.stateChanged.connect(self.on_save_invalid_changed)

        options_row = QHBoxLayout()
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(12)
        options_row.addWidget(self.check_timestamp)
        options_row.addWidget(self.check_backup)
        options_row.addWidget(self.check_save_invalid)
        options_row.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        form.addLayout(options_row, 3, 1, 1, 2)
        
        # Apply modern styling to all buttons and inputs
        self.apply_modern_styling()
        
        # Set heights for better visual hierarchy
        self.edit_input.setFixedHeight(35)
        self.edit_dict.setFixedHeight(35)
        self.edit_output.setFixedHeight(35)
        btn_input.setFixedHeight(35)
        btn_dict.setFixedHeight(35)
        btn_output.setFixedHeight(35)

        form.setColumnStretch(1, 1)
        # Do not add form directly to root; it will live inside the Basic tab

        # Tabs: Basic / Image / PDF / CSS
        self.tabs = QTabWidget(self)
        # Basic Tab (original inputs and basic options)
        self.tab_basic = QWidget(self)
        _lay_basic = QVBoxLayout(self.tab_basic)
        _lay_basic.setContentsMargins(8, 8, 8, 8)
        _lay_basic.addLayout(form)
        self.tabs.addTab(self.tab_basic, "Basic")
        # Image Tab (placeholder for now)
        self.tab_image = QWidget(self)
        _lay_img = QVBoxLayout(self.tab_image)
        _lay_img.setContentsMargins(8, 8, 8, 8)
        # General (single row with section label)
        row_gen = QHBoxLayout()
        _section_w = 70
        _label_w = None
        _lbl_general = QLabel("General", self)
        _lbl_general.setProperty("class", "field-label")
        _lbl_general.setFixedWidth(_section_w)
        _lbl_general.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_gen.addWidget(_lbl_general)
        row_gen.addSpacing(8)
        _lbl_width = QLabel("Width(px):", self)
        _lbl_width.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_gen.addWidget(_lbl_width)
        self.img_width = QLineEdit(self)
        self.img_width.setPlaceholderText("0 = auto")
        self.img_width.setFixedWidth(80)
        row_gen.addWidget(self.img_width)
        row_gen.addSpacing(12)
        _lbl_zoom = QLabel("Zoom:", self)
        _lbl_zoom.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_gen.addWidget(_lbl_zoom)
        # Zoom slider (0.5 ~ 3.0, step 0.1 via int scale 5~30)
        self.img_zoom_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.img_zoom_slider.setRange(5, 30)
        self.img_zoom_slider.setSingleStep(1)
        self.img_zoom_slider.setFixedWidth(160)
        row_gen.addWidget(self.img_zoom_slider)
        self.img_zoom_value = QLineEdit(self)
        self.img_zoom_value.setFixedWidth(50)
        row_gen.addWidget(self.img_zoom_value)
        row_gen.addSpacing(12)
        self.img_background = QCheckBox("Draw background", self)
        row_gen.addWidget(self.img_background)
        row_gen.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # JPG options (single row)
        row_jpg = QHBoxLayout()
        _lbl_jpg = QLabel("JPG/JPEG", self)
        _lbl_jpg.setProperty("class", "field-label")
        _lbl_jpg.setFixedWidth(_section_w)
        _lbl_jpg.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_jpg.addWidget(_lbl_jpg)
        row_jpg.addSpacing(8)
        _lbl_jpg_q = QLabel("Quality:", self)
        _lbl_jpg_q.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_jpg.addWidget(_lbl_jpg_q)
        self.jpg_quality_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.jpg_quality_slider.setRange(1, 100)
        self.jpg_quality_slider.setFixedWidth(160)
        row_jpg.addWidget(self.jpg_quality_slider)
        self.jpg_quality_value = QLineEdit(self)
        self.jpg_quality_value.setFixedWidth(50)
        row_jpg.addWidget(self.jpg_quality_value)
        row_jpg.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # will add rows in desired order later

        # PNG options (single row)
        row_png = QHBoxLayout()
        _lbl_png = QLabel("PNG", self)
        _lbl_png.setProperty("class", "field-label")
        _lbl_png.setFixedWidth(_section_w)
        _lbl_png.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_png.addWidget(_lbl_png)
        row_png.addSpacing(8)
        self.png_optimize = QCheckBox("Optimize", self)
        row_png.addWidget(self.png_optimize)
        row_png.addSpacing(12)
        _lbl_png_c = QLabel("Compress:", self)
        _lbl_png_c.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_png.addWidget(_lbl_png_c)
        self.png_compress_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.png_compress_slider.setRange(0, 9)
        self.png_compress_slider.setFixedWidth(120)
        row_png.addWidget(self.png_compress_slider)
        self.png_compress_value = QLineEdit(self)
        self.png_compress_value.setFixedWidth(40)
        row_png.addWidget(self.png_compress_value)
        row_png.addSpacing(12)
        self.png_transparent = QCheckBox("Transparent background", self)
        row_png.addWidget(self.png_transparent)
        row_png.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # will add rows in desired order later

        # WEBP options (single row)
        row_webp = QHBoxLayout()
        _lbl_webp = QLabel("WEBP", self)
        _lbl_webp.setProperty("class", "field-label")
        _lbl_webp.setFixedWidth(_section_w)
        _lbl_webp.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_webp.addWidget(_lbl_webp)
        row_webp.addSpacing(8)
        _lbl_webp_q = QLabel("Quality:", self)
        _lbl_webp_q.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row_webp.addWidget(_lbl_webp_q)
        self.webp_quality_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.webp_quality_slider.setRange(1, 100)
        self.webp_quality_slider.setFixedWidth(160)
        row_webp.addWidget(self.webp_quality_slider)
        self.webp_quality_value = QLineEdit(self)
        self.webp_quality_value.setFixedWidth(50)
        row_webp.addWidget(self.webp_quality_value)
        row_webp.addSpacing(12)
        self.webp_lossless = QCheckBox("Lossless", self)
        row_webp.addWidget(self.webp_lossless)
        row_webp.addSpacing(12)
        self.webp_transparent = QCheckBox("Transparent background", self)
        row_webp.addWidget(self.webp_transparent)
        row_webp.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # Reorder Image tab rows: General, WEBP, PNG, JPG/JPEG
        _lay_img.addLayout(row_gen)
        _lay_img.addLayout(row_webp)
        _lay_img.addLayout(row_png)
        _lay_img.addLayout(row_jpg)
        self.tabs.addTab(self.tab_image, "Image")

        # PDF Tab
        self.tab_pdf = QWidget(self)
        _lay_pdf = QVBoxLayout(self.tab_pdf)
        _lay_pdf.setContentsMargins(8, 8, 8, 8)
        row_pdf = QHBoxLayout()
        row_pdf.addWidget(QLabel("Preset:", self))
        self.pdf_combo = QComboBox(self)
        self.pdf_combo.currentTextChanged.connect(self.on_pdf_preset_changed)
        row_pdf.addWidget(self.pdf_combo, 1)
        self.btn_pdf_save = QPushButton("Save", self)
        self.btn_pdf_save.clicked.connect(self.on_pdf_save_clicked)
        row_pdf.addWidget(self.btn_pdf_save)
        _lay_pdf.addLayout(row_pdf)
        self.pdf_editor = QTextEdit(self)
        self.pdf_editor.setPlaceholderText("[pdf]\n# wkhtmltopdf options in TOML ...")
        _lay_pdf.addWidget(self.pdf_editor, 1)
        self.tabs.addTab(self.tab_pdf, "PDF")

        # CSS Tab
        self.tab_css = QWidget(self)
        _lay_css = QVBoxLayout(self.tab_css)
        _lay_css.setContentsMargins(8, 8, 8, 8)
        row_css = QHBoxLayout()
        row_css.addWidget(QLabel("Preset:", self))
        self.css_combo = QComboBox(self)
        self.css_combo.currentTextChanged.connect(self.on_css_preset_changed)
        row_css.addWidget(self.css_combo, 1)
        self.btn_css_save = QPushButton("Save", self)
        self.btn_css_save.clicked.connect(self.on_css_save_clicked)
        row_css.addWidget(self.btn_css_save)
        _lay_css.addLayout(row_css)
        self.css_editor = QTextEdit(self)
        self.css_editor.setPlaceholderText("[style]\n# h1_style=..., scrap_style=..., additional_styles=... (TOML)")
        _lay_css.addWidget(self.css_editor, 1)
        self.tabs.addTab(self.tab_css, "CSS")

        # About Tab
        self.tab_about = QWidget(self)
        _lay_about = QVBoxLayout(self.tab_about)
        _lay_about.setContentsMargins(8, 8, 8, 8)
        # Center the two-line block vertically and horizontally
        _lay_about.addStretch(1)
        _about_block = QVBoxLayout()
        _about_block.setContentsMargins(0, 0, 0, 0)
        _about_title = QLabel('<b>Homepage</b>', self)
        _about_title.setAlignment(Qt.AlignHCenter)
        _about_block.addWidget(_about_title)
        _about_link = QLabel('<a href="https://github.com/VimWei/MdxScraper">https://github.com/VimWei/MdxScraper</a>', self)
        _about_link.setOpenExternalLinks(True)
        _about_link.setAlignment(Qt.AlignHCenter)
        _about_block.addWidget(_about_link)
        _lay_about.addLayout(_about_block)
        _lay_about.addStretch(1)
        self.tabs.addTab(self.tab_about, "About")

        # Reorder tabs to: Basic, CSS, Image, PDF
        try:
            desired_order = [
                (self.tab_basic, "Basic"),
                (self.tab_css, "CSS"),
                (self.tab_image, "Image"),
                (self.tab_pdf, "PDF"),
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
        # Load presets and set tab enablement
        self.reload_presets()
        self.update_tab_enablement()
        # Sync Image tab inputs from config
        self.sync_image_from_config()
        # Restore last PDF/CSS editor contents if present
        last_pdf_text = self.settings.get('output.pdf.preset_text', '')
        if last_pdf_text:
            self.pdf_editor.setPlainText(last_pdf_text)
        last_css_text = self.settings.get('output.css.preset_text', '')
        if last_css_text:
            self.css_editor.setPlainText(last_css_text)
        # Wire sliders and numeric displays
        self.img_zoom_slider.valueChanged.connect(lambda v: self.img_zoom_value.setText(f"{v/10:.1f}"))
        self.jpg_quality_slider.valueChanged.connect(lambda v: self.jpg_quality_value.setText(str(v)))
        self.png_compress_slider.valueChanged.connect(lambda v: self.png_compress_value.setText(str(v)))
        self.webp_quality_slider.valueChanged.connect(lambda v: self.webp_quality_value.setText(str(v)))
        
        # Wire Image Tab controls to sync changes to config
        self.img_width.textChanged.connect(self.sync_image_to_config)
        self.img_zoom_slider.valueChanged.connect(self.sync_image_to_config)
        self.img_background.toggled.connect(self.sync_image_to_config)
        self.jpg_quality_slider.valueChanged.connect(self.sync_image_to_config)
        self.png_optimize.toggled.connect(self.sync_image_to_config)
        self.png_compress_slider.valueChanged.connect(self.sync_image_to_config)
        self.png_transparent.toggled.connect(self.sync_image_to_config)
        self.webp_quality_slider.valueChanged.connect(self.sync_image_to_config)
        self.webp_lossless.toggled.connect(self.sync_image_to_config)
        self.webp_transparent.toggled.connect(self.sync_image_to_config)

        # Config buttons centered, compact - fixed height to prevent expansion
        row_session = QHBoxLayout()
        row_session.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        row_session.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        btn_restore = QPushButton("Restore last config", self)
        btn_import = QPushButton("Import config", self)
        btn_export = QPushButton("Export config", self)
        for b in (btn_restore, btn_import, btn_export):
            b.setFixedWidth(150)
            b.setFixedHeight(32)
        btn_restore.clicked.connect(self.restore_last_config)
        btn_import.clicked.connect(self.import_config)
        btn_export.clicked.connect(self.export_config)
        row_session.addWidget(btn_restore)
        row_session.addSpacing(12)
        row_session.addWidget(btn_import)
        row_session.addSpacing(12)
        row_session.addWidget(btn_export)
        row_session.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        root.addLayout(row_session)

        # Scrape button centered with fixed width - fixed height to prevent expansion
        row_run = QHBoxLayout()
        row_run.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        row_run.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_run = QPushButton("Scrape", self)
        self.btn_run.setFixedWidth(220)
        self.btn_run.setFixedHeight(45)  # Make button taller
        self.btn_run.setObjectName("scrape-button")  # Set ID for CSS targeting
        self.btn_run.clicked.connect(self.run_conversion)
        row_run.addWidget(self.btn_run)
        row_run.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        root.addLayout(row_run)

        # Progress bar only
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(25)
        root.addWidget(self.progress)

        # Log area - flexible height that expands with window
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("log message")
        self.log.setMinimumHeight(120)  # Set minimum height instead of fixed
        self.log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Allow expansion
        root.addWidget(self.log)

        self.setMinimumSize(800, 520)
        self.setCentralWidget(central)
        # Load presets and set tab enablement
        self.reload_presets()
        self.update_tab_enablement()
        # Sync Image tab inputs from config
        self.sync_image_from_config()
        # After UI ready, show normalization log if any
        if hasattr(self, 'log_message_later') and self.log_message_later:
            # defer until log widget exists
            self.log = self.log if hasattr(self, 'log') else None
            if self.log:
                self.log.append(self.log_message_later)
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
    
    def closeEvent(self, event):
        """Handle application close event - save config before closing"""
        # Persist live PDF/CSS editor content on exit via SettingsService
        try:
            pdf_text = self.pdf_editor.toPlainText() if hasattr(self, 'pdf_editor') else ''
            pdf_label = self.pdf_combo.currentText() if hasattr(self, 'pdf_combo') else ''
            css_text = self.css_editor.toPlainText() if hasattr(self, 'css_editor') else ''
            css_label = self.css_combo.currentText() if hasattr(self, 'css_combo') else ''
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
            width = int(self.img_width.text().strip() or '0')
            zoom = float(self.img_zoom_value.text().strip() or '1.0')
            self.settings.set('output.image.width', width)
            self.settings.set('output.image.zoom', zoom)
        except Exception:
            pass
        self.settings.set('output.image.background', bool(self.img_background.isChecked()))
        try:
            self.settings.set('output.image.jpg.quality', int(self.jpg_quality_value.text().strip() or '85'))
        except Exception:
            pass
        self.settings.set('output.image.png.optimize', bool(self.png_optimize.isChecked()))
        try:
            self.settings.set('output.image.png.compress_level', int(self.png_compress_value.text().strip() or '9'))
        except Exception:
            pass
        self.settings.set('output.image.png.transparent_bg', bool(self.png_transparent.isChecked()))
        try:
            self.settings.set('output.image.webp.quality', int(self.webp_quality_value.text().strip() or '80'))
        except Exception:
            pass
        self.settings.set('output.image.webp.lossless', bool(self.webp_lossless.isChecked()))
        self.settings.set('output.image.webp.transparent_bg', bool(self.webp_transparent.isChecked()))

        output = self.settings.get("output.file")
        if not output:
            QMessageBox.warning(self, "Run", "Please set output file first.")
            return
        self.btn_run.setEnabled(False)
        # Collect current preset editor contents
        pdf_text = self.pdf_editor.toPlainText() if hasattr(self, 'pdf_editor') else ''
        css_text = self.css_editor.toPlainText() if hasattr(self, 'css_editor') else ''
        self.worker = ConversionWorker(self.project_root, self.cm, pdf_text=pdf_text, css_text=css_text)
        self.worker.finished_sig.connect(self.on_run_finished)
        self.worker.error_sig.connect(self.on_run_error)
        self.worker.log_sig.connect(self.on_log)
        self.progress.setValue(0)
        self.worker.start()

    def on_run_finished(self, message: str):
        self.btn_run.setEnabled(True)
        self.progress.setValue(100)
        self.log.append(f"✅ {message}")

    def on_run_error(self, message: str):
        self.btn_run.setEnabled(True)
        self.progress.setValue(0)
        self.log.append(f"❌ Error: {message}")

    def on_log(self, text: str):
        # Skip progress messages as they're redundant with progress bar
        if not text.startswith("Progress:"):
            self.log.append(text)

    # --- Config buttons ---
    def restore_last_config(self):
        try:
            # Reload latest config from disk and refresh GUI
            self.settings.load()
            self.sync_from_config()
            self.log.append("ℹ️ Restored last saved config.")
        except Exception as e:
            self.log.append(f"❌ Failed to restore config: {e}")

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
            self.log.append(f"✅ Imported config applied: {file}")
            if info.get("changed"):
                removed, added, type_fixed = info.get("removed", 0), info.get("added", 0), info.get("type_fixed", 0)
                self.log.append(f"⚙️ Config normalized after import (removed: {removed}, added: {added}, type fixed: {type_fixed}). Please save to persist.")
        except Exception as e:
            self.log.append(f"❌ Failed to import config: {e}")

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
            if hasattr(self, 'pdf_editor'):
                self.settings.set('output.pdf.preset_text', self.pdf_editor.toPlainText())
                if hasattr(self, 'pdf_combo'):
                    self.settings.set('output.pdf.preset_label', self.pdf_combo.currentText())
            if hasattr(self, 'css_editor'):
                self.settings.set('output.css.preset_text', self.css_editor.toPlainText())
                if hasattr(self, 'css_combo'):
                    self.settings.set('output.css.preset_label', self.css_combo.currentText())
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
                self.log.append("⚠️ Config validation issues before export:\n" + problems)
            # Write selected path
            from pathlib import Path as _P
            from mdxscraper.config import config_manager as _cm
            data = self.settings.get_config_dict()
            content = _cm.tomli_w.dumps(data)
            p = _P(file)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.log.append(f"✅ Exported config to: {file}")
        except Exception as e:
            self.log.append(f"❌ Failed to export config: {e}")

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
        # Sync PDF/CSS editors and preset labels from config
        try:
            if hasattr(self, 'pdf_editor'):
                pdf_text = self.settings.get('output.pdf.preset_text', '') or ''
                self.pdf_editor.setPlainText(pdf_text)
                if hasattr(self, 'pdf_combo'):
                    pdf_label = self.settings.get('output.pdf.preset_label', '') or ''
                    if pdf_label:
                        for i in range(self.pdf_combo.count()):
                            if self.pdf_combo.itemText(i) == pdf_label:
                                self.pdf_combo.setCurrentIndex(i)
                                break
            if hasattr(self, 'css_editor'):
                css_text = self.settings.get('output.css.preset_text', '') or ''
                self.css_editor.setPlainText(css_text)
                if hasattr(self, 'css_combo'):
                    css_label = self.settings.get('output.css.preset_label', '') or ''
                    if css_label:
                        for i in range(self.css_combo.count()):
                            if self.css_combo.itemText(i) == css_label:
                                self.css_combo.setCurrentIndex(i)
                                break
        except Exception:
            # Non-fatal: keep going if presets cannot be synced
            pass

    def sync_image_from_config(self):
        # Populate image fields from config defaults
        get = self.cm.get
        self.img_width.setText(str(get("output.image.width", 0)))
        zoom = float(get("output.image.zoom", 1.0))
        self.img_zoom_slider.setValue(int(round(zoom * 10)))
        self.img_zoom_value.setText(f"{zoom:.1f}")
        self.img_background.setChecked(bool(get("output.image.background", True)))
        jpg_q = int(get("output.image.jpg.quality", 85))
        self.jpg_quality_slider.setValue(jpg_q)
        self.jpg_quality_value.setText(str(jpg_q))
        self.png_optimize.setChecked(bool(get("output.image.png.optimize", True)))
        png_c = int(get("output.image.png.compress_level", 9))
        self.png_compress_slider.setValue(png_c)
        self.png_compress_value.setText(str(png_c))
        self.png_transparent.setChecked(bool(get("output.image.png.transparent_bg", False)))
        webp_q = int(get("output.image.webp.quality", 80))
        self.webp_quality_slider.setValue(webp_q)
        self.webp_quality_value.setText(str(webp_q))
        self.webp_lossless.setChecked(bool(get("output.image.webp.lossless", False)))
        self.webp_transparent.setChecked(bool(get("output.image.webp.transparent_bg", False)))

    def sync_image_to_config(self):
        # Sync current Image Tab GUI values to config
        try:
            # General settings
            width_text = self.img_width.text().strip()
            if width_text:
                width = int(width_text)
                self.settings.set("output.image.width", width)
            else:
                self.settings.set("output.image.width", 0)
            
            zoom = self.img_zoom_slider.value() / 10.0
            self.settings.set("output.image.zoom", zoom)
            
            self.settings.set("output.image.background", self.img_background.isChecked())
            
            # JPG settings
            jpg_quality = self.jpg_quality_slider.value()
            self.settings.set("output.image.jpg.quality", jpg_quality)
            
            # PNG settings
            self.settings.set("output.image.png.optimize", self.png_optimize.isChecked())
            png_compress = self.png_compress_slider.value()
            self.settings.set("output.image.png.compress_level", png_compress)
            self.settings.set("output.image.png.transparent_bg", self.png_transparent.isChecked())
            
            # WEBP settings
            webp_quality = self.webp_quality_slider.value()
            self.settings.set("output.image.webp.quality", webp_quality)
            self.settings.set("output.image.webp.lossless", self.webp_lossless.isChecked())
            self.settings.set("output.image.webp.transparent_bg", self.webp_transparent.isChecked())
            
        except (ValueError, TypeError) as e:
            # Ignore invalid values during typing, they'll be handled on export
            pass

    # ---- Presets loading/saving ----
    def reload_presets(self):
        # PDF presets
        self.pdf_combo.blockSignals(True)
        self.pdf_combo.clear()
        for label, path in self.presets.iter_presets('pdf'):
            self.pdf_combo.addItem(label, userData=str(path))
        self.pdf_combo.blockSignals(False)
        if self.pdf_combo.count() > 0:
            # Prefer 'default' built-in if present, else first
            preferred_idx = 0
            for i in range(self.pdf_combo.count()):
                txt = self.pdf_combo.itemText(i).lower()
                if txt.startswith('default'):
                    preferred_idx = i
                    break
            self.pdf_combo.setCurrentIndex(preferred_idx)
            self.on_pdf_preset_changed(self.pdf_combo.currentText())
        # CSS presets
        self.css_combo.blockSignals(True)
        self.css_combo.clear()
        for label, path in self.presets.iter_presets('css'):
            self.css_combo.addItem(label, userData=str(path))
        self.css_combo.blockSignals(False)
        if self.css_combo.count() > 0:
            # Prefer 'original' built-in if present, else first
            preferred_idx = 0
            for i in range(self.css_combo.count()):
                txt = self.css_combo.itemText(i).lower()
                if txt.startswith('original'):
                    preferred_idx = i
                    break
            self.css_combo.setCurrentIndex(preferred_idx)
            self.on_css_preset_changed(self.css_combo.currentText())

    def _iter_presets(self, kind: str):
        # Backward compatibility shim if needed elsewhere
        yield from self.presets.iter_presets(kind)

    def on_pdf_preset_changed(self, label: str):
        idx = self.pdf_combo.currentIndex()
        path = self.pdf_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                self.pdf_editor.setPlainText(text)
                # Persist selection and text in config
                self.settings.set('output.pdf.preset_label', label)
                self.settings.set('output.pdf.preset_text', text)
            except Exception as e:
                self.log.append(f"❌ Failed to load PDF preset: {e}")

    def on_css_preset_changed(self, label: str):
        idx = self.css_combo.currentIndex()
        path = self.css_combo.itemData(idx)
        if path:
            try:
                text = self.presets.load_preset_text(Path(path))
                self.css_editor.setPlainText(text)
                # Persist selection and text in config
                self.settings.set('output.css.preset_label', label)
                self.settings.set('output.css.preset_text', text)
            except Exception as e:
                self.log.append(f"❌ Failed to load CSS preset: {e}")

    def on_pdf_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'pdf').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save PDF preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            text = self.pdf_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set('output.pdf.preset_label', Path(file).stem)
            self.settings.set('output.pdf.preset_text', text)
            self.log.append(f"✅ Saved PDF preset: {file}")
            self.reload_presets()
        except Exception as e:
            self.log.append(f"❌ Failed to save PDF preset: {e}")

    def on_css_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'css').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save CSS preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            text = self.css_editor.toPlainText()
            self.presets.save_preset_text(Path(file), text)
            self.settings.set('output.css.preset_label', Path(file).stem)
            self.settings.set('output.css.preset_text', text)
            self.log.append(f"✅ Saved CSS preset: {file}")
            self.reload_presets()
        except Exception as e:
            self.log.append(f"❌ Failed to save CSS preset: {e}")

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
