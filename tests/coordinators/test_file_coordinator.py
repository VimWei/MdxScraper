"""Tests for FileCoordinator"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mdxscraper.coordinators.file_coordinator import FileCoordinator
from mdxscraper.services.settings_service import SettingsService


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def mock_settings():
    """Create mock SettingsService"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    return settings


@pytest.fixture
def file_coordinator(mock_settings):
    """Create FileCoordinator instance"""
    return FileCoordinator(mock_settings, _project_root())


def test_file_coordinator_initialization(file_coordinator, mock_settings):
    """Test FileCoordinator initialization"""
    assert file_coordinator.settings == mock_settings
    assert file_coordinator.project_root == _project_root()


def test_choose_input_file(file_coordinator, mock_settings):
    """Test choosing input file"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_input.txt")

    # Mock file dialog
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
        mock_dialog.return_value = ("test_input.txt", "Text files (*.txt)")

        # Call the method
        result = file_coordinator.choose_input(mock_mw)

        # Verify result
        assert result is None

        # Verify file dialog was called with correct parameters
        mock_dialog.assert_called_once()
        args, kwargs = mock_dialog.call_args
        assert "Select input file" in args[1]
        assert "Supported files (*.txt *.md *.json *.xlsx)" in args[3]

        # Verify UI was updated
        mock_mw.edit_input.setText.assert_called_once()


def test_choose_input_file_cancelled(file_coordinator, mock_settings):
    """Test choosing input file when cancelled"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_input.txt")

    # Mock file dialog (cancelled)
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
        mock_dialog.return_value = ("", "")

        # Call the method
        result = file_coordinator.choose_input(mock_mw)

        # Verify result
        assert result is None

        # Verify UI was NOT updated
        mock_mw.tab_basic.input_file.setText.assert_not_called()


def test_choose_dictionary_file(file_coordinator, mock_settings):
    """Test choosing dictionary file"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_dict.mdx")

    # Mock file dialog
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
        mock_dialog.return_value = ("test_dict.mdx", "MDX files (*.mdx)")

        # Call the method
        result = file_coordinator.choose_dictionary(mock_mw)

        # Verify result
        assert result is None

        # Verify file dialog was called with correct parameters
        mock_dialog.assert_called_once()
        args, kwargs = mock_dialog.call_args
        assert "Select MDX dictionary" in args[1]
        assert "MDX Files (*.mdx)" in args[3]

        # Verify UI was updated
        mock_mw.edit_dict.setText.assert_called_once()


def test_choose_dictionary_file_cancelled(file_coordinator, mock_settings):
    """Test choosing dictionary file when cancelled"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_dict.mdx")

    # Mock file dialog (cancelled)
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
        mock_dialog.return_value = ("", "")

        # Call the method
        result = file_coordinator.choose_dictionary(mock_mw)

        # Verify result
        assert result is None

        # Verify UI was NOT updated
        mock_mw.tab_basic.dictionary_file.setText.assert_not_called()


def test_choose_output_file(file_coordinator, mock_settings):
    """Test choosing output file"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_output.html")
    mock_settings.get.return_value = "data/output"

    # Mock file dialog
    with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName") as mock_dialog:
        mock_dialog.return_value = ("test_output.html", "HTML files (*.html)")

        # Call the method
        result = file_coordinator.choose_output(mock_mw)

        # Verify result
        assert result is None

        # Verify file dialog was called with correct parameters
        mock_dialog.assert_called_once()
        args, kwargs = mock_dialog.call_args
        assert "Select output file" in args[1]
        assert (
            "HTML files (*.html);;PDF files (*.pdf);;JPG files (*.jpg);;PNG files (*.png);;WEBP files (*.webp);;All files (*.*)"
            in args[3]
        )

        # Verify UI was updated
        mock_mw.edit_output.setText.assert_called_once()


def test_choose_output_file_cancelled(file_coordinator, mock_settings):
    """Test choosing output file when cancelled"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock settings
    mock_settings.resolve_path.return_value = Path("test_output.html")
    mock_settings.get.return_value = "data/output"

    # Mock file dialog (cancelled)
    with patch("PySide6.QtWidgets.QFileDialog.getSaveFileName") as mock_dialog:
        mock_dialog.return_value = ("", "")

        # Call the method
        result = file_coordinator.choose_output(mock_mw)

        # Verify result
        assert result is None

        # Verify UI was NOT updated
        mock_mw.tab_basic.output_file.setText.assert_not_called()


def test_open_output_dir(file_coordinator, mock_settings):
    """Test opening output directory"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock UI methods
    mock_mw.tab_basic.output_file.text.return_value = "test_output.html"

    # Mock system utils
    with patch("mdxscraper.coordinators.file_coordinator.open_file_or_directory") as mock_open:
        # Call the method
        result = file_coordinator.open_user_data_dir(mock_mw)

        # Verify result
        assert result is None

        # Verify system utils was called
        mock_open.assert_called_once()
        # Check that the path passed is the parent directory of the output file
        call_args = mock_open.call_args[0][0]
        assert call_args.name == "data"  # Should be the parent directory


def test_open_output_dir_no_file(file_coordinator, mock_settings):
    """Test opening output directory when no file is selected"""
    # Mock main window
    mock_mw = Mock()
    mock_mw.tab_basic = Mock()

    # Mock UI methods (empty file path)
    mock_mw.tab_basic.output_file.text.return_value = ""

    # Mock system utils
    with patch("mdxscraper.coordinators.file_coordinator.open_file_or_directory") as mock_open:
        # Call the method
        result = file_coordinator.open_user_data_dir(mock_mw)

        # Verify result
        assert result is None

        # Verify system utils was called with data directory
        mock_open.assert_called_once()
        call_args = mock_open.call_args[0][0]
        assert call_args.name == "data"


def test_open_user_data_dir(file_coordinator, mock_settings):
    """Test opening user data directory"""
    # Mock main window
    mock_mw = Mock()

    # Mock system utils
    with patch("mdxscraper.coordinators.file_coordinator.open_file_or_directory") as mock_open:
        # Call the method
        result = file_coordinator.open_user_data_dir(mock_mw)

        # Verify result
        assert result is None

        # Verify system utils was called with data directory
        mock_open.assert_called_once()
        call_args = mock_open.call_args[0][0]
        assert call_args.name == "data"


def test_open_user_config_dir(file_coordinator, mock_settings):
    """Test opening user data directory (config test)"""
    # Mock main window
    mock_mw = Mock()

    # Mock system utils
    with patch("mdxscraper.coordinators.file_coordinator.open_file_or_directory") as mock_open:
        # Call the method
        result = file_coordinator.open_user_data_dir(mock_mw)

        # Verify result
        assert result is None

        # Verify system utils was called with configs directory
        mock_open.assert_called_once()
        call_args = mock_open.call_args[0][0]
        assert call_args.name == "data"
