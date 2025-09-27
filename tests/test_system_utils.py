"""Tests for system utility functions"""

import pytest
import platform
from unittest.mock import patch, Mock
from pathlib import Path
from mdxscraper.utils.system_utils import open_file_or_directory


def test_open_file_or_directory_windows():
    """Test opening file/directory on Windows"""
    test_path = Path("test_file.txt")
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile") as mock_startfile:
            open_file_or_directory(test_path)
            mock_startfile.assert_called_once_with("test_file.txt")


def test_open_file_or_directory_macos():
    """Test opening file/directory on macOS"""
    test_path = Path("test_file.txt")
    
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.Popen") as mock_popen:
            open_file_or_directory(test_path)
            mock_popen.assert_called_once_with(['open', 'test_file.txt'])


def test_open_file_or_directory_linux():
    """Test opening file/directory on Linux"""
    test_path = Path("test_file.txt")
    
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.Popen") as mock_popen:
            open_file_or_directory(test_path)
            mock_popen.assert_called_once_with(['xdg-open', 'test_file.txt'])


def test_open_file_or_directory_unknown_os():
    """Test opening file/directory on unknown OS (defaults to Linux behavior)"""
    test_path = Path("test_file.txt")
    
    with patch("platform.system", return_value="UnknownOS"):
        with patch("subprocess.Popen") as mock_popen:
            open_file_or_directory(test_path)
            mock_popen.assert_called_once_with(['xdg-open', 'test_file.txt'])


def test_open_file_or_directory_with_path_object():
    """Test opening file/directory with Path object"""
    test_path = Path("test_directory")
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile") as mock_startfile:
            open_file_or_directory(test_path)
            mock_startfile.assert_called_once_with("test_directory")


def test_open_file_or_directory_with_string():
    """Test opening file/directory with string path"""
    test_path = "test_file.txt"
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile") as mock_startfile:
            open_file_or_directory(test_path)
            mock_startfile.assert_called_once_with("test_file.txt")


def test_open_file_or_directory_windows_error():
    """Test Windows file opening with error"""
    test_path = Path("nonexistent_file.txt")
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile", side_effect=OSError("File not found")):
            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to open"):
                open_file_or_directory(test_path)


def test_open_file_or_directory_macos_error():
    """Test macOS file opening with error"""
    test_path = Path("nonexistent_file.txt")
    
    with patch("platform.system", return_value="Darwin"):
        with patch("subprocess.Popen", side_effect=OSError("Command not found")):
            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to open"):
                open_file_or_directory(test_path)


def test_open_file_or_directory_linux_error():
    """Test Linux file opening with error"""
    test_path = Path("nonexistent_file.txt")
    
    with patch("platform.system", return_value="Linux"):
        with patch("subprocess.Popen", side_effect=OSError("Command not found")):
            # Should raise RuntimeError
            with pytest.raises(RuntimeError, match="Failed to open"):
                open_file_or_directory(test_path)


def test_open_file_or_directory_complex_path():
    """Test opening file/directory with complex path"""
    test_path = Path("C:/Users/Test/Documents/test file with spaces.txt")
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile") as mock_startfile:
            open_file_or_directory(test_path)
            mock_startfile.assert_called_once_with("C:\\Users\\Test\\Documents\\test file with spaces.txt")


def test_open_file_or_directory_unicode_path():
    """Test opening file/directory with unicode path"""
    test_path = Path("测试文件.txt")
    
    with patch("platform.system", return_value="Windows"):
        with patch("os.startfile") as mock_startfile:
            open_file_or_directory(test_path)
            mock_startfile.assert_called_once_with("测试文件.txt")
