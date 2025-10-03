from __future__ import annotations

from unittest import mock

from mdxscraper.core.dictionary import Dictionary


class DummyIndex:
    def __init__(self, _):
        pass

    def mdx_lookup(self, word: str, ignorecase: bool = False):
        db = {
            "hello": ["<div>hello</div>"],
            "LINK": ["@@@LINK=hello"],
        }
        if ignorecase:
            for k, v in db.items():
                if k.lower() == word.lower():
                    return v
            return []
        return db.get(word, [])


def test_dictionary_context_and_impl_and_lookup(monkeypatch, tmp_path):
    monkeypatch.setattr("mdxscraper.core.dictionary.IndexBuilder", DummyIndex)
    d = Dictionary(tmp_path / "dummy.mdx")
    # context manager
    with d as ctx:
        assert ctx is d
        # impl property
        assert d.impl is not None
        assert d.lookup_html("hello") == "<div>hello</div>"
        assert d.lookup_html("LINK") == "<div>hello</div>"
        # fallback behavior for missing
        assert d.lookup_html("missing") == ""


