from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit

from mdxscraper.gui.models.config_models import PdfConfig


class PdfPage(QWidget):
    # Signals for communicating with MainWindow
    preset_changed = Signal(str)  # preset label
    save_clicked = Signal()
    text_changed = Signal()  # text editor content changed

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Preset selection row
        row_pdf = QHBoxLayout()
        row_pdf.addWidget(QLabel("Preset:", self))
        self.pdf_combo = QComboBox(self)
        self.pdf_combo.currentTextChanged.connect(self.preset_changed.emit)
        row_pdf.addWidget(self.pdf_combo, 1)
        self.btn_pdf_save = QPushButton("Save", self)
        self.btn_pdf_save.clicked.connect(self.save_clicked.emit)
        row_pdf.addWidget(self.btn_pdf_save)
        layout.addLayout(row_pdf)
        
        # PDF editor
        self.pdf_editor = QTextEdit(self)
        self.pdf_editor.setPlaceholderText("[pdf]\n# wkhtmltopdf options in TOML ...")
        self.pdf_editor.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self.pdf_editor, 1)

    def get_config(self) -> PdfConfig:
        """Get current page configuration as data class"""
        return PdfConfig(
            preset_text=self.pdf_editor.toPlainText(),
            preset_label=self.pdf_combo.currentText()
        )

    def set_config(self, config: PdfConfig) -> None:
        """Set page configuration from data class"""
        self.pdf_editor.setPlainText(config.preset_text)
        # Set preset label if it exists in combo box
        for i in range(self.pdf_combo.count()):
            if self.pdf_combo.itemText(i) == config.preset_label:
                self.pdf_combo.setCurrentIndex(i)
                break


