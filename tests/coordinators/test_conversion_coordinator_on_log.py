from __future__ import annotations

from pathlib import Path

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.coordinators.conversion_coordinator import ConversionCoordinator
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


class DummyMW:
    def __init__(self):
        self.logs: list[str] = []

        class LogPanel:
            def __init__(self, outer):
                self._outer = outer

            def appendLog(self, text: str) -> None:
                self._outer.logs.append(text)

        self.log_panel = LogPanel(self)


def test_on_log_filters_progress_messages(tmp_path: Path):
    # minimal wiring
    (tmp_path / "src" / "mdxscraper" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / "src" / "mdxscraper" / "config" / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n", encoding="utf-8"
    )
    ss = SettingsService(tmp_path, ConfigManager(tmp_path))
    ps = PresetsService(tmp_path)
    cc = ConversionCoordinator(ss, ps, tmp_path, ss.cm)
    mw = DummyMW()

    # should ignore progress-prefixed lines
    cc.on_log(mw, "Progress: 40%")
    cc.on_log(mw, "Normal log")
    assert mw.logs == ["Normal log"]
