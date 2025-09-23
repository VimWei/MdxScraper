from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup

from mdxscraper.mdict.mdict_query import IndexBuilder


class Dictionary:
    def __init__(self, mdx_file: Path | str):
        self.mdx_path = Path(mdx_file)
        self._impl = IndexBuilder(self.mdx_path)

    def lookup_html(self, word: str) -> str:
        word = word.strip()
        definitions = self._impl.mdx_lookup(word)
        if len(definitions) == 0:
            definitions = self._impl.mdx_lookup(word, ignorecase=True)
        if len(definitions) == 0:
            definitions = self._impl.mdx_lookup(word.replace("-", ""), ignorecase=True)
        if len(definitions) == 0:
            return ""
        definition = definitions[0]
        if definition.startswith("@@@LINK="):
            return self._impl.mdx_lookup(definition.replace("@@@LINK=", "").strip())[0].strip()
        else:
            return definition.strip()

    @property
    def impl(self):
        return self._impl


