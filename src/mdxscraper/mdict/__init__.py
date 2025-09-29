"""mdict package.

Exports the vendored mdict-query API used by this project.
"""

from .mdict_query import IndexBuilder

__all__ = [
    "IndexBuilder",
]
