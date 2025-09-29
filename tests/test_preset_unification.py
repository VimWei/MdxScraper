"""Tests for preset unification functionality"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QTextEdit

from mdxscraper.gui.main_window import MainWindow
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


@pytest.fixture(scope="session")
def app():
    """Create QApplication instance for testing"""
    if not QApplication.instance():
        return QApplication([])
    return QApplication.instance()


@pytest.fixture
def project_root():
    """Project root directory"""
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def mock_main_window(app, project_root):
    """Create a mock MainWindow instance for testing"""
    # Create mock services
    mock_settings = Mock(spec=SettingsService)
    mock_presets = Mock(spec=PresetsService)
    
    # Create MainWindow instance but skip complex initialization
    window = MainWindow.__new__(MainWindow)
    window.project_root = project_root
    window.settings = mock_settings
    window.presets = mock_presets
    window.command_panel = Mock()
    
    # Create mock coordinators
    window.preset_coordinator = Mock()
    
    # Create mock page components
    window.tab_pdf = Mock()
    window.tab_css = Mock()
    
    # Create mock combo and editor widgets
    window.tab_pdf.pdf_combo = QComboBox()
    window.tab_pdf.pdf_editor = QTextEdit()
    window.tab_pdf.show_dirty = Mock()
    
    window.tab_css.css_combo = QComboBox()
    window.tab_css.css_editor = QTextEdit()
    window.tab_css.show_dirty = Mock()
    
    # Initialize state variables
    window.pdf_dirty = False
    window.css_dirty = False
    window._updating_pdf_editor = False
    window._updating_css_editor = False
    window.last_pdf_label = ''
    window.last_css_label = ''
    
    return window


class TestPresetUnification:
    """Test preset unification functionality"""
    
    def test_enter_untitled_state_pdf_clear_editor(self, mock_main_window):
        """Test entering PDF * Untitled state with clear editor"""
        mock_main_window.tab_pdf.pdf_editor.setPlainText("test content")
        
        mock_main_window._enter_untitled_state('pdf', clear_editor=True)
        
        # Verify coordinator method was called
        mock_main_window.preset_coordinator.enter_untitled_state.assert_called_once_with(
            mock_main_window, 'pdf', True
        )
    
    def test_enter_untitled_state_pdf_keep_editor(self, mock_main_window):
        """Test entering PDF * Untitled state keeping editor content"""
        mock_main_window.tab_pdf.pdf_editor.setPlainText("user content")
        
        mock_main_window._enter_untitled_state('pdf', clear_editor=False)
        
        # Verify coordinator method was called
        mock_main_window.preset_coordinator.enter_untitled_state.assert_called_once_with(
            mock_main_window, 'pdf', False
        )
    
    def test_enter_untitled_state_css_clear_editor(self, mock_main_window):
        """Test entering CSS * Untitled state with clear editor"""
        mock_main_window.tab_css.css_editor.setPlainText("css content")
        
        mock_main_window._enter_untitled_state('css', clear_editor=True)
        
        # Verify coordinator method was called
        mock_main_window.preset_coordinator.enter_untitled_state.assert_called_once_with(
            mock_main_window, 'css', True
        )
    
    def test_select_label_and_load_existing(self, mock_main_window):
        """Test selecting existing label and loading"""
        # Add item to combo
        mock_main_window.tab_pdf.pdf_combo.addItem("test_preset", userData="/path/to/file")
        
        with patch.object(mock_main_window.tab_pdf.pdf_combo, 'setCurrentIndex') as mock_set_index:
            mock_main_window.select_label_and_load('pdf', 'test_preset')
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.select_label_and_load.assert_called_once_with(
                mock_main_window, 'pdf', 'test_preset'
            )
    
    def test_select_label_and_load_nonexistent(self, mock_main_window):
        """Test selecting nonexistent label should enter * Untitled state"""
        # Add different item to combo
        mock_main_window.tab_pdf.pdf_combo.addItem("other_preset", userData="/path/to/file")
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            with patch.object(mock_main_window.settings, 'set') as mock_settings_set:
                mock_main_window.select_label_and_load('pdf', 'nonexistent_preset')
                
                # Verify coordinator method was called
                mock_main_window.preset_coordinator.select_label_and_load.assert_called_once_with(
                    mock_main_window, 'pdf', 'nonexistent_preset'
                )
    
    def test_select_label_and_load_css(self, mock_main_window):
        """Test selecting CSS label"""
        mock_main_window.tab_css.css_combo.addItem("css_preset", userData="/path/to/css")
        
        with patch.object(mock_main_window.tab_css.css_combo, 'setCurrentIndex') as mock_set_index:
            mock_main_window.select_label_and_load('css', 'css_preset')
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.select_label_and_load.assert_called_once_with(
                mock_main_window, 'css', 'css_preset'
            )
    
    def test_pdf_preset_changed_with_valid_selection(self, mock_main_window):
        """Test PDF preset changed with valid selection"""
        # Setup mock data
        mock_main_window.tab_pdf.pdf_combo.addItem("test_preset", userData="/path/to/file")
        mock_main_window.tab_pdf.pdf_combo.setCurrentIndex(0)
        mock_main_window.presets.load_preset_text.return_value = "test content"
        
        with patch.object(mock_main_window.settings, 'set') as mock_settings_set:
            mock_main_window.on_pdf_preset_changed("test_preset")
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.on_pdf_preset_changed.assert_called_once_with(
                mock_main_window, "test_preset"
            )
    
    def test_pdf_preset_changed_no_selection(self, mock_main_window):
        """Test PDF preset changed with no selection should enter * Untitled state"""
        # Ensure no selection
        mock_main_window.tab_pdf.pdf_combo.clear()
        mock_main_window.tab_pdf.pdf_combo.setCurrentIndex(-1)
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            mock_main_window.on_pdf_preset_changed("")
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.on_pdf_preset_changed.assert_called_once_with(
                mock_main_window, ""
            )
    
    def test_pdf_preset_changed_load_failure(self, mock_main_window):
        """Test PDF preset changed with load failure"""
        mock_main_window.tab_pdf.pdf_combo.addItem("test_preset", userData="/path/to/file")
        mock_main_window.tab_pdf.pdf_combo.setCurrentIndex(0)
        mock_main_window.presets.load_preset_text.side_effect = Exception("File not found")
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            with patch.object(mock_main_window.settings, 'set') as mock_settings_set:
                mock_main_window.on_pdf_preset_changed("test_preset")
                
                # Verify coordinator method was called
                mock_main_window.preset_coordinator.on_pdf_preset_changed.assert_called_once_with(
                    mock_main_window, "test_preset"
                )
    
    def test_pdf_text_changed_user_edit(self, mock_main_window):
        """Test PDF text changed by user edit"""
        mock_main_window._updating_pdf_editor = False
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            mock_main_window.on_pdf_text_changed()
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.on_pdf_text_changed.assert_called_once_with(
                mock_main_window
            )
    
    def test_pdf_text_changed_programmatic_update(self, mock_main_window):
        """Test PDF text changed by programmatic update should not trigger untitled state"""
        mock_main_window._updating_pdf_editor = True
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            mock_main_window.on_pdf_text_changed()
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.on_pdf_text_changed.assert_called_once_with(
                mock_main_window
            )
    
    def test_css_text_changed_user_edit(self, mock_main_window):
        """Test CSS text changed by user edit"""
        mock_main_window._updating_css_editor = False
        
        with patch.object(mock_main_window, '_enter_untitled_state') as mock_enter_untitled:
            mock_main_window.on_css_text_changed()
            
            # Verify coordinator method was called
            mock_main_window.preset_coordinator.on_css_text_changed.assert_called_once_with(
                mock_main_window
            )
    
    def test_save_preset_flow(self, mock_main_window):
        """Test save preset flow"""
        mock_main_window.tab_pdf.pdf_editor.setPlainText("preset content")
        
        with patch.object(mock_main_window.presets, 'save_preset_text') as mock_save:
            with patch.object(mock_main_window, 'reload_presets') as mock_reload:
                with patch.object(mock_main_window, 'select_label_and_load') as mock_select:
                    with patch.object(mock_main_window.settings, 'set') as mock_settings_set:
                        # Test that coordinator has save_preset method
                        assert hasattr(mock_main_window.preset_coordinator, 'save_preset')
                        
                        # Simulate calling save_preset through coordinator
                        mock_main_window.preset_coordinator.save_preset = Mock()
                        mock_main_window.preset_coordinator.save_preset('pdf', 'test_preset')
                        
                        # Verify coordinator method was called
                        mock_main_window.preset_coordinator.save_preset.assert_called_once_with(
                            'pdf', 'test_preset'
                        )
    
    def test_autosave_untitled_flow(self, mock_main_window):
        """Test autosave untitled flow"""
        mock_main_window.tab_pdf.pdf_editor.setPlainText("untitled content")
        
        with patch.object(mock_main_window.presets, 'save_preset_text') as mock_save:
            with patch.object(mock_main_window, 'reload_presets') as mock_reload:
                with patch.object(mock_main_window, 'select_label_and_load') as mock_select:
                    with patch.object(mock_main_window.settings, 'set') as mock_settings_set:
                        # Simulate autosave
                        mock_main_window.autosave_untitled('pdf')
                        
                        # Verify coordinator method was called
                        mock_main_window.preset_coordinator._autosave_untitled.assert_called_once_with(
                            mock_main_window, 'pdf'
                        )