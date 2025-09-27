# 架构重构计划：正确的分层设计

## 问题分析

当前架构存在严重的分层混乱问题：

### 现状问题
1. **职责混乱**: `gui/` 目录下包含了大量非UI逻辑
2. **分层不清**: Services、Coordinators、Workers 这些业务逻辑层被错误地放在了 GUI 层
3. **依赖倒置**: 业务逻辑层依赖了 GUI 层，违反了分层架构原则

### 当前 `gui/` 目录下的非UI内容
- **Services**: `settings_service.py`, `presets_service.py`, `export_service.py` - 业务服务层
- **Coordinators**: `config_coordinator.py`, `preset_coordinator.py`, `file_coordinator.py`, `conversion_coordinator.py` - 应用协调层
- **Workers**: `conversion_worker.py` - 后台任务层
- **Models**: `config_models.py` - 数据模型层

## 重新设计的架构

### 目标目录结构
```
src/mdxscraper/
├── __init__.py
├── __main__.py
├── config/                    # 配置层
│   ├── __init__.py
│   ├── config_manager.py
│   ├── default_config.toml
│   ├── css_styles/
│   └── pdf_options/
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
│   ├── config_models.py       # 从 gui/models/ 迁移
│   └── preset_models.py       # 新增
├── services/                  # 业务服务层
│   ├── __init__.py
│   ├── settings_service.py    # 从 gui/services/ 迁移
│   ├── presets_service.py     # 从 gui/services/ 迁移
│   └── export_service.py      # 从 gui/services/ 迁移
├── coordinators/              # 应用协调层
│   ├── __init__.py
│   ├── config_coordinator.py  # 从 gui/coordinators/ 迁移
│   ├── preset_coordinator.py  # 从 gui/coordinators/ 迁移
│   ├── file_coordinator.py    # 从 gui/coordinators/ 迁移
│   └── conversion_coordinator.py # 从 gui/coordinators/ 迁移
├── workers/                   # 执行层 (UI交互的执行器)
│   ├── __init__.py
│   └── conversion_worker.py   # 从 gui/workers/ 迁移
├── gui/                       # 纯UI层
│   ├── __init__.py
│   ├── main_window.py
│   ├── config_dialog.py
│   ├── components/            # UI组件
│   │   ├── __init__.py
│   │   ├── command_panel.py
│   │   ├── file_picker.py
│   │   ├── log_panel.py
│   │   └── progress_panel.py
│   ├── pages/                 # UI页面
│   │   ├── __init__.py
│   │   ├── basic_page.py
│   │   ├── image_page.py
│   │   ├── pdf_page.py
│   │   ├── css_page.py
│   │   ├── advanced_page.py
│   │   └── about_page.py
│   ├── styles/                # UI样式
│   │   ├── __init__.py
│   │   ├── theme_loader.py
│   │   └── themes/
│   └── assets/                # UI资源
│       ├── app_icon.ico
│       └── app_icon.gfie
└── utils/                     # 工具层
    ├── __init__.py
    ├── path_utils.py          # 路径和系统工具
    ├── system_utils.py        # 系统操作工具
    └── time_utils.py          # 时间处理工具
```

## 重新定义的分层职责

### 1. 核心基础设施层 (`mdict/`) - **真正的核心**
- **职责**: 提供MDX文件处理的基础能力，整个程序存在的前提
- **内容**:
  - `mdict_query.py` - 第三方库包装器，提供稳定的API接口
  - `vendor/` - 完整的第三方 mdict-query 库
- **特点**: 外部依赖，提供最底层的基础设施，整个程序的核心

### 2. 业务核心层 (`core/`) - **基于基础设施的业务算法**
- **职责**: 基于mdict基础设施，提供业务相关的核心算法
- **内容**:
  - `converter.py` - 转换算法 (mdx2html, mdx2pdf, mdx2img)
  - `dictionary.py` - 字典查询封装和回退策略
  - `parser.py` - 文件解析算法 (支持多种格式)
  - `renderer.py` - HTML渲染算法 (CSS合并、图片嵌入)
- **特点**: 纯算法实现，依赖mdict层，无UI依赖，高度可测试

