from __future__ import annotations

import pytest

from mdxscraper.gui.pages.advanced_page import AdvancedPage


@pytest.mark.usefixtures("mock_qt_application")
def test_resolve_filec_and_cfgc_walks_parents(monkeypatch):
    # Build a small parent chain mimicking Qt parent() traversal
    class Owner:
        def __init__(self):
            self.filec = object()
            self.cfgc = object()

    owner = Owner()
    page = AdvancedPage()

    # Create an intermediate QWidget to sit between page and owner
    from PySide6.QtWidgets import QWidget

    mid = QWidget()
    page.setParent(mid)

    # Monkeypatch parent() chain to return owner after mid
    original_parent = QWidget.parent

    def chained_parent(self):
        if self is page:
            return mid
        if self is mid:
            return owner
        return original_parent(self)

    # Patch QWidget.parent for this test's scope only
    monkeypatch.setattr(QWidget, "parent", chained_parent, raising=False)

    assert page._resolve_filec() is owner.filec
    assert page._resolve_cfgc() is owner.cfgc


@pytest.mark.usefixtures("mock_qt_application")
def test_resolve_helpers_return_none_on_errors(monkeypatch):
    page = AdvancedPage()

    # Force parent() to raise to hit exception handling
    from PySide6.QtWidgets import QWidget

    def bad_parent(*_a, **_k):
        raise RuntimeError("boom")

    monkeypatch.setattr(QWidget, "parent", bad_parent, raising=False)

    assert page._resolve_filec() is None
    assert page._resolve_cfgc() is None


