from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.usefixtures("mock_qt_application")
def test_run_gui_invokes_qapp_and_mainwindow(monkeypatch, tmp_path: Path):
    # Seed minimal theme/assets structure so icon lookup does not fail
    (tmp_path / "src" / "mdxscraper" / "gui" / "assets").mkdir(parents=True, exist_ok=True)

    # Import the module under test after seeding tmp path on sys.path
    import sys

    sys.modules.pop("mdxscraper.gui.main_window", None)
    sys.path.insert(0, str(tmp_path / "src"))

    from mdxscraper.gui import main_window as mw_mod

    created = {}

    class StubMainWindow:
        def __init__(self, root: Path):
            created["root"] = root

        def resize(self, *_):
            pass

        def show(self):
            created["shown"] = True

    # Monkeypatch MainWindow symbol in module to avoid heavy UI
    monkeypatch.setattr(mw_mod, "MainWindow", StubMainWindow)

    # Replace QApplication with a lightweight stub to avoid singleton issues
    class FakeApp:
        _instance = None

        def __init__(self, *_args, **_kwargs):
            type(self)._instance = self

        @classmethod
        def instance(cls):
            return cls._instance

        def setWindowIcon(self, *_):
            pass

        def exec(self):
            return 0

    monkeypatch.setattr(mw_mod, "QApplication", FakeApp)

    # Run and expect SystemExit(0)
    with pytest.raises(SystemExit) as e:
        mw_mod.run_gui()

    # Assertions: exit code is 0 and window constructed/shown
    assert (e.value.code or 0) == 0
    assert isinstance(created.get("root"), Path)
    assert created.get("shown", False) is True


