# MdxScraper 测试指南

## 测试概述

测试是项目的**质量保证基石**，为开发、重构和维护提供可靠的安全网。

- **🛡️ 质量保护**: 防止代码修改时破坏现有功能
- **📚 学习资源**: 展示API使用方法和最佳实践
- **🔍 功能验证**: 确保所有功能按预期工作
- **🚀 重构支持**: 重构时提供安全保障
- **👥 团队协作**: 帮助团队成员理解代码行为

## 安装与配置

### 安装依赖（最小集）
```bash
# 已假设已安装 uv
uv add -g dev pytest pytest-cov
```

### 立即可用的运行方式（无需配置）
```bash
# 运行所有测试
uv run pytest

# 生成覆盖度（不改 pyproject 的情况下）
uv run pytest --cov --cov-report=term-missing
```

### 最小化配置
如需将约定固化到 `pyproject.toml`，保留最少字段即可：

```toml
[tool.pytest.ini_options]
# 仅在 tests/ 下收集测试
testpaths = ["tests"]
```


## 测试文件组织结构

本目录按功能模块对测试文件进行分类组织，采用扁平化结构以提高测试的可维护性和覆盖度。

```
tests/
├── core/                   # 核心功能模块测试
│   ├── test_converter.py   # MDX到HTML/PDF/图片的转换功能
│   ├── test_dictionary.py  # MDX字典查询功能
│   ├── test_parser.py      # 多种文件格式解析 (TXT, MD, JSON, XLS, XLSX)
│   └── test_renderer.py    # CSS样式和图片嵌入功能
├── coordinators/           # 协调器模块测试
│   ├── test_config_coordinator.py      # 配置同步和导入导出
│   ├── test_conversion_coordinator.py  # 转换流程协调
│   ├── test_file_coordinator.py        # 文件选择功能
│   └── test_preset_coordinator.py      # 预设选择和编辑功能
├── services/               # 服务模块测试
│   ├── test_export_service.py          # HTML/PDF/图片导出功能
│   ├── test_presets_service.py         # 预设管理功能
│   ├── test_settings_service.py        # 配置管理功能 (路径问题)
│   └── test_unified_config_service.py  # 统一配置管理 (路径问题)
├── models/                 # 数据模型测试
│   ├── test_config_models.py   # 配置数据模型验证
│   └── test_preset_models.py   # 预设数据模型验证
├── utils/                  # 工具函数测试
│   ├── test_file_utils.py      # 文件操作功能
│   ├── test_path_utils.py      # 路径处理和wkhtmltopdf检测
│   ├── test_system_utils.py    # 系统操作功能
│   └── test_time_utils.py      # 时间处理功能
├── gui/                    # GUI组件测试
│   └── test_about_page.py  # 关于页面功能验证
├── integration/            # 集成测试
│   └── test_preset_unification.py  # 预设统一化功能
├── fixtures/               # 测试夹具和共享数据
│   ├── sample_data.py      # 示例数据，包括MDX文件路径、词汇列表、配置数据等
│   └── mock_objects.py     # Mock对象定义，包括文件系统、服务、配置等
└── conftest.py            # pytest配置和全局夹具
```

## 运行测试

### 基础命令

#### 运行所有测试
```bash
# 运行所有测试
uv run pytest

# 快速运行所有测试（简洁输出）
uv run pytest --tb=no -q

# 详细运行所有测试
uv run pytest -v

# 运行所有测试并显示失败详情
uv run pytest --tb=short
```

#### 运行特定模块测试
```bash
# 运行特定分类的测试
uv run pytest tests/core/
uv run pytest tests/coordinators/
uv run pytest tests/services/
uv run pytest tests/models/
uv run pytest tests/utils/
uv run pytest tests/gui/
uv run pytest tests/integration/

# 运行单元测试（核心+协调器+服务+模型+工具）
uv run pytest tests/core/ tests/coordinators/ tests/services/ tests/models/ tests/utils/
```

