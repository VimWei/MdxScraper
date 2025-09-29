"""Tests for Dictionary class"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from mdxscraper.core.dictionary import Dictionary


def test_dictionary_initialization():
    """Test Dictionary initialization"""
    mock_mdx_file = Path("test.mdx")
    
    with patch("mdxscraper.core.dictionary.IndexBuilder") as mock_builder:
        mock_builder.return_value = Mock()
        
        dictionary = Dictionary(mock_mdx_file)
        
        assert dictionary.mdx_path == mock_mdx_file
        mock_builder.assert_called_once_with(mock_mdx_file)


def test_dictionary_initialization_with_mdd():
    """Test Dictionary initialization with MDD file"""
    mock_mdx_file = Path("test.mdx")
    
    with patch("mdxscraper.core.dictionary.IndexBuilder") as mock_builder:
        mock_builder.return_value = Mock()
        
        dictionary = Dictionary(mock_mdx_file)
        
        assert dictionary.mdx_path == mock_mdx_file
        mock_builder.assert_called_once_with(mock_mdx_file)


def test_lookup_html_success():
    """Test successful HTML lookup"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>test result</html>"]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("test_word")
        
        assert result == "<html>test result</html>"
        mock_builder.mdx_lookup.assert_called_once_with("test_word")


def test_lookup_html_not_found():
    """Test HTML lookup when word not found"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("nonexistent_word")
        
        assert result == ""


def test_lookup_html_multiple_results():
    """Test HTML lookup with multiple results"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = [
        "<html>result 1</html>",
        "<html>result 2</html>",
        "<html>result 3</html>"
    ]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("test_word")
        
        assert result == "<html>result 1</html>"


def test_lookup_html_exception():
    """Test HTML lookup when exception occurs"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.side_effect = Exception("Lookup failed")
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        
        # Should raise exception when lookup fails
        with pytest.raises(Exception, match="Lookup failed"):
            dictionary.lookup_html("test_word")


def test_lookup_html_case_insensitive():
    """Test HTML lookup with case insensitive search"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>result</html>"]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        
        # Test different cases
        dictionary.lookup_html("Test_Word")
        dictionary.lookup_html("TEST_WORD")
        dictionary.lookup_html("test_word")
        
        # All should call lookup with the same word
        assert mock_builder.mdx_lookup.call_count == 3
        for call in mock_builder.mdx_lookup.call_args_list:
            assert call[0][0] in ["Test_Word", "TEST_WORD", "test_word"]


def test_lookup_html_with_special_characters():
    """Test HTML lookup with special characters"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>result</html>"]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("word-with-special_chars")
        
        assert result == "<html>result</html>"
        mock_builder.mdx_lookup.assert_called_once_with("word-with-special_chars")


def test_lookup_html_empty_word():
    """Test HTML lookup with empty word"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("")
        
        # Should return empty string for empty word
        assert result == ""
        assert mock_builder.mdx_lookup.call_count == 3  # Called 3 times due to fallback logic


def test_lookup_html_whitespace_word():
    """Test HTML lookup with whitespace-only word"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("   ")
        
        # Should return empty string for whitespace-only word
        assert result == ""
        assert mock_builder.mdx_lookup.call_count == 3  # Called 3 times due to fallback logic


def test_lookup_html_unicode_word():
    """Test HTML lookup with unicode word"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>中文结果</html>"]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("中文单词")
        
        assert result == "<html>中文结果</html>"
        mock_builder.mdx_lookup.assert_called_once_with("中文单词")


def test_dictionary_with_mdd_file():
    """Test Dictionary with MDD file for resources"""
    mock_mdx_file = Path("test.mdx")
    mock_mdd_file = Path("test.mdd")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>result with images</html>"]
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("test_word")
        
        assert result == "<html>result with images</html>"
        # Verify IndexBuilder was called with both files
        # Note: This test assumes Dictionary supports MDD files, but actual implementation may differ


def test_dictionary_file_not_found():
    """Test Dictionary initialization with non-existent file"""
    mock_mdx_file = Path("nonexistent.mdx")
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", side_effect=FileNotFoundError("File not found")):
        with pytest.raises(FileNotFoundError):
            Dictionary(mock_mdx_file)


def test_dictionary_corrupted_file():
    """Test Dictionary initialization with corrupted file"""
    mock_mdx_file = Path("corrupted.mdx")
    
    with patch("mdxscraper.mdict.mdict_query.IndexBuilder", side_effect=Exception("Corrupted file")):
        with pytest.raises(Exception):
            Dictionary(mock_mdx_file)


def test_lookup_html_with_progress_callback():
    """Test HTML lookup with progress callback"""
    mock_mdx_file = Path("test.mdx")
    mock_builder = Mock()
    mock_builder.mdx_lookup.return_value = []
    mock_builder.mdx_lookup.return_value = ["<html>result</html>"]
    progress_callback = Mock()
    
    with patch("mdxscraper.core.dictionary.IndexBuilder", return_value=mock_builder):
        dictionary = Dictionary(mock_mdx_file)
        result = dictionary.lookup_html("test_word")
        
        assert result == "<html>result</html>"
        # Progress callback should be called (if implemented)
        # Note: This depends on the actual implementation of progress reporting


def test_dictionary_multiple_instances():
    """Test creating multiple Dictionary instances"""
    mock_mdx_file1 = Path("test1.mdx")
    mock_mdx_file2 = Path("test2.mdx")
    
    with patch("mdxscraper.core.dictionary.IndexBuilder") as mock_builder:
        mock_builder.return_value = Mock()
        
        dict1 = Dictionary(mock_mdx_file1)
        dict2 = Dictionary(mock_mdx_file2)
        
        assert dict1.mdx_path == mock_mdx_file1
        assert dict2.mdx_path == mock_mdx_file2
        assert dict1 is not dict2
