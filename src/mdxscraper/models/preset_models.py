"""预设数据模型 - 定义预设相关的数据结构"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PresetInfo:
    """预设信息数据类"""
    name: str
    label: str
    description: str = ""
    category: str = "default"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class PresetData:
    """预设数据类"""
    info: PresetInfo
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class PresetCategory:
    """预设分类数据类"""
    name: str
    label: str
    description: str = ""
    presets: list[PresetInfo] = None
    
    def __post_init__(self):
        if self.presets is None:
            self.presets = []
