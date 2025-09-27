# MdxScraper 开发指南

基于重构后的分层架构，为未来新增功能、配置选项、页面等提供规范化指南。

## 一、架构概览

### 目录结构（重构后实现）

```
src/mdxscraper/
├── __init__.py
├── __main__.py
├── config/                    # 配置层
│   ├── __init__.py
│   ├── config_manager.py      # 配置管理器
│   ├── default_config.toml    # 默认配置
│   ├── css_styles/            # CSS预设
│   └── pdf_options/           # PDF预设
├── mdict/                     # 核心基础设施层 (真正的核心)
│   ├── __init__.py
│   ├── mdict_query.py         # 第三方库包装器
│   └── vendor/                # 第三方 mdict-query 库
├── core/                      # 业务核心层 (基于mdict的业务算法)
│   ├── __init__.py
│   ├── converter.py           # 转换算法 (mdx2html, mdx2pdf, mdx2img)
│   ├── dictionary.py          # 字典查询封装
│   ├── parser.py              # 文件解析算法
│   └── renderer.py            # 渲染算法
├── models/                    # 数据模型层
│   ├── __init__.py
│   ├── config_models.py       # 配置数据模型
│   └── preset_models.py       # 预设数据模型
├── services/                  # 业务服务层
│   ├── __init__.py
│   ├── settings_service.py    # 配置管理服务
│   ├── presets_service.py     # 预设管理服务
│   └── export_service.py      # 导出服务
├── coordinators/              # 应用协调层
│   ├── __init__.py
│   ├── config_coordinator.py  # 配置协调
│   ├── preset_coordinator.py  # 预设协调
│   ├── file_coordinator.py    # 文件操作协调
│   └── conversion_coordinator.py # 转换协调
├── workers/                   # 执行层 (UI交互的执行器)
│   ├── __init__.py
│   └── conversion_worker.py   # 转换执行器
├── gui/                       # 纯UI层
│   ├── __init__.py
│   ├── main_window.py         # 主窗口
│   ├── config_dialog.py       # 配置对话框
│   ├── components/            # UI组件
│   │   ├── __init__.py
│   │   ├── command_panel.py   # 全局操作面板
│   │   ├── file_picker.py     # 文件选择器
│   │   ├── log_panel.py       # 日志面板
│   │   └── progress_panel.py  # 进度面板
│   ├── pages/                 # UI页面
│   │   ├── __init__.py
│   │   ├── basic_page.py      # 基础输入/输出页面
│   │   ├── image_page.py      # 图像选项页面
│   │   ├── pdf_page.py        # PDF 预设页面
│   │   ├── css_page.py        # CSS 样式页面
│   │   ├── advanced_page.py   # 高级选项页面
│   │   └── about_page.py      # 关于页面
│   ├── styles/                # UI样式
│   │   ├── __init__.py
│   │   ├── theme_loader.py    # 主题加载器
│   │   └── themes/            # 主题文件
│   └── assets/                # UI资源
│       ├── app_icon.ico
│       └── app_icon.gfie
└── utils/                     # 工具层
    ├── __init__.py
    ├── path_utils.py          # 路径和系统工具
    ├── system_utils.py        # 系统操作工具
    ├── time_utils.py          # 时间处理工具
    └── file_utils.py          # 文件操作工具
```

### 分层架构

#### 1. 核心基础设施层 (`mdict/`) - **真正的核心**
- **职责**: 提供MDX文件处理的基础能力，整个程序存在的前提
- **内容**:
  - `mdict_query.py` - 第三方库包装器，提供稳定的API接口
  - `vendor/` - 完整的第三方 mdict-query 库
- **特点**: 外部依赖，提供最底层的基础设施，整个程序的核心

#### 2. 业务核心层 (`core/`) - **基于基础设施的业务算法**
- **职责**: 基于mdict基础设施，提供业务相关的核心算法
- **内容**:
  - `converter.py` - 转换算法 (mdx2html, mdx2pdf, mdx2img)
  - `dictionary.py` - 字典查询封装和回退策略
  - `parser.py` - 文件解析算法 (支持多种格式)
  - `renderer.py` - HTML渲染算法 (CSS合并、图片嵌入)
