"""全局pytest配置和夹具"""

import sys
from pathlib import Path
from typing import Generator

import pytest

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# 导入共享夹具
try:
    from fixtures.mock_objects import (
        mock_converter,
        mock_dictionary,
        mock_file_system,
        mock_input_file,
        mock_mdx_file,
        mock_output_dir,
        mock_presets_service,
        mock_qt_application,
        mock_settings_service,
        sample_advanced_config,
        sample_basic_config,
        sample_image_config,
    )
    from fixtures.sample_data import (
        SAMPLE_ADVANCED_CONFIG,
        SAMPLE_BASIC_CONFIG,
        SAMPLE_CHINESE_WORDS,
        SAMPLE_INPUT_FILES,
        SAMPLE_LESSONS,
        SAMPLE_MDX_FILES,
        SAMPLE_PRESETS,
        SAMPLE_WORDS,
    )
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    from pathlib import Path

    fixtures_path = Path(__file__).parent / "fixtures"
    sys.path.insert(0, str(fixtures_path))

    from mock_objects import (
        mock_converter,
        mock_dictionary,
        mock_file_system,
        mock_input_file,
        mock_mdx_file,
        mock_output_dir,
        mock_presets_service,
        mock_qt_application,
        mock_settings_service,
        sample_advanced_config,
        sample_basic_config,
        sample_image_config,
    )
    from sample_data import (
        SAMPLE_ADVANCED_CONFIG,
        SAMPLE_BASIC_CONFIG,
        SAMPLE_CHINESE_WORDS,
        SAMPLE_INPUT_FILES,
        SAMPLE_LESSONS,
        SAMPLE_MDX_FILES,
        SAMPLE_PRESETS,
        SAMPLE_WORDS,
    )


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """项目根目录路径"""
    return project_root


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """测试数据目录"""
    return project_root / "data"


@pytest.fixture(scope="session")
def sample_mdx_files():
    """示例MDX文件路径"""
    return SAMPLE_MDX_FILES


@pytest.fixture(scope="session")
def sample_input_files():
    """示例输入文件路径"""
    return SAMPLE_INPUT_FILES


@pytest.fixture(scope="session")
def sample_words():
    """示例英文词汇"""
    return SAMPLE_WORDS


@pytest.fixture(scope="session")
def sample_chinese_words():
    """示例中文词汇"""
    return SAMPLE_CHINESE_WORDS


@pytest.fixture(scope="session")
def sample_lessons():
    """示例课程数据"""
    return SAMPLE_LESSONS


@pytest.fixture(scope="session")
def sample_basic_config_dict():
    """示例基础配置字典"""
    return SAMPLE_BASIC_CONFIG


@pytest.fixture(scope="session")
def sample_advanced_config_dict():
    """示例高级配置字典"""
    return SAMPLE_ADVANCED_CONFIG


@pytest.fixture(scope="session")
def sample_presets():
    """示例预设数据"""
    return SAMPLE_PRESETS


# 重新导出所有Mock夹具
__all__ = [
    "mock_mdx_file",
    "mock_input_file",
    "mock_output_dir",
    "mock_settings_service",
    "mock_presets_service",
    "sample_basic_config",
    "sample_advanced_config",
    "sample_image_config",
    "mock_qt_application",
    "mock_file_system",
    "mock_dictionary",
    "mock_converter",
    "project_root_path",
    "test_data_dir",
    "sample_mdx_files",
    "sample_input_files",
    "sample_words",
    "sample_chinese_words",
    "sample_lessons",
    "sample_basic_config_dict",
    "sample_advanced_config_dict",
    "sample_presets",
]
