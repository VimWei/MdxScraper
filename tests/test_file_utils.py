"""Tests for file utility functions"""

from collections import OrderedDict
from pathlib import Path
from unittest.mock import call, mock_open, patch

import pytest

from mdxscraper.utils.file_utils import (
    get_image_format_from_src,
    write_invalid_words_file,
)


def test_write_invalid_words_file_empty():
    """Test writing empty invalid words file"""
    invalid_words = OrderedDict()
    output_file = Path("test_invalid.txt")

    with patch("builtins.open", mock_open()) as mock_file:
        write_invalid_words_file(invalid_words, output_file)

        # Should not write anything for empty dict
        mock_file.assert_not_called()


def test_write_invalid_words_file_single_lesson():
    """Test writing invalid words file with single lesson"""
    invalid_words = OrderedDict()
    invalid_words["Lesson 1"] = ["word1", "word2", "word3"]
    output_file = Path("test_invalid.txt")

    with patch("builtins.open", mock_open()) as mock_file:
        write_invalid_words_file(invalid_words, output_file)

        # Verify file was opened
        mock_file.assert_called_once_with(output_file, "w", encoding="utf-8")

        # Verify content was written
        handle = mock_file()
        expected_calls = [
            call("# Lesson 1\n"),
            call("word1\n"),
            call("word2\n"),
            call("word3\n"),
            call("\n"),
        ]
        handle.write.assert_has_calls(expected_calls)


def test_write_invalid_words_file_multiple_lessons():
    """Test writing invalid words file with multiple lessons"""
    invalid_words = OrderedDict()
    invalid_words["Lesson 1"] = ["word1", "word2"]
    invalid_words["Lesson 2"] = ["word3", "word4", "word5"]
    output_file = Path("test_invalid.txt")

    with patch("builtins.open", mock_open()) as mock_file:
        write_invalid_words_file(invalid_words, output_file)

        # Verify file was opened
        mock_file.assert_called_once_with(output_file, "w", encoding="utf-8")

        # Verify content was written
        handle = mock_file()
        expected_calls = [
            call("# Lesson 1\n"),
            call("word1\n"),
            call("word2\n"),
            call("\n"),
            call("# Lesson 2\n"),
            call("word3\n"),
            call("word4\n"),
            call("word5\n"),
            call("\n"),
        ]
        handle.write.assert_has_calls(expected_calls)


def test_write_invalid_words_file_empty_lesson():
    """Test writing invalid words file with empty lesson"""
    invalid_words = OrderedDict()
    invalid_words["Lesson 1"] = []
    output_file = Path("test_invalid.txt")

    with patch("builtins.open", mock_open()) as mock_file:
        write_invalid_words_file(invalid_words, output_file)

        # Verify file was opened
        mock_file.assert_called_once_with(output_file, "w", encoding="utf-8")

        # Verify content was written
        handle = mock_file()
        expected_calls = [call("# Lesson 1\n"), call("\n")]
        handle.write.assert_has_calls(expected_calls)


def test_write_invalid_words_file_string_path():
    """Test writing invalid words file with string path"""
    invalid_words = OrderedDict()
    invalid_words["Lesson 1"] = ["word1"]
    output_file = "test_invalid.txt"

    with patch("builtins.open", mock_open()) as mock_file:
        write_invalid_words_file(invalid_words, output_file)

        # Verify file was opened
        mock_file.assert_called_once_with(Path(output_file), "w", encoding="utf-8")


def test_write_invalid_words_file_create_directory():
    """Test writing invalid words file creates parent directory"""
    invalid_words = OrderedDict()
    invalid_words["Lesson 1"] = ["word1"]
    output_file = Path("nonexistent_dir/test_invalid.txt")

    with patch("builtins.open", mock_open()) as mock_file:
        with patch.object(Path, "mkdir") as mock_mkdir:
            write_invalid_words_file(invalid_words, output_file)

            # Verify directory was created
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


def test_get_image_format_from_src_png():
    """Test getting PNG image format"""
    result = get_image_format_from_src("test.png")
    assert result == "png"


def test_get_image_format_from_src_jpg():
    """Test getting JPG image format"""
    result = get_image_format_from_src("test.jpg")
    assert result == "jpeg"


def test_get_image_format_from_src_jpeg():
    """Test getting JPEG image format"""
    result = get_image_format_from_src("test.jpeg")
    assert result == "jpeg"


def test_get_image_format_from_src_gif():
    """Test getting GIF image format"""
    result = get_image_format_from_src("test.gif")
    assert result == "gif"


def test_get_image_format_from_src_webp():
    """Test getting WebP image format"""
    result = get_image_format_from_src("test.webp")
    assert result == "webp"


def test_get_image_format_from_src_svg():
    """Test getting SVG image format"""
    result = get_image_format_from_src("test.svg")
    assert result == "svg"


def test_get_image_format_from_src_tiff():
    """Test getting TIFF image format"""
    result = get_image_format_from_src("test.tiff")
    assert result == "tiff"


def test_get_image_format_from_src_tif():
    """Test getting TIF image format"""
    result = get_image_format_from_src("test.tif")
    assert result == "tiff"


def test_get_image_format_from_src_bmp():
    """Test getting BMP image format"""
    result = get_image_format_from_src("test.bmp")
    assert result == "bmp"


def test_get_image_format_from_src_unknown():
    """Test getting unknown image format (defaults to jpg)"""
    result = get_image_format_from_src("test.unknown")
    assert result == "jpg"


def test_get_image_format_from_src_no_extension():
    """Test getting image format with no extension (defaults to jpg)"""
    result = get_image_format_from_src("test")
    assert result == "jpg"


def test_get_image_format_from_src_uppercase():
    """Test getting image format with uppercase extension"""
    result = get_image_format_from_src("test.PNG")
    assert result == "png"


def test_get_image_format_from_src_mixed_case():
    """Test getting image format with mixed case extension"""
    result = get_image_format_from_src("test.JpEg")
    assert result == "jpeg"


def test_get_image_format_from_src_full_path():
    """Test getting image format from full path"""
    result = get_image_format_from_src("/path/to/image/test.png")
    assert result == "png"


def test_get_image_format_from_src_url():
    """Test getting image format from URL"""
    result = get_image_format_from_src("https://example.com/image.jpg")
    assert result == "jpeg"


def test_get_image_format_from_src_with_query():
    """Test getting image format from URL with query parameters"""
    result = get_image_format_from_src("https://example.com/image.png?v=1")
    assert result == "jpg"  # URL with query parameters defaults to jpg


def test_get_image_format_from_src_multiple_dots():
    """Test getting image format from filename with multiple dots"""
    result = get_image_format_from_src("test.backup.png")
    assert result == "png"
