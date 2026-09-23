"""Double-click launcher for MdxScraper.

A ``.pyw`` file is started by ``pythonw.exe``, so the launcher itself runs
without a console window. On Windows it hands off to the project virtual
environment's base interpreter; if the ``.venv`` does not exist yet it opens a
visible ``uv run`` console so the first-time setup stays observable.

The hand-off deliberately:
* launches the *base* interpreter's ``python.exe`` (from ``.venv/pyvenv.cfg``
  ``home``), not ``.venv\\Scripts\\pythonw.exe`` — uv's venv launcher is a shim
  that re-executes the base interpreter as a second process;
* uses ``python.exe`` (not ``pythonw.exe``) together with ``CREATE_NO_WINDOW``,
  which allocates an *invisible* console. MdxScraper shells out to console
  tools (``uv version --short``, wkhtmltopdf, ...); with a console-less
  ``pythonw`` parent each child would pop its own console window;
* activates the venv via ``__PYVENV_LAUNCHER__`` and points the child's
  stdout/stderr at ``%LOCALAPPDATA%\\MdxScraper\\launcher.log``.

Everywhere else, and whenever a console is present, it simply runs
``mdxscraper`` in-process. The visible entry point for troubleshooting is:

    uv run mdxscraper

This file is deliberately stdlib-only and self-contained: it must start under a
bare system ``pythonw`` before the project virtual environment exists.
"""

from __future__ import annotations

import os
import runpy
import subprocess
import sys
import traceback
from pathlib import Path

_MODULE = "mdxscraper"
_SCRIPT = Path(__file__).resolve()
_PROJECT_ROOT = _SCRIPT.parent
_VENV_DIR = _PROJECT_ROOT / ".venv"

#: Set on the relaunched child so it never relaunches again.
_NO_RELAUNCH_ENV = "PC_NO_CONSOLE"
#: Optional log-path override, used by tests.
_LOG_PATH_ENV = "PC_LOG"


def _is_windows() -> bool:
    return os.name == "nt"


def _has_console() -> bool:
    """True when stdout/stderr are usable streams (not pythonw's ``None``)."""
    return sys.stdout is not None and sys.stderr is not None


def _log_path() -> Path:
    override = os.environ.get(_LOG_PATH_ENV)
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "MdxScraper" / "launcher.log"


def _redirect_streams_to_log() -> None:
    """Send stdout/stderr to launcher.log when running without a console.

    ``pythonw.exe`` leaves ``sys.stdout`` / ``sys.stderr`` as ``None``. Without
    this, ``print`` / ``sys.stdout.flush()`` calls raise ``AttributeError`` and
    the GUI dies silently.
    """
    if _has_console():
        return
    try:
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("a", encoding="utf-8", buffering=1)
    except OSError:
        return

    sys.stdout = stream
    sys.stderr = stream
    sys.__stdout__ = stream
    sys.__stderr__ = stream

    def _excepthook(exc_type, exc_value, exc_tb) -> None:
        traceback.print_exception(exc_type, exc_value, exc_tb, file=stream)
        stream.flush()

    sys.excepthook = _excepthook


def _venv_interpreter() -> Path | None:
    for name in ("python.exe", "pythonw.exe"):
        candidate = _VENV_DIR / "Scripts" / name
        if candidate.is_file():
            return candidate
    return None


def _base_interpreter() -> Path | None:
    """Return the base interpreter from ``pyvenv.cfg`` ``home``.

    Prefers ``python.exe`` so the invisible console can be inherited by child
    console tools; bypasses uv's ``Scripts\\pythonw.exe`` shim.
    """
    try:
        text = (_VENV_DIR / "pyvenv.cfg").read_text(encoding="utf-8")
    except OSError:
        return None
    home = ""
    for line in text.splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip().lower() == "home":
            home = value.strip()
            break
    if not home:
        return None
    for name in ("python.exe", "pythonw.exe"):
        candidate = Path(home) / name
        if candidate.is_file():
            return candidate
    return None


def _windowed_python() -> Path | None:
    """Interpreter that should host the GUI, or ``None``.

    Prefers the base interpreter (no uv shim); falls back to the venv launcher.
    """
    if not _is_windows():
        return None
    return _base_interpreter() or _venv_interpreter()


def _venv_active() -> bool:
    try:
        return Path(sys.prefix).resolve() == _VENV_DIR.resolve()
    except OSError:
        return False


def _venv_activation_env(env: dict) -> dict:
    """Make a base interpreter behave as the venv, without uv's shim."""
    launcher = _venv_interpreter()
    if launcher is not None:
        env["__PYVENV_LAUNCHER__"] = str(launcher)
    scripts = _VENV_DIR / "Scripts"
    if scripts.is_dir():
        env["VIRTUAL_ENV"] = str(_VENV_DIR)
        env["PATH"] = str(scripts) + os.pathsep + env.get("PATH", "")
    return env


def _relaunch_windowed(interpreter: Path) -> None:
    """Start ``interpreter`` on this script detached, then let the parent exit.

    ``CREATE_NO_WINDOW`` gives the child an invisible console (inherited by the
    console tools the app spawns) while ``stdout``/``stderr`` are pointed at the
    log so the application never sees ``sys.stdout is None``.
    """
    try:
        path = _log_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        stream = path.open("a", encoding="utf-8", buffering=1)
    except OSError:
        stream = subprocess.DEVNULL

    env = _venv_activation_env(dict(os.environ))
    env[_NO_RELAUNCH_ENV] = "1"
    env[_LOG_PATH_ENV] = str(_log_path())

    subprocess.Popen(
        [str(interpreter), str(_SCRIPT)],
        cwd=str(_PROJECT_ROOT),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=stream,
        stderr=subprocess.STDOUT,
        close_fds=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if stream is not subprocess.DEVNULL:
        stream.close()


def _bootstrap_venv_visibly() -> None:
    """First run with no venv: open a visible console so uv progress is readable."""
    subprocess.Popen(
        ["cmd", "/c", f"uv run {_MODULE} || pause"],
        cwd=str(_PROJECT_ROOT),
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )


def _prepare_windows_launch() -> bool:
    """Relaunch windowed when appropriate.

    Returns ``True`` when this process has handed off and should exit, ``False``
    when the caller should run the application in this process.
    """
    if not _is_windows() or _has_console():
        return False
    if os.environ.get(_NO_RELAUNCH_ENV) or _venv_active():
        return False

    interpreter = _windowed_python()
    if interpreter is None:
        # No venv yet: let uv create it in a visible console.
        _bootstrap_venv_visibly()
        return True

    _relaunch_windowed(interpreter)
    return True


def main() -> int:
    # Decide the launch mode first: _redirect_streams_to_log() replaces
    # sys.stdout, which would make the later _has_console() check report a
    # console and skip the windowed relaunch.
    if _prepare_windows_launch():
        return 0

    _redirect_streams_to_log()
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))
    runpy.run_module(_MODULE, run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