- **特点**: 纯算法实现，依赖mdict层，无UI依赖，高度可测试

#### 3. 数据模型层 (`models/`)
- **职责**: 定义数据结构、数据验证、数据转换
- **内容**: 
  - `config_models.py` - 配置数据模型
  - `preset_models.py` - 预设数据模型
- **特点**: 纯数据类，无业务逻辑，无UI依赖

#### 4. 业务服务层 (`services/`)
- **职责**: 封装业务逻辑，提供业务API，调用业务核心层
- **内容**:
  - `settings_service.py` - 配置管理服务 (包含配置验证)
  - `presets_service.py` - 预设管理服务
  - `export_service.py` - 导出服务 (调用core.converter)
- **特点**: 纯业务逻辑，依赖业务核心层，无UI依赖，可独立测试

#### 5. 应用协调层 (`coordinators/`)
- **职责**: 协调多个服务，处理复杂的业务流程
- **内容**:
  - `config_coordinator.py` - 配置协调
  - `preset_coordinator.py` - 预设协调
  - `file_coordinator.py` - 文件操作协调
  - `conversion_coordinator.py` - 转换协调
- **特点**: 依赖服务层，协调业务流程，无UI依赖

#### 6. 执行层 (`workers/`) - **UI交互的执行器**
- **职责**: 在后台线程中执行耗时任务，提供UI交互能力
- **内容**:
  - `conversion_worker.py` - 转换执行器 (调用core层 + UI进度报告)
- **特点**: 继承QThread，调用业务核心层，通过信号与UI通信

#### 7. UI层 (`gui/`)
- **职责**: 用户界面展示和交互
- **内容**:
  - `main_window.py` - 主窗口
  - `components/` - UI组件
  - `pages/` - UI页面
  - `styles/` - UI样式
- **特点**: 纯UI逻辑，依赖协调器层和执行层

#### 8. 工具层 (`utils/`)
- **职责**: 提供通用工具函数，系统检测，路径处理，时间处理
- **内容**:
  - `path_utils.py` - 路径处理和wkhtmltopdf检测 (已存在，包含OS检测)
  - `system_utils.py` - 系统操作工具 (新增，从file_coordinator.py迁移)
  - `time_utils.py` - 时间处理工具 (新增，从core/converter.py迁移)
  - `file_utils.py` - 文件操作工具 (新增，从core/converter.py迁移)
- **特点**: 纯工具函数，无状态，可被任何层调用

### 依赖关系

```
GUI Layer (gui/)
    ↓ 依赖
Coordinators Layer (coordinators/) + Workers Layer (workers/)
    ↓ 依赖
Services Layer (services/)
    ↓ 依赖
Models Layer (models/) + Business Core Layer (core/)
    ↓ 依赖
Infrastructure Layer (mdict/) + Utils Layer (utils/)
```

### 分层收益

- **可维护**: 流程变化只改协调器；算法/数据变化只改服务；样式变化只改样式层。职责清晰、改动局部化。
- **可测试**: 服务与协调器天然可单测（输入/输出与调用顺序可验证），减少集成测试压力。
- **可演化**: 新增功能优先判断"属于哪个协调器/服务"，避免逻辑分散到 UI；支持并行开发（UI 与业务解耦）。
- **可读性**: UI 代码可保持"薄壳"姿态，MainWindow 主要做装配与委托，规模可控。

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

- **单一职责**: 每个页面只负责一个功能领域
- **信号通信**: 页面通过信号与 MainWindow 通信，不直接访问服务
- **配置绑定**: 页面状态与配置系统双向绑定
- **类型注解**: 所有方法都有完整的类型注解

## 三、新增配置选项指南

### 3.1 在 SettingsService 中添加配置

1. **添加配置访问方法**
   ```python
   # 在 services/settings_service.py 中
   def get_new_option(self) -> str:
       return self.cm.get("new.option", "default")

   def set_new_option(self, value: str) -> None:
       self.cm.set("new.option", value)
   ```

