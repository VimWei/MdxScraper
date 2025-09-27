"""Tests for unified configuration service functionality"""

import pytest
from pathlib import Path
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.models.config_models import BasicConfig, ImageConfig, AdvancedConfig


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_get_basic_config():
    """Test getting Basic page configuration"""
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


def test_update_basic_config():
    """Test updating Basic page configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = BasicConfig(
        input_file="new_input.txt",
        dictionary_file="new_dict.mdx",
        output_file="new_output.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    
    service.update_basic_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_basic_config()
    assert updated_config.input_file == "new_input.txt"
    assert updated_config.dictionary_file == "new_dict.mdx"
    assert updated_config.output_file == "new_output.html"
    assert updated_config.output_add_timestamp is True
    assert updated_config.backup_input is False
    assert updated_config.save_invalid_words is True
    assert updated_config.with_toc is True


def test_get_image_config():
    """Test getting Image page configuration"""
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


def test_update_image_config():
    """Test updating Image page configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = ImageConfig(
        width=1200,
        zoom=2.0,
        background=False,
        jpg_quality=95,
        png_optimize=False,
        png_compress_level=3,
        png_transparent_bg=True,
        webp_quality=90,
        webp_lossless=True,
        webp_transparent_bg=True
    )
    
    service.update_image_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_image_config()
    assert updated_config.width == 1200
    assert updated_config.zoom == 2.0
    assert updated_config.background is False
    assert updated_config.jpg_quality == 95
    assert updated_config.png_optimize is False
    assert updated_config.png_compress_level == 3
    assert updated_config.png_transparent_bg is True
    assert updated_config.webp_quality == 90
    assert updated_config.webp_lossless is True
    assert updated_config.webp_transparent_bg is True


def test_get_advanced_config():
    """Test getting Advanced page configuration"""
    service = SettingsService(project_root=_project_root())
    config = service.get_advanced_config()
    
    assert isinstance(config, AdvancedConfig)
    assert hasattr(config, 'wkhtmltopdf_path')


def test_update_advanced_config():
    """Test updating Advanced page configuration"""
    service = SettingsService(project_root=_project_root())
    
    config = AdvancedConfig(wkhtmltopdf_path="/custom/path/wkhtmltopdf")
    service.update_advanced_config(config)
    
    # Verify the configuration was updated
    updated_config = service.get_advanced_config()
    assert updated_config.wkhtmltopdf_path == "/custom/path/wkhtmltopdf"


def test_configuration_persistence():
    """Test that configuration changes can be made and retrieved"""
    service = SettingsService(project_root=_project_root())
    
    # Get original config
    original_config = service.get_basic_config()
    
    # Update config
    config = BasicConfig(
        input_file="persistent_test.txt",
        dictionary_file="persistent_dict.mdx",
        output_file="persistent_output.html",
        output_add_timestamp=True,
        backup_input=True,
        save_invalid_words=False,
        with_toc=False
    )
    service.update_basic_config(config)
    
    # Verify config was updated
    updated_config = service.get_basic_config()
    assert updated_config.input_file == "persistent_test.txt"
    assert updated_config.dictionary_file == "persistent_dict.mdx"
    assert updated_config.output_file == "persistent_output.html"
    assert updated_config.output_add_timestamp is True
    assert updated_config.backup_input is True
    assert updated_config.save_invalid_words is False
    assert updated_config.with_toc is False


def test_configuration_defaults():
    """Test that configuration has expected structure"""
    service = SettingsService(project_root=_project_root())
    
    # Test basic config structure
    basic_config = service.get_basic_config()
    assert hasattr(basic_config, 'input_file')
    assert hasattr(basic_config, 'dictionary_file')
    assert hasattr(basic_config, 'output_file')
    assert hasattr(basic_config, 'output_add_timestamp')
    assert hasattr(basic_config, 'backup_input')
    assert hasattr(basic_config, 'save_invalid_words')
    assert hasattr(basic_config, 'with_toc')
    
    # Test image config structure
    image_config = service.get_image_config()
    assert hasattr(image_config, 'width')
    assert hasattr(image_config, 'zoom')
    assert hasattr(image_config, 'background')
    assert hasattr(image_config, 'jpg_quality')
    assert hasattr(image_config, 'png_optimize')
    assert hasattr(image_config, 'png_compress_level')
    assert hasattr(image_config, 'png_transparent_bg')
    assert hasattr(image_config, 'webp_quality')
    assert hasattr(image_config, 'webp_lossless')
    assert hasattr(image_config, 'webp_transparent_bg')
    
    # Test advanced config structure
    advanced_config = service.get_advanced_config()
    assert hasattr(advanced_config, 'wkhtmltopdf_path')