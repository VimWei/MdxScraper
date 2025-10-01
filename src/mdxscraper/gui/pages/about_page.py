from __future__ import annotations

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from mdxscraper.services.version_check_service import VersionCheckService


class VersionCheckThread(QThread):
    """Thread for checking version updates without blocking UI."""
    
    update_available = Signal(bool, str, str)  # is_latest, message, latest_version
    
    def __init__(self):
        super().__init__()
        self.version_service = VersionCheckService()
    
    def run(self):
        """Run version check in background thread."""
        is_latest, message, latest_version = self.version_service.check_for_updates()
        self.update_available.emit(is_latest, message, latest_version or "")


class AboutPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Row: Homepage (match Advanced page style)
        home_row = QHBoxLayout()
        _lbl_home = QLabel("Homepage:", self)
        _lbl_home.setProperty("class", "field-label")
        _lbl_home.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _lbl_home.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        home_row.addWidget(_lbl_home)
        home_row.addSpacing(8)

        _val_home = QLabel(
            '<a href="https://github.com/VimWei/MdxScraper">https://github.com/VimWei/MdxScraper</a>',
            self,
        )
        _val_home.setOpenExternalLinks(True)
        _val_home.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        _val_home.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        home_row.addWidget(_val_home, 1)
        layout.addLayout(home_row)

        # Row: Update check
        update_row = QHBoxLayout()
        _lbl_update = QLabel("Updates:", self)
        _lbl_update.setProperty("class", "field-label")
        _lbl_update.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _lbl_update.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        update_row.addWidget(_lbl_update)
        update_row.addSpacing(8)

        # Update status label
        self.update_status_label = QLabel("Click 'Check for Updates' to check", self)
        self.update_status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.update_status_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        update_row.addWidget(self.update_status_label, 1)
        
        # Check for updates button
        self.check_updates_btn = QPushButton("Check for Updates", self)
        self.check_updates_btn.clicked.connect(self.check_for_updates)
        self.check_updates_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        update_row.addWidget(self.check_updates_btn)
        
        layout.addLayout(update_row)

        # Make label columns share the same width
        max_label_w = max(_lbl_home.sizeHint().width(), _lbl_update.sizeHint().width())
        _lbl_home.setFixedWidth(max_label_w)
        _lbl_update.setFixedWidth(max_label_w)

        # Keep rows at the top; prevent vertical stretch of rows when resizing
        layout.addStretch(1)
        
        # Initialize version check thread
        self.version_thread = None
    
    def check_for_updates(self):
        """Start checking for updates in background thread."""
        if self.version_thread and self.version_thread.isRunning():
            return  # Already checking
        
        # Update UI to show checking status
        self.update_status_label.setText("Checking for updates...")
        self.check_updates_btn.setEnabled(False)
        self.check_updates_btn.setText("Checking...")
        
        # Create and start version check thread
        self.version_thread = VersionCheckThread()
        self.version_thread.update_available.connect(self.on_update_check_complete)
        self.version_thread.finished.connect(self.on_version_thread_finished)
        self.version_thread.start()
    
    def on_update_check_complete(self, is_latest: bool, message: str, latest_version: str):
        """Handle update check completion."""
        self.update_status_label.setText(message)
        
        # Update button text based on result
        if is_latest:
            self.check_updates_btn.setText("Check Again")
        else:
            self.check_updates_btn.setText("Check Again")
    
    def on_version_thread_finished(self):
        """Handle version check thread completion."""
        self.check_updates_btn.setEnabled(True)
        self.check_updates_btn.setText("Check Again")
        if self.version_thread:
            self.version_thread.deleteLater()
            self.version_thread = None