2. **更新配置结构**
   ```toml
   # 在 config/default_config.toml 中
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
   # src/mdxscraper/services/new_service.py
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
   from mdxscraper.services.new_service import NewService

   # 创建服务实例
   self.new_service = NewService(project_root)
   ```

### 4.2 服务设计原则

- **无状态**: 服务不持有 UI 状态
- **类型安全**: 所有方法都有完整类型注解
- **错误处理**: 异常在服务层处理，通过返回值或信号传递
- **可测试**: 服务方法应该是纯函数或易于测试

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

- **可复用**: 组件应该可以在多个页面中使用
- **信号通信**: 组件通过信号与父组件通信
- **状态管理**: 组件管理自己的内部状态
- **API 设计**: 提供清晰的公共 API

## 六、新增工作线程指南

### 6.1 创建新工作线程

1. **创建工作线程文件**
   ```python
   # src/mdxscraper/workers/new_worker.py
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
   from mdxscraper.workers.new_worker import NewWorker

   def start_new_worker(self):
       self.new_worker = NewWorker(self.project_root, "data")
       self.new_worker.progress_sig.connect(self.command_panel.setProgress)
       self.new_worker.finished_sig.connect(self.on_new_finished)
       self.new_worker.error_sig.connect(self.on_new_error)
       self.new_worker.start()
   ```

### 6.2 工作线程设计原则

- **无 UI 依赖**: 线程不直接操作 UI 控件
- **信号通信**: 通过信号与主线程通信
- **可中断**: 支持 `requestInterruption()` 和 `isInterruptionRequested()`
- **错误处理**: 异常在线程内捕获，通过信号传递

## 七、新增协调器指南

### 7.1 创建新协调器

1. **创建协调器文件**
   ```python
   # src/mdxscraper/coordinators/new_coordinator.py
   from __future__ import annotations

   from pathlib import Path
   from mdxscraper.services.settings_service import SettingsService
   from mdxscraper.services.presets_service import PresetsService

   class NewCoordinator:
       def __init__(self, settings: SettingsService, presets: PresetsService):
           self.settings = settings
           self.presets = presets

       def handle_new_action(self, main_window) -> None:
           """处理新的业务流程"""
           # 协调多个服务完成复杂业务逻辑
           data = self.settings.get_new_option()
           result = self.presets.process_data(data)
           # 更新UI状态
           main_window.update_new_status(result)
   ```

2. **在 MainWindow 中集成**
   ```python
   # 在 main_window.py 的 __init__ 中
   from mdxscraper.coordinators.new_coordinator import NewCoordinator

   # 创建协调器实例
   self.new_coordinator = NewCoordinator(self.settings, self.presets)

   # 连接信号
   self.some_signal.connect(lambda: self.new_coordinator.handle_new_action(self))
   ```

### 7.2 协调器设计原则

- **流程编排**: 协调多个服务完成复杂业务流程
- **无UI依赖**: 不直接操作UI控件，通过参数传递UI引用
- **单一职责**: 每个协调器负责一个特定的业务流程
- **可测试**: 协调器逻辑应该易于单元测试

## 八、新增工具函数指南

### 8.1 创建新工具函数

1. **选择合适的工具文件**
   - `time_utils.py` - 时间相关工具
   - `system_utils.py` - 系统操作工具
   - `file_utils.py` - 文件操作工具
   - `path_utils.py` - 路径处理工具

2. **添加工具函数**
   ```python
   # 在 utils/time_utils.py 中
   def format_timestamp(timestamp: float) -> str:
       """格式化时间戳为可读字符串"""
       from datetime import datetime
       return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
   ```

3. **更新 __init__.py**
   ```python
   # 在 utils/__init__.py 中
   from .time_utils import format_timestamp

   __all__ = [
       # ... 其他工具函数
       "format_timestamp",
   ]
   ```

### 8.2 工具函数设计原则

- **纯函数**: 无副作用，输入确定输出确定
- **无状态**: 不持有任何状态
- **通用性**: 可以被任何层调用
- **类型注解**: 完整的类型注解

## 九、测试指南

> **📖 详细测试指南**: 请参考 [Testing_Guide.md](Testing_Guide.md) 获取完整的测试使用指南，包括如何运行测试、测试分类、开发工作流中的测试使用等详细内容。

