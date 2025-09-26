# MdxScraper GUI 开发指引

基于重构后的架构，为未来新增功能、配置选项、页面等提供规范化指南。

## 一、架构概览

### 目录结构（当前实现）
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
│   ├── command_panel.py    # 全局操作面板（按钮+进度条）
│   ├── log_panel.py        # 日志面板（独立组件）
│   ├── file_picker.py      # 文件选择器（基础版，可扩展过滤/策略）
│   └── progress_panel.py   # 进度面板（已实现，统一由协调器驱动）
├── services/               # 业务服务层
│   ├── settings_service.py # 配置管理服务
│   ├── presets_service.py  # 预设管理服务
│   └── export_service.py   # 导出服务
├── workers/                # 后台工作线程
│   └── conversion_worker.py # 转换工作线程
└── assets/                 # 资源文件
    └── app_icon.ico        # 应用图标
├── coordinators/           # 协调器层（统一编排）
│   ├── preset_coordinator.py      # 预设列表/选择/脏态/快照
│   ├── file_coordinator.py        # 文件对话框/路径建议/打开目录
│   ├── config_coordinator.py      # 同步/导入/导出/校验编排
│   └── conversion_coordinator.py  # 运行/进度/日志/中断编排
└── styles/                 # 样式与主题
    ├── theme_loader.py     # 主题加载与基础样式应用
    └── themes/
        ├── default.qss/.json
        └── dark.qss/.json
```

### 分层架构
- **UI 层（Pages + Components）**：只负责可视化与交互（布局、输入、按钮、进度显示、日志面板）。不直接进行文件 I/O、不读写配置树内细节、不跑耗时任务；以信号/槽向上游“表达意图”。
- **协调器层（Coordinators）**：负责“流程编排”和“信号整合”。把 UI 的意图转化为一系列服务调用与线程启动，并将线程信号（进度/日志/完成/错误）统一回传 UI。当前包含：
  - `PresetCoordinator`（预设列表/选择/编辑器加载/脏态/Untitled/快照）
  - `FileCoordinator`（文件选择、起始目录与命名建议、打开数据目录）
  - `ConfigCoordinator`（从配置拉取到页面、从页面回写到配置、导入/导出与校验）
  - `ConversionCoordinator`（运行/进度/日志/错误与中断编排）
- **服务层（Services）**：承载具体业务能力（配置 CRUD 与校验、预设 I/O 与解析、导出参数构建等）。不依赖 UI 控件与线程细节，接口稳定、易于测试与复用。
- **工作层（Workers）**：执行耗时任务（如转换流程），仅通过信号回报进度和日志；不直接操作任何 UI，不弹窗，支持中断请求。
- **样式与主题（Styles）**：通过 `ThemeLoader + QSS` 统一管理主题与基础样式，避免在代码中散落 `setStyleSheet`；支持多主题与按主题配置基础样式（如 Fusion）。

分层收益（为什么要这样做）：
- 可维护：流程变化只改协调器；算法/数据变化只改服务；样式变化只改样式层。职责清晰、改动局部化。
- 可测试：服务与协调器天然可单测（输入/输出与调用顺序可验证），减少集成测试压力。
- 可演化：新增功能优先判断“属于哪个协调器/服务”，避免逻辑分散到 UI；支持并行开发（UI 与业务解耦）。
- 可读性：UI 代码可保持“薄壳”姿态，MainWindow 主要做装配与委托，规模可控。

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

### 9.1 配置同步模式（经协调器统一）

```python
# 推荐做法：通过 ConfigCoordinator 统一同步

# MainWindow 初始化：
self.cfgc = ConfigCoordinator(self.settings, self.presets)

# 从配置同步到页面：
self.cfgc.sync_all_from_config(self)

# 页面变更时回写（示例：Image 页任一变更信号触发）：
self.tab_image.width_changed.connect(lambda: self.cfgc.sync_all_to_config(self))
```

### 9.2 信号连接模式（委托协调器）

```python
# 页面信号连接 → 统一回写
self.page.option_changed.connect(lambda: self.cfgc.sync_all_to_config(self))

# 预设信号连接 → 交给 PresetCoordinator
self.presetc = PresetCoordinator(self.presets, self.settings)
self.tab_pdf.preset_changed.connect(lambda label: self.presetc.on_pdf_preset_changed(self, label))
self.tab_css.preset_changed.connect(lambda label: self.presetc.on_css_preset_changed(self, label))
self.tab_pdf.text_changed.connect(lambda: self.presetc.on_pdf_text_changed(self))
self.tab_css.text_changed.connect(lambda: self.presetc.on_css_text_changed(self))

# 运行 → 由 ConversionCoordinator 处理
self.convc = ConversionCoordinator(self.settings, self.presets, project_root, self.cm)
self.command_panel.scrapeRequested.connect(lambda: self.convc.run(self))
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

### 9.4 预设加载与选择保留模式（一步一步，易于落地）

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
  - 调用 `presetc.autosave_untitled_if_needed(self)`：如处于脏态，直接写入 `data/configs/{css|pdf}/Untitled.toml`，并将 `preset_label` 设为 `Untitled`

- 导出（冻结 Untitled）
  - 通过 `cfgc.export_config(...)`：若 label 为 `Untitled` 或正处脏态，则生成时间戳快照并把导出配置指向该快照；随后 `reload_presets(False)` 并 `select_label_and_load(..., 新快照)`

最小代码骨架：
```python
# 初始化/导入/恢复
self.reload_presets(auto_select_default=False)
self.cfgc.sync_all_from_config(self)

# 选择变化（由协调器处理加载+去脏）
self.tab_pdf.preset_changed.connect(lambda label: self.presetc.on_pdf_preset_changed(self, label))
self.tab_css.preset_changed.connect(lambda label: self.presetc.on_css_preset_changed(self, label))

# 用户编辑（进入 * Untitled）
self.tab_pdf.text_changed.connect(lambda: self.presetc.on_pdf_text_changed(self))
self.tab_css.text_changed.connect(lambda: self.presetc.on_css_text_changed(self))

# 运行/退出/导入 前
self.presetc.autosave_untitled_if_needed(self)

# 导出（冻结 Untitled 并回选新快照）
self.cfgc.export_config(self, Path('.../config.toml'))
```

注意：
- 选择变化是唯一触发“加载编辑器内容”的入口；不要在其他地方重复加载
- `* Untitled` 是“无选中”显示态（`index == -1`），不同于名为 `Untitled` 的实际文件项
- 刷新预设仅刷新列表，不改变当前有效选择；需要改变时调用 `select_label_and_load(kind, label)`

## 十、关键UI特性维护指南

### 10.1 可拖拽分割器布局

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

### 10.2 实时进度条系统

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

### 10.3 组件分离原则

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

## 十一、最佳实践

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

---

遵循这些指南，可以确保新增功能与现有架构保持一致，提高代码质量和可维护性。
