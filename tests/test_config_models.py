"""Tests for configuration data models"""

import pytest

from mdxscraper.models.config_models import (
    AdvancedConfig,
    BasicConfig,
    CssConfig,
    ImageConfig,
    PdfConfig,
)


def test_basic_config():
    """Test BasicConfig data class"""
    config = BasicConfig(
        input_file="test.txt",
        dictionary_file="dict.mdx",
        output_file="output.html",
        output_add_timestamp=True,
        backup_input=False,
        save_invalid_words=True,
        with_toc=True
    )
    
    assert config.input_file == "test.txt"
    assert config.dictionary_file == "dict.mdx"
    assert config.output_file == "output.html"
    assert config.output_add_timestamp is True
    assert config.backup_input is False
    assert config.save_invalid_words is True
    assert config.with_toc is True


def test_basic_config_defaults():
    """Test BasicConfig default values"""
    config = BasicConfig()
    
    assert config.input_file == ""
    assert config.dictionary_file == ""
    assert config.output_file == ""
    assert config.output_add_timestamp is False
    assert config.backup_input is False
    assert config.save_invalid_words is False
    assert config.with_toc is True  # Default is True


def test_image_config():
    """Test ImageConfig data class"""
    config = ImageConfig(
        width=800,
        zoom=1.5,
        background=False,
        jpg_quality=90,
        png_optimize=False,
        png_compress_level=5,
        png_transparent_bg=True,
        webp_quality=85,
        webp_lossless=True,
        webp_transparent_bg=True
    )
    
    assert config.width == 800
    assert config.zoom == 1.5
    assert config.background is False
    assert config.jpg_quality == 90
    assert config.png_optimize is False
    assert config.png_compress_level == 5
    assert config.png_transparent_bg is True
    assert config.webp_quality == 85
    assert config.webp_lossless is True
    assert config.webp_transparent_bg is True


def test_image_config_defaults():
    """Test ImageConfig default values"""
    config = ImageConfig()
    
    assert config.width == 0
    assert config.zoom == 1.0
    assert config.background is True
    assert config.jpg_quality == 85
    assert config.png_optimize is True
    assert config.png_compress_level == 9
    assert config.png_transparent_bg is False
    assert config.webp_quality == 80
    assert config.webp_lossless is False
    assert config.webp_transparent_bg is False


def test_advanced_config():
    """Test AdvancedConfig data class"""
    config = AdvancedConfig(wkhtmltopdf_path="/usr/bin/wkhtmltopdf")
    assert config.wkhtmltopdf_path == "/usr/bin/wkhtmltopdf"


def test_advanced_config_defaults():
    """Test AdvancedConfig default values"""
    config = AdvancedConfig()
    assert config.wkhtmltopdf_path == "auto"


def test_pdf_config():
    """Test PdfConfig data class"""
    config = PdfConfig(
        preset_text="test preset content",
        preset_label="test_preset"
    )
    assert config.preset_text == "test preset content"
    assert config.preset_label == "test_preset"


def test_pdf_config_defaults():
    """Test PdfConfig default values"""
    config = PdfConfig()
    assert config.preset_text == ""
    assert config.preset_label == ""


def test_css_config():
    """Test CssConfig data class"""
    config = CssConfig(
        preset_text="body { margin: 0; }",
        preset_label="custom_css"
    )
    assert config.preset_text == "body { margin: 0; }"
    assert config.preset_label == "custom_css"


def test_css_config_defaults():
    """Test CssConfig default values"""
    config = CssConfig()
    assert config.preset_text == ""
    assert config.preset_label == ""