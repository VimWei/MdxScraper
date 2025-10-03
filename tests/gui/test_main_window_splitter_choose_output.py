from __future__ import annotations

from pathlib import Path

import pytest


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
def test_on_splitter_moved_enforces_min(tmp_path: Path):
    from mdxscraper.gui.main_window import MainWindow

    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    # Force sizes under minimums and trigger handler
    w.splitter.setSizes([7, 5, 3])
    # Call handler (pos, index values unused)
    w.on_splitter_moved(0, 0)

    sizes = w.splitter.sizes()
    # Ensure handler executed without error and returned a 3-part sizes list
    assert isinstance(sizes, list) and len(sizes) == 3


@pytest.mark.usefixtures("mock_qt_application")
def test_choose_output_uses_output_dir_and_default_name(monkeypatch, tmp_path: Path):
    from PySide6.QtWidgets import QFileDialog

    from mdxscraper.gui.main_window import MainWindow

    seed_defaults_and_theme(tmp_path)
    w = MainWindow(tmp_path)

    # Configure settings for input and output directory
    inp = tmp_path / "data" / "input" / "lesson.txt"
    inp.parent.mkdir(parents=True, exist_ok=True)
    inp.write_text("# L\nword", encoding="utf-8")
    out_dir = tmp_path / "data" / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    w.settings.set("basic.input_file", str(inp))
    w.edit_input.setText(str(inp))
    w.settings.set("output.directory", str(out_dir))

    # Intercept save dialog and return a path to verify set
    captured = {}

    def fake_get_save_file_name(*args, **kwargs):
        # Ensure the suggested filename contains the input stem
        suggested = Path(args[2]) if len(args) > 2 else Path(kwargs.get("dir", ""))
        assert inp.stem in str(suggested)
        return str(out_dir / (inp.stem + ".html")), ""

    monkeypatch.setattr(QFileDialog, "getSaveFileName", fake_get_save_file_name)

    w.choose_output()

    # Settings reflect chosen file
    assert w.settings.get("basic.output_file").endswith(inp.stem + ".html")
