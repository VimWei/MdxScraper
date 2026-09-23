"""Windows subprocess helpers.

Keeps short-lived console child processes (``uv``, ``wkhtmltopdf``, ...) from
opening their own console window when the GUI itself was started without a
console (``pythonw.exe``).
"""

import subprocess

#: Pass as ``creationflags`` so a console child does not pop a window. ``0`` on
#: non-Windows platforms, where the argument is a harmless no-op.
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
