from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from mdxscraper.models.config_models import CssConfig


class CssPage(QWidget):
    # Signals for communicating with MainWindow
    preset_changed = Signal(str)  # preset label
    save_clicked = Signal()
    refresh_clicked = Signal()
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
        # Dirty indicator label (display-only '* Untitled')
        self.dirty_label = QLabel("* Untitled", self)
        self.dirty_label.setProperty("class", "dirty-label")
        self.dirty_label.setVisible(False)
        row_css.addWidget(self.dirty_label)
        # Refresh button (left of Save)
        self.btn_css_refresh = QPushButton("Refresh", self)
        self.btn_css_refresh.clicked.connect(self.refresh_clicked.emit)
        row_css.addWidget(self.btn_css_refresh)
        self.btn_css_save = QPushButton("Save", self)
        self.btn_css_save.clicked.connect(self.save_clicked.emit)
        row_css.addWidget(self.btn_css_save)
        layout.addLayout(row_css)

        # CSS editor
        self.css_editor = QTextEdit(self)
        self.css_editor.setAcceptRichText(False)  # Disable rich text for plain text editing
        self.css_editor.setPlaceholderText(
            "[style]\n# h1_style=..., scrap_style=..., additional_styles=... (TOML)"
        )
        self.css_editor.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self.css_editor, 1)

    def show_dirty(self, is_dirty: bool) -> None:
        self.dirty_label.setVisible(bool(is_dirty))

    def get_config(self) -> CssConfig:
        """Get current page configuration as data class"""
        return CssConfig(
            preset_text=self.css_editor.toPlainText(), preset_label=self.css_combo.currentText()
        )

    def set_config(self, config: CssConfig) -> None:
        """Set page configuration from data class"""
        # Set preset label if it exists in combo box
        label_raw = (config.preset_label or "").strip()
        base_label = label_raw
        # 1) exact match (may include [built-in])
        for i in range(self.css_combo.count()):
            if self.css_combo.itemText(i) == label_raw:
                self.css_combo.setCurrentIndex(i)
                return
        # 2) user-first base-name match (no [built-in] in item)
        for i in range(self.css_combo.count()):
            item = self.css_combo.itemText(i)
            if " [built-in]" in item:
                continue
            item_base = item.split(" [", 1)[0]
            if item_base == base_label:
                self.css_combo.setCurrentIndex(i)
                return
        # 3) built-in base-name match as last resort
        for i in range(self.css_combo.count()):
            item = self.css_combo.itemText(i)
            item_base = item.split(" [", 1)[0]
            if item_base == base_label:
                self.css_combo.setCurrentIndex(i)
                return
