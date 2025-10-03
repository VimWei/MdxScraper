from __future__ import annotations

import pytest

from mdxscraper.gui.pages.css_page import CssPage
from mdxscraper.gui.pages.pdf_page import PdfPage
from mdxscraper.models.config_models import CssConfig, PdfConfig


@pytest.mark.usefixtures("mock_qt_application")
@pytest.mark.parametrize(
    "items,label,expected_text",
    [
        # 1) exact match (may include [built-in])
        (["Alpha [built-in]", "Beta"], "Alpha [built-in]", "Alpha [built-in]"),
        # 2) user-first base-name match when both exist -> choose user one
        (["Gamma", "Gamma [built-in]"], "Gamma", "Gamma"),
        # 3) built-in fallback when only built-in exists
        (["Delta [built-in]"], "Delta", "Delta [built-in]"),
    ],
)
def test_css_page_set_config_selection(items, label, expected_text):
    page = CssPage()
    for it in items:
        page.css_combo.addItem(it)

    page.set_config(CssConfig(preset_text="", preset_label=label))
    assert page.css_combo.currentText() == expected_text


@pytest.mark.usefixtures("mock_qt_application")
@pytest.mark.parametrize(
    "items,label,expected_text",
    [
        (["Alpha [built-in]", "Beta"], "Alpha [built-in]", "Alpha [built-in]"),
        (["Gamma", "Gamma [built-in]"], "Gamma", "Gamma"),
        (["Delta [built-in]"], "Delta", "Delta [built-in]"),
    ],
)
def test_pdf_page_set_config_selection(items, label, expected_text):
    page = PdfPage()
    for it in items:
        page.pdf_combo.addItem(it)

    page.set_config(PdfConfig(preset_text="", preset_label=label))
    assert page.pdf_combo.currentText() == expected_text
