from __future__ import annotations

from pathlib import Path

import pytest

from mdxscraper.gui.main_window import MainWindow


def seed_defaults_and_theme(root: Path) -> None:
    # default config
    d = root / "src" / "mdxscraper" / "config"
    d.mkdir(parents=True, exist_ok=True)
    (d / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n\n[pdf]\npreset_label=''\n\n[css]\npreset_label=''\n",
        encoding="utf-8",
    )
    # theme files (optional but present)
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "default.qss").write_text(".root { }", encoding="utf-8")


@pytest.mark.usefixtures("mock_qt_application")
def test_main_window_smoke_and_slots(monkeypatch, tmp_path: Path):
    seed_defaults_and_theme(tmp_path)

    w = MainWindow(tmp_path)

    # on_log filters progress
    initial_count = (
        len(w.log_panel.text_edit.toPlainText()) if hasattr(w.log_panel, "text_edit") else 0
    )
    w.on_log("Progress: 10%")
    w.on_log("Hello")
    # Just ensure it didn't crash and something got appended for non-progress

    # Replace convc with a stub to capture slot forwarding
    class StubConv:
        def __init__(self):
            self.progress = None
            self.finished = None
            self.error = None

        def on_progress(self, mw, p, t):
            self.progress = (p, t)

        def on_finished(self, mw, msg):
            self.finished = msg

        def on_error(self, mw, msg):
            self.error = msg

        def run(self, mw):
            # do nothing
            pass

    w.convc = StubConv()
    w.on_progress_update(55, "half")
    w.on_run_finished("ok")
    w.on_run_error("bad")
    assert w.convc.progress == (55, "half")
    assert w.convc.finished == "ok"
    assert w.convc.error == "bad"

    # Methods that open dialogs should early-return if no file is chosen
    from PySide6.QtWidgets import QFileDialog

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: ("", ""))
    monkeypatch.setattr(QFileDialog, "getSaveFileName", lambda *a, **k: ("", ""))
    w.choose_input()
    w.choose_dictionary()
    w.choose_output()
    w.import_config()
    w.export_config()

    # autosave helpers should not crash
    w.autosave_untitled_if_needed()
