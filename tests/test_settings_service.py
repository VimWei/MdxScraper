"""Tests for SettingsService"""

import pytest
from pathlib import Path
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.models.config_models import BasicConfig, ImageConfig, AdvancedConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_settings_service_initialization():
    """Test SettingsService initialization"""
    service = SettingsService(project_root=_project_root())
    assert service is not None
    assert service.project_root == _project_root()


def test_get_basic_config():
    """Test getting basic configuration"""
    service = SettingsService(project_root=_project_root())
    config = service.get_basic_config()
    
    assert isinstance(config, BasicConfig)
    assert hasattr(config, 'input_file')
    assert hasattr(config, 'dictionary_file')
    assert hasattr(config, 'output_file')
    assert hasattr(config, 'output_add_timestamp')
    assert hasattr(config, 'backup_input')
    assert hasattr(config, 'save_invalid_words')
    assert hasattr(config, 'with_toc')


def test_get_image_config():
    """Test getting image configuration"""
    service = SettingsService(project_root=_project_root())
    config = service.get_image_config()
    
    assert isinstance(config, ImageConfig)
    assert hasattr(config, 'width')
    assert hasattr(config, 'zoom')
    assert hasattr(config, 'background')
    assert hasattr(config, 'jpg_quality')
    assert hasattr(config, 'png_optimize')
    assert hasattr(config, 'png_compress_level')
    assert hasattr(config, 'png_transparent_bg')
    assert hasattr(config, 'webp_quality')
    assert hasattr(config, 'webp_lossless')
    assert hasattr(config, 'webp_transparent_bg')


def test_get_advanced_config():
    """Test getting advanced configuration"""
    service = SettingsService(project_root=_project_root())
    config = service.get_advanced_config()
    
    assert isinstance(config, AdvancedConfig)
    assert hasattr(config, 'wkhtmltopdf_path')


def test_update_basic_config():
    """Test updating basic configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = BasicConfig(
        input_file="test_input.txt",
        dictionary_file="test_dict.mdx",
        output_file="test_output.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    
    service.update_basic_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_basic_config()
    assert updated_config.input_file == "test_input.txt"
    assert updated_config.dictionary_file == "test_dict.mdx"
    assert updated_config.output_file == "test_output.html"
    assert updated_config.output_add_timestamp is True
    assert updated_config.backup_input is False
    assert updated_config.save_invalid_words is True
    assert updated_config.with_toc is True


def test_update_image_config():
    """Test updating image configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = ImageConfig(
        width=1200,
        zoom=1.5,
        background=False,
        jpg_quality=95,
        png_optimize=False,
        png_compress_level=5,
        png_transparent_bg=True,
        webp_quality=90,
        webp_lossless=True,
        webp_transparent_bg=True
    )
    
    service.update_image_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_image_config()
    assert updated_config.width == 1200
    assert updated_config.zoom == 1.5
    assert updated_config.background is False
    assert updated_config.jpg_quality == 95
    assert updated_config.png_optimize is False
    assert updated_config.png_compress_level == 5
    assert updated_config.png_transparent_bg is True
    assert updated_config.webp_quality == 90
    assert updated_config.webp_lossless is True
    assert updated_config.webp_transparent_bg is True


def test_update_advanced_config():
    """Test updating advanced configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = AdvancedConfig(wkhtmltopdf_path="/custom/path/wkhtmltopdf")
    service.update_advanced_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_advanced_config()
    assert updated_config.wkhtmltopdf_path == "/custom/path/wkhtmltopdf"


def test_get_set_methods():
    """Test basic get/set methods"""
    service = SettingsService(project_root=_project_root())
    
    # Test setting and getting a value
    service.set("test.key", "test_value")
    assert service.get("test.key") == "test_value"
    assert service.get("test.key", "default") == "test_value"
    
    # Test getting non-existent key with default
    assert service.get("non.existent.key", "default_value") == "default_value"