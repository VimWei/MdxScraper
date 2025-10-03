from __future__ import annotations

import pytest

from mdxscraper.gui.pages.about_page import VersionCheckThread


@pytest.mark.usefixtures("mock_qt_application")
def test_version_check_thread_run_emits_signal(monkeypatch):
    # Arrange: stub service to return a known tuple
    result = (True, "You are up to date", "1.2.3")

    class StubService:
        def check_for_updates(self):
            return result

    captured = {"args": None}

    t = VersionCheckThread()
    # Inject stub service
    t.version_service = StubService()

    def handler(is_latest, message, latest_version):
        captured["args"] = (is_latest, message, latest_version)

    t.update_available.connect(handler)

    # Act: call run synchronously to avoid thread scheduling in tests
    t.run()

    # Assert: emitted values match stub
    assert captured["args"] == (True, "You are up to date", "1.2.3")


