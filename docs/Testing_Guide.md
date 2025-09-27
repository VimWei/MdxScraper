# MdxScraper 测试指南

## 测试概述

MdxScraper项目包含**231个测试**，覆盖了从核心算法到UI协调的完整功能栈。这些测试是项目的**质量保证基石**，为开发、重构和维护提供可靠的安全网。

### 测试的价值
- **🛡️ 质量保护**: 防止代码修改时破坏现有功能
- **📚 学习资源**: 展示API使用方法和最佳实践
- **🔍 功能验证**: 确保所有功能按预期工作
- **🚀 重构支持**: 重构时提供安全保障
- **👥 团队协作**: 帮助团队成员理解代码行为

## 测试文件结构

```
tests/
├── test_config_models.py          # 配置数据模型测试
├── test_config_coordinator.py     # 配置协调器测试
├── test_conversion_coordinator.py # 转换协调器测试
├── test_converter.py              # 核心转换算法测试
├── test_dictionary.py             # 字典查询测试
├── test_export_service.py         # 导出服务测试
├── test_file_coordinator.py       # 文件操作协调器测试
├── test_file_utils.py             # 文件工具函数测试
├── test_parser.py                 # 文件解析测试
├── test_path_utils.py             # 路径工具测试
├── test_preset_coordinator.py     # 预设协调器测试
├── test_preset_models.py          # 预设数据模型测试
├── test_preset_unification.py     # 预设统一测试
├── test_presets_service.py        # 预设服务测试
├── test_renderer.py               # 渲染算法测试
├── test_settings_service.py       # 设置服务测试
├── test_system_utils.py           # 系统工具测试
├── test_time_utils.py             # 时间工具测试
└── test_unified_config_service.py # 统一配置服务测试
```

## 运行测试

### 基础命令

#### 运行所有测试
```bash
# 快速运行所有测试（简洁输出）
uv run pytest tests/ --tb=no -q

# 详细运行所有测试
uv run pytest tests/ -v

# 运行所有测试并显示失败详情
uv run pytest tests/ --tb=short
```

#### 运行特定测试文件
```bash
# 运行转换功能测试
uv run pytest tests/test_converter.py -v

# 运行配置相关测试
uv run pytest tests/test_config_*.py -v

# 运行协调器测试
uv run pytest tests/test_*_coordinator.py -v
```

#### 运行特定测试方法
```bash
# 运行特定测试方法
uv run pytest tests/test_converter.py::test_mdx2html_basic -v

# 运行多个特定测试
uv run pytest tests/test_converter.py::test_mdx2html_basic tests/test_converter.py::test_mdx2pdf_basic -v
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

#### 并行测试（如果支持）
```bash
# 并行运行测试（需要安装pytest-xdist）
uv run pytest tests/ -n auto
```

## 测试分类

### 1. 核心功能测试

#### 转换算法测试 (`test_converter.py`)
- **用途**: 验证MDX到HTML/PDF/图片的转换功能
- **关键测试**:
  - `test_mdx2html_basic` - 基础HTML转换
  - `test_mdx2pdf_basic` - 基础PDF转换
  - `test_mdx2img_basic` - 基础图片转换
- **运行命令**: `uv run pytest tests/test_converter.py -v`

#### 字典查询测试 (`test_dictionary.py`)
- **用途**: 验证MDX字典查询功能
- **关键测试**:
  - `test_lookup_html` - HTML查询
  - `test_dictionary_with_mdd` - MDD文件支持
- **运行命令**: `uv run pytest tests/test_dictionary.py -v`

#### 文件解析测试 (`test_parser.py`)
- **用途**: 验证多种文件格式的解析
- **支持格式**: TXT, MD, JSON, XLS, XLSX
- **运行命令**: `uv run pytest tests/test_parser.py -v`

### 2. 服务层测试

#### 配置服务测试 (`test_settings_service.py`)
- **用途**: 验证配置管理功能
- **关键功能**: 配置读取、写入、验证
- **运行命令**: `uv run pytest tests/test_settings_service.py -v`

#### 预设服务测试 (`test_presets_service.py`)
- **用途**: 验证预设管理功能
- **关键功能**: 预设加载、保存、解析
- **运行命令**: `uv run pytest tests/test_presets_service.py -v`

#### 导出服务测试 (`test_export_service.py`)
- **用途**: 验证导出功能
- **关键功能**: HTML/PDF/图片导出
- **运行命令**: `uv run pytest tests/test_export_service.py -v`

### 3. 协调器测试

#### 配置协调器测试 (`test_config_coordinator.py`)
- **用途**: 验证配置同步和导入导出
- **关键功能**: 配置同步、导入、导出、验证
- **运行命令**: `uv run pytest tests/test_config_coordinator.py -v`

#### 预设协调器测试 (`test_preset_coordinator.py`)
- **用途**: 验证预设选择和编辑功能
- **关键功能**: 预设选择、文本编辑、自动保存
- **运行命令**: `uv run pytest tests/test_preset_coordinator.py -v`

#### 文件协调器测试 (`test_file_coordinator.py`)
- **用途**: 验证文件选择功能
- **关键功能**: 输入文件、字典文件、输出文件选择
- **运行命令**: `uv run pytest tests/test_file_coordinator.py -v`

#### 转换协调器测试 (`test_conversion_coordinator.py`)
- **用途**: 验证转换流程协调
- **关键功能**: 转换启动、进度监控、错误处理
- **运行命令**: `uv run pytest tests/test_conversion_coordinator.py -v`

### 4. 工具函数测试

#### 路径工具测试 (`test_path_utils.py`)
- **用途**: 验证路径处理和wkhtmltopdf检测
- **关键功能**: 路径解析、工具检测
- **运行命令**: `uv run pytest tests/test_path_utils.py -v`

#### 系统工具测试 (`test_system_utils.py`)
- **用途**: 验证系统操作功能
- **关键功能**: 文件打开、系统检测
- **运行命令**: `uv run pytest tests/test_system_utils.py -v`

#### 时间工具测试 (`test_time_utils.py`)
- **用途**: 验证时间处理功能
- **关键功能**: 时间格式化、持续时间计算
- **运行命令**: `uv run pytest tests/test_time_utils.py -v`

#### 文件工具测试 (`test_file_utils.py`)
- **用途**: 验证文件操作功能
- **关键功能**: 文件写入、图片格式检测
- **运行命令**: `uv run pytest tests/test_file_utils.py -v`

## 开发工作流中的测试

### 1. 日常开发流程

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

# 2. 添加新功能
# ... 你的新功能 ...

# 3. 为新功能编写测试
# ... 编写测试代码 ...

# 4. 验证新功能
uv run pytest tests/test_your_new_feature.py -v

# 5. 确保没有破坏现有功能
uv run pytest tests/ --tb=short -q
```