### 9.1 测试概述

MdxScraper项目包含**231个测试**，覆盖了从核心算法到UI协调的完整功能栈。这些测试是项目的**质量保证基石**，为开发、重构和维护提供可靠的安全网。

### 9.2 快速开始

#### 运行所有测试
```bash
# 快速运行所有测试（推荐）
uv run pytest tests/ --tb=no -q

# 详细运行所有测试
uv run pytest tests/ -v
```

#### 运行特定功能测试
```bash
# 测试转换功能
uv run pytest tests/test_converter.py -v

# 测试配置功能
uv run pytest tests/test_settings_service.py -v

# 测试协调器功能
uv run pytest tests/test_*_coordinator.py -v
```

### 9.3 测试分类

- **核心功能测试**: 转换算法、字典查询、文件解析
- **服务层测试**: 配置管理、预设管理、导出服务
- **协调器测试**: 配置协调、预设协调、文件协调、转换协调
- **工具函数测试**: 路径处理、系统操作、时间处理、文件操作

### 9.4 开发工作流中的测试

#### 修改现有功能
```bash
# 1. 运行相关测试了解当前状态
uv run pytest tests/test_converter.py -v

# 2. 进行代码修改
# ... 你的修改 ...

# 3. 验证修改没有破坏功能
uv run pytest tests/test_converter.py -v

# 4. 运行所有测试确保整体稳定
uv run pytest tests/ --tb=short -q
```

#### 添加新功能
```bash
# 1. 确保基础功能正常
uv run pytest tests/ --tb=short -q

# 2. 添加新功能并编写测试
# ... 你的新功能和测试 ...

# 3. 验证新功能
uv run pytest tests/test_your_new_feature.py -v

# 4. 确保没有破坏现有功能
uv run pytest tests/ --tb=short -q
```

### 9.5 测试文件管理

#### 应该纳入Git的测试文件
```
tests/
├── test_*.py              # 所有测试文件 ✅
└── __init__.py           # 如果存在 ✅
```

#### 应该忽略的文件
```
tests/
├── __pycache__/          # Python缓存 ❌
├── .pytest_cache/       # pytest缓存 ❌
├── temp_*.py            # 临时测试文件 ❌
└── test_data/           # 大型测试数据 ❌
```

### 9.6 测试学习价值

测试文件是**活生生的API使用文档**，展示了：
- 如何正确使用各种功能
- 错误处理的最佳实践
- 项目架构的依赖关系
- 代码的预期行为

### 9.7 最佳实践

1. **每次修改后运行测试** - 确保功能正常
2. **将测试作为学习工具** - 通过测试代码理解项目
3. **为新功能编写测试** - 保持测试的完整性
4. **将测试文件纳入Git管理** - 它们是项目的重要组成部分

> **💡 提示**: 查看 [Testing_Guide.md](Testing_Guide.md) 获取更详细的测试使用指南，包括故障排除、性能优化、团队协作等内容。

## 十、代码规范

### 10.1 命名规范

- **类名**: PascalCase（如 `NewPage`、`NewService`）
- **方法名**: snake_case（如 `process_data`、`sync_from_config`）
- **信号名**: snake_case + `_sig` 后缀（如 `progress_sig`、`finished_sig`）
- **文件名**: snake_case（如 `new_page.py`、`new_service.py`）

### 10.2 类型注解

- **所有方法**: 必须有完整的类型注解
- **返回值**: 明确指定返回类型
- **参数**: 明确指定参数类型
- **导入**: 使用 `from __future__ import annotations`

### 10.3 文档规范

- **类文档**: 简要说明类的职责
- **方法文档**: 说明方法的功能、参数、返回值
- **复杂逻辑**: 添加行内注释

## 十一、常见模式

### 11.1 配置同步模式（经协调器统一）

```python
# 推荐做法：通过 ConfigCoordinator 统一同步

# MainWindow 初始化：
self.cfgc = ConfigCoordinator(self.settings, self.presets)

# 从配置同步到页面：
self.cfgc.sync_all_from_config(self)

# 页面变更时回写（示例：Image 页任一变更信号触发）：
self.tab_image.width_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
```

