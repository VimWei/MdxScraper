from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit

from mdxscraper.gui.models.config_models import CssConfig


class CssPage(QWidget):
    # Signals for communicating with MainWindow
    preset_changed = Signal(str)  # preset label
    save_clicked = Signal()
    text_changed = Signal()  # text editor content changed

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
        self.css_editor.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self.css_editor, 1)

    def get_config(self) -> CssConfig:
        """Get current page configuration as data class"""
        return CssConfig(
            preset_text=self.css_editor.toPlainText(),
            preset_label=self.css_combo.currentText()
        )

    def set_config(self, config: CssConfig) -> None:
        """Set page configuration from data class"""
        self.css_editor.setPlainText(config.preset_text)
        # Set preset label if it exists in combo box
        for i in range(self.css_combo.count()):
            if self.css_combo.itemText(i) == config.preset_label:
                self.css_combo.setCurrentIndex(i)
                break


