# MdxScraper GUI 开发指引

基于重构后的架构，为未来新增功能、配置选项、页面等提供规范化指南。

## 一、架构概览

### 目录结构
```
src/mdxscraper/gui/
├── main_window.py          # 主窗口壳与编排
├── pages/                  # 页面组件
│   ├── basic_page.py       # 基础输入/输出页面
│   ├── image_page.py       # 图像选项页面
│   ├── pdf_page.py         # PDF 预设页面
│   ├── css_page.py         # CSS 样式页面
│   ├── advanced_page.py    # 高级选项页面
│   └── about_page.py       # 关于页面
├── components/             # 可复用组件
│   ├── command_panel.py    # 全局操作面板
│   ├── file_picker.py      # 文件选择器（待完善）
│   └── progress_panel.py   # 进度面板（待完善）
├── services/               # 业务服务层
│   ├── settings_service.py # 配置管理服务
│   ├── presets_service.py  # 预设管理服务
│   └── export_service.py   # 导出服务
├── workers/                # 后台工作线程
│   └── conversion_worker.py # 转换工作线程
└── assets/                 # 资源文件
    └── app_icon.ico        # 应用图标
```

### 分层架构
- **UI 层**：Pages + Components（展示/交互）
- **服务层**：Services（业务逻辑）
- **工作层**：Workers（耗时操作）

## 二、新增页面指南

### 2.1 创建新页面

1. **创建页面文件**
   ```python
   # src/mdxscraper/gui/pages/new_page.py
   from __future__ import annotations
   
   from PySide6.QtCore import Signal
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
   
   class NewPage(QWidget):
       # 定义页面信号
       option_changed = Signal()
       value_changed = Signal(str)
       
       def __init__(self, parent: QWidget | None = None):
           super().__init__(parent)
           self._setup_ui()
           self._connect_signals()
       
       def _setup_ui(self):
           """设置 UI 布局"""
           layout = QVBoxLayout(self)
           layout.setContentsMargins(8, 8, 8, 8)
           # 添加控件...
       
       def _connect_signals(self):
           """连接内部信号"""
           # 连接控件信号到页面信号
           pass
   ```

2. **在 MainWindow 中集成**
   ```python
   # 在 main_window.py 的 __init__ 中
   from mdxscraper.gui.pages.new_page import NewPage
   
   # 创建页面实例
   self.tab_new = NewPage(self)
   
   # 添加到标签页
   self.tabs.addTab(self.tab_new, "New")
   
   # 连接信号
   self.tab_new.option_changed.connect(self.sync_new_to_config)
   self.tab_new.value_changed.connect(self.on_new_value_changed)
   
   # 同步配置
   self.sync_new_from_config()
   ```

3. **实现配置同步方法**
   ```python
   def sync_new_from_config(self):
       """从配置同步到页面"""
       value = self.settings.get("new.option", "default")
       self.tab_new.set_value(value)
   
   def sync_new_to_config(self):
       """从页面同步到配置"""
       value = self.tab_new.get_value()
       self.settings.set("new.option", value)
   ```

### 2.2 页面设计原则

- **单一职责**：每个页面只负责一个功能领域
- **信号通信**：页面通过信号与 MainWindow 通信，不直接访问服务
- **配置绑定**：页面状态与配置系统双向绑定
- **类型注解**：所有方法都有完整的类型注解

## 三、新增配置选项指南

### 3.1 在 SettingsService 中添加配置

1. **添加配置访问方法**
   ```python
   # 在 settings_service.py 中
   def get_new_option(self) -> str:
       return self.cm.get("new.option", "default")
   
   def set_new_option(self, value: str) -> None:
       self.cm.set("new.option", value)
   ```

2. **更新配置结构**
   ```toml
   # 在 default_config.toml 中
   [new]
   option = "default_value"
   ```

### 3.2 在页面中使用配置

1. **页面控件绑定**
   ```python
   # 在页面中
   def _setup_ui(self):
       self.option_input = QLineEdit(self)
       self.option_input.setText(self.parent().settings.get_new_option())
   
   def _connect_signals(self):
       self.option_input.textChanged.connect(self._on_option_changed)
   
   def _on_option_changed(self):
       self.parent().settings.set_new_option(self.option_input.text())
       self.option_changed.emit()
   ```

