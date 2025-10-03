from __future__ import annotations

import pytest

from mdxscraper.gui.pages.css_page import CssPage
from mdxscraper.gui.pages.pdf_page import PdfPage
from mdxscraper.gui.pages.image_page import ImagePage
from mdxscraper.models.config_models import CssConfig, PdfConfig, ImageConfig


@pytest.mark.usefixtures("mock_qt_application")
def test_css_page_dirty_and_config():
    p = CssPage()
    p.css_combo.addItem("A [built-in]")
    p.css_combo.addItem("B")
    p.show_dirty(True)
    assert not p.dirty_label.isHidden()
    p.set_config(CssConfig(preset_text="t", preset_label="B"))
    got = p.get_config()
    assert got.preset_label in ("B",)


@pytest.mark.usefixtures("mock_qt_application")
def test_pdf_page_dirty_and_config():
    p = PdfPage()
    p.pdf_combo.addItem("A [built-in]")
    p.pdf_combo.addItem("B")
    p.show_dirty(True)
    assert not p.dirty_label.isHidden()
    p.set_config(PdfConfig(preset_text="t", preset_label="B"))
    got = p.get_config()
    assert got.preset_label in ("B",)


@pytest.mark.usefixtures("mock_qt_application")
def test_image_page_get_set_config():
    p = ImagePage()
    cfg = ImageConfig(
        width=800,
        zoom=1.5,
        background=True,
        jpg_quality=90,
        png_optimize=True,
        png_compress_level=5,
        png_transparent_bg=True,
        webp_quality=88,
        webp_lossless=False,
        webp_transparent_bg=True,
    )
    p.set_config(cfg)
    got = p.get_config()
    assert got.width == 800
    assert abs(got.zoom - 1.5) < 1e-6
    assert got.jpg_quality == 90 and got.png_compress_level == 5 and got.webp_quality == 88


