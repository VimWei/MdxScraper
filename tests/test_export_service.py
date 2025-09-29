"""Tests for ExportService"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mdxscraper.services.export_service import ExportService
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_export_service_initialization():
    """Test ExportService initialization"""
    settings = Mock(spec=SettingsService)
    presets = Mock(spec=PresetsService)
    
    service = ExportService(settings, presets)
    
    assert service.settings == settings
    assert service.presets == presets


def test_build_pdf_options_empty():
    """Test building PDF options with empty preset"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    settings.cm.get.side_effect = lambda key, default: {
        "pdf.page_size": "A4",
        "pdf.margin_top": "20mm",
        "pdf.encoding": "UTF-8"
    }.get(key, default)
    
    presets = Mock(spec=PresetsService)
    presets.parse_pdf_preset.return_value = {}
    
    service = ExportService(settings, presets)
    result = service.build_pdf_options("")
    
    assert "page-size" in result
    assert "margin-top" in result
    assert "encoding" in result


def test_build_pdf_options_with_preset():
    """Test building PDF options with preset content"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    settings.cm.get.side_effect = lambda key, default: {
        "pdf.page_size": "A4",
        "pdf.margin_top": "20mm",
        "pdf.encoding": "UTF-8"
    }.get(key, default)
    
    presets = Mock(spec=PresetsService)
    presets.parse_pdf_preset.return_value = {
        "page-size": "Letter",
        "margin-top": "15mm",
        "encoding": "UTF-8"
    }
    
    service = ExportService(settings, presets)
    result = service.build_pdf_options("--page-size Letter\n--margin-top 15mm")
    
    assert result["page-size"] == "Letter"
    assert result["margin-top"] == "15mm"
    assert result["encoding"] == "UTF-8"


def test_build_image_options_jpg():
    """Test building image options for JPG format"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    settings.cm.get.side_effect = lambda key, default: {
        "image.width": 800,
        "image.zoom": 1.2,
        "image.background": True,
        "image.jpg.quality": 90
    }.get(key, default)
    
    presets = Mock(spec=PresetsService)
    service = ExportService(settings, presets)
    result = service.build_image_options(".jpg")
    
    assert result["width"] == "800"
    assert result["zoom"] == "1.2"
    assert result["quality"] == 90
    assert "no-background" not in result


def test_build_image_options_png():
    """Test building image options for PNG format"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    settings.cm.get.side_effect = lambda key, default: {
        "image.width": 0,  # no width
        "image.zoom": 1.0,  # default zoom
        "image.background": False,
        "image.png.optimize": True,
        "image.png.compress_level": 6
    }.get(key, default)
    
    presets = Mock(spec=PresetsService)
    service = ExportService(settings, presets)
    result = service.build_image_options(".png")
    
    assert "width" not in result
    assert "zoom" not in result
    assert result["no-background"] == ""
    assert result["png_optimize"] is True
    assert result["png_compress_level"] == 6


def test_parse_css_styles():
    """Test parsing CSS styles"""
    settings = Mock(spec=SettingsService)
    presets = Mock(spec=PresetsService)
    presets.parse_css_preset.return_value = ("body { margin: 0; }", "h1 { color: red; }", "custom")
    
    service = ExportService(settings, presets)
    result = service.parse_css_styles("body { margin: 0; }")
    
    assert result == ("body { margin: 0; }", "h1 { color: red; }", "custom")
    presets.parse_css_preset.assert_called_once_with("body { margin: 0; }")


@patch('mdxscraper.core.converter.mdx2html')
def test_execute_export_html(mock_mdx2html):
    """Test executing HTML export"""
    mock_mdx2html.return_value = (10, 2, ["word1", "word2"])
    
    settings = Mock(spec=SettingsService)
    settings.get.return_value = True  # with_toc
    presets = Mock(spec=PresetsService)
    presets.parse_css_preset.return_value = (None, None, None)
    service = ExportService(settings, presets)
    
    input_file = Path("test.txt")
    mdx_file = Path("dict.mdx")
    output_path = Path("output.html")
    
    result = service.execute_export(input_file, mdx_file, output_path, settings_service=settings)
    
    assert result == (10, 2, ["word1", "word2"])
    mock_mdx2html.assert_called_once()


@patch('mdxscraper.core.converter.mdx2pdf')
def test_execute_export_pdf(mock_mdx2pdf):
    """Test executing PDF export"""
    mock_mdx2pdf.return_value = (5, 1, ["word1"])
    
    settings = Mock(spec=SettingsService)
    settings.get.return_value = "auto"  # wkhtmltopdf_path
    presets = Mock(spec=PresetsService)
    presets.parse_css_preset.return_value = (None, None, None)
    presets.parse_pdf_preset.return_value = {}  # Return empty dict for PDF parsing
    service = ExportService(settings, presets)
    
    input_file = Path("test.txt")
    mdx_file = Path("dict.mdx")
    output_path = Path("output.pdf")
    
    result = service.execute_export(input_file, mdx_file, output_path, pdf_text="--page-size A4", settings_service=settings)
    
    assert result == (5, 1, ["word1"])
    mock_mdx2pdf.assert_called_once()


@patch('mdxscraper.core.converter.mdx2img')
def test_execute_export_image(mock_mdx2img):
    """Test executing image export"""
    mock_mdx2img.return_value = (8, 0, [])
    
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    settings.cm.get.return_value = 0  # Default values for image options
    settings.get.return_value = True  # with_toc
    presets = Mock(spec=PresetsService)
    presets.parse_css_preset.return_value = (None, None, None)
    service = ExportService(settings, presets)
    
    input_file = Path("test.txt")
    mdx_file = Path("dict.mdx")
    output_path = Path("output.png")
    
    result = service.execute_export(input_file, mdx_file, output_path, css_text="body { margin: 0; }", settings_service=settings)
    
    assert result == (8, 0, [])
    mock_mdx2img.assert_called_once()