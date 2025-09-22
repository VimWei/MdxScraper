# 工具函数 API 文档

## 概述

工具函数模块提供 MdxScraper 的辅助功能，包括文件操作、GUI 工具、编码检测等实用功能。

## 模块结构

```
src/mdxscraper/utils/
├── __init__.py
├── file_utils.py       # 文件操作工具
└── gui_utils.py        # GUI 工具函数
```

## file_utils.py - 文件操作工具

### 编码检测和文件操作

#### detect_encoding
```python
def detect_encoding(file_path: Path, default_encoding: str = 'utf-8') -> str
```
检测文件编码格式。

- **参数**：
  - `file_path` (Path): 文件路径
  - `default_encoding` (str): 默认编码，默认 'utf-8'
- **返回**：
  - `str`: 检测到的编码格式
- **异常**：
  - `FileNotFoundError`: 文件不存在
  - `OSError`: 文件读取错误

#### open_encoding_file
```python
def open_encoding_file(file_path: Path, default_encoding: str = 'utf-8') -> TextIO
```
以检测到的编码打开文件。

- **参数**：
  - `file_path` (Path): 文件路径
  - `default_encoding` (str): 默认编码
- **返回**：
  - `TextIO`: 文件对象
- **异常**：
  - `FileNotFoundError`: 文件不存在
  - `UnicodeDecodeError`: 编码错误

#### get_file_size
```python
def get_file_size(file_path: Path) -> int
```
获取文件大小。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `int`: 文件大小（字节）
- **异常**：
  - `FileNotFoundError`: 文件不存在

#### get_file_extension
```python
def get_file_extension(file_path: Path) -> str
```
获取文件扩展名。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `str`: 文件扩展名（小写）

### 路径操作

#### ensure_directory
```python
def ensure_directory(dir_path: Path) -> None
```
确保目录存在，如果不存在则创建。

- **参数**：
  - `dir_path` (Path): 目录路径
- **异常**：
  - `OSError`: 目录创建失败

#### get_relative_path
```python
def get_relative_path(file_path: Path, base_path: Path) -> Path
```
获取相对路径。

- **参数**：
  - `file_path` (Path): 目标文件路径
  - `base_path` (Path): 基础路径
- **返回**：
  - `Path`: 相对路径

#### normalize_path
```python
def normalize_path(path: str) -> Path
```
标准化路径，处理跨平台路径分隔符。

- **参数**：
  - `path` (str): 路径字符串
- **返回**：
  - `Path`: 标准化后的路径对象

### 文件类型检测

#### is_text_file
```python
def is_text_file(file_path: Path) -> bool
```
检测是否为文本文件。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `bool`: 是否为文本文件

#### is_binary_file
```python
def is_binary_file(file_path: Path) -> bool
```
检测是否为二进制文件。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `bool`: 是否为二进制文件

#### get_mime_type
```python
def get_mime_type(file_path: Path) -> str
```
获取文件的 MIME 类型。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `str`: MIME 类型

### 文件操作

#### safe_copy
```python
def safe_copy(src_path: Path, dst_path: Path, overwrite: bool = False) -> None
```
安全复制文件。

- **参数**：
  - `src_path` (Path): 源文件路径
  - `dst_path` (Path): 目标文件路径
  - `overwrite` (bool): 是否覆盖已存在的文件
- **异常**：
  - `FileExistsError`: 目标文件已存在且不允许覆盖
  - `OSError`: 复制操作失败

#### safe_move
```python
def safe_move(src_path: Path, dst_path: Path, overwrite: bool = False) -> None
```
安全移动文件。

- **参数**：
  - `src_path` (Path): 源文件路径
  - `dst_path` (Path): 目标文件路径
  - `overwrite` (bool): 是否覆盖已存在的文件
- **异常**：
  - `FileExistsError`: 目标文件已存在且不允许覆盖
  - `OSError`: 移动操作失败

#### backup_file
```python
def backup_file(file_path: Path, backup_suffix: str = None) -> Path
```
备份文件。

- **参数**：
  - `file_path` (Path): 要备份的文件路径
  - `backup_suffix` (str): 备份文件后缀，默认使用时间戳
- **返回**：
  - `Path`: 备份文件路径
- **异常**：
  - `FileNotFoundError`: 源文件不存在
  - `OSError`: 备份操作失败

### 文件搜索

#### find_files
```python
def find_files(directory: Path, pattern: str = "*", recursive: bool = True) -> List[Path]
```
搜索文件。

- **参数**：
  - `directory` (Path): 搜索目录
  - `pattern` (str): 文件名模式
  - `recursive` (bool): 是否递归搜索
- **返回**：
  - `List[Path]`: 找到的文件路径列表

#### find_files_by_extension
```python
def find_files_by_extension(directory: Path, extensions: List[str], recursive: bool = True) -> List[Path]
```
按扩展名搜索文件。

- **参数**：
  - `directory` (Path): 搜索目录
  - `extensions` (List[str]): 扩展名列表
  - `recursive` (bool): 是否递归搜索
- **返回**：
  - `List[Path]`: 找到的文件路径列表

## gui_utils.py - GUI 工具函数

### 样式和主题

#### load_style_sheet
```python
def load_style_sheet(style_name: str) -> str
```
加载样式表。

- **参数**：
  - `style_name` (str): 样式名称
- **返回**：
  - `str`: 样式表内容
- **异常**：
  - `FileNotFoundError`: 样式文件不存在

#### apply_theme
```python
def apply_theme(widget: QWidget, theme_name: str) -> None
```
应用主题到控件。

