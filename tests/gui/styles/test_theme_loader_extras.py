from __future__ import annotations

from pathlib import Path

from mdxscraper.gui.styles.theme_loader import ThemeLoader


def write_theme(root: Path, name: str, qss: str, base_style: str | None = None):
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / f"{name}.qss").write_text(qss, encoding="utf-8")
    if base_style is not None:
        (themes / f"{name}.json").write_text(
            f'{"{"}"base_style" : "' + base_style + '"}', encoding="utf-8"
        )


def test_theme_loader_load_extract_and_cache(tmp_path: Path):
    write_theme(
        tmp_path, "default", ".btn { color: red; }\n.other { padding: 4px; }", base_style="Fusion"
    )

    tl = ThemeLoader(tmp_path)
    content1 = tl.load_theme("default")
    assert "color: red" in content1

    # cache path
    content2 = tl.load_theme("default")
    assert content2 == content1

    # extract style
    s = tl.get_style("btn", "default")
    assert s.startswith(".btn") and "color: red" in s

    # available themes
    names = tl.get_available_themes()
    assert "default" in names

    # base style fetch
    assert tl._get_base_style("default") == "Fusion"

    # clear cache
    tl.clear_cache()
    assert tl.load_theme("default") == content1
