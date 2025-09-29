from __future__ import annotations

from pathlib import Path

from mdxscraper.mdict.mdict_query import IndexBuilder


class Dictionary:
    def __init__(self, mdx_file: Path | str):
        self.mdx_path = Path(mdx_file)
        self._impl = IndexBuilder(self.mdx_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理资源，如关闭数据库连接
        # IndexBuilder 内部会管理自己的资源清理
        pass

    def _lookup_with_fallback(self, word: str) -> str:
        """查找词条，包含多种回退策略"""
        definitions = self._impl.mdx_lookup(word)
        if len(definitions) == 0:
            definitions = self._impl.mdx_lookup(word, ignorecase=True)
        if len(definitions) == 0:
            definitions = self._impl.mdx_lookup(word.replace("-", ""), ignorecase=True)
        if len(definitions) == 0:
            return ""
        return definitions[0].strip()

    def lookup_html(self, word: str) -> str:
        word = word.strip()
        definition = self._lookup_with_fallback(word)
        if not definition:
            return ""

        if definition.startswith("@@@LINK="):
            linked_word = definition.replace("@@@LINK=", "").strip()
            return self._lookup_with_fallback(linked_word)
        else:
            return definition

    @property
    def impl(self):
        return self._impl