#### 重构代码
```bash
# 1. 重构前：记录当前状态
uv run pytest tests/ --tb=short -q > before_refactor.txt

# 2. 进行重构
# ... 你的重构 ...

# 3. 重构后：验证功能一致
uv run pytest tests/ --tb=short -q > after_refactor.txt

# 4. 比较结果确保没有回归
diff before_refactor.txt after_refactor.txt
```

### 2. 问题调试流程

#### 功能异常时
```bash
# 1. 运行相关测试定位问题
uv run pytest tests/test_converter.py -v --tb=long

# 2. 查看具体失败的测试
uv run pytest tests/test_converter.py::test_mdx2html_basic -v --tb=long

# 3. 修复问题后重新验证
uv run pytest tests/test_converter.py -v
```

#### 性能问题时
```bash
# 1. 分析测试执行时间
uv run pytest tests/ --durations=10

# 2. 识别慢速测试
uv run pytest tests/test_converter.py --durations=0

# 3. 优化后重新测试
uv run pytest tests/test_converter.py --durations=0
```

### 3. 发布前验证

#### 完整测试套件
```bash
# 运行所有测试确保发布质量
uv run pytest tests/ --tb=short -q

# 如果所有测试通过，输出应该显示：231 passed
```

#### 关键功能验证
```bash
# 验证核心转换功能
uv run pytest tests/test_converter.py tests/test_dictionary.py -v

# 验证配置功能
uv run pytest tests/test_settings_service.py tests/test_config_coordinator.py -v

# 验证协调器功能
uv run pytest tests/test_*_coordinator.py -v
```

## 测试文件管理

### 1. Git版本控制

#### 应该纳入Git的文件
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

#### .gitignore配置
```gitignore
# 测试相关忽略
tests/__pycache__/
tests/.pytest_cache/
tests/temp_*
tests/test_data/

# 但保留正式测试文件
!tests/test_*.py
!tests/__init__.py
```

### 2. 测试文件组织

#### 按功能分组
```
tests/
├── core/                 # 核心功能测试
│   ├── test_converter.py
│   ├── test_dictionary.py
│   ├── test_parser.py
│   └── test_renderer.py
├── services/            # 服务层测试
│   ├── test_settings_service.py
│   ├── test_presets_service.py
│   └── test_export_service.py
├── coordinators/        # 协调器测试
│   ├── test_config_coordinator.py
│   ├── test_preset_coordinator.py
│   ├── test_file_coordinator.py
│   └── test_conversion_coordinator.py
├── models/              # 模型测试
│   ├── test_config_models.py
│   └── test_preset_models.py
└── utils/               # 工具测试
    ├── test_path_utils.py
    ├── test_system_utils.py
    ├── test_time_utils.py
    └── test_file_utils.py
```

## 测试学习价值

### 1. API使用示例

每个测试文件都是**活生生的API使用文档**：

#### 转换功能使用示例
```python
# 从 test_converter.py 学习如何使用转换功能
def test_mdx2html_basic():
    result = mdx2html(
        input_file="test.txt",
        dictionary_file="test.mdx",
        output_file="output.html"
    )
    assert result is not None
```

#### 配置服务使用示例
```python
# 从 test_settings_service.py 学习如何使用配置
def test_get_basic_config():
    config = settings.get_basic_config()
    assert config.input_file == ""
    assert config.output_file == ""
```