### 3. 数据模型层 (`models/`)
- **职责**: 定义数据结构、数据验证、数据转换
- **内容**: 
  - `config_models.py` - 配置数据模型
  - `preset_models.py` - 预设数据模型
- **特点**: 纯数据类，无业务逻辑，无UI依赖

### 4. 业务服务层 (`services/`)
- **职责**: 封装业务逻辑，提供业务API，调用业务核心层
- **内容**:
  - `settings_service.py` - 配置管理服务 (包含配置验证)
  - `presets_service.py` - 预设管理服务
  - `export_service.py` - 导出服务 (调用core.converter)
- **特点**: 纯业务逻辑，依赖业务核心层，无UI依赖，可独立测试

### 5. 应用协调层 (`coordinators/`)
- **职责**: 协调多个服务，处理复杂的业务流程
- **内容**:
  - `config_coordinator.py` - 配置协调
  - `preset_coordinator.py` - 预设协调
  - `file_coordinator.py` - 文件操作协调
  - `conversion_coordinator.py` - 转换协调
- **特点**: 依赖服务层，协调业务流程，无UI依赖

### 6. 执行层 (`workers/`) - **UI交互的执行器**
- **职责**: 在后台线程中执行耗时任务，提供UI交互能力
- **内容**:
  - `conversion_worker.py` - 转换执行器 (调用core层 + UI进度报告)
- **特点**: 继承QThread，调用业务核心层，通过信号与UI通信

### 7. UI层 (`gui/`)
- **职责**: 用户界面展示和交互
- **内容**:
  - `main_window.py` - 主窗口
  - `components/` - UI组件
  - `pages/` - UI页面
  - `styles/` - UI样式
- **特点**: 纯UI逻辑，依赖协调器层和执行层

### 8. 工具层 (`utils/`)
- **职责**: 提供通用工具函数，系统检测，路径处理，时间处理
- **内容**:
  - `path_utils.py` - 路径处理和wkhtmltopdf检测 (已存在，包含OS检测)
  - `system_utils.py` - 系统操作工具 (新增，从file_coordinator.py迁移)
  - `time_utils.py` - 时间处理工具 (新增，从core/converter.py迁移)
- **特点**: 纯工具函数，无状态，可被任何层调用

## 重新设计的依赖关系

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

### 详细依赖说明
- **GUI层**: 依赖协调器层和执行层，不直接调用服务或核心算法
- **协调器层**: 依赖服务层，协调多个服务完成复杂业务流程
- **执行层**: 依赖业务核心层，在后台线程中执行任务并提供UI交互
- **服务层**: 依赖模型层和业务核心层，封装业务逻辑
- **模型层**: 纯数据结构，无依赖
- **业务核心层**: 依赖基础设施层和工具层，提供业务算法
- **工具层**: 纯工具函数，无依赖，可被任何层调用
- **基础设施层**: 外部依赖，提供MDX文件处理的基础能力

## 关于重新设计架构的说明

### 为什么 `mdict/` 是真正的核心基础设施层？

1. **程序存在的前提**: 没有 `mdict/` 提供的 MDX 处理能力，整个程序就无法工作
   - `mdict_query.py`: 第三方库的包装器，提供稳定的API接口
   - `vendor/`: 完整的第三方 `mdict-query` 库，包含所有依赖文件

2. **最底层的基础设施**: 其他所有功能都依赖它
   - 提供MDX文件处理的基础能力
   - 可以被业务核心层调用
   - 独立于我们的业务逻辑

3. **基础设施与业务分离**:
   - **基础设施层** (`mdict/`): 提供MDX文件处理的基础能力
   - **业务核心层** (`core/`): 基于基础设施实现业务算法
   - **业务服务层** (`services/`): 封装业务逻辑，调用业务核心层

### 为什么 `core/` 是业务核心层？

1. **基于基础设施的业务算法**: `core/` 目录包含的是**基于mdict的业务算法**
   - `converter.py`: 转换算法 (mdx2html, mdx2pdf, mdx2img)
   - `dictionary.py`: 字典查询封装和回退策略
   - `parser.py`: 文件解析算法
   - `renderer.py`: HTML渲染算法

