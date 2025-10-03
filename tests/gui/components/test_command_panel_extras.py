from __future__ import annotations

import pytest

from mdxscraper.gui.components.command_panel import CommandPanel


@pytest.mark.usefixtures("mock_qt_application")
def test_command_panel_init_and_controls():
    w = CommandPanel()
    # basic sanity: button exists and enabled by default
    assert hasattr(w, "btn_scrape")
    assert w.btn_scrape.isEnabled()

    # progress API
    w.setProgress(42)
    w.setProgressText("Working...")
    # Enabled toggle
    w.setEnabled(False)
    assert not w.isEnabled()
    w.setEnabled(True)
    assert w.isEnabled()


