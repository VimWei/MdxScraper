"""测试用的示例数据"""

from pathlib import Path
from typing import Dict, List

# 示例MDX文件路径
SAMPLE_MDX_FILES = {
    "ahd": Path("data/mdict/AHD/AHD双解.mdx"),
    "cod": Path("data/mdict/COD 9th/Concise Oxford English-Chinese Dictionary 9th.MDX"),
    "collins": Path("data/mdict/Collins COBUILD 8th/Collins COBUILD 8th.mdx"),
}

# 示例输入文件
SAMPLE_INPUT_FILES = {
    "english_words": Path("data/input/Word-English.txt"),
    "chinese_words": Path("data/input/Word-Chinese.txt"),
    "mixed_words": Path("data/input/words_to_lookup.txt"),
}

# 示例词汇列表
SAMPLE_WORDS = [
    "apple", "banana", "cherry", "date", "elderberry",
    "fig", "grape", "honeydew", "kiwi", "lemon"
]

SAMPLE_CHINESE_WORDS = [
    "苹果", "香蕉", "樱桃", "枣", "接骨木莓",
    "无花果", "葡萄", "蜜瓜", "猕猴桃", "柠檬"
]

# 示例课程数据
SAMPLE_LESSONS = [
    {
        "name": "Lesson 1: Fruits",
        "words": ["apple", "banana", "cherry"]
    },
    {
        "name": "Lesson 2: Colors", 
        "words": ["red", "blue", "green"]
    },
    {
        "name": "Lesson 3: Animals",
        "words": ["cat", "dog", "bird"]
    }
]

# 示例配置数据
SAMPLE_BASIC_CONFIG = {
    "mdx_file": str(SAMPLE_MDX_FILES["ahd"]),
    "input_file": str(SAMPLE_INPUT_FILES["english_words"]),
    "output_dir": "data/output",
    "output_format": "html"
}

SAMPLE_ADVANCED_CONFIG = {
    "css_style": "classic",
    "pdf_options": "classic",
    "image_format": "webp",
    "image_quality": 85,
    "max_workers": 4
}

# 示例预设数据
SAMPLE_PRESETS = {
    "basic_html": {
        "name": "Basic HTML",
        "description": "Basic HTML output with default styling",
        "config": SAMPLE_BASIC_CONFIG
    },
    "high_quality_pdf": {
        "name": "High Quality PDF",
        "description": "High quality PDF with custom styling",
        "config": {
            **SAMPLE_BASIC_CONFIG,
            "output_format": "pdf",
            "css_style": "classic",
            "pdf_options": "classic"
        }
    }
}
