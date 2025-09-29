"""Tests for path utility functions"""

import platform
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mdxscraper.utils.path_utils import (
    detect_wkhtmltopdf_path,
    get_wkhtmltopdf_path,
    validate_wkhtmltopdf_path,
)


def test_detect_wkhtmltopdf_path_windows_found():
    """Test detecting wkhtmltopdf path on Windows when found"""
    with patch("platform.system", return_value="Windows"):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
                
                result = detect_wkhtmltopdf_path()
                
                assert result is not None
                assert "wkhtmltopdf.exe" in str(result)


def test_detect_wkhtmltopdf_path_windows_not_found():
    """Test detecting wkhtmltopdf path on Windows when not found"""
    with patch("platform.system", return_value="Windows"):
        with patch("pathlib.Path.exists", return_value=False):
            result = detect_wkhtmltopdf_path()
            assert result == "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"


def test_detect_wkhtmltopdf_path_macos_found():
    """Test detecting wkhtmltopdf path on macOS when found"""
    with patch("platform.system", return_value="Darwin"):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
                
                result = detect_wkhtmltopdf_path()
                
                assert result is not None
                assert "wkhtmltopdf" in str(result)


def test_detect_wkhtmltopdf_path_linux_found():
    """Test detecting wkhtmltopdf path on Linux when found"""
    with patch("platform.system", return_value="Linux"):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 0
                mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
                
                result = detect_wkhtmltopdf_path()
                
                assert result is not None
                assert "wkhtmltopdf" in str(result)


def test_detect_wkhtmltopdf_path_execution_failed():
    """Test detecting wkhtmltopdf path when execution fails"""
    with patch("platform.system", return_value="Windows"):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                
                result = detect_wkhtmltopdf_path()
                assert result == "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"


def test_validate_wkhtmltopdf_path_valid():
    """Test validating wkhtmltopdf path with valid path"""
    test_path = "test_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
            
            is_valid, error = validate_wkhtmltopdf_path(test_path)
            
            assert is_valid is True
            assert error == "✓ wkhtmltopdf 0.12.6"


def test_validate_wkhtmltopdf_path_not_found():
    """Test validating wkhtmltopdf path when not found"""
    test_path = "nonexistent_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=False):
        is_valid, error = validate_wkhtmltopdf_path(test_path)
        
        assert is_valid is False
        assert "not found" in error.lower()


def test_validate_wkhtmltopdf_path_execution_failed():
    """Test validating wkhtmltopdf path when execution fails"""
    test_path = "test_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = "Permission denied"
            
            is_valid, error = validate_wkhtmltopdf_path(test_path)
            
            assert is_valid is False
            assert "Command failed (exit code: 1)" in error


def test_validate_wkhtmltopdf_path_wrong_version():
    """Test validating wkhtmltopdf path with wrong version"""
    test_path = "test_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "wkhtmltopdf 0.10.0"  # Old version
            
            is_valid, error = validate_wkhtmltopdf_path(test_path)
            
            assert is_valid is True
            error_lower = error.lower()
            assert "wkhtmltopdf" in error_lower


def test_get_wkhtmltopdf_path_provided_valid():
    """Test getting wkhtmltopdf path when valid path is provided"""
    provided_path = "custom_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
            
            result = get_wkhtmltopdf_path(provided_path)
            
            assert result == provided_path


def test_get_wkhtmltopdf_path_provided_invalid():
    """Test getting wkhtmltopdf path when invalid path is provided"""
    provided_path = "invalid_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=False):
        with patch("mdxscraper.utils.path_utils.detect_wkhtmltopdf_path") as mock_detect:
            mock_detect.return_value = "detected_wkhtmltopdf.exe"
            
            result = get_wkhtmltopdf_path(provided_path)
            
            assert result == "invalid_wkhtmltopdf.exe"


def test_get_wkhtmltopdf_path_auto_detect():
    """Test getting wkhtmltopdf path with auto detection"""
    with patch("mdxscraper.utils.path_utils.detect_wkhtmltopdf_path") as mock_detect:
        mock_detect.return_value = "detected_wkhtmltopdf.exe"
        
        result = get_wkhtmltopdf_path("auto")
        
        assert result == "detected_wkhtmltopdf.exe"


def test_get_wkhtmltopdf_path_auto_detect_not_found():
    """Test getting wkhtmltopdf path with auto detection when not found"""
    with patch("mdxscraper.utils.path_utils.detect_wkhtmltopdf_path") as mock_detect:
        mock_detect.return_value = "wkhtmltopdf"  # Fallback to PATH
        
        result = get_wkhtmltopdf_path("auto")
        
        assert result == "wkhtmltopdf"


def test_get_wkhtmltopdf_path_string_input():
    """Test getting wkhtmltopdf path with string input"""
    provided_path = "custom_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = "wkhtmltopdf 0.12.6"
            
            result = get_wkhtmltopdf_path(provided_path)
            
            assert result == provided_path


def test_validate_wkhtmltopdf_path_subprocess_exception():
    """Test validating wkhtmltopdf path when subprocess raises exception"""
    test_path = "test_wkhtmltopdf.exe"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("subprocess.run", side_effect=FileNotFoundError("Command not found")):
            is_valid, error = validate_wkhtmltopdf_path(test_path)
            
            assert is_valid is False
            assert "Executable not found" in error


def test_detect_wkhtmltopdf_path_subprocess_exception():
    """Test detecting wkhtmltopdf path when subprocess raises exception"""
    with patch("platform.system", return_value="Windows"):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("subprocess.run", side_effect=FileNotFoundError("Command not found")):
                result = detect_wkhtmltopdf_path()
                assert result == "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
