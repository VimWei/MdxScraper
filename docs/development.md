# MdxScraper 现代化重构开发指南

## 项目概述

MdxScraper 是一个用于从 MDX 字典中提取特定词汇并生成 HTML、PDF 或 JPG 文件的工具。本项目旨在将现有的单文件脚本重构为现代化的 Python 项目结构，提供更好的可维护性、扩展性和用户体验。

## 重构目标

1. **代码模块化**：将 388 行的单文件拆分为逻辑清晰的模块
2. **现代化架构**：采用现代 Python 项目结构和最佳实践
3. **GUI 界面**：提供用户友好的图形界面
4. **便携式设计**：保持程序的便携性，用户数据与程序同目录
5. **配置管理**：智能的配置管理系统
6. **测试覆盖**：完整的测试体系

## 项目结构设计

```
MdxScraper/
├── MdxScraper.py                    # 主程序入口
├── MdxScraper.vbs                   # Windows 启动脚本
├── pyproject.toml                   # uv 依赖配置
├── uv.lock
├── README.md
├── .gitignore
├── docs/                            # 开发文档
│   ├── README.md                    # 文档首页
│   ├── development.md               # 开发指南（本文件）
│   ├── api/                         # API 文档
│   │   ├── core.md
│   │   ├── utils.md
│   │   └── config.md
│   ├── user_guide/                  # 用户指南
│   │   └── troubleshooting.md
│   └── changelog.md                 # 更新日志
├── tests/                           # 测试代码
│   ├── __init__.py
│   ├── conftest.py                  # pytest 配置
│   ├── test_core/                   # 核心功能测试
│   │   ├── __init__.py
│   │   ├── test_dictionary.py
│   │   ├── test_parser.py
│   │   ├── test_converter.py
│   │   └── test_renderer.py
│   ├── test_utils/                  # 工具函数测试
│   │   ├── __init__.py
│   │   ├── test_file_utils.py
│   │   └── test_config_manager.py
│   ├── test_gui/                    # GUI 测试
│   │   ├── __init__.py
│   │   └── test_main_window.py
│   └── fixtures/                    # 测试数据
│       ├── sample_words.txt
│       ├── test_config.toml
│       └── sample_mdx/
├── src/                             # 源代码
│   └── mdxscraper/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   ├── default_config.toml  # 默认配置
│       │   └── config_manager.py    # 配置管理
│       ├── core/                    # 核心功能模块
│       │   ├── __init__.py
│       │   ├── dictionary.py        # 词典处理
│       │   ├── parser.py           # 文件解析
│       │   ├── converter.py        # 格式转换
│       │   └── renderer.py         # 渲染引擎
│       ├── utils/                   # 工具函数
│       │   ├── __init__.py
│       │   ├── file_utils.py       # 文件操作
│       │   └── gui_utils.py        # GUI 工具
│       ├── mdict/                   # 内置 mdict-query
│       │   ├── __init__.py
│       │   ├── mdict_query.py
│       │   ├── readmdict.py
│       │   └── ...                  # 其他 mdict-query 文件
│       └── gui/                     # GUI 界面
│           ├── __init__.py
│           ├── main_window.py
│           └── config_dialog.py
└── data/                            # 用户数据
    ├── configs/                     # 配置文件目录
    │   ├── config_latest.toml      # 用户当前配置
    │   ├── english_basic.toml      # 配置方案
    │   └── ...
    ├── input/
    ├── mdict/
    └── output/
```

## 核心模块设计

### 1. 配置管理模块 (`src/mdxscraper/config/`)

**职责**：
- 管理默认配置和用户配置
- 提供配置方案的保存和加载功能
- 处理配置文件的读写操作

**主要类**：
- `ConfigManager`: 配置管理器，负责所有配置相关操作

**配置层次**：
1. **默认配置** (`default_config.toml`): 程序内部，版本控制
2. **用户当前配置** (`data/configs/config_latest.toml`): 用户最近使用的配置
3. **配置方案** (`data/configs/*.toml`): 用户保存的配置方案

### 2. 核心功能模块 (`src/mdxscraper/core/`)

**dictionary.py** - 词典处理
- 封装 mdict-query 功能
- 提供统一的词典查询接口
- 处理词典缓存和性能优化

**parser.py** - 文件解析
- 统一的文件格式解析接口
- 支持 txt、json、xlsx 等格式
- 编码自动检测

**converter.py** - 格式转换
- 实现不同输出格式的转换
- HTML、PDF、JPG 转换逻辑
- 模板引擎支持

**renderer.py** - 渲染引擎
- HTML/CSS 处理优化
- 图片内嵌和优化
- 样式处理

### 3. 工具函数模块 (`src/mdxscraper/utils/`)

**file_utils.py** - 文件操作
- 文件编码检测
- 文件读写操作
- 路径处理

**gui_utils.py** - GUI 工具
- GUI 相关的工具函数
- 样式和主题管理
- 用户界面辅助功能

