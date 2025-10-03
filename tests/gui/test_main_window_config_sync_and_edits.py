from __future__ import annotations

from pathlib import Path

import pytest

from mdxscraper.gui.main_window import MainWindow


def seed_defaults_and_theme(root: Path) -> None:
    d = root / "src" / "mdxscraper" / "config"
    d.mkdir(parents=True, exist_ok=True)
    (d / "default_config.toml").write_text(
        "[basic]\ninput_file='a.txt'\ndictionary_file='a.mdx'\noutput_file='out.html'\n\n[pdf]\npreset_label=''\n\n[css]\npreset_label=''\n",
        encoding="utf-8",
    )
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "default.qss").write_text(".root { }", encoding="utf-8")


@pytest.mark.usefixtures("mock_qt_application")
def test_restore_last_config_and_sync_shims(monkeypatch, tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    called = {"restore": 0, "sync_from": 0}

    monkeypatch.setattr(
        w.cfgc,
        "restore_last_config",
        lambda _mw: called.__setitem__("restore", called["restore"] + 1),
    )
    monkeypatch.setattr(
        w.cfgc,
        "sync_all_from_config",
        lambda _mw: called.__setitem__("sync_from", called["sync_from"] + 1),
    )

    w.restore_last_config()
    assert called["restore"] == 1

    # deprecated shim
    w.sync_from_config()
    assert called["sync_from"] == 1


@pytest.mark.usefixtures("mock_qt_application")
def test_iter_presets_and_on_edited_updates_settings(monkeypatch, tmp_path: Path):
    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    # _iter_presets delegates to presets.iter_presets
    monkeypatch.setattr(
        w.presets, "iter_presets", lambda kind: iter([("A", "fileA"), ("B", "fileB")])
    )
    assert list(w._iter_presets("pdf")) == [("A", "fileA"), ("B", "fileB")]

    # on_input_edited also adjusts output filename base
    w.edit_output.setText(str(tmp_path / "data" / "output" / "x.html"))
    w.edit_input.setText(str(tmp_path / "data" / "input" / "new_input.md"))
    w.on_input_edited()
    assert w.settings.get("basic.input_file")
    assert w.settings.get("basic.output_file").endswith("new_input.html")

    # dictionary edit
    w.edit_dict.setText("dict.mdx")
    w.on_dictionary_edited()
    assert w.settings.get("basic.dictionary_file").endswith("dict.mdx")

    # output edit
    w.edit_output.setText("final.html")
    w.on_output_edited()
    assert w.settings.get("basic.output_file").endswith("final.html")