2. **MainWindow 同步**
   ```python
   def sync_new_from_config(self):
       value = self.settings.get_new_option()
       self.tab_new.option_input.setText(value)
   ```

## 四、新增服务指南

### 4.1 创建新服务

1. **创建服务文件**
   ```python
   # src/mdxscraper/gui/services/new_service.py
   from __future__ import annotations
   
   from pathlib import Path
   from typing import Dict, Any, Optional
   
   class NewService:
       def __init__(self, project_root: Path):
           self.project_root = project_root
       
       def process_data(self, data: str) -> Dict[str, Any]:
           """处理数据的业务逻辑"""
           # 实现业务逻辑
           return {"result": "processed"}
       
       def validate_input(self, input_data: str) -> bool:
           """验证输入数据"""
           return len(input_data) > 0
   ```

2. **在 MainWindow 中集成**
   ```python
   # 在 main_window.py 的 __init__ 中
   from mdxscraper.gui.services.new_service import NewService
   
   # 创建服务实例
   self.new_service = NewService(project_root)
   ```

### 4.2 服务设计原则

- **无状态**：服务不持有 UI 状态
- **类型安全**：所有方法都有完整类型注解
- **错误处理**：异常在服务层处理，通过返回值或信号传递
- **可测试**：服务方法应该是纯函数或易于测试

## 五、新增组件指南

### 5.1 创建可复用组件

1. **创建组件文件**
   ```python
   # src/mdxscraper/gui/components/new_component.py
   from __future__ import annotations
   
   from PySide6.QtCore import Signal
   from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
   
   class NewComponent(QWidget):
       # 定义组件信号
       action_requested = Signal()
       
       def __init__(self, parent: QWidget | None = None):
           super().__init__(parent)
           self._setup_ui()
       
       def _setup_ui(self):
           layout = QVBoxLayout(self)
           self.button = QPushButton("Action", self)
           self.button.clicked.connect(self.action_requested.emit)
           layout.addWidget(self.button)
       
       def set_enabled(self, enabled: bool) -> None:
           """设置组件启用状态"""
           self.button.setEnabled(enabled)
   ```

2. **在页面中使用**
   ```python
   # 在页面中
   from mdxscraper.gui.components.new_component import NewComponent
   
   def _setup_ui(self):
       self.new_component = NewComponent(self)
       self.new_component.action_requested.connect(self._on_action)
       layout.addWidget(self.new_component)
   ```

### 5.2 组件设计原则

- **可复用**：组件应该可以在多个页面中使用
- **信号通信**：组件通过信号与父组件通信
- **状态管理**：组件管理自己的内部状态
- **API 设计**：提供清晰的公共 API

## 六、新增工作线程指南

### 6.1 创建新工作线程

1. **创建工作线程文件**
   ```python
   # src/mdxscraper/gui/workers/new_worker.py
   from __future__ import annotations
   
   from PySide6.QtCore import QThread, Signal
   from pathlib import Path
   
   class NewWorker(QThread):
       # 定义线程信号
       progress_sig = Signal(int)
       finished_sig = Signal(str)
       error_sig = Signal(str)
       
       def __init__(self, project_root: Path, data: str):
           super().__init__()
           self.project_root = project_root
           self.data = data
       
       def run(self):
           try:
               # 执行耗时操作
               for i in range(100):
                   if self.isInterruptionRequested():
                       return
                   # 处理数据
                   self.progress_sig.emit(i + 1)
               
               self.finished_sig.emit("处理完成")
           except Exception as e:
               self.error_sig.emit(f"处理失败: {e}")
   ```

2. **在 MainWindow 中使用**
   ```python
   # 在 main_window.py 中
   from mdxscraper.gui.workers.new_worker import NewWorker
   
   def start_new_worker(self):
       self.new_worker = NewWorker(self.project_root, "data")
       self.new_worker.progress_sig.connect(self.command_panel.setProgress)
       self.new_worker.finished_sig.connect(self.on_new_finished)
       self.new_worker.error_sig.connect(self.on_new_error)
       self.new_worker.start()
   ```

### 6.2 工作线程设计原则

