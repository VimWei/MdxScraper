from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from mdxscraper.models.config_models import BasicConfig


class BasicPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.setSpacing(8)

        # Determine label width from actual texts to minimize unused space
        label_w = None
        btn_w = 90

        # Input row
        row_in = QHBoxLayout()
        row_in.setContentsMargins(0, 0, 0, 0)
        row_in.setSpacing(8)
        lbl_in = QLabel("Input:")
        lbl_in.setProperty("class", "field-label")
        lbl_in.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_in.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_input = QLineEdit(self)
        btn_input = QPushButton("Browse...", self)
        btn_input.setFixedWidth(btn_w)
        self.btn_input = btn_input
        row_in.addWidget(lbl_in)
        row_in.addWidget(self.edit_input, 1)
        row_in.addWidget(btn_input)

        # Dictionary row
        row_dict = QHBoxLayout()
        row_dict.setContentsMargins(0, 0, 0, 0)
        row_dict.setSpacing(8)
        lbl_dict = QLabel("Dictionary:")
        lbl_dict.setProperty("class", "field-label")
        lbl_dict.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_dict.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_dict = QLineEdit(self)
        btn_dict = QPushButton("Browse...", self)
        btn_dict.setFixedWidth(btn_w)
        self.btn_dict = btn_dict
        row_dict.addWidget(lbl_dict)
        row_dict.addWidget(self.edit_dict, 1)
        row_dict.addWidget(btn_dict)

        # Output row
        row_out = QHBoxLayout()
        row_out.setContentsMargins(0, 0, 0, 0)
        row_out.setSpacing(8)
        lbl_out = QLabel("Output:")
        lbl_out.setProperty("class", "field-label")
        lbl_out.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lbl_out.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.edit_output = QLineEdit(self)
        btn_output = QPushButton("Browse...", self)
        btn_output.setFixedWidth(btn_w)
        self.btn_output = btn_output
        row_out.addWidget(lbl_out)
        row_out.addWidget(self.edit_output, 1)
        row_out.addWidget(btn_output)

        # Align labels to longest label width (add a small safety margin)
        label_w = (
            max(
                lbl_in.sizeHint().width(),
                lbl_dict.sizeHint().width(),
                lbl_out.sizeHint().width(),
            )
            + 6
        )
        lbl_in.setFixedWidth(label_w)
        lbl_dict.setFixedWidth(label_w)
        lbl_out.setFixedWidth(label_w)

        # Options row
        self.check_timestamp = QCheckBox("Add timestamp to filename", self)
        self.check_backup = QCheckBox("Backup input file", self)
        self.check_save_invalid = QCheckBox("Save invalid words file", self)
        self.check_with_toc = QCheckBox("Include table of contents", self)

        options_row = QHBoxLayout()
        options_row.setContentsMargins(0, 0, 0, 0)
        options_row.setSpacing(12)
        # Add expanding spacer on the left to center the group
        options_row.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        options_row.addWidget(self.check_with_toc)
        options_row.addWidget(self.check_timestamp)
        options_row.addWidget(self.check_backup)
        options_row.addWidget(self.check_save_invalid)
        # Add expanding spacer on the right to balance
        options_row.addItem(QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # ---- Assemble rows into root with equal stretch ----
        root.addLayout(row_in, 1)
        root.addLayout(row_dict, 1)
        root.addLayout(row_out, 1)
        root.addLayout(options_row, 1)

        # Sizing
        self.edit_input.setFixedHeight(35)
        self.edit_dict.setFixedHeight(35)
        self.edit_output.setFixedHeight(35)
        btn_input.setFixedHeight(35)
        btn_dict.setFixedHeight(35)
        btn_output.setFixedHeight(35)
        # Ensure labels don't overlap and fields expand horizontally
        self.edit_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.edit_dict.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.edit_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def get_config(self) -> BasicConfig:
        """Get current page configuration as data class"""
        return BasicConfig(
            input_file=self.edit_input.text(),
            dictionary_file=self.edit_dict.text(),
            output_file=self.edit_output.text(),
            output_add_timestamp=self.check_timestamp.isChecked(),
            backup_input=self.check_backup.isChecked(),
            save_invalid_words=self.check_save_invalid.isChecked(),
            with_toc=self.check_with_toc.isChecked(),
        )

    def set_config(self, config: BasicConfig) -> None:
        """Set page configuration from data class"""
        self.edit_input.setText(config.input_file)
        self.edit_dict.setText(config.dictionary_file)
        self.edit_output.setText(config.output_file)
        self.check_timestamp.setChecked(config.output_add_timestamp)
        self.check_backup.setChecked(config.backup_input)
        self.check_save_invalid.setChecked(config.save_invalid_words)
        self.check_with_toc.setChecked(config.with_toc)
