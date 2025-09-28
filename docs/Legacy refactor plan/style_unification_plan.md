# 样式统一管理实施方案

## 目标
将分散在 MainWindow 和各页面中的样式代码统一管理，减少代码重复，提高维护性。

## 当前问题
- MainWindow 中有 75 行样式代码
- PDF/CSS 页面重复 `dirty_label` 样式
- Advanced 页面有独立的只读输入框样式
- 样式硬编码在 Python 中，难以维护

## 实施方案

### 1. 目录结构
```
src/mdxscraper/gui/styles/
├── __init__.py
├── theme_loader.py          # 主题加载器
├── themes/
│   ├── default.qss         # 默认主题
│   ├── dark.qss            # 暗色主题（可选）
│   └── compact.qss         # 紧凑主题（可选）
└── constants.py            # 样式常量
```

### 2. 核心组件

#### theme_loader.py
```python
from pathlib import Path
from typing import Dict, Optional

class ThemeLoader:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.styles_dir = project_root / "src" / "mdxscraper" / "gui" / "styles"
        self._cache: Dict[str, str] = {}
    
    def load_theme(self, theme_name: str = "default") -> str:
        """加载主题样式"""
        if theme_name in self._cache:
            return self._cache[theme_name]
        
        qss_file = self.styles_dir / "themes" / f"{theme_name}.qss"
        if qss_file.exists():
            content = qss_file.read_text(encoding="utf-8")
            self._cache[theme_name] = content
            return content
        return ""
    
    def get_style(self, style_class: str) -> str:
        """获取特定样式类的样式"""
        # 从当前主题中提取特定样式
        theme = self.load_theme()
        # 实现样式解析逻辑
        return self._extract_style(theme, style_class)
    
    def apply_style(self, widget, style_class: str):
        """为控件应用样式"""
        style = self.get_style(style_class)
        widget.setStyleSheet(style)
```

#### themes/default.qss
```css
/* 全局样式 */
QMainWindow {
    background-color: #ffffff;
}

/* 标签样式 */
QLabel[class="field-label"] {
    font-weight: bold;
}

.dirty-label {
    color: #d9831f;
    font-weight: bold;
}

/* 按钮样式 */
QPushButton#scrape-button {
    background-color: #0078d4;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: bold;
    padding: 12px 24px;
}

QPushButton#scrape-button:hover {
    background-color: #106ebe;
}

QPushButton#scrape-button:pressed {
    background-color: #005a9e;
}

QPushButton#scrape-button:disabled {
    background-color: #cccccc;
    color: #666666;
}

QPushButton#open-data-button {
    background-color: #4caf50;
    color: white;
    border: 1px solid #388e3c;
    border-radius: 4px;
    font-weight: 600;
    padding: 4px 8px;
}

QPushButton#open-data-button:hover {
    background-color: #388e3c;
    border-color: #2e7d32;
}

QPushButton#open-data-button:pressed {
    background-color: #2e7d32;
    border-color: #1b5e20;
}

/* 进度条样式 */
QProgressBar {
    border: 1px solid #bdbdbd;
    border-radius: 6px;
    background-color: #e6e6e6;
    text-align: center;
    color: #333333;
}

QProgressBar::chunk {
    background-color: #4caf50;
    border-radius: 6px;
}

/* 文本编辑器样式 */
QTextEdit {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
}

/* 只读输入框样式 */
.readonly-input {
    color: gray;
    background-color: #f5f5f5;
}
```

### 3. 使用方式

#### MainWindow 简化
```python
def apply_modern_styling(self):
    """Apply modern PySide6 styling using built-in styles"""
    from PySide6.QtWidgets import QApplication
    from mdxscraper.gui.styles.theme_loader import ThemeLoader

    app = QApplication.instance()
    if app:
        app.setStyle('Fusion')
    
    theme_loader = ThemeLoader(self.project_root)
    self.setStyleSheet(theme_loader.load_theme())
```

#### 页面中使用
```python
# PDF/CSS 页面
def _setup_ui(self):
    # ... 其他代码 ...
    self.dirty_label = QLabel("* Untitled", self)
    self.dirty_label.setProperty("class", "dirty-label")  # 使用 CSS 类
    # 不再需要 setStyleSheet

# Advanced 页面
def _setup_ui(self):
    # ... 其他代码 ...
    self.edit_data_path = QLineEdit(self)
    self.edit_data_path.setReadOnly(True)
    self.edit_data_path.setProperty("class", "readonly-input")  # 使用 CSS 类
```

## 预期效果

### 代码量减少
- MainWindow: 减少 22 行（从 30 行减少到 8 行）
- PDF 页面: 减少 1 行重复样式
- CSS 页面: 减少 1 行重复样式
- Advanced 页面: 减少 1 行独立样式
- **总计减少**: ~25 行 Python 代码

### 维护性提升
- 样式集中管理，修改一处即可
- 支持多主题切换
- 样式与逻辑分离
- 易于扩展新样式

### 功能增强
- 支持运行时主题切换
- 支持暗色主题
- 支持紧凑布局主题
- 样式缓存，提高性能

## 实施步骤

1. **创建样式目录结构**
2. **实现 ThemeLoader 类**
3. **创建 default.qss 主题文件**
4. **修改 MainWindow 使用主题加载器**
5. **修改各页面使用 CSS 类**
6. **测试样式效果**
7. **可选：添加暗色主题支持**

## 总结

样式统一管理虽然不能大幅减少 MainWindow 的代码量（只减少 22 行），但能带来：
- 更好的维护性
- 消除代码重复
- 支持主题扩展
- 样式与逻辑分离

这是一个值得实施的改进，特别是考虑到未来的主题扩展需求。
