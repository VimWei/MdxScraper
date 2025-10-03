"""测试用的Mock对象和夹具"""

from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, Mock

import pytest
from PySide6.QtWidgets import QApplication

from mdxscraper.models.config_models import AdvancedConfig, BasicConfig, ImageConfig
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


@pytest.fixture
def mock_mdx_file():
    """Mock MDX文件"""
    mock_file = Mock(spec=Path)
    mock_file.exists.return_value = True
    mock_file.is_file.return_value = True
    mock_file.name = "test.mdx"
    mock_file.suffix = ".mdx"
    return mock_file


@pytest.fixture
def mock_input_file():
    """Mock输入文件"""
    mock_file = Mock(spec=Path)
    mock_file.exists.return_value = True
    mock_file.is_file.return_value = True
    mock_file.name = "test.txt"
    mock_file.suffix = ".txt"
    return mock_file


@pytest.fixture
def mock_output_dir():
    """Mock输出目录"""
    mock_dir = Mock(spec=Path)
    mock_dir.exists.return_value = True
    mock_dir.is_dir.return_value = True
    mock_dir.mkdir.return_value = None
    return mock_dir


@pytest.fixture
def mock_settings_service():
    """Mock设置服务"""
    mock_service = Mock(spec=SettingsService)
    mock_service.get.return_value = "default_value"
    mock_service.set.return_value = None
    mock_service.save.return_value = None
    return mock_service


@pytest.fixture
def mock_presets_service():
    """Mock预设服务"""
    mock_service = Mock(spec=PresetsService)
    mock_service.get_presets.return_value = []
    mock_service.save_preset.return_value = None
    mock_service.delete_preset.return_value = None
    return mock_service


@pytest.fixture
def sample_basic_config():
    """示例基础配置"""
    return BasicConfig(
        mdx_file="test.mdx", input_file="test.txt", output_dir="output", output_format="html"
    )


@pytest.fixture
def sample_advanced_config():
    """示例高级配置"""
    return AdvancedConfig(css_style="classic", pdf_options="classic", max_workers=4)


@pytest.fixture
def sample_image_config():
    """示例图像配置"""
    return ImageConfig(image_format="webp", image_quality=85, image_width=800, image_height=600)


@pytest.fixture
def mock_qt_application():
    """Mock Qt应用程序"""
    if not QApplication.instance():
        app = QApplication([])
        yield app
        app.quit()
    else:
        yield QApplication.instance()


@pytest.fixture
def mock_file_system():
    """Mock文件系统操作"""
    mock_fs = Mock()
    mock_fs.exists.return_value = True
    mock_fs.is_file.return_value = True
    mock_fs.is_dir.return_value = True
    mock_fs.mkdir.return_value = None
    mock_fs.write_text.return_value = None
    mock_fs.read_text.return_value = "test content"
    return mock_fs


@pytest.fixture
def mock_dictionary():
    """Mock字典对象"""
    mock_dict = Mock()
    mock_dict.lookup.return_value = {
        "word": "test",
        "definition": "A test definition",
        "pronunciation": "/test/",
        "examples": ["This is a test example."],
    }
    mock_dict.get_keys.return_value = ["test", "testing", "tested"]
    return mock_dict


@pytest.fixture
def mock_converter():
    """Mock转换器"""
    mock_conv = Mock()
    mock_conv.convert_to_html.return_value = "<html>Test HTML</html>"
    mock_conv.convert_to_pdf.return_value = b"PDF content"
    mock_conv.convert_to_image.return_value = b"Image content"
    return mock_conv