#### 运行特定测试文件
```bash
# 运行转换功能测试
uv run pytest tests/core/test_converter.py -v

# 运行配置相关测试
uv run pytest tests/services/test_settings_service.py -v

# 运行协调器测试
uv run pytest tests/coordinators/ -v
```

#### 运行特定测试方法
```bash
# 运行特定测试方法
uv run pytest tests/core/test_converter.py::test_mdx2html_basic -v

# 运行多个特定测试
uv run pytest tests/core/test_converter.py::test_mdx2html_basic tests/core/test_converter.py::test_mdx2pdf_basic -v
```

### 高级测试选项

#### 性能分析
```bash
# 显示最慢的10个测试
uv run pytest tests/ --durations=10

# 显示所有测试的执行时间
uv run pytest tests/ --durations=0
```

#### 失败重试
```bash
# 只运行上次失败的测试
uv run pytest tests/ --lf

# 运行失败的测试并显示详细信息
uv run pytest tests/ --lf -v --tb=long
```

#### 并行测试
```bash
# 并行运行测试（需要安装pytest-xdist）
uv run pytest tests/ -n auto
```

## 测试覆盖度

项目集成了**pytest-cov**模块，提供全面的代码覆盖度分析。

### 覆盖度配置

```toml
# pyproject.toml 中的配置
[tool.pytest.ini_options]
addopts = [
    "--cov=src/mdxscraper",           # 覆盖度分析目标目录
    "--cov-report=html:tests/htmlcov", # HTML报告输出到tests/htmlcov/
    "--cov-report=term-missing",      # 终端显示缺失覆盖度的行
    "--cov-report=xml:tests/coverage.xml", # XML报告输出到tests/coverage.xml
    "--cov-fail-under=80"             # 覆盖度低于80%时测试失败
]

[tool.coverage.run]
source = ["src/mdxscraper"]          # 源代码目录
omit = [                             # 排除的目录和文件
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/migrations/*"
]
data_file = "tests/.coverage"        # 覆盖度数据文件位置

[tool.coverage.report]
exclude_lines = [                    # 排除的行（不计算覆盖度）
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]
```

### 运行覆盖度测试

#### 基础覆盖度测试
```bash
# 运行所有测试并生成覆盖度报告
uv run pytest tests/ --cov

# 运行测试并显示覆盖度摘要
uv run pytest tests/ --cov --cov-report=term-missing

# 运行测试并生成HTML报告
uv run pytest tests/ --cov --cov-report=html:tests/htmlcov
```

#### 详细覆盖度分析
```bash
# 显示未覆盖的具体行号
uv run pytest tests/ --cov --cov-report=term-missing -v

# 生成多种格式的覆盖度报告
uv run pytest tests/ --cov --cov-report=html:tests/htmlcov --cov-report=xml:tests/coverage.xml --cov-report=term

# 设置最低覆盖度要求
uv run pytest tests/ --cov --cov-fail-under=85
```

#### 特定模块覆盖度
```bash
# 分析特定模块的覆盖度
uv run pytest tests/test_converter.py --cov=src/mdxscraper/core --cov-report=term-missing

# 分析多个模块的覆盖度
uv run pytest tests/ --cov=src/mdxscraper/core --cov=src/mdxscraper/services --cov-report=term-missing

# 排除特定文件或目录
uv run pytest tests/ --cov=src/mdxscraper --cov-omit="*/__init__.py" --cov-report=term-missing
```

### 覆盖度文件位置
```
tests/
├── .coverage              # 覆盖度数据文件（二进制）
├── coverage.xml           # XML格式覆盖度报告
└── htmlcov/               # HTML覆盖度报告目录
    ├── index.html         # 主报告页面
    ├── style.css          # 样式文件
    └── *.html             # 各模块的详细报告
```

### 覆盖度报告解读

