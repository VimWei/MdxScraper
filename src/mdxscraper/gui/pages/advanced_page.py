from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from mdxscraper.models.config_models import AdvancedConfig


class AdvancedPage(QWidget):
    # Signals for communicating with MainWindow
    wkhtmltopdf_path_changed = Signal()
    open_user_data_requested = Signal()
    restore_default_config_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Label width for fields in this page
        _section_w = 120  # Increased width for better text visibility

        # wkhtmltopdf path section
        path_section = QHBoxLayout()
        _lbl_path = QLabel("wkhtmltopdf Path:", self)
        _lbl_path.setProperty("class", "field-label")
        _lbl_path.setFixedWidth(_section_w)
        _lbl_path.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        path_section.addWidget(_lbl_path)
        path_section.addSpacing(8)

        self.edit_wkhtmltopdf_path = QLineEdit(self)
        self.edit_wkhtmltopdf_path.setPlaceholderText(
            "Auto-detect (click Browse to specify manually)"
        )
        path_section.addWidget(self.edit_wkhtmltopdf_path, 1)

        self.btn_browse_wkhtmltopdf = QPushButton("Browse...", self)
        self.btn_browse_wkhtmltopdf.setFixedWidth(90)
        path_section.addWidget(self.btn_browse_wkhtmltopdf)

        self.btn_auto_detect = QPushButton("Auto-detect", self)
        self.btn_auto_detect.setFixedWidth(90)
        path_section.addWidget(self.btn_auto_detect)
        layout.addLayout(path_section)

        # User data directory section
        data_section = QHBoxLayout()
        _lbl_data = QLabel("User Data Path:", self)
        _lbl_data.setProperty("class", "field-label")
        _lbl_data.setFixedWidth(_section_w)
        _lbl_data.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        data_section.addWidget(_lbl_data)
        data_section.addSpacing(8)

        self.edit_data_path = QLineEdit(self)
        self.edit_data_path.setReadOnly(True)
        # Always show as grey text to indicate non-editable
        self.edit_data_path.setProperty("class", "readonly-input")
        data_section.addWidget(self.edit_data_path, 1)

        self.btn_open_data = QPushButton("Open", self)
        self.btn_open_data.setFixedWidth(90)
        self.btn_open_data.setObjectName("open-data-button")
        data_section.addWidget(self.btn_open_data)

        layout.addLayout(data_section)

        # Configuration actions section
        config_section = QHBoxLayout()
        _lbl_config = QLabel("Config Actions:", self)
        _lbl_config.setProperty("class", "field-label")
        _lbl_config.setFixedWidth(_section_w)
        _lbl_config.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        config_section.addWidget(_lbl_config)
        config_section.addSpacing(8)

        self.btn_restore_default = QPushButton("Restore default config", self)
        self.btn_restore_default.setFixedWidth(150)
        self.btn_restore_default.setObjectName("restore-default-button")
        config_section.addWidget(self.btn_restore_default)

        # Add spacer to push button to the left
        config_section.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(config_section)

        # Add some spacing at the bottom
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Validation state (lightweight)
        self.auto_detect_failed = False

        # Connect signals
        self._connect_signals()

        # Initialize data path (default: relative hint)
        self._update_data_path()

    def _connect_signals(self):
        """Connect internal widget signals to page signals"""
        self.edit_wkhtmltopdf_path.editingFinished.connect(self._on_path_changed)
        self.btn_browse_wkhtmltopdf.clicked.connect(self._browse_wkhtmltopdf_path)
        self.btn_auto_detect.clicked.connect(self._auto_detect)
        self.btn_open_data.clicked.connect(self.open_user_data_requested.emit)
        self.btn_restore_default.clicked.connect(self.restore_default_config_requested.emit)

    def _on_path_changed(self):
        """Handle path text changes and update status indicator"""
        self._validate_current_path()
        self.wkhtmltopdf_path_changed.emit()

    def _validate_current_path(self, force_redetect: bool = False):
        """Validate or auto-detect via ConfigCoordinator (no threading)."""
        try:
            filec = self._resolve_cfgc()
            path = self.edit_wkhtmltopdf_path.text().strip()
            if filec is None:
                # Can't reach coordinator; keep placeholder states
                return
            ok, resolved, msg = filec.validate_wkhtmltopdf(path, force_redetect)
            # Update placeholder
            self._update_placeholder_text(ok)
            # Apply detected path only when appropriate
            if ok and resolved and (not path or path in ("auto", "")):
                self.edit_wkhtmltopdf_path.setText(resolved)
                self.auto_detect_failed = False
            elif not ok:
                self.auto_detect_failed = True
        except Exception:
            self.auto_detect_failed = True

    def _auto_detect(self):
        """Trigger auto-detection"""
        # Clear the input field to trigger auto-detect
        self.edit_wkhtmltopdf_path.setText("")

        self._validate_current_path(force_redetect=True)
        self.wkhtmltopdf_path_changed.emit()

    def _resolve_filec(self):
        """Walk up the parent chain to find an object that owns 'filec'."""
        try:
            p = self.parent()
            # Traverse up to a reasonable depth to find filec
            for _ in range(6):
                if p is None:
                    break
                if hasattr(p, "filec"):
                    return getattr(p, "filec")
                if hasattr(p, "parent") and callable(p.parent):
                    p = p.parent()
                else:
                    break
        except Exception:
            return None
        return None

    def _resolve_cfgc(self):
        """Walk up the parent chain to find an object that owns 'cfgc' (ConfigCoordinator)."""
        try:
            p = self.parent()
            for _ in range(6):
                if p is None:
                    break
                if hasattr(p, "cfgc"):
                    return getattr(p, "cfgc")
                if hasattr(p, "parent") and callable(p.parent):
                    p = p.parent()
                else:
                    break
        except Exception:
            return None
        return None

    def _update_data_path(self):
        """Show default relative hint in grey text."""
        self.edit_data_path.setText("data/ (relative to project root)")

    def _update_placeholder_text(self, is_valid: bool = None):
        """Update placeholder text based on validation status"""
        current_path = self.edit_wkhtmltopdf_path.text().strip()

        if not current_path or current_path in ("auto", ""):
            if is_valid is False or self.auto_detect_failed:
                # Auto-detect failed, show simplified message
                self.edit_wkhtmltopdf_path.setPlaceholderText("Click Browse to specify manually")
            else:
                # Default auto-detect message
                self.edit_wkhtmltopdf_path.setPlaceholderText(
                    "Auto-detect (click Browse to specify manually)"
                )
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
            self,
            "Select wkhtmltopdf executable",
            start_dir,
            "Executable files (*.exe);;All files (*.*)",
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
        return AdvancedConfig(wkhtmltopdf_path=self.get_wkhtmltopdf_path())

    def set_config(self, config: AdvancedConfig) -> None:
        """Set page configuration from data class"""
        self.set_wkhtmltopdf_path(config.wkhtmltopdf_path)
