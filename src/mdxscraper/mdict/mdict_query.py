from __future__ import annotations

"""mdict-query wrapper.

Adds the vendored mdict-query directory to sys.path and imports the upstream
module unchanged, so we can sync vendor code without edits.
"""

from pathlib import Path
import sys


# Ensure vendored mdict-query is importable as top-level module names
_vendor_dir = Path(__file__).resolve().parent / "vendor"
if str(_vendor_dir) not in sys.path:
    sys.path.insert(0, str(_vendor_dir))

import mdict_query as _mdict_query  # type: ignore

# Re-export stable API
IndexBuilder = _mdict_query.IndexBuilder  # noqa: N816 (preserve original name)

__all__ = ["IndexBuilder"]