- **无 UI 依赖**：线程不直接操作 UI 控件
- **信号通信**：通过信号与主线程通信
- **可中断**：支持 `requestInterruption()` 和 `isInterruptionRequested()`
- **错误处理**：异常在线程内捕获，通过信号传递

## 七、测试指南

### 7.1 单元测试

1. **服务测试**
   ```python
   # tests/test_new_service.py
   from pathlib import Path
   from mdxscraper.gui.services.new_service import NewService
   
   def test_process_data():
       service = NewService(Path("."))
       result = service.process_data("test")
       assert result["result"] == "processed"
   
   def test_validate_input():
       service = NewService(Path("."))
       assert service.validate_input("valid") is True
       assert service.validate_input("") is False
   ```

2. **页面测试**
   ```python
   # tests/test_new_page.py
   from PySide6.QtWidgets import QApplication
   from mdxscraper.gui.pages.new_page import NewPage
   
   def test_page_creation():
       app = QApplication([])
       page = NewPage()
       assert page is not None
       app.quit()
   ```

### 7.2 集成测试

- **功能测试**：测试完整的功能流程
- **UI 测试**：测试用户界面交互
- **性能测试**：测试大数据量处理性能

## 八、代码规范

### 8.1 命名规范

- **类名**：PascalCase（如 `NewPage`、`NewService`）
- **方法名**：snake_case（如 `process_data`、`sync_from_config`）
- **信号名**：snake_case + `_sig` 后缀（如 `progress_sig`、`finished_sig`）
- **文件名**：snake_case（如 `new_page.py`、`new_service.py`）

### 8.2 类型注解

- **所有方法**：必须有完整的类型注解
- **返回值**：明确指定返回类型
- **参数**：明确指定参数类型
- **导入**：使用 `from __future__ import annotations`

### 8.3 文档规范

- **类文档**：简要说明类的职责
- **方法文档**：说明方法的功能、参数、返回值
- **复杂逻辑**：添加行内注释

## 九、常见模式

### 9.1 配置同步模式

```python
# 统一页面同步模式（推荐）
# 1) 为页面建立数据类 NewConfig
# 2) 在 SettingsService 中提供 get_new_config()/update_new_config()
# 3) 页面实现 get_config()/set_config()，只绑定控件与 DTO

# MainWindow 侧：
def sync_new_from_config(self):
    config = self.settings.get_new_config()
    self.tab_new.set_config(config)

def sync_new_to_config(self):
    config = self.tab_new.get_config()
    self.settings.update_new_config(config)
```

### 9.2 信号连接模式

```python
# 页面信号连接
self.page.option_changed.connect(self.sync_to_config)

# 工作线程信号连接
self.worker.progress_sig.connect(self.command_panel.setProgress)
self.worker.finished_sig.connect(self.on_finished)
self.worker.error_sig.connect(self.on_error)
```

### 9.3 错误处理模式

```python
# 服务层错误处理
def process_data(self, data: str) -> Optional[Dict[str, Any]]:
    try:
        return self._do_process(data)
    except Exception as e:
        self.log_error(f"处理失败: {e}")
        return None

# UI 层错误处理
def on_error(self, message: str):
    self.command_panel.appendLog(f"❌ Error: {message}")
```

### 9.4 预设加载与选择保留模式（重要）

```python
# 初始化/导入/恢复：先加载列表，后按配置恢复选择
self.reload_presets(auto_select_default=False)
self.sync_from_config()  # set_config 内部设置 combo 选中项

# 保存预设：重载列表但不改动选择，再回写配置
self.reload_presets(auto_select_default=False)
self.sync_pdf_to_config()  # 或 sync_css_to_config()
```

注意：避免在 `reload_presets()` 中自动选择默认项（如 `default [built-in]`），否则会触发 `on_*_preset_changed` 覆盖已保存的 `preset_label`。

## 十、最佳实践

1. **保持简单**：优先选择简单的解决方案
2. **单一职责**：每个类/方法只做一件事
3. **依赖注入**：通过构造函数注入依赖
4. **信号解耦**：使用信号/槽机制解耦组件
5. **类型安全**：充分利用类型注解
6. **错误处理**：在适当的层级处理错误
7. **测试覆盖**：为关键功能编写测试
8. **文档更新**：及时更新相关文档

---

遵循这些指南，可以确保新增功能与现有架构保持一致，提高代码质量和可维护性。
