from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QGridLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCheckBox, QSizePolicy, QSpacerItem, QVBoxLayout
)

from mdxscraper.gui.models.config_models import BasicConfig


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        form = QGridLayout()
        form.setHorizontalSpacing(6)
        form.setVerticalSpacing(8)

        label_w = 80
        btn_w = 90

        # Input row
        lbl_in = QLabel("Input:")
        lbl_in.setFixedWidth(label_w)
        lbl_in.setProperty("class", "field-label")
        self.edit_input = QLineEdit(self)
        btn_input = QPushButton("Choose...", self)
        btn_input.setFixedWidth(btn_w)
        self.btn_input = btn_input
        form.addWidget(lbl_in, 0, 0)
        form.addWidget(self.edit_input, 0, 1)
        form.addWidget(btn_input, 0, 2)

        # Dictionary row
        lbl_dict = QLabel("Dictionary:")
        lbl_dict.setFixedWidth(label_w)
        lbl_dict.setProperty("class", "field-label")
        self.edit_dict = QLineEdit(self)
        btn_dict = QPushButton("Choose...", self)
        btn_dict.setFixedWidth(btn_w)
        self.btn_dict = btn_dict
        form.addWidget(lbl_dict, 1, 0)
        form.addWidget(self.edit_dict, 1, 1)
        form.addWidget(btn_dict, 1, 2)

        # Output row
        lbl_out = QLabel("Output:")
        lbl_out.setFixedWidth(label_w)
        lbl_out.setProperty("class", "field-label")
        self.edit_output = QLineEdit(self)
        btn_output = QPushButton("Choose...", self)
        btn_output.setFixedWidth(btn_w)
        self.btn_output = btn_output
        form.addWidget(lbl_out, 2, 0)
        form.addWidget(self.edit_output, 2, 1)
        form.addWidget(btn_output, 2, 2)

        # Options row
        self.check_timestamp = QCheckBox("Add timestamp to output filename", self)
        self.check_backup = QCheckBox("Backup input file", self)
        self.check_save_invalid = QCheckBox("Save invalid words file", self)

        options_row = QHBoxLayout()
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(12)
        options_row.addWidget(self.check_timestamp)
        options_row.addWidget(self.check_backup)
        options_row.addWidget(self.check_save_invalid)
        options_row.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        form.addLayout(options_row, 3, 1, 1, 2)

        # Sizing
        self.edit_input.setFixedHeight(35)
        self.edit_dict.setFixedHeight(35)
        self.edit_output.setFixedHeight(35)
        btn_input.setFixedHeight(35)
        btn_dict.setFixedHeight(35)
        btn_output.setFixedHeight(35)
        form.setColumnStretch(1, 1)

        root.addLayout(form)

    def get_config(self) -> BasicConfig:
        """Get current page configuration as data class"""
        return BasicConfig(
            input_file=self.edit_input.text(),
            dictionary_file=self.edit_dict.text(),
            output_file=self.edit_output.text(),
            output_add_timestamp=self.check_timestamp.isChecked(),
            backup_input=self.check_backup.isChecked(),
            save_invalid_words=self.check_save_invalid.isChecked()
        )

    def set_config(self, config: BasicConfig) -> None:
        """Set page configuration from data class"""
        self.edit_input.setText(config.input_file)
        self.edit_dict.setText(config.dictionary_file)
        self.edit_output.setText(config.output_file)
        self.check_timestamp.setChecked(config.output_add_timestamp)
        self.check_backup.setChecked(config.backup_input)
        self.check_save_invalid.setChecked(config.save_invalid_words)


