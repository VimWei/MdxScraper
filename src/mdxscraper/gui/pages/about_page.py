from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class AboutPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addStretch(1)
        title = QLabel('<b>Homepage</b>', self)
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)
        link = QLabel('<a href="https://github.com/VimWei/MdxScraper">https://github.com/VimWei/MdxScraper</a>', self)
        link.setOpenExternalLinks(True)
        link.setAlignment(Qt.AlignHCenter)
        layout.addWidget(link)
        layout.addStretch(1)


