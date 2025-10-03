from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from mdxscraper.gui.components.log_panel import LogPanel


@pytest.mark.usefixtures("mock_qt_application")
def test_log_panel_on_copy_log_copies_all_text():
    w = LogPanel()
    # Seed multiple lines to ensure selectAll copies everything
    w.appendLog("line 1")
    w.appendLog("line 2")
    w.appendLog("line 3")

    # Ensure clipboard starts empty
    clipboard = QApplication.clipboard()
    clipboard.clear()

    # Perform copy
    w._on_copy_log()

    # Assert clipboard now has the concatenated text
    text = clipboard.text()
    assert "line 1" in text
    assert "line 2" in text
    assert "line 3" in text


