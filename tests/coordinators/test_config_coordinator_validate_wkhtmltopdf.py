from __future__ import annotations

from pathlib import Path

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.coordinators.config_coordinator import ConfigCoordinator
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


def test_validate_wkhtmltopdf_auto_and_manual(monkeypatch, tmp_path: Path):
    # bootstrap defaults
    (tmp_path / "src" / "mdxscraper" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "mdxscraper" / "config" / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n", encoding="utf-8"
    )

    cm = ConfigManager(tmp_path)
    ss = SettingsService(tmp_path, cm)
    ps = PresetsService(tmp_path)
    cc = ConfigCoordinator(ss, ps)

    # auto path, cached detection path ok
    import mdxscraper.utils.path_utils as pu

    monkeypatch.setattr(pu, "get_auto_detect_status", lambda: (True, "/bin/wkhtmltopdf", "ok"))
    ok, resolved, msg = cc.validate_wkhtmltopdf("auto")
    assert ok and resolved.endswith("wkhtmltopdf")

    # manual invalid path
    monkeypatch.setattr(pu, "validate_wkhtmltopdf_path", lambda p: (False, "bad"))
    ok2, resolved2, msg2 = cc.validate_wkhtmltopdf("/nope/wkhtmltopdf")
    assert ok2 is False and resolved2 == ""
