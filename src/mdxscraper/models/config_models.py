from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class BasicConfig:
    """Basic page configuration data class"""
    input_file: str = ""
    dictionary_file: str = ""
    output_file: str = ""
    output_add_timestamp: bool = False
    backup_input: bool = False
    save_invalid_words: bool = False
    with_toc: bool = True


@dataclass
class ImageConfig:
    """Image page configuration data class"""
    width: int = 0
    zoom: float = 1.0
    background: bool = True
    jpg_quality: int = 85
    png_optimize: bool = True
    png_compress_level: int = 9
    png_transparent_bg: bool = False
    webp_quality: int = 80
    webp_lossless: bool = False
    webp_transparent_bg: bool = False


@dataclass
class AdvancedConfig:
    """Advanced page configuration data class"""
    wkhtmltopdf_path: str = "auto"


@dataclass
class PdfConfig:
    """PDF page configuration data class"""
    preset_text: str = ""
    preset_label: str = ""


@dataclass
class CssConfig:
    """CSS page configuration data class"""
    preset_text: str = ""
    preset_label: str = ""
