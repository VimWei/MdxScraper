from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QSlider, QSizePolicy, QSpacerItem
)

from mdxscraper.gui.models.config_models import ImageConfig


class ImagePage(QWidget):
    # Signals for communicating with MainWindow
    width_changed = Signal()
    zoom_changed = Signal()
    background_changed = Signal()
    jpg_quality_changed = Signal()
    png_optimize_changed = Signal()
    png_compress_changed = Signal()
    png_transparent_changed = Signal()
    webp_quality_changed = Signal()
    webp_lossless_changed = Signal()
    webp_transparent_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # General (single row with section label)
        row_gen = QHBoxLayout()
        _section_w = 70
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
        layout.addLayout(row_gen)
        layout.addLayout(row_webp)
        layout.addLayout(row_png)
        layout.addLayout(row_jpg)
        
        # Connect internal signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect internal widget signals to page signals"""
        # Wire sliders and numeric displays
        self.img_zoom_slider.valueChanged.connect(lambda v: self.img_zoom_value.setText(f"{v/10:.1f}"))
        self.jpg_quality_slider.valueChanged.connect(lambda v: self.jpg_quality_value.setText(str(v)))
        self.png_compress_slider.valueChanged.connect(lambda v: self.png_compress_value.setText(str(v)))
        self.webp_quality_slider.valueChanged.connect(lambda v: self.webp_quality_value.setText(str(v)))
        
        # Connect to page signals
        self.img_width.textChanged.connect(lambda: self.width_changed.emit())
        self.img_zoom_slider.valueChanged.connect(lambda: self.zoom_changed.emit())
        self.img_background.toggled.connect(lambda: self.background_changed.emit())
        self.jpg_quality_slider.valueChanged.connect(lambda: self.jpg_quality_changed.emit())
        self.png_optimize.toggled.connect(lambda: self.png_optimize_changed.emit())
        self.png_compress_slider.valueChanged.connect(lambda: self.png_compress_changed.emit())
        self.png_transparent.toggled.connect(lambda: self.png_transparent_changed.emit())
        self.webp_quality_slider.valueChanged.connect(lambda: self.webp_quality_changed.emit())
        self.webp_lossless.toggled.connect(lambda: self.webp_lossless_changed.emit())
        self.webp_transparent.toggled.connect(lambda: self.webp_transparent_changed.emit())

    def get_config(self) -> ImageConfig:
        """Get current page configuration as data class"""
        return ImageConfig(
            width=int(self.img_width.text() or 0),
            zoom=float(self.img_zoom_value.text() or 1.0),
            background=self.img_background.isChecked(),
            jpg_quality=int(self.jpg_quality_value.text() or 85),
            png_optimize=self.png_optimize.isChecked(),
            png_compress_level=int(self.png_compress_value.text() or 9),
            png_transparent_bg=self.png_transparent.isChecked(),
            webp_quality=int(self.webp_quality_value.text() or 80),
            webp_lossless=self.webp_lossless.isChecked(),
            webp_transparent_bg=self.webp_transparent.isChecked()
        )

    def set_config(self, config: ImageConfig) -> None:
        """Set page configuration from data class"""
        self.img_width.setText(str(config.width))
        self.img_zoom_slider.setValue(int(round(config.zoom * 10)))
        self.img_zoom_value.setText(f"{config.zoom:.1f}")
        self.img_background.setChecked(config.background)
        self.jpg_quality_slider.setValue(config.jpg_quality)
        self.jpg_quality_value.setText(str(config.jpg_quality))
        self.png_optimize.setChecked(config.png_optimize)
        self.png_compress_slider.setValue(config.png_compress_level)
        self.png_compress_value.setText(str(config.png_compress_level))
        self.png_transparent.setChecked(config.png_transparent_bg)
        self.webp_quality_slider.setValue(config.webp_quality)
        self.webp_quality_value.setText(str(config.webp_quality))
        self.webp_lossless.setChecked(config.webp_lossless)
        self.webp_transparent.setChecked(config.webp_transparent_bg)


