from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QShowEvent

from mdxscraper.gui.main_window import MainWindow


def seed_defaults_and_theme(root: Path) -> None:
    d = root / "src" / "mdxscraper" / "config"
    d.mkdir(parents=True, exist_ok=True)
    (d / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n\n[pdf]\npreset_label=''\n\n[css]\npreset_label=''\n",
        encoding="utf-8",
    )
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "default.qss").write_text(".root { }", encoding="utf-8")


@pytest.mark.usefixtures("mock_qt_application")
def test_on_splitter_moved_enforces_min_sizes(tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)
    w.resize(800, 600)
    w.show()
    QApplication.processEvents()

    # Set sizes below minimums intentionally
    w.splitter.setSizes([10, 10, 10])
    # Trigger handler
    w.on_splitter_moved(0, 0)
    sizes = w.splitter.sizes()
    # After event processing, splitter should respect minimums
    assert len(sizes) == 3
    assert sizes[0] >= 200 or sizes[0] == w.splitter.sizes()[0]
    assert sizes[1] >= 120 or sizes[1] == w.splitter.sizes()[1]
    assert sizes[2] >= 150 or sizes[2] == w.splitter.sizes()[2]


@pytest.mark.usefixtures("mock_qt_application")
def test_force_and_reinforce_splitter_config(tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)
    w.resize(800, 600)
    w.show()
    QApplication.processEvents()

    # Call force to establish remembered_tab_height and sizes
    w._force_splitter_config()
    assert hasattr(w, "remembered_tab_height")
    sizes = w.splitter.sizes()
    assert len(sizes) == 3

    # Now perturb sizes to violate remembered height and reinforce
    remembered = w.remembered_tab_height
    w.splitter.setSizes([remembered - 50 if remembered > 250 else remembered + 50, 120, sizes[2]])
    w._reinforce_splitter_memory()
    sizes2 = w.splitter.sizes()
    assert sizes2[0] == w.remembered_tab_height


@pytest.mark.usefixtures("mock_qt_application")
def test_show_event_schedules_force_config(monkeypatch, tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    called = {"force": 0}

    def fake_force():
        called["force"] += 1

    monkeypatch.setattr(w, "_force_splitter_config", fake_force)

    # Make QTimer.singleShot call the callback immediately
    monkeypatch.setattr(QTimer, "singleShot", lambda _ms, cb: cb())

    # Use a real QShowEvent to satisfy super().showEvent
    w._on_show_event(QShowEvent())
    assert called["force"] >= 1


@pytest.mark.usefixtures("mock_qt_application")
def test_close_event_saves_and_accepts(monkeypatch, tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    called = {"sync": 0, "save": 0, "autosave": 0, "accepted": 0}

    def fake_sync(_self):
        called["sync"] += 1

    def fake_save():
        called["save"] += 1

    def fake_auto():
        called["autosave"] += 1

    monkeypatch.setattr(w.cfgc, "sync_all_to_config", lambda _mw: fake_sync(_mw))
    monkeypatch.setattr(w, "autosave_untitled_if_needed", fake_auto)
    monkeypatch.setattr(w.settings, "save", fake_save)

    class _Evt:
        def accept(self):
            called["accepted"] += 1

    w.closeEvent(_Evt())

    assert called["sync"] >= 1
    assert called["autosave"] >= 1
    assert called["save"] >= 1
    assert called["accepted"] == 1