- **参数**：
  - `widget` (QWidget): 要应用主题的控件
  - `theme_name` (str): 主题名称

#### get_icon
```python
def get_icon(icon_name: str, size: int = 16) -> QIcon
```
获取图标。

- **参数**：
  - `icon_name` (str): 图标名称
  - `size` (int): 图标大小
- **返回**：
  - `QIcon`: 图标对象

### 对话框工具

#### show_info_dialog
```python
def show_info_dialog(parent: QWidget, title: str, message: str) -> None
```
显示信息对话框。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `message` (str): 消息内容

#### show_warning_dialog
```python
def show_warning_dialog(parent: QWidget, title: str, message: str) -> None
```
显示警告对话框。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `message` (str): 消息内容

#### show_error_dialog
```python
def show_error_dialog(parent: QWidget, title: str, message: str) -> None
```
显示错误对话框。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `message` (str): 消息内容

#### show_question_dialog
```python
def show_question_dialog(parent: QWidget, title: str, message: str) -> bool
```
显示问题对话框。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `message` (str): 消息内容
- **返回**：
  - `bool`: 用户选择结果

### 文件选择

#### select_file
```python
def select_file(parent: QWidget, title: str, filter: str = "All Files (*)") -> Optional[str]
```
选择文件。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `filter` (str): 文件过滤器
- **返回**：
  - `Optional[str]`: 选择的文件路径，如果取消则返回 None

#### select_directory
```python
def select_directory(parent: QWidget, title: str) -> Optional[str]
```
选择目录。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
- **返回**：
  - `Optional[str]`: 选择的目录路径，如果取消则返回 None

#### select_save_file
```python
def select_save_file(parent: QWidget, title: str, filter: str = "All Files (*)") -> Optional[str]
```
选择保存文件。

- **参数**：
  - `parent` (QWidget): 父控件
  - `title` (str): 对话框标题
  - `filter` (str): 文件过滤器
- **返回**：
  - `Optional[str]`: 选择的文件路径，如果取消则返回 None

### 进度显示

#### ProgressDialog
```python
class ProgressDialog(QDialog):
    """进度对话框类"""
    
    def __init__(self, parent: QWidget, title: str = "处理中..."):
        super().__init__(parent)
        self.setup_ui(title)
    
    def setup_ui(self, title: str) -> None:
        """设置界面"""
        pass
    
    def update_progress(self, value: int, text: str = "") -> None:
        """更新进度"""
        pass
    
    def set_maximum(self, maximum: int) -> None:
        """设置最大值"""
        pass
```

### 日志显示

#### LogWidget
```python
class LogWidget(QTextEdit):
    """日志显示控件"""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """设置界面"""
        pass
    
    def append_log(self, message: str, level: str = "INFO") -> None:
        """添加日志"""
        pass
    
    def clear_log(self) -> None:
        """清空日志"""
        pass
```

### 配置控件

#### ConfigWidget
```python
class ConfigWidget(QWidget):
    """配置编辑控件"""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """设置界面"""
        pass
    
    def set_config(self, config: Dict[str, Any]) -> None:
        """设置配置"""
        pass
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        pass
    
    def validate_config(self) -> bool:
        """验证配置"""
        pass
```

## 使用示例

### 文件操作示例

```python
from pathlib import Path
from mdxscraper.utils.file_utils import (
    detect_encoding, open_encoding_file, 
    ensure_directory, backup_file
)

# 检测文件编码
file_path = Path("data/input/words.txt")
encoding = detect_encoding(file_path)
print(f"文件编码: {encoding}")

# 以正确编码打开文件
with open_encoding_file(file_path) as f:
    content = f.read()

# 确保目录存在
output_dir = Path("data/output")
ensure_directory(output_dir)

# 备份文件
backup_path = backup_file(file_path)
print(f"文件已备份到: {backup_path}")
```

### GUI 工具示例

```python
from PySide6.QtWidgets import QApplication, QMainWindow
from mdxscraper.utils.gui_utils import (
    show_info_dialog, select_file, 
    ProgressDialog, LogWidget
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # 设置界面
        pass
    
    def on_select_file(self):
        # 选择文件
        file_path = select_file(self, "选择输入文件", "Text Files (*.txt)")
        if file_path:
            print(f"选择的文件: {file_path}")
    
    def on_show_progress(self):
        # 显示进度对话框
        progress = ProgressDialog(self, "处理中...")
        progress.set_maximum(100)
        
        for i in range(101):
            progress.update_progress(i, f"处理进度: {i}%")
            QApplication.processEvents()
            time.sleep(0.01)
        
        progress.close()
    
    def show_message(self):
        # 显示信息对话框
        show_info_dialog(self, "信息", "操作完成！")
```

### 错误处理示例

```python
from mdxscraper.utils.file_utils import safe_copy
from mdxscraper.utils.gui_utils import show_error_dialog

try:
    safe_copy(Path("source.txt"), Path("destination.txt"))
except FileExistsError:
    show_error_dialog(self, "错误", "目标文件已存在")
except OSError as e:
    show_error_dialog(self, "错误", f"复制失败: {e}")
```

## 性能优化

### 文件操作优化
- 使用 Path 对象进行路径操作
- 批量文件操作
- 异步 I/O 操作

### GUI 优化
- 延迟加载控件
- 虚拟化长列表
- 缓存样式和图标

## 扩展性

### 插件支持
```python
# 支持自定义文件处理器
def register_file_handler(extension: str, handler: Callable) -> None:
    """注册文件处理器"""
    pass

# 支持自定义 GUI 主题
def register_theme(name: str, theme_data: Dict) -> None:
    """注册主题"""
    pass
```
