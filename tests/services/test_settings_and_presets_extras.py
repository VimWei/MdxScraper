from __future__ import annotations

from pathlib import Path

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


def test_settings_wrappers_and_to_relative(tmp_path: Path) -> None:
    project_root = tmp_path
    # prepare defaults
    (project_root / "src" / "mdxscraper" / "config").mkdir(parents=True, exist_ok=True)
    (project_root / "src" / "mdxscraper" / "config" / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n", encoding="utf-8"
    )

    cm = ConfigManager(project_root)
    ss = SettingsService(project_root, cm)
    ss.load()

    # set via wrappers and save
    f1 = project_root / "data" / "input" / "a.txt"
    f2 = project_root / "data" / "mdict" / "d.mdx"
    f3 = project_root / "data" / "output" / "o.html"
    f1.parent.mkdir(parents=True, exist_ok=True)
    f2.parent.mkdir(parents=True, exist_ok=True)
    f3.parent.mkdir(parents=True, exist_ok=True)
    f1.write_text("x", encoding="utf-8")
    f2.write_text("y", encoding="utf-8")

    ss.set_input_file(str(f1))
    ss.set_dictionary_file(str(f2))
    ss.set_output_file(str(f3))
    ss.save()

    # validate
    res = ss.validate()
    assert res.is_valid

    # to_relative should strip project root (normalize separators)
    rel = ss.to_relative(f1).replace("\\", "/")
    assert rel.startswith("data/")


def test_presets_dirs_and_iter_and_snapshot(tmp_path: Path) -> None:
    project_root = tmp_path
    ps = PresetsService(project_root)

    # built-in and user dirs
    built_in_pdf = project_root / "src" / "mdxscraper" / "config" / "pdf_options"
    built_in_css = project_root / "src" / "mdxscraper" / "config" / "css_styles"
    built_in_pdf.mkdir(parents=True, exist_ok=True)
    built_in_css.mkdir(parents=True, exist_ok=True)
    (built_in_pdf / "A.toml").write_text("[pdf]\nkey='v'\n", encoding="utf-8")
    (built_in_css / "B.toml").write_text("[style]\nh1_style='x'\n", encoding="utf-8")

    # user dirs
    user_pdf = ps.user_pdf_dir()
    user_css = ps.user_css_dir()
    user_pdf.mkdir(parents=True, exist_ok=True)
    user_css.mkdir(parents=True, exist_ok=True)
    (user_pdf / "U.toml").write_text("[pdf]\nkey='u'\n", encoding="utf-8")
    (user_css / "V.toml").write_text("[style]\nh1_style='y'\n", encoding="utf-8")

    # iterate
    pdf_labels = [name for name, _ in ps.iter_presets("pdf")]
    css_labels = [name for name, _ in ps.iter_presets("css")]
    assert any(x.endswith("[built-in]") for x in pdf_labels)
    assert any(x.endswith("[built-in]") for x in css_labels)
    assert "U" in pdf_labels
    assert "V" in css_labels

    # snapshot
    snap = ps.create_untitled_snapshot("pdf", "[pdf]\na=1\n")
    assert snap.is_file()


