from __future__ import annotations

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QProgressBar,
    QTextEdit, QSizePolicy, QSpacerItem
)


class CommandPanel(QWidget):
    restoreRequested = Signal()
    importRequested = Signal()
    exportRequested = Signal()
    scrapeRequested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        # Row 1: restore/import/export (centered)
        row_actions = QHBoxLayout()
        row_actions.setContentsMargins(0, 0, 0, 0)
        row_actions.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btn_restore = QPushButton("Restore last config", self)
        self.btn_import = QPushButton("Import config", self)
        self.btn_export = QPushButton("Export config", self)
        for b in (self.btn_restore, self.btn_import, self.btn_export):
            b.setFixedWidth(150)
            b.setFixedHeight(32)
        self.btn_restore.clicked.connect(self.restoreRequested.emit)
        self.btn_import.clicked.connect(self.importRequested.emit)
        self.btn_export.clicked.connect(self.exportRequested.emit)

        row_actions.addWidget(self.btn_restore)
        row_actions.addSpacing(12)
        row_actions.addWidget(self.btn_import)
        row_actions.addSpacing(12)
        row_actions.addWidget(self.btn_export)
        row_actions.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        root.addLayout(row_actions)

        # Row 2: scrape (centered alone)
        row_scrape = QHBoxLayout()
        row_scrape.setContentsMargins(0, 0, 0, 0)
        row_scrape.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.btn_scrape = QPushButton("Scrape", self)
        self.btn_scrape.setFixedWidth(220)
        self.btn_scrape.setFixedHeight(45)
        self.btn_scrape.setObjectName("scrape-button")
        self.btn_scrape.clicked.connect(self.scrapeRequested.emit)
        row_scrape.addWidget(self.btn_scrape)
        row_scrape.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        root.addLayout(row_scrape)

        # Progress
        self.progress = QProgressBar(self)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFixedHeight(16)
        root.addWidget(self.progress)

        self.log = QTextEdit(self)
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("log message")
        self.log.setMinimumHeight(120)
        self.log.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        root.addWidget(self.log)

        # Bottom row: log actions (left) + spacer (reserve for future i18n switch)
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

    # Public API
    def setProgress(self, value: int) -> None:  # noqa: N802 (Qt naming style)
        self.progress.setValue(max(0, min(100, int(value))))

    def appendLog(self, text: str) -> None:  # noqa: N802
        if text:
            self.log.append(text)

    def setEnabled(self, enabled: bool) -> None:  # noqa: A003, N802
        super().setEnabled(enabled)
        # Keep buttons consistent when disabling panel
        for b in (self.btn_restore, self.btn_import, self.btn_export, self.btn_scrape, self.btn_clear_log, self.btn_copy_log):
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


