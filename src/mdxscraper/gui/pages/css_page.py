from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit


class CssPage(QWidget):
    # Signals for communicating with MainWindow
    preset_changed = Signal(str)  # preset label
    save_clicked = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Preset selection row
        row_css = QHBoxLayout()
        row_css.addWidget(QLabel("Preset:", self))
        self.css_combo = QComboBox(self)
        self.css_combo.currentTextChanged.connect(self.preset_changed.emit)
        row_css.addWidget(self.css_combo, 1)
        self.btn_css_save = QPushButton("Save", self)
        self.btn_css_save.clicked.connect(self.save_clicked.emit)
        row_css.addWidget(self.btn_css_save)
        layout.addLayout(row_css)
        
        # CSS editor
        self.css_editor = QTextEdit(self)
        self.css_editor.setPlaceholderText("[style]\n# h1_style=..., scrap_style=..., additional_styles=... (TOML)")
        layout.addWidget(self.css_editor, 1)


