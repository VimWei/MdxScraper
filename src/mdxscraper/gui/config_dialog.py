from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout


class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration (stub)")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Future advanced options here."))


