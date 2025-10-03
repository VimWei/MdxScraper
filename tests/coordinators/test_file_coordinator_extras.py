from __future__ import annotations

from pathlib import Path

from mdxscraper.coordinators.file_coordinator import FileCoordinator
from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.services.settings_service import SettingsService


def test_get_user_data_dir_creates_and_returns_absolute(tmp_path: Path) -> None:
    project_root = tmp_path
    (project_root / "src" / "mdxscraper" / "config").mkdir(parents=True, exist_ok=True)
    (project_root / "src" / "mdxscraper" / "config" / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n", encoding="utf-8"
    )
    ss = SettingsService(project_root, ConfigManager(project_root))
    fc = FileCoordinator(ss, project_root)
    target = fc.get_user_data_dir()
    assert target.is_absolute()
    assert target.exists()


