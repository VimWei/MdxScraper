"""主题加载器 - 统一管理 GUI 样式"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


class ThemeLoader:
    """主题加载器，负责加载和管理 GUI 样式主题"""

    def __init__(self, project_root: Path):
        """初始化主题加载器

        Args:
            project_root: 项目根目录路径
        """
        self.project_root = project_root
        self.styles_dir = project_root / "src" / "mdxscraper" / "gui" / "styles"
        self._cache: Dict[str, str] = {}

    def load_theme(self, theme_name: str = "default") -> str:
        """加载主题样式

        Args:
            theme_name: 主题名称，默认为 "default"

        Returns:
            主题样式字符串，如果加载失败返回空字符串
        """
        if theme_name in self._cache:
            return self._cache[theme_name]

        qss_file = self.styles_dir / "themes" / f"{theme_name}.qss"
        if qss_file.exists():
            try:
                content = qss_file.read_text(encoding="utf-8")
                self._cache[theme_name] = content
                return content
            except Exception:
                return ""
        return ""

    def apply_base_style(self, app, theme_name: str = "default"):
        """应用基础样式设置

        Args:
            app: QApplication 实例
            theme_name: 主题名称，用于读取基础样式配置
        """
        if app:
            base_style = self._get_base_style(theme_name)
            app.setStyle(base_style)

    def _get_base_style(self, theme_name: str) -> str:
        """获取主题的基础样式配置

        Args:
            theme_name: 主题名称

        Returns:
            基础样式名称，默认为 'Fusion'
        """
        config_file = self.styles_dir / "themes" / f"{theme_name}.json"
        if config_file.exists():
            try:
                import json

                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return config.get("base_style", "Fusion")
            except Exception:
                pass
        return "Fusion"  # 默认使用 Fusion 样式

    def get_style(self, style_class: str, theme_name: str = "default") -> str:
        """获取特定样式类的样式

        Args:
            style_class: 样式类名
            theme_name: 主题名称

        Returns:
            样式字符串
        """
        theme = self.load_theme(theme_name)
        return self._extract_style(theme, style_class)

    def apply_style(self, widget, style_class: str, theme_name: str = "default"):
        """为控件应用样式

        Args:
            widget: 要应用样式的控件
            style_class: 样式类名
            theme_name: 主题名称
        """
        style = self.get_style(style_class, theme_name)
        widget.setStyleSheet(style)

    def _extract_style(self, theme_content: str, style_class: str) -> str:
        """从主题内容中提取特定样式类

        Args:
            theme_content: 主题内容
            style_class: 样式类名

        Returns:
            提取的样式字符串
        """
        # 简单的样式提取实现
        # 查找 .style_class { ... } 块
        import re

        pattern = rf"\.{re.escape(style_class)}\s*\{{([^}}]+)\}}"
        match = re.search(pattern, theme_content, re.DOTALL)

        if match:
            return f".{style_class} {{ {match.group(1).strip()} }}"

        return ""

    def clear_cache(self):
        """清空样式缓存"""
        self._cache.clear()

    def get_available_themes(self) -> list[str]:
        """获取可用的主题列表

        Returns:
            可用主题名称列表
        """
        themes_dir = self.styles_dir / "themes"
        if not themes_dir.exists():
            return []

        themes = []
        for qss_file in themes_dir.glob("*.qss"):
            themes.append(qss_file.stem)

        return sorted(themes)
