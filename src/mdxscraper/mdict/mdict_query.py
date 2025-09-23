from __future__ import annotations

"""mdict-query shim package.

Exposes a thin compatibility layer to the vendored mdict-query code
shipped within this repository under src/mdxscraper/mdict/vendor.
"""

__all__ = [
    "mdict_query",
]

from pathlib import Path
import sys


def _import_bundled_mdict_query():
    """Import the existing mdict_query module from lib/mdict-query.

    Returns the imported module. This keeps the current source of truth
    in lib/mdict-query and avoids duplication during Phase 1.
    """
    project_root = Path(__file__).resolve().parents[3]
    # Load vendored copy inside src/mdxscraper/mdict/vendor
    vendor_dir = project_root / "src" / "mdxscraper" / "mdict" / "vendor"
    if str(vendor_dir) not in sys.path:
        sys.path.insert(0, str(vendor_dir))
    import mdict_query as _impl  # type: ignore

    return _impl


# Re-export commonly used symbols to provide a stable import surface
_impl = _import_bundled_mdict_query()

# Allow: from mdxscraper.mdict.mdict_query import IndexBuilder
IndexBuilder = _impl.IndexBuilder  # noqa: N816 (preserve original name)