### 4. GUI 界面模块 (`src/mdxscraper/gui/`)

**main_window.py** - 主窗口
- 程序主界面
- 用户交互逻辑
- 工作流程控制

**config_dialog.py** - 配置对话框
- 配置编辑界面
- 配置方案管理
- 设置保存和加载

## 技术栈选择

### 核心依赖
- **tomllib (读) + tomli_w (写)**: 配置文件处理（Python 3.11+ 内置 tomllib 读取；写入用 tomli_w）
- **BeautifulSoup4 + lxml**: HTML 解析和处理
- **openpyxl**: Excel 文件处理
- **chardet**: 文件编码检测
- **imgkit + pdfkit**: 图片和 PDF 生成

### 计划中的依赖
- **PySide6**: GUI 框架，提供现代化的用户界面（实施阶段添加）

### 开发工具
- **uv**: 包管理和虚拟环境
- **pytest**: 测试框架
- **black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查
- **pre-commit**: Git 钩子

## 重构实施计划

### 第一阶段：项目结构搭建
1. 创建新的目录结构
2. 设置 pyproject.toml 和开发环境
3. 移动现有文件到新结构
4. 确保基本功能正常运行

### 第二阶段：配置文件重构
1. **分离程序逻辑和配置**
   - 将 `InvalidAction` 枚举移到 `src/mdxscraper/core/enums.py`
   - 创建配置管理器 `src/mdxscraper/config/config_manager.py`
   - 实现 TOML 配置读写

2. **简化配置结构**
   - 输入文件直接指定完整路径
   - 词典文件直接指定完整路径
   - 输出文件直接指定完整路径

3. **实现智能检测**
   - 动态词典发现
   - 自动路径检测
   - 系统兼容性处理

4. **创建预设方案**
   - PDF 选项预设
   - CSS 样式预设
   - 配置方案管理

#### GUI 对接注意事项（第二阶段落地项）
- 配置Schema稳定：键名固定、类型明确、默认值完备；枚举以字符串表示（如 invalid_action="collect_warning"）。
- 统一API：实现 `ConfigManager`（load/get/set/save/list_schemes/apply_scheme/validate/backup）。GUI 仅依赖该层。
- 字段级接口：提供 `get_input_file()/set_input_file(path)` 等，避免 GUI 直接操作原始字典。
- 目录约定：程序预设放 `src/mdxscraper/presets/`；用户配置放 `data/configs/`（扁平：`config_latest.toml` + 方案文件）。
- 路径策略：对外存相对路径（相对程序/数据根），内部解析为绝对路径，保证便携迁移。
- 输出格式：从 `output.file` 后缀自动推断（不再单独存 format）。
- 兼容迁移：提供 `settings.py → TOML` 一次性迁移函数；在配置中加入 `config_version` 便于后续 schema 升级。
- 校验与提示：`validate()` 返回结构化错误（字段/类型/建议）；含路径可用性（存在/可写/权限）与 wkhtmltopdf 探测。
- wkhtmltopdf：支持 "auto" + 各平台候选路径 + PATH 探测，允许用户覆盖为绝对路径。
- 原子写入与备份：`.tmp` 写入后替换；提供 `backup_*`；避免 GUI 与后台并发写（文件锁/互斥）。
- 预设可枚举：可列出 `presets/` 中 PDF/CSS 预设，GUI 下拉直接使用；高级项仅保存“预设名称”，具体合并由程序完成。
- 平台与i18n：键名/值用英文；GUI 层做多语言映射。
- 性能与线程：配置读写轻；字典扫描/导出提供可选异步版本（GUI 通过 signal/slot 不阻塞主线程）。
- 文档与测试：补充字段说明、默认值、错误码；单测覆盖 load/save/validate/apply_scheme/atomic write/路径解析。

### 第三阶段：代码模块化
1. 将 MdxScraper.py 拆分为核心模块
2. 重构文件处理逻辑
3. 添加类型注解
4. 实现配置迁移工具

### 第四阶段：GUI 界面开发
1. 设计主窗口界面
2. 实现配置管理界面
3. 集成核心功能到 GUI
4. 优化用户体验

### 第五阶段：测试和文档
1. 编写单元测试
2. 添加集成测试
3. 完善 API 文档
4. 编写用户指南

### 第六阶段：优化和发布
1. 性能优化
2. 错误处理完善
3. 用户体验优化
4. 发布准备

## 配置文件重构详情

详细的配置文件重构设计请参考：[配置文件重构设计](development_config_refactor.md)

## 配置管理设计

### 目录结构
```
data/                               # 用户数据目录（可删除）
├── configs/
│   ├── config_latest.toml          # 用户当前配置
│   ├── my_english_study.toml       # 用户保存的配置方案
│   ├── chinese_learning.toml
│   └── work_documents.toml
├── input/                          # 用户输入文件
├── output/                         # 用户输出文件
└── mdict/                          # 用户词典文件

src/mdxscraper/presets/             # 程序预设方案（不可删除）
├── pdf_options/
└── css_styles/
```

