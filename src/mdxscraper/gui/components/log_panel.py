from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class LogPanel(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Set minimum height for log panel
        self.setMinimumHeight(150)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Log text area
        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("log message")
        self.log.setMinimumHeight(120)
        self.log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.log)

        # Bottom row: log actions
        row_log_actions = QHBoxLayout()
        row_log_actions.setContentsMargins(0, 0, 0, 0)
        self.btn_clear_log = QPushButton("Clear log", self)
        self.btn_copy_log = QPushButton("Copy log", self)
        self.btn_clear_log.setFixedWidth(100)
        self.btn_copy_log.setFixedWidth(100)
        self.btn_clear_log.clicked.connect(self._on_clear_log)
        self.btn_copy_log.clicked.connect(self._on_copy_log)
        row_log_actions.addWidget(self.btn_clear_log)
        row_log_actions.addSpacing(8)
        row_log_actions.addWidget(self.btn_copy_log)
        row_log_actions.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        root.addLayout(row_log_actions)

    def appendLog(self, text: str) -> None:  # noqa: N802
        if text:
            self.log.append(text)

    def setEnabled(self, enabled: bool) -> None:  # noqa: A003, N802
        super().setEnabled(enabled)
        # Keep buttons consistent when disabling panel
        for b in (self.btn_clear_log, self.btn_copy_log):
            b.setEnabled(enabled)

    # Internal handlers
    def _on_clear_log(self) -> None:
        self.log.clear()

    def _on_copy_log(self) -> None:
        self.log.selectAll()
        self.log.copy()
        cursor = self.log.textCursor()
        cursor.clearSelection()
        self.log.setTextCursor(cursor)
