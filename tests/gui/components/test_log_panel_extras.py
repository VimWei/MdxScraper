from __future__ import annotations

import pytest

from mdxscraper.gui.components.log_panel import LogPanel


@pytest.mark.usefixtures("mock_qt_application")
def test_log_panel_init_and_actions(monkeypatch):
    w = LogPanel()

    # append and enable toggles
    w.appendLog("hello")
    w.setEnabled(False)
    assert not w.isEnabled()
    w.setEnabled(True)
    assert w.isEnabled()

    # trigger clear/copy via private handlers; they should not raise
    # Bypass clipboard interaction by monkeypatching
    monkeypatch.setattr(w, "_on_copy_log", lambda: None)
    w._on_copy_log()
    w._on_clear_log()