### 11.2 信号连接模式（委托协调器）

```python
# 页面信号连接 → 统一回写
self.page.option_changed.connect(lambda: self.cfgc.sync_all_to_config(self))

# 预设信号连接 → 交给 PresetCoordinator
self.preset_coordinator = PresetCoordinator(self.presets, self.settings)
self.tab_pdf.preset_changed.connect(lambda label: self.preset_coordinator.on_pdf_preset_changed(self, label))
self.tab_css.preset_changed.connect(lambda label: self.preset_coordinator.on_css_preset_changed(self, label))
self.tab_pdf.text_changed.connect(lambda: self.preset_coordinator.on_pdf_text_changed(self))
self.tab_css.text_changed.connect(lambda: self.preset_coordinator.on_css_text_changed(self))

# 运行 → 由 ConversionCoordinator 处理
self.convc = ConversionCoordinator(self.settings, self.presets, project_root, self.cm)
self.command_panel.scrapeRequested.connect(lambda: self.convc.run(self))
```

### 11.3 错误处理模式

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

### 11.4 预设加载与选择保留模式

目标：让下拉选择与编辑器内容始终保持一致；仅保存 `preset_label`，编辑器文本按需从文件加载；用户编辑进入 `* Untitled` 缓冲态，运行/导入/退出会自动落盘。

步骤：
- 启动/导入/恢复（只做两件事）
  1) `reload_presets(auto_select_default=False)`（只刷新下拉数据，不自动选默认）
  2) `cfgc.sync_all_from_config(self)`（根据配置里的 label 触发选择，实际加载由 on_*_preset_changed 完成）

- 选择变化（唯一入口）
  - `on_pdf_preset_changed/on_css_preset_changed` 读取所选文件文本 → 设置到编辑器 → 仅更新 `preset_label` → 取消脏态

- 用户编辑（进入 `* Untitled`）
  - `text_changed` → `_enter_untitled_state(kind, clear_editor=False)`：下拉 `index = -1`，显示 `* Untitled`，保留用户内容，不立即落盘

- 运行/退出/导入 前的自动保存
  - 调用 `preset_coordinator.autosave_untitled_if_needed(self)`：如处于脏态，直接写入 `data/configs/{css|pdf}/Untitled.toml`，并将 `preset_label` 设为 `Untitled`

- 导出（冻结 Untitled）
  - 通过 `cfgc.export_config(...)`：若 label 为 `Untitled` 或正处脏态，则生成时间戳快照并把导出配置指向该快照；随后 `reload_presets(False)` 并 `select_label_and_load(..., 新快照)`

最小代码骨架：
```python
# 初始化/导入/恢复
self.reload_presets(auto_select_default=False)
self.cfgc.sync_all_from_config(self)

# 选择变化（由协调器处理加载+去脏）
self.tab_pdf.preset_changed.connect(lambda label: self.preset_coordinator.on_pdf_preset_changed(self, label))
self.tab_css.preset_changed.connect(lambda label: self.preset_coordinator.on_css_preset_changed(self, label))

# 用户编辑（进入 * Untitled）
self.tab_pdf.text_changed.connect(lambda: self.preset_coordinator.on_pdf_text_changed(self))
self.tab_css.text_changed.connect(lambda: self.preset_coordinator.on_css_text_changed(self))

# 运行/退出/导入 前
self.preset_coordinator.autosave_untitled_if_needed(self)

# 导出（冻结 Untitled 并回选新快照）
self.cfgc.export_config(self, Path('.../config.toml'))
```

注意：
- 选择变化是唯一触发"加载编辑器内容"的入口；不要在其他地方重复加载
- `* Untitled` 是"无选中"显示态（`index == -1`），不同于名为 `Untitled` 的实际文件项
- 刷新预设仅刷新列表，不改变当前有效选择；需要改变时调用 `select_label_and_load(kind, label)`

## 十二、关键UI特性维护指南

### 12.1 可拖拽分割器布局

**核心架构**：
- 使用 `QSplitter(Qt.Vertical)` 实现垂直分割
- 三个区域：Tab区域（可拉伸）→ 按钮区域（固定）→ Log区域（可拉伸）
- 通过 `setStretchFactor()` 控制拉伸行为