### 配置管理逻辑

- **当前配置**：`config_latest.toml`（程序退出时保存，下次启动时加载）
- **配置方案**：其他 `.toml` 文件（用户保存的命名方案）
- **方案切换**：用户选择方案 → 程序使用 → 程序退出时保存到 `config_latest.toml`

### 配置文件结构

```toml
# 主配置文件示例
[input]
file = "data/input/words_to_lookup.txt"

[dictionary]
file = "data/mdict/English/Collins COBUILD 8th/Collins COBUILD 8th.mdx"

[output]
file = "data/output/lookup_results.html"  # 格式从文件扩展名自动推断
with_toc = true

[processing]
invalid_action = "collect_warning"
parallel = true
max_workers = 4

[advanced]
wkhtmltopdf_path = "auto"  # "auto" 表示自动检测
```

### 预设方案结构

```
data/configs/presets/
├── pdf_options/
│   ├── default.toml
│   ├── high_quality.toml
│   └── compact.toml
└── css_styles/
    ├── modern.toml
    ├── classic.toml
    └── minimal.toml
```

### 配置管理流程

1. **首次使用**：
   - 程序自动检测词典文件
   - 创建默认配置
   - 智能检测系统路径

2. **日常使用**：
   - 加载用户当前配置
   - 验证配置有效性
   - 自动修复常见问题

3. **配置修改**：
   - 通过 GUI 界面修改（未来）
   - 直接编辑配置文件
   - 使用预设方案

4. **方案管理**：
   - 保存当前配置为方案
   - 快速切换不同方案
   - 导入导出配置方案

## 启动方式设计

### 用户使用流程

**首次使用**：
```bash
# 1. 克隆或下载项目
git clone https://github.com/your-repo/MdxScraper
cd MdxScraper

# 2. 安装依赖
uv sync

# 3. 运行程序
# Windows: 双击 MdxScraper.vbs
# Linux/macOS: ./start.sh 或 uv run python MdxScraper.py
```

**后续使用**：
- Windows: 直接双击 `MdxScraper.vbs`
- 其他平台: `uv run python MdxScraper.py`

### 启动脚本

**MdxScraper.vbs** (Windows):
```vbs
Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' 获取脚本所在目录
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' 切换到脚本目录
objShell.CurrentDirectory = strScriptPath

' 运行 uv 命令
objShell.Run "uv run python MdxScraper.py", 1, True
```

## 测试策略

### 测试类型
1. **单元测试**：测试各个模块的独立功能
2. **集成测试**：测试模块间的协作
3. **GUI 测试**：测试用户界面功能
4. **端到端测试**：测试完整的用户工作流

### 测试覆盖
- 核心功能模块：100% 覆盖
- 工具函数：100% 覆盖
- GUI 组件：主要功能覆盖
- 配置管理：100% 覆盖

## 开发环境设置

### 环境要求
- Python 3.11+
- uv 包管理器
- Git

### 开发命令
```bash
# 安装依赖
uv sync

# 安装开发依赖
uv sync --group dev

# 运行程序
uv run python MdxScraper.py

# 运行测试
uv run pytest

# 代码格式化
uv run black src/ tests/
uv run isort src/ tests/

# 类型检查
uv run mypy src/

# 运行所有检查
uv run pre-commit run --all-files
```

## 兼容性考虑

### 向后兼容
- 保持现有配置文件格式的兼容性
- 保持现有数据目录结构
- 提供迁移工具帮助用户升级

### 跨平台支持
- Windows: 通过 .vbs 脚本启动
- Linux/macOS: 通过 shell 脚本启动
- 统一的配置和数据处理逻辑

## 性能优化

### 优化策略
1. **并发处理**：使用多线程处理大文件
2. **缓存机制**：词典索引和查询结果缓存
3. **内存优化**：流式处理，避免全量加载
4. **启动优化**：延迟加载非关键模块

## 错误处理

### 错误分类
1. **配置错误**：配置文件格式错误、路径不存在等
2. **文件错误**：文件不存在、权限不足、格式不支持等
3. **词典错误**：词典文件损坏、查询失败等
4. **系统错误**：内存不足、磁盘空间不足等

### 错误处理策略
- 友好的错误提示
- 详细的错误日志
- 自动恢复机制
- 用户操作指导

## 发布策略

### 版本管理
- 使用语义化版本号
- 详细的更新日志
- 向后兼容性保证

### 分发方式
- 源码分发（推荐）
- 可执行文件分发（可选）
- 包管理器分发（未来考虑）

## 维护计划

### 代码质量
- 定期代码审查
- 自动化测试
- 持续集成

### 用户支持
- 详细的文档
- 常见问题解答
- 社区支持

---

*本文档将随着项目开发进度持续更新*
