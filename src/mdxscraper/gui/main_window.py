from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel,
    QFileDialog, QMessageBox, QTextEdit, QHBoxLayout, QLineEdit, QProgressBar,
    QGridLayout, QSizePolicy, QSpacerItem, QCheckBox, QTabWidget, QComboBox, QSlider
)
from PySide6.QtCore import QThread, Signal, Qt

from mdxscraper.config.config_manager import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self, project_root: Path):
        super().__init__()
        self.setWindowTitle("MdxScraper")
        self.project_root = project_root
        self.cm = ConfigManager(project_root)
        self.cm.load()
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
        self.edit_input = QLineEdit(self.cm.get("input.file", ""), self)
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
        self.edit_dict = QLineEdit(self.cm.get("dictionary.file", ""), self)
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
        self.edit_output = QLineEdit(self.cm.get("output.file", ""), self)
        self.edit_output.editingFinished.connect(self.on_output_edited)
        btn_output = QPushButton("Choose...", self)
        btn_output.setFixedWidth(btn_w)
        btn_output.clicked.connect(self.choose_output)
        form.addWidget(lbl_out, 2, 0)
        form.addWidget(self.edit_output, 2, 1)
        form.addWidget(btn_output, 2, 2)

        # Add timestamp and backup options in one row under the output field, left-aligned together
        self.check_timestamp = QCheckBox("Add timestamp to output filename", self)
        self.check_timestamp.setChecked(self.cm.get_output_add_timestamp())
        self.check_timestamp.stateChanged.connect(self.on_timestamp_changed)

        self.check_backup = QCheckBox("Backup input file", self)
        self.check_backup.setChecked(self.cm.get_backup_input())
        self.check_backup.stateChanged.connect(self.on_backup_changed)

        self.check_save_invalid = QCheckBox("Save invalid words file", self)
        self.check_save_invalid.setChecked(self.cm.get_save_invalid_words())
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
        _lay_img.addLayout(row_gen)

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
        _lay_img.addLayout(row_jpg)

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
        _lay_img.addLayout(row_png)

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
        _lay_img.addLayout(row_webp)
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

        root.addWidget(self.tabs)
        # Prefer showing Basic tab first
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.tab_basic))
        # Load presets and set tab enablement
        self.reload_presets()
        self.update_tab_enablement()
        # Sync Image tab inputs from config
        self.sync_image_from_config()
        # Restore last PDF/CSS editor contents if present
        last_pdf_text = self.cm.get('output.pdf.preset_text', '')
        if last_pdf_text:
            self.pdf_editor.setPlainText(last_pdf_text)
        last_css_text = self.cm.get('output.css.preset_text', '')
        if last_css_text:
            self.css_editor.setPlainText(last_css_text)
        # Wire sliders and numeric displays
        self.img_zoom_slider.valueChanged.connect(lambda v: self.img_zoom_value.setText(f"{v/10:.1f}"))
        self.jpg_quality_slider.valueChanged.connect(lambda v: self.jpg_quality_value.setText(str(v)))
        self.png_compress_slider.valueChanged.connect(lambda v: self.png_compress_value.setText(str(v)))
        self.webp_quality_slider.valueChanged.connect(lambda v: self.webp_quality_value.setText(str(v)))

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
        if current and Path(current).exists():
            start_dir = str(Path(current).parent)
        else:
            start_dir = str(self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            self, "Select input file", start_dir,
            "Text/Markdown files (*.txt *.md);;JSON files (*.json);;Excel files (*.xlsx);;All files (*.*)"
        )
        if file:
            self.cm.set_input_file(file)
            self.edit_input.setText(self.cm.get("input.file"))
            # Also update output base name to match input base
            self.on_input_edited()

    def choose_dictionary(self):
        current = self.edit_dict.text()
        if current and Path(current).exists():
            start_dir = str(Path(current).parent)
        else:
            start_dir = str(self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            self, "Select MDX dictionary", start_dir, "MDX Files (*.mdx)"
        )
        if file:
            self.cm.set_dictionary_file(file)
            self.edit_dict.setText(self.cm.get("dictionary.file"))

    def choose_output(self):
        current = self.edit_output.text()
        if current and Path(current).exists():
            start_dir = str(Path(current).parent)
        else:
            # Default to output directory from config
            output_dir = self.cm.get("output.directory", "data/output")
            if Path(output_dir).exists():
                start_dir = str(Path(output_dir).resolve())
            else:
                start_dir = str(self.project_root / "data" / "output")
        file, _ = QFileDialog.getSaveFileName(
            self, "Select output file", start_dir,
            "HTML files (*.html);;PDF files (*.pdf);;JPG files (*.jpg);;PNG files (*.png);;WEBP files (*.webp);;All files (*.*)"
        )
        if file:
            self.cm.set_output_file(file)
            self.edit_output.setText(self.cm.get("output.file"))
            self.update_tab_enablement()

    def on_timestamp_changed(self, state):
        """Handle timestamp checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.cm.set_output_add_timestamp(is_checked)
    
    def on_backup_changed(self, state):
        """Handle backup checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.cm.set_backup_input(is_checked)
    
    def on_save_invalid_changed(self, state):
        """Handle save invalid words checkbox state change"""
        is_checked = state == Qt.CheckState.Checked.value
        self.cm.set_save_invalid_words(is_checked)
    
    def closeEvent(self, event):
        """Handle application close event - save config before closing"""
        # Persist live PDF/CSS editor content on exit
        try:
            if hasattr(self, 'pdf_editor'):
                self.cm.set('output.pdf.preset_text', self.pdf_editor.toPlainText())
                if hasattr(self, 'pdf_combo'):
                    self.cm.set('output.pdf.preset_label', self.pdf_combo.currentText())
            if hasattr(self, 'css_editor'):
                self.cm.set('output.css.preset_text', self.css_editor.toPlainText())
                if hasattr(self, 'css_combo'):
                    self.cm.set('output.css.preset_label', self.css_combo.currentText())
        except Exception:
            pass
        self.cm.save()
        event.accept()

    def run_conversion(self):
        # Ensure latest values from inputs are synced to config before running
        # Avoid calling on_input_edited() here to prevent unintended renaming of output
        input_text = self.edit_input.text().strip()
        if input_text:
            self.cm.set_input_file(input_text)
        dict_text = self.edit_dict.text().strip()
        if dict_text:
            self.cm.set_dictionary_file(dict_text)
        output_text = self.edit_output.text().strip()
        if output_text:
            self.cm.set_output_file(output_text)
        # Persist Image tab values to config
        try:
            width = int(self.img_width.text().strip() or '0')
            zoom = float(self.img_zoom_value.text().strip() or '1.0')
            self.cm.set('output.image.width', width)
            self.cm.set('output.image.zoom', zoom)
        except Exception:
            pass
        self.cm.set('output.image.background', bool(self.img_background.isChecked()))
        try:
            self.cm.set('output.image.jpg.quality', int(self.jpg_quality_value.text().strip() or '85'))
        except Exception:
            pass
        self.cm.set('output.image.png.optimize', bool(self.png_optimize.isChecked()))
        try:
            self.cm.set('output.image.png.compress_level', int(self.png_compress_value.text().strip() or '9'))
        except Exception:
            pass
        self.cm.set('output.image.png.transparent_bg', bool(self.png_transparent.isChecked()))
        try:
            self.cm.set('output.image.webp.quality', int(self.webp_quality_value.text().strip() or '80'))
        except Exception:
            pass
        self.cm.set('output.image.webp.lossless', bool(self.webp_lossless.isChecked()))
        self.cm.set('output.image.webp.transparent_bg', bool(self.webp_transparent.isChecked()))

        output = self.cm.get("output.file")
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
            self.cm.load()
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
            self.cm._config = cfg
            self.cm._normalize_config()
            info = self.cm.get_normalize_info_once()
            self.sync_from_config()
            self.log.append(f"✅ Imported config applied: {file}")
            if info.get("changed"):
                removed, added, type_fixed = info.get("removed", 0), info.get("added", 0), info.get("type_fixed", 0)
                self.log.append(f"⚙️ Config normalized after import (removed: {removed}, added: {added}, type fixed: {type_fixed}). Please save to persist.")
        except Exception as e:
            self.log.append(f"❌ Failed to import config: {e}")

    def export_config(self):
        start_dir = str((self.project_root / "data" / "configs").resolve())
        file, _ = QFileDialog.getSaveFileName(
            self, "Export config as (TOML)", start_dir, "TOML files (*.toml)"
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
                self.cm.set('output.pdf.preset_text', self.pdf_editor.toPlainText())
                if hasattr(self, 'pdf_combo'):
                    self.cm.set('output.pdf.preset_label', self.pdf_combo.currentText())
            if hasattr(self, 'css_editor'):
                self.cm.set('output.css.preset_text', self.css_editor.toPlainText())
                if hasattr(self, 'css_combo'):
                    self.cm.set('output.css.preset_label', self.css_combo.currentText())
            # Validate before export; log issues but proceed
            result = self.cm.validate()
            if not result.is_valid:
                problems = "\n".join(result.errors)
                self.log.append("⚠️ Config validation issues before export:\n" + problems)
            # Write selected path
            from pathlib import Path as _P
            from mdxscraper.config import config_manager as _cm
            data = self.cm._config
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
            self.cm.set_input_file(text)
            # Auto-adjust output filename base to match input base, keeping path and suffix
            current_output = self.cm.get("output.file")
            if current_output:
                out_path = Path(current_output)
                new_base = Path(text).stem
                new_name = new_base + out_path.suffix
                new_output_path = out_path.with_name(new_name)
                self.cm.set_output_file(str(new_output_path))
                # Reflect change in UI
                self.edit_output.setText(self.cm.get("output.file"))

    def on_dictionary_edited(self):
        text = self.edit_dict.text().strip()
        if text:
            self.cm.set_dictionary_file(text)

    def on_output_edited(self):
        text = self.edit_output.text().strip()
        if text:
            self.cm.set_output_file(text)
        self.update_tab_enablement()

    def sync_from_config(self):
        # Refresh GUI fields from in-memory config
        self.edit_input.setText(self.cm.get("input.file", ""))
        self.edit_dict.setText(self.cm.get("dictionary.file", ""))
        self.edit_output.setText(self.cm.get("output.file", ""))
        self.check_timestamp.setChecked(self.cm.get_output_add_timestamp())
        self.check_backup.setChecked(self.cm.get_backup_input())
        self.update_tab_enablement()
        self.sync_image_from_config()

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

    # ---- Presets loading/saving ----
    def reload_presets(self):
        # PDF presets
        self.pdf_combo.blockSignals(True)
        self.pdf_combo.clear()
        for label, path in self._iter_presets('pdf'):
            self.pdf_combo.addItem(label, userData=str(path))
        self.pdf_combo.blockSignals(False)
        if self.pdf_combo.count() > 0:
            self.pdf_combo.setCurrentIndex(0)
            self.on_pdf_preset_changed(self.pdf_combo.currentText())
        # CSS presets
        self.css_combo.blockSignals(True)
        self.css_combo.clear()
        for label, path in self._iter_presets('css'):
            self.css_combo.addItem(label, userData=str(path))
        self.css_combo.blockSignals(False)
        if self.css_combo.count() > 0:
            self.css_combo.setCurrentIndex(0)
            self.on_css_preset_changed(self.css_combo.currentText())

    def _iter_presets(self, kind: str):
        if kind == 'pdf':
            built_in = self.project_root / 'src' / 'mdxscraper' / 'config' / 'pdf_options'
            user_dir = self.project_root / 'data' / 'configs' / 'pdf'
        else:
            built_in = self.project_root / 'src' / 'mdxscraper' / 'config' / 'css_styles'
            user_dir = self.project_root / 'data' / 'configs' / 'css'
        if built_in.exists():
            for p in sorted(built_in.glob('*.toml')):
                yield f"{p.stem} [built-in]", p
        if user_dir.exists():
            for p in sorted(user_dir.glob('*.toml')):
                yield f"{p.stem}", p

    def on_pdf_preset_changed(self, label: str):
        idx = self.pdf_combo.currentIndex()
        path = self.pdf_combo.itemData(idx)
        if path:
            try:
                with open(Path(path), 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.pdf_editor.setPlainText(text)
                    # Persist selection and text in config
                    self.cm.set('output.pdf.preset_label', label)
                    self.cm.set('output.pdf.preset_text', text)
            except Exception as e:
                self.log.append(f"❌ Failed to load PDF preset: {e}")

    def on_css_preset_changed(self, label: str):
        idx = self.css_combo.currentIndex()
        path = self.css_combo.itemData(idx)
        if path:
            try:
                with open(Path(path), 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.css_editor.setPlainText(text)
                    # Persist selection and text in config
                    self.cm.set('output.css.preset_label', label)
                    self.cm.set('output.css.preset_text', text)
            except Exception as e:
                self.log.append(f"❌ Failed to load CSS preset: {e}")

    def on_pdf_save_clicked(self):
        user_dir = (self.project_root / 'data' / 'configs' / 'pdf').resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        file, _ = QFileDialog.getSaveFileName(self, "Save PDF preset as", str(user_dir), "TOML files (*.toml)")
        if not file:
            return
        try:
            with open(Path(file), 'w', encoding='utf-8') as f:
                text = self.pdf_editor.toPlainText()
                f.write(text)
            self.cm.set('output.pdf.preset_label', Path(file).stem)
            self.cm.set('output.pdf.preset_text', text)
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
            with open(Path(file), 'w', encoding='utf-8') as f:
                text = self.css_editor.toPlainText()
                f.write(text)
            self.cm.set('output.css.preset_label', Path(file).stem)
            self.cm.set('output.css.preset_text', text)
            self.log.append(f"✅ Saved CSS preset: {file}")
            self.reload_presets()
        except Exception as e:
            self.log.append(f"❌ Failed to save CSS preset: {e}")

    def update_tab_enablement(self):
        out = self.cm.get("output.file", "")
        suffix = Path(out).suffix.lower() if out else ""
        is_pdf = suffix == '.pdf'
        is_image = suffix in ('.jpg', '.jpeg', '.png', '.webp')
        self.tabs.setTabEnabled(self.tabs.indexOf(self.tab_pdf), is_pdf)
        self.tabs.setTabEnabled(self.tabs.indexOf(self.tab_image), is_image)
        # CSS always enabled


class ConversionWorker(QThread):
    finished_sig = Signal(str)
    error_sig = Signal(str)
    log_sig = Signal(str)

    def __init__(self, project_root: Path, cm: ConfigManager, pdf_text: str = '', css_text: str = ''):
        super().__init__()
        self.project_root = project_root
        self.cm = cm
        self._pdf_text = pdf_text
        self._css_text = css_text

    def run(self):
        try:
            from mdxscraper.core.converter import mdx2html, mdx2pdf, mdx2img
            import time

            # Start timing
            start_time = time.time()
            
            cfg = self.cm._config  # Use in-memory config instead of reloading from file
            input_file = self.cm._resolve_path(cfg.get('input', {}).get('file'))
            mdx_file = self.cm._resolve_path(cfg.get('dictionary', {}).get('file'))
            output_path = self.cm._resolve_path(cfg.get('output', {}).get('file'))
            
            # Apply timestamp if enabled
            timestamp_enabled = self.cm.get_output_add_timestamp()
            current_time = None
            if timestamp_enabled:
                from datetime import datetime
                current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_dir = output_path.parent
                output_name = output_path.name
                output_path = output_dir / (current_time + '_' + output_name)

            suffix = output_path.suffix.lower()
            self.log_sig.emit(f"🔄 Running conversion: {mdx_file.name} -> {output_path.name}")
            
            # Prepare CSS styles from CSS editor
            h1_style = None
            scrap_style = None
            additional_styles = None
            css_text = (self._css_text or '').strip()
            if css_text:
                try:
                    import tomllib as _tomllib
                    data = _tomllib.loads(css_text)
                    style = data.get('style', {}) if isinstance(data, dict) else {}
                    h1_style = style.get('h1_style')
                    scrap_style = style.get('scrap_style')
                    additional_styles = style.get('additional_styles')
                except Exception as ce:
                    self.log_sig.emit(f"⚠️ CSS preset parse failed, using defaults: {ce}")

            if suffix == '.html':
                found, not_found, invalid_words = mdx2html(mdx_file, input_file, output_path, with_toc=True, h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles)
            elif suffix == '.pdf':
                # Base PDF options
                pdf_options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                }
                # Merge PDF options from editor content if available
                pdf_text = (self._pdf_text or '').strip()
                if pdf_text:
                    try:
                        import tomllib as _tomllib
                        data = _tomllib.loads(pdf_text)
                        pdf = data.get('pdf', {}) if isinstance(data, dict) else {}
                        normalized = {k.replace('_', '-'): v for k, v in pdf.items()}
                        pdf_options.update(normalized)
                    except Exception as pe:
                        self.log_sig.emit(f"⚠️ PDF preset parse failed, using defaults: {pe}")
                found, not_found, invalid_words = mdx2pdf(mdx_file, input_file, output_path, pdf_options, h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles)
            elif suffix in ('.jpg', '.jpeg', '.png', '.webp'):
                # Build img options from config
                img_opts = {}
                w = int(self.cm.get('output.image.width', 0) or 0)
                if w > 0:
                    img_opts['width'] = str(w)
                z = float(self.cm.get('output.image.zoom', 1.0) or 1.0)
                if z and z != 1.0:
                    img_opts['zoom'] = str(z)
                if not bool(self.cm.get('output.image.background', True)):
                    img_opts['no-background'] = ''  # will be filtered out; kept for future
                # Format-specific
                if suffix in ('.jpg', '.jpeg'):
                    img_opts['quality'] = int(self.cm.get('output.image.jpg.quality', 85))
                elif suffix == '.png':
                    img_opts['png_optimize'] = bool(self.cm.get('output.image.png.optimize', True))
                    img_opts['png_compress_level'] = int(self.cm.get('output.image.png.compress_level', 9))
                    if bool(self.cm.get('output.image.png.transparent_bg', False)):
                        # Ensure transparent background via CSS already; flag kept for clarity
                        pass
                elif suffix == '.webp':
                    img_opts['webp_quality'] = int(self.cm.get('output.image.webp.quality', 80))
                    img_opts['webp_lossless'] = bool(self.cm.get('output.image.webp.lossless', False))
                found, not_found, invalid_words = mdx2img(
                    mdx_file, input_file, output_path, img_options=img_opts,
                    h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
                )
            else:
                raise RuntimeError(f"Unsupported output extension: {suffix}")

            # Backup input file to output directory if enabled
            if self.cm.get_backup_input():
                try:
                    src = Path(input_file)
                    backup_dir = output_path.parent
                    base_name = src.stem + "_backup" + src.suffix
                    if timestamp_enabled and current_time:
                        base_name = current_time + '_' + base_name
                    dest = backup_dir / base_name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    from shutil import copy2
                    copy2(src, dest)
                    self.log_sig.emit(f"📦 Backed up input to: {dest}")
                except Exception as be:
                    self.log_sig.emit(f"⚠️ Failed to backup input: {be}")

            # Calculate success rate
            total = found + not_found
            if total > 0:
                success_rate = (found / total) * 100
                msg = f"Done. Found: {found}, Success rate: {success_rate:.1f}%"
            else:
                msg = f"Done. Found: {found}, Success rate: 0%"
            
            # Emit success message first
            self.finished_sig.emit(msg)

            # Write invalid words file if enabled and there are any invalid words
            if self.cm.get_save_invalid_words() and invalid_words:
                from mdxscraper.core.converter import write_invalid_words_file
                # Filename pattern: [timestamp_]input_name_invalid.txt
                input_stem = Path(input_file).stem
                base_name = f"{input_stem}_invalid.txt"
                if timestamp_enabled and current_time:
                    base_name = f"{current_time}_{base_name}"
                invalid_words_dir = output_path.parent
                invalid_words_path = invalid_words_dir / base_name
                write_invalid_words_file(invalid_words, invalid_words_path)
                self.log_sig.emit(f"📝 Invalid words saved to: {invalid_words_path}")

            # Calculate and emit duration last
            end_time = time.time()
            duration = end_time - start_time
            
            # Format duration in human readable format
            if duration < 1:
                duration_str = f"{duration*1000:.0f}ms"
            elif duration < 60:
                duration_str = f"{duration:.3f}s"
            else:
                minutes = int(duration // 60)
                seconds = duration % 60
                duration_str = f"{minutes}m {seconds:.1f}s"
            
            self.log_sig.emit(f"⏱️ The entire process took a total of {duration_str}.")
        except Exception as e:
            self.error_sig.emit(str(e))


def run_gui():
    import sys
    app = QApplication(sys.argv)
    root = Path(__file__).resolve().parents[3]
    w = MainWindow(root)
    w.resize(640, 360)
    w.show()
    sys.exit(app.exec())


