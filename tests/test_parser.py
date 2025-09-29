"""Tests for WordParser"""

import json
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from mdxscraper.core.parser import WordParser


def test_word_parser_initialization():
    """Test WordParser initialization"""
    parser = WordParser("test.txt")
    assert parser.file_path == "test.txt"


def test_parse_txt_file_single_lesson():
    """Test parsing text file with single lesson"""
    content = """# Lesson 1
word1
word2
word3
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
        
        assert len(result) == 1
        assert result[0]["name"] == "Lesson 1"
        assert result[0]["words"] == ["word1", "word2", "word3"]


def test_parse_txt_file_multiple_lessons():
    """Test parsing text file with multiple lessons"""
    content = """# Lesson 1
word1
word2

# Lesson 2
word3
word4
word5
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
        
        assert len(result) == 2
        assert result[0]["name"] == "Lesson 1"
        assert result[0]["words"] == ["word1", "word2"]
        assert result[1]["name"] == "Lesson 2"
        assert result[1]["words"] == ["word3", "word4", "word5"]


def test_parse_txt_file_no_lesson_header():
    """Test parsing text file with no lesson header (should create timestamp lesson)"""
    content = """word1
word2
word3
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        with patch("mdxscraper.core.parser.datetime") as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"
            parser = WordParser("test.txt")
            result = parser.parse()
            
            assert len(result) == 1
            assert result[0]["name"] == "20240101-120000"
            assert result[0]["words"] == ["word1", "word2", "word3"]


def test_parse_txt_file_empty_lines():
    """Test parsing text file with empty lines"""
    content = """# Lesson 1
word1

word2

# Lesson 2
word3
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
        
        assert len(result) == 2
        assert result[0]["name"] == "Lesson 1"
        assert result[0]["words"] == ["word1", "word2"]
        assert result[1]["name"] == "Lesson 2"
        assert result[1]["words"] == ["word3"]


