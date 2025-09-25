from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFileDialog, QSizePolicy, QSpacerItem
)
from PySide6.QtGui import QFont

from mdxscraper.utils.path_utils import get_auto_detect_status, validate_wkhtmltopdf_path, force_auto_detect
from mdxscraper.gui.models.config_models import AdvancedConfig


class ValidationWorker(QThread):
    """Worker thread for validating wkhtmltopdf paths"""
    validation_complete = Signal(bool, str, str)  # is_valid, path, message
    
    def __init__(self, path: str, force_redetect: bool = False):
        super().__init__()
        self.path = path
        self.force_redetect = force_redetect
    
    def run(self):
        if not self.path or self.path in ("auto", ""):
            # Auto-detect
            if self.force_redetect:
                is_valid, detected_path, message = force_auto_detect()
            else:
                is_valid, detected_path, message = get_auto_detect_status()
            self.validation_complete.emit(is_valid, detected_path, message)
        else:
            # Manual path
            is_valid, message = validate_wkhtmltopdf_path(self.path)
            self.validation_complete.emit(is_valid, self.path, message)


class AdvancedPage(QWidget):
    # Signals for communicating with MainWindow
    with_toc_changed = Signal()
    wkhtmltopdf_path_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # HTML Options section
        html_section = QHBoxLayout()
        _section_w = 120  # Increased width for better text visibility
        _lbl_html = QLabel("HTML Options", self)
        _lbl_html.setProperty("class", "field-label")
        _lbl_html.setFixedWidth(_section_w)
        _lbl_html.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        html_section.addWidget(_lbl_html)
        html_section.addSpacing(8)
        
        # with_toc checkbox
        self.check_with_toc = QCheckBox("Generate table of contents", self)
        html_section.addWidget(self.check_with_toc)
        html_section.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(html_section)
        
        # wkhtmltopdf path section
        path_section = QHBoxLayout()
        _lbl_path = QLabel("wkhtmltopdf Path:", self)
        _lbl_path.setProperty("class", "field-label")
        _lbl_path.setFixedWidth(_section_w)
        _lbl_path.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        path_section.addWidget(_lbl_path)
        path_section.addSpacing(8)
        
        self.edit_wkhtmltopdf_path = QLineEdit(self)
        self.edit_wkhtmltopdf_path.setPlaceholderText("Auto-detect (click Browse to specify manually)")
        path_section.addWidget(self.edit_wkhtmltopdf_path, 1)
        
        self.btn_browse_wkhtmltopdf = QPushButton("Browse...", self)
        self.btn_browse_wkhtmltopdf.setFixedWidth(90)
        path_section.addWidget(self.btn_browse_wkhtmltopdf)
        
        self.btn_auto_detect = QPushButton("Auto-detect", self)
        self.btn_auto_detect.setFixedWidth(90)
        self.btn_auto_detect.setToolTip("Auto-detect wkhtmltopdf installation")
        path_section.addWidget(self.btn_auto_detect)
        layout.addLayout(path_section)
        
        # Add some spacing at the bottom
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Initialize validation worker
        self.validation_worker = None
        self.has_been_validated = False  # Track if validation has been performed
        self.auto_detect_failed = False  # Track if auto-detect has failed
        
        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect internal widget signals to page signals"""
        self.check_with_toc.toggled.connect(lambda: self.with_toc_changed.emit())
        self.edit_wkhtmltopdf_path.editingFinished.connect(self._on_path_changed)
        self.btn_browse_wkhtmltopdf.clicked.connect(self._browse_wkhtmltopdf_path)
        self.btn_auto_detect.clicked.connect(self._auto_detect)

    def _on_path_changed(self):
        """Handle path text changes and update status indicator"""
        self._validate_current_path()
        self.wkhtmltopdf_path_changed.emit()
    
    def _validate_current_path(self):
        """Start validation of the current path"""
        current_path = self.edit_wkhtmltopdf_path.text().strip()
        
        # Cancel any existing validation
        if self.validation_worker and self.validation_worker.isRunning():
            self.validation_worker.terminate()
            self.validation_worker.wait()
        
        # Show loading state
        self._update_status_indicator()
        
        # Start new validation
        self.validation_worker = ValidationWorker(current_path)
        self.validation_worker.validation_complete.connect(self._on_validation_complete)
        self.validation_worker.start()
        self.has_been_validated = True
    
    def _on_validation_complete(self, is_valid: bool, path: str, message: str):
        """Handle validation completion"""
        # Update placeholder text based on validation result
        self._update_placeholder_text(is_valid)
        
        # If auto-detect was successful, save the detected path to config
        if is_valid and path and path != "wkhtmltopdf":
            current_input = self.edit_wkhtmltopdf_path.text().strip()
            if not current_input or current_input in ("auto", ""):
                # Auto-detect was successful, save the detected path
                self.edit_wkhtmltopdf_path.setText(path)
                self.wkhtmltopdf_path_changed.emit()
                self.auto_detect_failed = False
        else:
            # Auto-detect failed
            self.auto_detect_failed = True
        
        # Clean up worker
        if self.validation_worker:
            self.validation_worker.deleteLater()
            self.validation_worker = None

    def _auto_detect(self):
        """Trigger auto-detection"""
        # Clear the input field to trigger auto-detect
        self.edit_wkhtmltopdf_path.setText("")
        
        # Cancel any existing validation
        if self.validation_worker and self.validation_worker.isRunning():
            self.validation_worker.terminate()
            self.validation_worker.wait()
        
        # Start forced validation
        self.validation_worker = ValidationWorker("", force_redetect=True)
        self.validation_worker.validation_complete.connect(self._on_validation_complete)
        self.validation_worker.start()
        
        self.wkhtmltopdf_path_changed.emit()

    def _update_placeholder_text(self, is_valid: bool = None):
        """Update placeholder text based on validation status"""
        current_path = self.edit_wkhtmltopdf_path.text().strip()
        
        if not current_path or current_path in ("auto", ""):
            if is_valid is False or self.auto_detect_failed:
                # Auto-detect failed, show simplified message
                self.edit_wkhtmltopdf_path.setPlaceholderText("Click Browse to specify manually")
            else:
                # Default auto-detect message
                self.edit_wkhtmltopdf_path.setPlaceholderText("Auto-detect (click Browse to specify manually)")
        else:
            # Manual path specified, no placeholder needed
            self.edit_wkhtmltopdf_path.setPlaceholderText("")

    def _browse_wkhtmltopdf_path(self):
        """Browse for wkhtmltopdf executable"""
        current_path = self.edit_wkhtmltopdf_path.text().strip()
        if current_path and current_path != "auto":
            try:
                # Try to use the current path as starting directory
                start_dir = str(Path(current_path).parent)
            except Exception:
                start_dir = ""
        else:
            start_dir = ""
        
        file, _ = QFileDialog.getOpenFileName(
            self, "Select wkhtmltopdf executable", start_dir,
            "Executable files (*.exe);;All files (*.*)"
        )
        if file:
            self.edit_wkhtmltopdf_path.setText(file)
            self._update_placeholder_text()
            self._validate_current_path()
            self.wkhtmltopdf_path_changed.emit()

    def set_wkhtmltopdf_path(self, path: str):
        """Set the wkhtmltopdf path value (called by MainWindow)"""
        # Convert "auto" to empty string for display
        display_path = "" if path in ("auto", "") else path
        self.edit_wkhtmltopdf_path.setText(display_path)
        # Update placeholder text based on current state
        self._update_placeholder_text()

    def get_wkhtmltopdf_path(self) -> str:
        """Get the current wkhtmltopdf path value"""
        current_path = self.edit_wkhtmltopdf_path.text().strip()
        # Return empty string if no path is specified (for auto-detect)
        return current_path if current_path else ""

    def get_config(self) -> AdvancedConfig:
        """Get current page configuration as data class"""
        return AdvancedConfig(
            with_toc=self.check_with_toc.isChecked(),
            wkhtmltopdf_path=self.get_wkhtmltopdf_path()
        )

    def set_config(self, config: AdvancedConfig) -> None:
        """Set page configuration from data class"""
        self.check_with_toc.setChecked(config.with_toc)
        self.set_wkhtmltopdf_path(config.wkhtmltopdf_path)
