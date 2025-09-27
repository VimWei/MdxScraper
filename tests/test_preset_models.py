"""Tests for preset data models"""

import pytest
from pathlib import Path
from mdxscraper.models.preset_models import PresetInfo, PresetData, PresetCategory


def test_preset_category_creation():
    """Test PresetCategory creation"""
    category = PresetCategory(
        name="pdf",
        label="PDF Presets",
        description="PDF conversion presets"
    )
    
    assert category.name == "pdf"
    assert category.label == "PDF Presets"
    assert category.description == "PDF conversion presets"
    assert category.presets == []


def test_preset_category_defaults():
    """Test PresetCategory default values"""
    category = PresetCategory(
        name="css",
        label="CSS Presets"
    )
    
    assert category.name == "css"
    assert category.label == "CSS Presets"
    assert category.description == ""
    assert category.presets == []


def test_preset_category_with_presets():
    """Test PresetCategory with presets"""
    preset1 = PresetInfo(name="preset1", label="Preset 1")
    preset2 = PresetInfo(name="preset2", label="Preset 2")
    
    category = PresetCategory(
        name="pdf",
        label="PDF Presets",
        presets=[preset1, preset2]
    )
    
    assert len(category.presets) == 2
    assert category.presets[0].name == "preset1"
    assert category.presets[1].name == "preset2"


def test_preset_info_creation():
    """Test PresetInfo creation"""
    preset_info = PresetInfo(
        name="test_preset",
        label="Test Preset",
        description="A test preset",
        category="pdf"
    )
    
    assert preset_info.name == "test_preset"
    assert preset_info.label == "Test Preset"
    assert preset_info.description == "A test preset"
    assert preset_info.category == "pdf"
    assert preset_info.created_at is None
    assert preset_info.updated_at is None


def test_preset_info_defaults():
    """Test PresetInfo default values"""
    preset_info = PresetInfo(
        name="test_preset",
        label="Test Preset"
    )
    
    assert preset_info.name == "test_preset"
    assert preset_info.label == "Test Preset"
    assert preset_info.description == ""
    assert preset_info.category == "default"
    assert preset_info.created_at is None
    assert preset_info.updated_at is None


def test_preset_info_with_timestamps():
    """Test PresetInfo with timestamps"""
    preset_info = PresetInfo(
        name="test_preset",
        label="Test Preset",
        description="A test preset",
        category="pdf",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-02T00:00:00Z"
    )
    
    assert preset_info.name == "test_preset"
    assert preset_info.label == "Test Preset"
    assert preset_info.description == "A test preset"
    assert preset_info.category == "pdf"
    assert preset_info.created_at == "2023-01-01T00:00:00Z"
    assert preset_info.updated_at == "2023-01-02T00:00:00Z"


def test_preset_data_creation():
    """Test PresetData creation"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = "h1_style = 'color: red;'\nscrap_style = 'font-size: 14px;'"
    
    preset_data = PresetData(
        info=info,
        content=content
    )
    
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == {}


def test_preset_data_with_metadata():
    """Test PresetData with metadata"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = "h1_style = 'color: red;'"
    metadata = {"version": "1.0", "author": "test"}
    
    preset_data = PresetData(
        info=info,
        content=content,
        metadata=metadata
    )
    
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == metadata


def test_preset_data_default_metadata():
    """Test PresetData with default metadata"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = "h1_style = 'color: red;'"
    
    preset_data = PresetData(
        info=info,
        content=content
    )
    
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == {}


def test_preset_data_unicode_content():
    """Test PresetData with unicode content"""
    info = PresetInfo(name="test_preset", label="测试预设")
    content = "h1_style = 'color: red; /* 红色标题 */'"
    
    preset_data = PresetData(
        info=info,
        content=content
    )
    
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == {}


def test_preset_data_complex_metadata():
    """Test PresetData with complex metadata"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = "h1_style = 'color: red;'"
    metadata = {
        "version": "1.0",
        "author": "test",
        "tags": ["pdf", "conversion"],
        "settings": {
            "margin": "1in",
            "orientation": "portrait"
        }
    }
    
    preset_data = PresetData(
        info=info,
        content=content,
        metadata=metadata
    )
    
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == metadata
    assert preset_data.metadata["version"] == "1.0"
    assert preset_data.metadata["tags"] == ["pdf", "conversion"]
    assert preset_data.metadata["settings"]["margin"] == "1in"


def test_preset_data_empty_content():
    """Test PresetData with empty content"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = ""
    
    preset_data = PresetData(
        info=info,
        content=content
    )
    
    assert preset_data.info == info
    assert preset_data.content == ""
    assert preset_data.metadata == {}


def test_preset_data_none_metadata():
    """Test PresetData with None metadata"""
    info = PresetInfo(name="test_preset", label="Test Preset")
    content = "h1_style = 'color: red;'"
    
    preset_data = PresetData(
        info=info,
        content=content,
        metadata=None
    )
    
    # Should be converted to empty dict in __post_init__
    assert preset_data.info == info
    assert preset_data.content == content
    assert preset_data.metadata == {}