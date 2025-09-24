from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton


class FilePicker(QWidget):
    textChanged = Signal(str)
    browseRequested = Signal()

    def __init__(self, text: str = '', parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.edit = QLineEdit(text, self)
        self.edit.editingFinished.connect(self._on_edit_finished)
        self.btn = QPushButton("Choose...", self)
        self.btn.clicked.connect(self.browseRequested.emit)
        layout.addWidget(self.edit)
        layout.addWidget(self.btn)

    def setText(self, text: str) -> None:  # noqa: N802
        self.edit.setText(text)

    def text(self) -> str:
        return self.edit.text()

    def _on_edit_finished(self) -> None:
        self.textChanged.emit(self.edit.text())


