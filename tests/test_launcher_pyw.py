"""Tests for the silent Windows launcher (``MdxScraper.pyw``)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYW = ROOT / "MdxScraper.pyw"


def _load():
    import importlib.util

    spec = importlib.util.spec_from_file_location("mdxscraper_launcher", PYW)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pyw_exists():
    assert PYW.is_file()


def test_pyw_is_stdlib_only_and_self_contained():
    text = PYW.read_text(encoding="utf-8")
    # Self-contained: no helper run.py, and no third-party / GUI imports at
    # module level, because it must start under a bare system pythonw.
    assert "run.py" not in text
    for banned in ("PySide6", "mdxscraper.gui", "import mdxscraper"):
        assert banned not in text


def test_pyw_delegates_to_module():
    text = PYW.read_text(encoding="utf-8")
    assert '_MODULE = "mdxscraper"' in text
    assert "run_module" in text


def test_vbs_launcher_removed():
    assert not list(ROOT.glob("*.vbs"))


def test_readme_does_not_reference_vbs():
    assert ".vbs" not in (ROOT / "README.md").read_text(encoding="utf-8")


def test_windowed_python_prefers_base_python_exe(tmp_path, monkeypatch):
    module = _load()
    venv = tmp_path / ".venv"
    (venv / "Scripts").mkdir(parents=True)
    (venv / "Scripts" / "python.exe").write_text("", encoding="utf-8")
    (venv / "Scripts" / "pythonw.exe").write_text("", encoding="utf-8")
    base = tmp_path / "base"
    base.mkdir()
    (base / "python.exe").write_text("", encoding="utf-8")
    (base / "pythonw.exe").write_text("", encoding="utf-8")
    (venv / "pyvenv.cfg").write_text(f"home = {base}\n", encoding="utf-8")

    monkeypatch.setattr(module, "_VENV_DIR", venv)
    monkeypatch.setattr(module, "_is_windows", lambda: True)

    assert module._windowed_python() == base / "python.exe"


def test_windowed_python_falls_back_to_venv_launcher(tmp_path, monkeypatch):
    module = _load()
    venv = tmp_path / ".venv"
    (venv / "Scripts").mkdir(parents=True)
    shim = venv / "Scripts" / "python.exe"
    shim.write_text("", encoding="utf-8")

    monkeypatch.setattr(module, "_VENV_DIR", venv)
    monkeypatch.setattr(module, "_is_windows", lambda: True)

    assert module._windowed_python() == shim


def test_relaunch_targets_the_pyw_and_activates_the_venv(tmp_path, monkeypatch):
    module = _load()
    venv = tmp_path / ".venv"
    (venv / "Scripts").mkdir(parents=True)
    launcher = venv / "Scripts" / "python.exe"
    launcher.write_text("", encoding="utf-8")
    base = tmp_path / "base"
    base.mkdir()
    base_python = base / "python.exe"
    base_python.write_text("", encoding="utf-8")
    (venv / "pyvenv.cfg").write_text(f"home = {base}\n", encoding="utf-8")

    monkeypatch.setattr(module, "_VENV_DIR", venv)
    monkeypatch.setattr(module, "_PROJECT_ROOT", tmp_path)
    monkeypatch.setenv(module._LOG_PATH_ENV, str(tmp_path / "launcher.log"))

    calls = []

    class FakePopen:
        def __init__(self, args, **kwargs):
            calls.append((args, kwargs))

    monkeypatch.setattr(module.subprocess, "Popen", FakePopen)
    module._relaunch_windowed(module._windowed_python())

    args, kwargs = calls[0]
    assert args[0] == str(base_python)
    assert args[1] == str(module._SCRIPT)
    assert "-m" not in args
    assert kwargs.get("creationflags") != 0
    env = kwargs["env"]
    assert env["__PYVENV_LAUNCHER__"] == str(launcher)
    assert env["VIRTUAL_ENV"] == str(venv)
    assert env["PATH"].startswith(str(venv / "Scripts"))
    assert env[module._NO_RELAUNCH_ENV] == "1"


def test_launcher_is_noop_off_windows(monkeypatch):
    module = _load()
    monkeypatch.setattr(module, "_is_windows", lambda: False)
    monkeypatch.setattr(module, "_has_console", lambda: False)
    assert module._windowed_python() is None
    assert module._prepare_windows_launch() is False