#### 协调器使用示例
```python
# 从 test_config_coordinator.py 学习如何使用协调器
def test_sync_all_from_config():
    coordinator.sync_all_from_config(mock_mw)
    # 验证UI状态已同步
```

### 2. 错误处理示例

#### 异常处理模式
```python
# 从测试中学习如何处理错误
def test_mdx2html_file_not_found():
    with pytest.raises(FileNotFoundError):
        mdx2html("nonexistent.txt", "test.mdx", "output.html")
```

#### 返回值验证
```python
# 从测试中学习如何验证返回值
def test_validate_input():
    result = service.validate_input("")
    assert result is False
```

### 3. 架构理解

#### 分层架构示例
```python
# 从测试中理解分层架构
def test_conversion_coordinator():
    # 协调器调用服务
    coordinator = ConversionCoordinator(settings, presets, ...)
    # 服务调用核心算法
    result = coordinator.run(main_window)
```

#### 依赖关系示例
```python
# 从测试中理解依赖关系
def test_settings_service():
    # 服务依赖配置管理器
    service = SettingsService(config_manager)
    # 服务提供业务API
    config = service.get_basic_config()
```

## 故障排除

### 1. 常见测试失败

#### 导入错误
```bash
# 错误: ImportError: No module named 'mdxscraper.gui.models'
# 解决: 更新导入路径
# 从: from mdxscraper.gui.models import ConfigModel
# 到: from mdxscraper.models import ConfigModel
```

#### Mock对象错误
```bash
# 错误: AttributeError: Mock object has no attribute 'method_name'
# 解决: 正确设置Mock对象
mock_object.method_name.return_value = expected_value
```

#### 断言失败
```bash
# 错误: AssertionError: expected 'value1', got 'value2'
# 解决: 检查期望值与实际值的差异
# 使用 -v 参数查看详细输出
uv run pytest tests/test_specific.py -v --tb=long
```

### 2. 测试环境问题

#### 依赖缺失
```bash
# 错误: ModuleNotFoundError: No module named 'pytest'
# 解决: 安装测试依赖
uv add pytest
```

#### 环境变量问题
```bash
# 错误: 测试依赖特定环境变量
# 解决: 设置测试环境变量
export TEST_MODE=true
uv run pytest tests/
```

### 3. 性能问题

#### 测试执行缓慢
```bash
# 问题: 测试执行时间过长
# 解决: 使用并行测试
uv run pytest tests/ -n auto

# 或跳过慢速测试
uv run pytest tests/ -m "not slow"
```

#### 内存使用过高
```bash
# 问题: 测试消耗过多内存
# 解决: 限制并发数
uv run pytest tests/ -n 2
```

## 最佳实践

### 1. 测试编写原则

#### 测试命名
```python
# 好的测试命名
def test_mdx2html_basic():
    """测试基础HTML转换功能"""
    pass

def test_mdx2html_with_css_styles():
    """测试带CSS样式的HTML转换"""
    pass

def test_mdx2html_file_not_found():
    """测试文件不存在时的错误处理"""
    pass
```

#### 测试结构
```python
def test_functionality():
    """测试功能描述"""
    # 1. 准备测试数据
    input_data = "test data"
    expected_result = "expected output"

    # 2. 执行被测试的功能
    actual_result = function_under_test(input_data)

    # 3. 验证结果
    assert actual_result == expected_result
```

### 2. 测试维护原则

#### 保持测试更新
- 修改功能时同步更新测试
- 重构时保持测试覆盖度
- 定期运行测试确保稳定性

#### 测试独立性
- 每个测试应该独立运行
- 测试之间不应该有依赖关系
- 使用Mock对象隔离外部依赖

#### 测试可读性
- 使用描述性的测试名称
- 添加必要的注释说明
- 保持测试代码简洁明了

### 3. 团队协作原则

#### 提交前验证
```bash
# 提交代码前运行测试
uv run pytest tests/ --tb=short -q

# 确保所有测试通过
# 输出应该显示: 231 passed
```

#### 代码审查
- 审查代码时同时审查测试
- 确保新功能有对应测试
- 验证测试覆盖度是否充分

#### 持续集成
- 设置自动化测试流程
- 测试失败时阻止代码合并
- 定期分析测试执行报告

## 总结

MdxScraper的231个测试文件是项目的**核心资产**，它们：

- **保护代码质量** - 防止修改时破坏现有功能
- **指导开发过程** - 展示如何正确使用各种功能
- **提供学习资源** - 通过测试代码理解项目架构
- **支持重构维护** - 重构时提供安全保障

**关键建议**：
1. **将测试文件纳入Git管理** - 它们是项目的重要组成部分
2. **每次修改后运行测试** - 确保功能正常
3. **将测试作为学习工具** - 通过测试代码理解项目
4. **为新功能编写测试** - 保持测试的完整性和有效性

遵循这些指南，你就能充分利用这些测试文件，让它们成为开发过程中的得力助手！
