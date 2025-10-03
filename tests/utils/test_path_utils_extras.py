from __future__ import annotations

from unittest import mock

from mdxscraper.utils import path_utils


def test_auto_detect_cache_and_force(monkeypatch) -> None:
    # Simulate detection returns a fake path and valid
    monkeypatch.setattr(path_utils, "detect_wkhtmltopdf_path", lambda: "wkhtmltopdf")
    monkeypatch.setattr(path_utils, "validate_wkhtmltopdf_path", lambda p: (True, "ok"))

    path_utils.clear_auto_detect_cache()
    ok1, p1, m1 = path_utils.get_auto_detect_status()
    ok2, p2, m2 = path_utils.get_auto_detect_status()  # cached
    assert (ok1, p1, m1) == (ok2, p2, m2)

    # Force should redo (we can change return)
    monkeypatch.setattr(path_utils, "validate_wkhtmltopdf_path", lambda p: (False, "bad"))
    ok3, p3, m3 = path_utils.force_auto_detect()
    assert ok3 is False
    assert m3 == "bad"


def test_validate_wkhtmltopdf_path_variants(monkeypatch):
    # simulate FileNotFoundError
    with mock.patch("subprocess.run", side_effect=FileNotFoundError()):
        ok, msg = path_utils.validate_wkhtmltopdf_path("/missing/binary")
        assert not ok and "not found" in msg.lower()
