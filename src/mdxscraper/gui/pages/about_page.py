from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QSpacerItem
from mdxscraper.version import get_version_display


class AboutPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Row: Version (match Advanced page style)
        version_row = QHBoxLayout()
        _lbl_version = QLabel("Version:", self)
        _lbl_version.setProperty("class", "field-label")
        _lbl_version.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        _lbl_version.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        version_row.addWidget(_lbl_version)
        version_row.addSpacing(8)

        _val_version = QLabel(f"MdxScraper {get_version_display()}", self)
        _val_version.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        _val_version.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        version_row.addWidget(_val_version, 1)
        layout.addLayout(version_row)

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

        # Make label columns share the same width based on the longest label
        max_label_w = max(_lbl_version.sizeHint().width(), _lbl_home.sizeHint().width())
        _lbl_version.setFixedWidth(max_label_w)
        _lbl_home.setFixedWidth(max_label_w)

        layout.addLayout(home_row)

        # Keep rows at the top; prevent vertical stretch of rows when resizing
        layout.addStretch(1)
