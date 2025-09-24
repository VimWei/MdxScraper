from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit


class PdfPage(QWidget):
    # Signals for communicating with MainWindow
    preset_changed = Signal(str)  # preset label
    save_clicked = Signal()

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
        layout.addWidget(self.pdf_editor, 1)


