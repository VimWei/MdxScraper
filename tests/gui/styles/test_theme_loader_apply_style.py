from __future__ import annotations

from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication, QWidget

from mdxscraper.gui.styles.theme_loader import ThemeLoader


def seed_theme(root: Path) -> None:
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "default.qss").write_text(
        """
QWidget.testClass { color: rgb(1,2,3); }
""".strip(),
        encoding="utf-8",
    )
    (themes / "default.json").write_text('{"base_style": "Fusion"}', encoding="utf-8")


@pytest.mark.usefixtures("mock_qt_application")
def test_apply_style_sets_stylesheet_and_base_style(tmp_path: Path):
    seed_theme(tmp_path)
    loader = ThemeLoader(tmp_path)

    # Apply base style to QApplication
    app = QApplication.instance()
    loader.apply_base_style(app, "default")
    # App style should be set to Fusion per json
    assert app.style().objectName().lower() in ("fusion",)

    # Apply class style to widget; ensure apply_style calls setStyleSheet with extracted class
    w = QWidget()
    loader.apply_style(w, "testClass", "default")
    # The widget stylesheet should include our class rule content
    ss = w.styleSheet()
    # Accept either exact class wrapper or whole theme containing the rule
    assert "testClass" in ss or "QWidget.testClass" in ss
    assert "rgb(1,2,3)" in ss