```bash
# 示例输出
Name                           Stmts   Miss  Cover   Missing
------------------------------------------------------------
src/mdxscraper/core/converter.py   150     12    92%   45-48, 67, 89-92
src/mdxscraper/services/settings.py  80      5    94%   23, 45, 67
------------------------------------------------------------
TOTAL                             230     17    93%
```

- **Stmts**: 总语句数
- **Miss**: 未覆盖的语句数
- **Cover**: 覆盖度百分比
- **Missing**: 未覆盖的具体行号

### 覆盖度最佳实践

#### 1. 开发流程中的覆盖度
```bash
# 日常开发：快速检查覆盖度
uv run pytest tests/ --cov --cov-report=term-missing -q

# 功能开发：详细分析新功能覆盖度
uv run pytest tests/test_new_feature.py --cov=src/mdxscraper/new_module --cov-report=term-missing -v

# 发布前：完整覆盖度验证
uv run pytest tests/ --cov --cov-report=html:tests/htmlcov --cov-fail-under=80
```

#### 2. 覆盖度目标设定
```bash
# 项目整体覆盖度目标：80%以上
uv run pytest tests/ --cov-fail-under=80

# 核心模块覆盖度目标：90%以上
uv run pytest tests/test_converter.py tests/test_dictionary.py --cov=src/mdxscraper/core --cov-fail-under=90

# 新功能覆盖度目标：95%以上
uv run pytest tests/test_new_feature.py --cov=src/mdxscraper/new_module --cov-fail-under=95
```

#### 3. 覆盖度分析技巧
```bash
# 识别覆盖度最低的模块
uv run pytest tests/ --cov --cov-report=term-missing | grep -E "^\s*[0-9]+%" | sort -k3 -n

# 分析特定文件的覆盖度详情
uv run pytest tests/ --cov=src/mdxscraper/core/converter.py --cov-report=term-missing -v

# 排除测试文件本身
uv run pytest tests/ --cov=src/mdxscraper --cov-omit="*/test_*.py" --cov-report=term-missing
```

#### 4. 提升覆盖度的方法
- **编写更多测试用例** - 覆盖未测试的代码路径
- **添加边界条件测试** - 测试异常情况和边界值
- **完善错误处理测试** - 确保异常处理代码被测试
- **增加集成测试** - 测试模块间的交互

## 测试文件 Git 版本控制

### 应该纳入Git的文件
```
tests/
├── core/                 # 核心功能测试 ✅
├── coordinators/         # 协调器测试 ✅
├── services/             # 服务层测试 ✅
├── models/               # 数据模型测试 ✅
├── utils/                # 工具函数测试 ✅
├── gui/                  # GUI测试 ✅
├── integration/          # 集成测试 ✅
├── fixtures/             # 测试夹具 ✅
├── conftest.py          # pytest配置 ✅
└── __init__.py          # 如果存在 ✅

# 项目根目录
pyproject.toml            # 包含覆盖度配置 ✅
```

### 应该忽略的文件
```
tests/
├── __pycache__/          # Python缓存 ❌
├── .pytest_cache/       # pytest缓存 ❌
├── temp_*.py            # 临时测试文件 ❌
├── test_data/           # 大型测试数据 ❌
├── .coverage            # 覆盖度数据文件 ❌
├── coverage.xml         # XML覆盖度报告 ❌
└── htmlcov/             # HTML覆盖度报告 ❌
```

* 忽略原因
- 覆盖度文件是**动态生成**的，每次运行测试都会变化
- 这些文件**体积较大**，不适合版本控制
- 不同开发者的覆盖度数据**可能不同**，合并时会产生冲突

### .gitignore配置
```gitignore
# 测试相关忽略
tests/__pycache__/
tests/.pytest_cache/
tests/temp_*
tests/test_data/
# 覆盖度生成的文件
tests/.coverage
tests/coverage.xml
tests/htmlcov/

# 但保留正式测试文件
!tests/test_*.py
!tests/__init__.py
```
