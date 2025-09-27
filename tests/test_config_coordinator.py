"""Tests for ConfigCoordinator"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from mdxscraper.coordinators.config_coordinator import ConfigCoordinator
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.models.config_models import BasicConfig, ImageConfig, AdvancedConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def mock_settings():
    """Create mock SettingsService"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    return settings


@pytest.fixture
def mock_presets():
    """Create mock PresetsService"""
    presets = Mock(spec=PresetsService)
    return presets


@pytest.fixture
def config_coordinator(mock_settings, mock_presets):
    """Create ConfigCoordinator instance"""
    return ConfigCoordinator(mock_settings, mock_presets)


def test_config_coordinator_initialization(config_coordinator, mock_settings, mock_presets):
    """Test ConfigCoordinator initialization"""
    assert config_coordinator.settings == mock_settings
    assert config_coordinator.presets == mock_presets


def test_sync_all_from_config(config_coordinator, mock_settings):
    """Test syncing all configuration from settings to UI"""
    # Mock main window with page attributes
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()
    mock_mw.tab_image = Mock()
    mock_mw.tab_advanced = Mock()
    
    # Mock settings methods
    mock_settings.get_basic_config.return_value = BasicConfig(
        input_file="test.txt",
        dictionary_file="dict.mdx",
        output_file="output.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    mock_settings.get_image_config.return_value = ImageConfig(
        width=800,
        zoom=1.0,
        background=True
    )
    mock_settings.get_advanced_config.return_value = AdvancedConfig(
        wkhtmltopdf_path="auto"
    )
    
    # Call the method
    config_coordinator.sync_all_from_config(mock_mw)
    
    # Verify settings methods were called
    mock_settings.get_basic_config.assert_called_once()
    mock_settings.get_image_config.assert_called_once()
    mock_settings.get_advanced_config.assert_called_once()


def test_sync_all_to_config(config_coordinator, mock_settings):
    """Test syncing all configuration from UI to settings"""
    # Mock main window with page attributes
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()
    mock_mw.tab_image = Mock()
    mock_mw.tab_advanced = Mock()
    
    # Mock page methods
    mock_mw.tab_basic.get_config.return_value = BasicConfig(
        input_file="test.txt",
        dictionary_file="dict.mdx",
        output_file="output.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    mock_mw.tab_image.get_config.return_value = ImageConfig(
        width=800,
        zoom=1.0,
        background=True
    )
    mock_mw.tab_advanced.get_config.return_value = AdvancedConfig(
        wkhtmltopdf_path="auto"
    )
    
    # Call the method
    config_coordinator.sync_all_to_config(mock_mw)
    
    # Verify settings methods were called
    mock_settings.update_basic_config.assert_called_once()
    mock_settings.update_image_config.assert_called_once()
    mock_settings.update_advanced_config.assert_called_once()


def test_import_config(config_coordinator, mock_settings, mock_presets):
    """Test importing configuration from file"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()
    mock_mw.tab_image = Mock()
    mock_mw.tab_advanced = Mock()
    mock_mw.tab_pdf = Mock()
    mock_mw.tab_css = Mock()
    mock_mw.preset_coordinator = Mock()
    mock_mw.log_panel = Mock()
    
    # Mock settings methods
    mock_settings.replace_config.return_value = None
    mock_settings.get_normalize_info_once.return_value = {"changed": False}
    
    # Mock file content
    config_content = """
[basic]
input_file = "imported.txt"
dictionary_file = "imported.mdx"
output_file = "imported.html"
output_add_timestamp = true
backup_input = false
save_invalid_words = true
with_toc = true

[image]
width = 1024
height = 768
format = "jpg"

[advanced]
h1_style = "color: blue;"
scrap_style = "font-size: 16px;"
additional_styles = "body { padding: 10px; }"
"""
    
    with patch("builtins.open", mock_open(read_data=config_content)):
        with patch("tomllib.load") as mock_toml:
            mock_toml.return_value = {
                "basic": {
                    "input_file": "imported.txt",
                    "dictionary_file": "imported.mdx",
                    "output_file": "imported.html",
                    "output_add_timestamp": True,
                    "backup_input": False,
                    "save_invalid_words": True,
                    "with_toc": True
                },
                "image": {
                    "width": 1024,
                    "height": 768,
                    "format": "jpg"
                },
                "advanced": {
                    "h1_style": "color: blue;",
                    "scrap_style": "font-size: 16px;",
                    "additional_styles": "body { padding: 10px; }"
                }
            }
            
            # Call the method
            result = config_coordinator.import_config(mock_mw, Path("test_config.toml"))
            
            # Verify result (import_config returns None)
            assert result is None
            
            # Verify settings were updated
            mock_settings.replace_config.assert_called_once()
            mock_settings.get_normalize_info_once.assert_called_once()


def test_export_config(config_coordinator, mock_settings, mock_presets):
    """Test exporting configuration to file"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()
    mock_mw.tab_image = Mock()
    mock_mw.tab_advanced = Mock()
    mock_mw.tab_pdf = Mock()
    mock_mw.tab_css = Mock()
    
    # Mock page methods
    mock_mw.tab_basic.get_config.return_value = BasicConfig(
        input_file="export.txt",
        dictionary_file="export.mdx",
        output_file="export.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    mock_mw.tab_image.get_config.return_value = ImageConfig(
        width=800,
        zoom=1.0,
        background=True
    )
    mock_mw.tab_advanced.get_config.return_value = AdvancedConfig(
        wkhtmltopdf_path="auto"
    )
    
    # Mock preset methods
    mock_mw.tab_pdf.get_preset_text.return_value = "pdf_preset_content"
    mock_mw.tab_css.get_preset_text.return_value = "css_preset_content"
    
    # Mock preset coordinator
    mock_mw.preset_coordinator = Mock()
    mock_mw.preset_coordinator.autosave_untitled_if_needed.return_value = None
    mock_mw.preset_coordinator.create_snapshots_if_needed_on_export.return_value = (None, None)
    
    # Mock log panel
    mock_mw.log_panel = Mock()
    
    with patch("builtins.open", mock_open()) as mock_file:
        with patch("mdxscraper.config.config_manager.tomli_w.dumps") as mock_toml:
            # Call the method
            result = config_coordinator.export_config(mock_mw, Path("export_config.toml"))
            
            # Verify result (export_config returns None)
            assert result is None
            
            # Verify file was opened and toml.dump was called
            mock_file.assert_called_once()
            mock_toml.assert_called_once()


# Note: validate_config method doesn't exist in ConfigCoordinator
# The validation is handled by SettingsService.validate()