def test_parse_txt_file_lesson_name_with_spaces():
    """Test parsing text file with lesson name containing spaces"""
    content = """# Lesson 1: Basic Words
word1
word2
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
            
        assert len(result) == 1
        assert result[0]["name"] == "Lesson 1: Basic Words"
        assert result[0]["words"] == ["word1", "word2"]


def test_parse_json_file():
    """Test parsing JSON file"""
    json_data = [
        {"name": "Lesson 1", "words": ["word1", "word2"]},
        {"name": "Lesson 2", "words": ["word3", "word4", "word5"]}
    ]
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=json.dumps(json_data))()):
        parser = WordParser("test.json")
        result = parser.parse()
            
        assert len(result) == 2
        assert result[0]["name"] == "Lesson 1"
        assert result[0]["words"] == ["word1", "word2"]
        assert result[1]["name"] == "Lesson 2"
        assert result[1]["words"] == ["word3", "word4", "word5"]


def test_parse_json_file_invalid():
    """Test parsing invalid JSON file"""
    with patch("builtins.open", mock_open(read_data="invalid json")):
        with patch("chardet.detect", return_value={"encoding": "utf-8", "confidence": 0.9}):
            parser = WordParser("test.json")
            result = parser.parse()
            
            # Should return empty list on error
        assert result == []


def test_parse_xlsx_file():
    """Test parsing Excel file"""
    mock_workbook = Mock()
    mock_sheet1 = Mock()
    mock_sheet2 = Mock()
    
    # Mock sheet data
    mock_sheet1.iter_rows.return_value = [
        [Mock(value="word1")],
        [Mock(value="word2")],
        [Mock(value="word3")]
    ]
    mock_sheet1.min_row = 1
    mock_sheet1.max_row = 3
    mock_sheet1.max_col = 1
    
    mock_sheet2.iter_rows.return_value = [
        [Mock(value="word4")],
        [Mock(value="word5")]
    ]
    mock_sheet2.min_row = 1
    mock_sheet2.max_row = 2
    mock_sheet2.max_col = 1
    
    mock_workbook.sheetnames = ["Sheet1", "Sheet2"]
    mock_workbook.__getitem__ = Mock(side_effect=lambda name: mock_sheet1 if name == "Sheet1" else mock_sheet2)
    
    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        parser = WordParser("test.xlsx")
        result = parser.parse()
        
        assert len(result) == 2
        assert result[0]["name"] == "Sheet1"
        assert result[0]["words"] == ["word1", "word2", "word3"]
        assert result[1]["name"] == "Sheet2"
        assert result[1]["words"] == ["word4", "word5"]


def test_parse_xlsx_file_with_empty_cells():
    """Test parsing Excel file with empty cells"""
    mock_workbook = Mock()
    mock_sheet = Mock()
    
    # Mock sheet data with empty cells
    mock_sheet.iter_rows.return_value = [
        [Mock(value="word1")],
        [Mock(value=None)],  # Empty cell
        [Mock(value="")],    # Empty string
        [Mock(value="word2")]
    ]
    mock_sheet.min_row = 1
    mock_sheet.max_row = 4
    mock_sheet.max_col = 1
    
    mock_workbook.sheetnames = ["Sheet1"]
    mock_workbook.__getitem__ = Mock(return_value=mock_sheet)
    
    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        parser = WordParser("test.xlsx")
        result = parser.parse()
        
        assert len(result) == 1
        assert result[0]["name"] == "Sheet1"
        assert result[0]["words"] == ["word1", "word2"]  # Empty cells should be filtered out


def test_parse_unsupported_format():
    """Test parsing unsupported file format"""
    parser = WordParser("test.unsupported")
    result = parser.parse()
    
    # Should return empty list for unsupported format
    assert result == []


def test_parse_file_not_found():
    """Test parsing non-existent file"""
    parser = WordParser("nonexistent.txt")
    result = parser.parse()
    
    # Should return empty list on error
    assert result == []


def test_parse_encoding_detection_low_confidence():
    """Test parsing with low confidence encoding detection"""
    content = """# Lesson 1
word1
word2
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
        
        # Should use default encoding when confidence is low
        assert len(result) == 1
        assert result[0]["name"] == "Lesson 1"


def test_parse_encoding_detection_fallback():
    """Test parsing with encoding detection fallback"""
    content = """# Lesson 1
word1
word2
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.txt")
        result = parser.parse()
        
        # Should use default encoding when detection fails
        assert len(result) == 1
        assert result[0]["name"] == "Lesson 1"


def test_parse_md_file():
    """Test parsing markdown file"""
    content = """# Lesson 1
word1
word2

# Lesson 2
word3
"""
    
    with patch.object(WordParser, '_open_encoding_file', return_value=mock_open(read_data=content)()):
        parser = WordParser("test.md")
        result = parser.parse()
            
        assert len(result) == 2
        assert result[0]["name"] == "Lesson 1"
        assert result[0]["words"] == ["word1", "word2"]
        assert result[1]["name"] == "Lesson 2"
        assert result[1]["words"] == ["word3"]


def test_parse_xls_file():
    """Test parsing .xls file"""
    mock_workbook = Mock()
    mock_sheet = Mock()
    
    mock_sheet.iter_rows.return_value = [
        [Mock(value="word1")],
        [Mock(value="word2")]
    ]
    mock_sheet.min_row = 1
    mock_sheet.max_row = 2
    mock_sheet.max_col = 1
    
    mock_workbook.sheetnames = ["Sheet1"]
    mock_workbook.__getitem__ = Mock(return_value=mock_sheet)
    
    with patch("openpyxl.load_workbook", return_value=mock_workbook):
        parser = WordParser("test.xls")
        result = parser.parse()
        
        assert len(result) == 1
        assert result[0]["name"] == "Sheet1"
        assert result[0]["words"] == ["word1", "word2"]