2. **纯算法特性**: 这些是**无状态、无副作用**的纯函数
   - 输入确定，输出确定
   - 依赖基础设施层，但不依赖UI
   - 高度可测试
   - 可以被服务层和执行层调用

3. **业务核心与执行分离**:
   - **业务核心层** (`core/`): 提供业务算法
   - **执行层** (`workers/`): 调用业务核心层 + 提供UI交互
   - **服务层** (`services/`): 封装业务逻辑，调用业务核心层

### 为什么 `workers/` 是执行层？

1. **UI交互的执行器**: `workers/` 目录包含的是**带UI交互的执行器**
   - `conversion_worker.py`: 转换执行器 (调用core层 + UI进度报告)

2. **执行特性**: 这些是**有状态、有UI交互**的执行器
   - 继承QThread，在后台线程中执行
   - 调用业务核心层完成实际工作
   - 通过信号与UI通信，提供进度报告
   - 处理错误和异常

3. **执行与业务分离**:
   - **业务核心层** (`core/`): 提供纯算法
   - **执行层** (`workers/`): 调用算法 + 提供UI交互
   - **协调层** (`coordinators/`): 协调执行流程

### 各层级的区别

| 层级 | 职责 | 特点 | 示例 |
|------|------|------|------|
| **mdict/** | 基础设施 | 外部依赖、MDX处理基础能力 | `IndexBuilder` |
| **core/** | 业务核心 | 基于基础设施的业务算法、纯函数 | `mdx2html()`, `parse_file()` |
| **utils/** | 通用工具 | 跨层通用、系统级、无业务逻辑 | `detect_wkhtmltopdf_path()`, `validate_path()` |
| **services/** | 业务服务 | 有状态、业务规则、配置管理 | `ExportService.execute_export()` |
| **workers/** | 执行层 | UI交互的执行器、后台线程 | `ConversionWorker.run()` |

### 调用关系示例

```python
# services/export_service.py (业务服务层)
def execute_export(self, input_file, mdx_file, output_path, ...):
    # 业务逻辑：参数验证、配置构建
    suffix = output_path.suffix.lower()
    h1_style, scrap_style, additional_styles = self.parse_css_styles(css_text)
    
    # 调用业务核心算法
    if suffix == '.html':
        return mdx2html(mdx_file, input_file, output_path, ...)  # 来自 core/
    elif suffix == '.pdf':
        pdf_options = self.build_pdf_options(pdf_text)
        return mdx2pdf(mdx_file, input_file, output_path, pdf_options, ...)  # 来自 core/

# core/converter.py (业务核心层)
def mdx2pdf(mdx_file, input_file, output_file, pdf_options, ...):
    # 使用基础设施层处理MDX
    dictionary = Dictionary(mdx_file)  # 来自 core/dictionary.py
    lessons = WordParser(str(input_file)).parse()  # 来自 core/parser.py
    
    # 使用工具层进行时间格式化
    duration_str = human_readable_duration(duration)  # 来自 utils/time_utils.py
    
    # 业务核心算法...

# workers/conversion_worker.py (执行层)
def run(self):
    # 调用业务服务层
    found, not_found, invalid_words = self._export_service.execute_export(...)  # 来自 services/
    
    # 通过信号与UI通信
    self.progress_sig.emit(100, "Conversion completed!")
    self.finished_sig.emit("Done!")
```

### 工具层使用示例

```python
# coordinators/file_coordinator.py (协调层)
def choose_output(self, mw):
    # 使用工具函数获取默认路径
    start_dir = self.settings.get_start_dir('output')  # 业务逻辑
    default_filename = self.settings.suggest_output_filename(input_path)  # 业务逻辑
    
    # 使用工具函数处理文件对话框
    file, _ = QFileDialog.getSaveFileName(...)  # UI工具

# services/export_service.py (业务服务层)
def execute_export(self, input_file, mdx_file, output_path, ...):
    # 使用工具函数验证系统依赖
    is_valid, error = validate_wkhtmltopdf_for_pdf_conversion(path)  # 来自 utils/
    if not is_valid:
        raise RuntimeError(error)
    
    # 使用工具函数获取配置路径
    config_path = get_wkhtmltopdf_path(wkhtmltopdf_path)  # 来自 utils/
    
    # 调用业务核心层
    return mdx2pdf(mdx_file, input_file, output_path, pdf_options, ...)  # 来自 core/

# workers/conversion_worker.py (执行层)
def run(self):
    start_time = time.time()
    # ... 转换逻辑 ...
    end_time = time.time()
    duration = end_time - start_time
    
    # 使用工具函数格式化时间
    duration_str = human_readable_duration(duration)  # 来自 utils/time_utils.py
    self.log_sig.emit(f"⏱️ The entire process took a total of {duration_str}.")
```

### 函数迁移示例

**迁移前** (`core/converter.py`):
```python
def human_readable_duration(seconds: float) -> str:
    # 时间格式化逻辑...
    return ''.join(parts)
```

**迁移后** (`utils/time_utils.py`):
```python
from datetime import timedelta

def human_readable_duration(seconds: float) -> str:
    """Convert seconds to human readable duration string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Human readable duration string (e.g., "01h 23m 45.123s")
    """
    time_delta = timedelta(seconds=seconds)
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes, int_seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(hours) * 3600 - int(minutes) * 60 - int(int_seconds)) * 1000)

    parts: list[str] = []
    if int(hours) > 0:
        parts.append(f'{int(hours):02d}h')
    if int(minutes) > 0 or int(hours) > 0:
        parts.append(f'{int(minutes):02d}m')
    parts.append(f'{int(int_seconds):02d}.{milliseconds:03d}s')

    return ' '.join(parts)
```

**导入更新**:
```python
# 迁移前
from mdxscraper.core.converter import human_readable_duration

# 迁移后  
from mdxscraper.utils.time_utils import human_readable_duration
```

### 系统工具迁移示例

**迁移前** (`gui/coordinators/file_coordinator.py`):
```python
def open_user_data_dir(self, mw):
    # ... 其他逻辑 ...
    import platform, subprocess, os
    system = platform.system()
    if system == 'Windows':
        os.startfile(str(target))
    elif system == 'Darwin':
        subprocess.Popen(['open', str(target)])
    else:
        subprocess.Popen(['xdg-open', str(target)])
```

**迁移后** (`utils/system_utils.py`):
```python
import platform
import subprocess
import os
from pathlib import Path

def open_file_or_directory(path: Path) -> None:
    """Open file or directory using system default application.
    
    Args:
        path: Path to file or directory to open
    """
    system = platform.system()
    if system == 'Windows':
        os.startfile(str(path))
    elif system == 'Darwin':
        subprocess.Popen(['open', str(path)])
    else:
        subprocess.Popen(['xdg-open', str(path)])
```

**更新后的调用**:
```python
# coordinators/file_coordinator.py
from mdxscraper.utils.system_utils import open_file_or_directory

def open_user_data_dir(self, mw):
    # ... 其他逻辑 ...
    open_file_or_directory(target)
```

## 迁移步骤

### 阶段1: 创建新目录结构
1. 创建 `models/`, `services/`, `coordinators/`, `workers/` 目录
2. 创建相应的 `__init__.py` 文件

### 阶段2: 迁移数据模型
1. 将 `gui/models/config_models.py` → `models/config_models.py`
2. 创建 `models/preset_models.py`
3. 更新所有导入路径

### 阶段3: 迁移业务服务
1. 将 `gui/services/settings_service.py` → `services/settings_service.py`
2. 将 `gui/services/presets_service.py` → `services/presets_service.py`
3. 将 `gui/services/export_service.py` → `services/export_service.py`
4. 更新所有导入路径

### 阶段4: 迁移协调器
1. 将 `gui/coordinators/config_coordinator.py` → `coordinators/config_coordinator.py`
2. 将 `gui/coordinators/preset_coordinator.py` → `coordinators/preset_coordinator.py`
3. 将 `gui/coordinators/file_coordinator.py` → `coordinators/file_coordinator.py`
4. 将 `gui/coordinators/conversion_coordinator.py` → `coordinators/conversion_coordinator.py`
5. 更新所有导入路径

### 阶段5: 迁移工作线程
1. 将 `gui/workers/conversion_worker.py` → `workers/conversion_worker.py`
2. 更新所有导入路径

### 阶段6: 清理GUI目录
1. 删除 `gui/models/`, `gui/services/`, `gui/coordinators/`, `gui/workers/` 目录
2. 更新 `gui/main_window.py` 中的导入路径

### 阶段7: 迁移时间工具
1. 创建 `utils/time_utils.py` 文件
2. 将 `core/converter.py` 中的 `human_readable_duration` 函数迁移到 `utils/time_utils.py`
3. 更新所有调用 `human_readable_duration` 的地方的导入路径
4. 测试时间格式化功能

### 阶段8: 迁移系统工具
1. 创建 `utils/system_utils.py` 文件
2. 将 `file_coordinator.py` 中的跨平台文件打开逻辑迁移到 `utils/system_utils.py`
3. 更新所有调用文件打开逻辑的地方的导入路径
4. 测试跨平台文件打开功能

### 阶段9: 最终清理
1. 检查 `write_invalid_words_file` 函数是否也应该迁移到 `utils/`
2. 清理未使用的导入
3. 检查是否有其他可以迁移到工具层的函数

### 阶段10: 测试和验证
1. **功能测试**:
   - 运行所有现有测试确保功能正常
   - 测试转换功能 (HTML, PDF, Image)
   - 测试配置管理功能
   - 测试预设管理功能
2. **导入路径验证**:
   - 检查所有导入路径是否正确
   - 确保没有循环导入
   - 验证相对导入和绝对导入
3. **架构验证**:
   - 验证分层依赖关系
   - 检查是否有违反分层原则的调用
   - 确认工具层可以被任何层调用
4. **性能测试**:
   - 确保迁移后性能没有下降
   - 测试内存使用情况

## 优势

1. **清晰的分层**: 每层职责明确，依赖关系清晰
2. **基础设施与业务分离**: 基础设施层可独立更新，业务核心层可独立演化
3. **业务与执行分离**: 业务算法可复用，执行器可独立测试
4. **可测试性**: 各层都可以独立测试，基础设施层和业务核心层测试最简单
5. **可维护性**: 修改UI不影响业务逻辑，修改业务逻辑不影响基础设施
6. **可扩展性**: 可以轻松添加新的服务、协调器、执行器或UI组件
7. **符合架构原则**: 遵循分层架构和依赖倒置原则

## 风险控制

1. **渐进式迁移**: 分阶段进行，每阶段完成后测试
2. **保持功能**: 迁移过程中确保所有功能正常工作
3. **回滚准备**: 每个阶段都可以回滚到上一个状态
4. **测试覆盖**: 迁移前后运行完整的测试套件
5. **依赖关系验证**: 确保不违反分层原则，避免循环依赖

### 回滚策略
- **阶段1-5**: 如果出现问题，删除新创建的目录，恢复原文件
- **阶段6**: 如果GUI目录清理出现问题，从git恢复被删除的目录
- **阶段7-9**: 如果工具迁移出现问题，恢复原函数，删除新创建的工具文件
- **阶段10**: 如果测试失败，回滚到阶段9，重新检查问题

## 迁移注意事项

### 1. 依赖关系检查
迁移完成后，需要验证：
- 没有循环依赖
- 每层只依赖其下层
- 工具层可以被任何层调用

### 2. 测试策略
- 每层独立测试
- 集成测试验证层间调用
- 端到端测试验证完整流程

## 实施前检查清单

### 环境准备
- [ ] 确保所有现有测试通过
- [ ] 创建当前代码的完整备份
- [ ] 确保git工作区干净，没有未提交的更改
- [ ] 记录当前代码的git commit hash

### 依赖检查
- [ ] 确认所有依赖包已安装
- [ ] 检查是否有外部依赖需要更新
- [ ] 验证当前代码可以正常运行

### 工具准备
- [ ] 准备代码编辑器/IDE
- [ ] 确保有足够的磁盘空间
- [ ] 准备测试数据

这个重构将显著提升代码的架构质量和可维护性。
