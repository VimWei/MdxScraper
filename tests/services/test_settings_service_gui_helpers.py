from __future__ import annotations

from pathlib import Path

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.models.config_models import PdfConfig, CssConfig


def seed_defaults(root: Path) -> None:
    d = root / "src" / "mdxscraper" / "config"
    d.mkdir(parents=True, exist_ok=True)
    (d / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n\n[pdf]\npreset_label=''\n\n[css]\npreset_label=''\n",
        encoding="utf-8",
    )


def test_persist_session_and_pdf_css_helpers(tmp_path: Path) -> None:
    seed_defaults(tmp_path)
    cm = ConfigManager(tmp_path)
    ss = SettingsService(tmp_path, cm)
    ss.load()

    # PDF helpers
    pdf = ss.get_pdf_config()
    assert pdf.preset_text == ""
    assert isinstance(pdf.preset_label, str)
    ss.update_pdf_config(PdfConfig(preset_text="ignored", preset_label="L1"))
    assert ss.get("pdf.preset_label") == "L1"

    # CSS helpers
    css = ss.get_css_config()
    assert css.preset_text == ""
    ss.update_css_config(CssConfig(preset_text="ignored", preset_label="C1"))
    assert ss.get("css.preset_label") == "C1"

    # persist session should set labels safely
    ss.persist_session_state(pdf_text="X", pdf_label="P2", css_text="Y", css_label="S2")
    assert ss.get("pdf.preset_label") == "P2"
    assert ss.get("css.preset_label") == "S2"