**关键配置**：
```python
# 必须保持的配置
self.splitter.setStretchFactor(0, 1)     # Tab区域可拉伸
self.splitter.setStretchFactor(1, 0)     # 按钮区域固定
self.splitter.setStretchFactor(2, 1)     # Log区域可拉伸
self.splitter.setChildrenCollapsible(False)  # 防止折叠
self.splitter.splitterMoved.connect(self.on_splitter_moved)  # 动态保护
```

**保护机制**：
- 各区域最小高度：Tab(200px)、按钮(120px)、Log(150px)
- 动态调整：`on_splitter_moved()` 方法实时检查并调整
- 防止递归：调整时临时断开信号连接

**维护注意事项**：
1. **不要修改区域顺序**：Tab → 按钮 → Log 的顺序不可改变
2. **不要移除保护机制**：`setChildrenCollapsible(False)` 和 `splitterMoved` 信号必须保留
3. **不要改变按钮区域**：CommandPanel 必须保持固定高度120px
4. **新增区域时**：必须更新 `on_splitter_moved()` 中的最小尺寸数组
5. **测试极端拖拽**：确保任何区域都不会消失

### 12.2 实时进度条系统

**核心架构**：
- 进度信号：`ConversionWorker.progress_sig` 发送 (进度值, 状态文字)
- 进度回调：核心转换函数支持 `progress_callback` 参数
- 智能显示：进度条上显示状态文字或百分比

**关键组件**：
```python
# ConversionWorker 信号
progress_sig = Signal(int, str)  # 进度值, 状态文字

# 核心转换函数签名
def mdx2html(..., progress_callback: Optional[Callable[[int, str], None]] = None)
def mdx2pdf(..., progress_callback: Optional[Callable[[int, str], None]] = None)
def mdx2img(..., progress_callback: Optional[Callable[[int, str], None]] = None)
```

**进度阶段**：
- 5%: 加载字典和解析输入
- 10-70%: 处理课程（按课程数量动态计算）
- 75%: 合并CSS样式
- 85%: 嵌入图片
- 90%: 写入HTML文件
- 80-90%: PDF/图片转换
- 90-100%: 后处理（备份、保存无效词汇等）

**维护注意事项**：
1. **新增转换步骤时**：必须在相应位置添加进度更新
2. **修改转换流程时**：确保进度回调正确传递
3. **不要移除进度信号**：`progress_sig` 是UI反馈的关键
4. **保持进度比例**：确保进度值在0-100范围内
5. **测试长时间操作**：确保进度条平滑更新，不会卡住

### 12.3 组件分离原则

**CommandPanel**：
- 职责：按钮操作 + 进度条显示
- 固定高度：120px，不可拉伸
- 不包含：日志功能（已分离到LogPanel）

**LogPanel**：
- 职责：日志显示 + 日志操作
- 最小高度：150px，可拉伸
- 独立组件：可在其他项目中复用

**维护注意事项**：
1. **不要混合职责**：CommandPanel 和 LogPanel 功能不可合并
2. **保持组件独立**：LogPanel 应该可以在其他窗口中使用
3. **信号连接**：确保日志信号正确连接到 LogPanel
4. **不要修改高度**：CommandPanel 固定120px，LogPanel 最小150px

## 十三、最佳实践

1. **保持简单**：优先选择简单的解决方案
2. **单一职责**：每个类/方法只做一件事
3. **依赖注入**：通过构造函数注入依赖
4. **信号解耦**：使用信号/槽机制解耦组件
5. **类型安全**：充分利用类型注解
6. **错误处理**：在适当的层级处理错误
7. **测试覆盖**：为关键功能编写测试
8. **文档更新**：及时更新相关文档
9. **UI特性保护**：维护可拖拽布局和实时进度条
10. **组件分离**：保持CommandPanel和LogPanel的独立性
11. **分层原则**：严格遵循分层架构，不跨层调用
12. **工具函数复用**：优先使用utils层的工具函数

---

遵循这些指南，可以确保新增功能与现有架构保持一致，提高代码质量和可维护性。
