"""Shim around the bundled lib/mdict-query implementation.

This allows future imports as `from mdxscraper.mdict import mdict_query`
while reusing the existing implementation under lib/mdict-query.
"""

from __future__ import annotations

from pathlib import Path
import sys


def _import_bundled_mdict_query():
    """Import the existing mdict_query module from lib/mdict-query.

    Returns the imported module. This keeps the current source of truth
    in lib/mdict-query and avoids duplication during Phase 1.
    """
    project_root = Path(__file__).resolve().parents[3]
    mdict_lib_dir = project_root / "lib" / "mdict-query"
    if str(mdict_lib_dir) not in sys.path:
        sys.path.append(str(mdict_lib_dir))
    import mdict_query as _impl  # type: ignore

    return _impl


# Re-export commonly used symbols to provide a stable import surface
_impl = _import_bundled_mdict_query()

# Allow: from mdxscraper.mdict.mdict_query import IndexBuilder
IndexBuilder = _impl.IndexBuilder  # noqa: N816 (preserve original name)


