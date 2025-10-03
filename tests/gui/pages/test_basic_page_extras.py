from __future__ import annotations

import pytest

from mdxscraper.gui.pages.basic_page import BasicPage
from mdxscraper.models.config_models import BasicConfig


@pytest.mark.usefixtures("mock_qt_application")
def test_basic_page_get_set_config():
    page = BasicPage()
    cfg = BasicConfig(
        input_file="in.txt",
        dictionary_file="d.mdx",
        output_file="o.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=False,
    )
    page.set_config(cfg)
    got = page.get_config()
    assert got.input_file == "in.txt"
    assert got.dictionary_file == "d.mdx"
    assert got.output_file == "o.html"
    assert got.output_add_timestamp is True
    assert got.backup_input is False
    assert got.save_invalid_words is True
    assert got.with_toc is False
