# 配置文件重构设计总结

## 讨论背景

当前 `settings.py` 文件存在以下问题：
1. **混合了配置和程序逻辑**：包含 `InvalidAction` 枚举类等程序代码
2. **配置过于细粒度**：输入文件拆分为路径+文件名，词典列表手工维护
3. **缺乏灵活性**：硬编码的词典列表，固定的路径结构
4. **GUI 不友好**：配置结构不适合图形界面操作

## 重构目标

1. **分离关注点**：配置与程序逻辑分离
2. **简化配置**：减少用户需要配置的项目
3. **提高灵活性**：支持动态发现和智能默认
4. **GUI 友好**：配置结构适合图形界面操作

## 最终方案

### 1. 配置格式：TOML
- **原因**：与项目 `pyproject.toml` 保持一致
- **Python 版本**：3.12+，使用内置 `tomllib` 和 `tomli_w`
- **优势**：零外部依赖，性能最佳

### 2. 配置文件结构

#### 用户数据目录：`data/`
```
data/
├── configs/
│   ├── config_latest.toml          # 用户当前配置
│   ├── my_english_study.toml       # 用户保存的配置方案
│   ├── chinese_learning.toml
│   └── work_documents.toml
├── input/                          # 用户输入文件
├── output/                         # 用户输出文件
└── mdict/                          # 用户词典文件
```

#### 主配置文件：`data/configs/config_latest.toml`
```toml
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
wkhtmltopdf_path = "auto"  # "auto" 表示自动检测，或指定具体路径
```

#### 程序预设方案目录：`src/mdxscraper/presets/`
```
src/mdxscraper/presets/
├── pdf_options/
│   ├── default.toml
│   ├── high_quality.toml
│   └── compact.toml
└── css_styles/
    ├── modern.toml
    ├── classic.toml
    └── minimal.toml
```

**设计原则**：
- `data/` 目录：用户数据，可完全删除恢复默认状态
- `src/mdxscraper/presets/` 目录：程序预设方案，不可删除

### 配置管理逻辑

- **当前配置**：`config_latest.toml`（程序退出时保存，下次启动时加载）
- **配置方案**：其他 `.toml` 文件（用户保存的命名方案）
- **方案切换**：用户选择方案 → 程序使用 → 程序退出时保存到 `config_latest.toml`

### 3. 程序逻辑分离

#### 枚举类移到主程序
```python
# src/mdxscraper/core/enums.py
from enum import IntEnum

class InvalidAction(IntEnum):
    Exit = 0
    Collect = 1
    OutputWarning = 2
    Collect_OutputWarning = 3
```

#### 智能路径检测
```python
# src/mdxscraper/utils/path_utils.py
def get_wkhtmltopdf_path(config_path: str) -> str:
    """获取 wkhtmltopdf 路径"""
    if config_path == "auto":
        return detect_wkhtmltopdf_path()
    else:
        return config_path

def detect_wkhtmltopdf_path() -> str:
    """自动检测 wkhtmltopdf 路径"""
    # 根据操作系统检测常见安装路径
    # 如果都找不到，返回 'wkhtmltopdf' 尝试 PATH 中的命令
```

#### 动态词典发现
```python
# src/mdxscraper/core/dictionary_scanner.py
def scan_dictionaries(mdict_dir: Path) -> Dict[str, List[Dict]]:
    """扫描词典目录，自动发现词典"""
    # 递归扫描 .mdx 文件
    # 按目录结构分类
    # 返回词典信息
```

## 实施计划

### 第一阶段：基础重构
1. **创建新的目录结构**
   - `src/mdxscraper/config/` - 配置管理模块
   - `src/mdxscraper/core/` - 核心功能模块
   - `src/mdxscraper/utils/` - 工具函数模块

2. **分离程序逻辑**
   - 将 `InvalidAction` 移到 `src/mdxscraper/core/enums.py`
   - 创建配置管理器 `src/mdxscraper/config/config_manager.py`

3. **创建默认配置**
   - `src/mdxscraper/config/default_config.toml`
   - 预设方案模板

### 第二阶段：功能实现
1. **实现配置管理器**
   - 支持 TOML 读写
   - 配置验证
   - 预设方案管理

2. **实现智能检测**
   - 词典自动发现
   - 路径自动检测
   - 系统兼容性处理

3. **更新主程序**
   - 使用新的配置系统
   - 保持向后兼容

### 第三阶段：GUI 集成
1. **配置界面**
   - 文件选择器
   - 词典选择器
   - 选项配置

2. **预设方案管理**
   - 方案选择
   - 方案编辑
   - 方案导入导出

## 配置项说明

### 输入配置
- `file`: 输入文件完整路径（替代原来的路径+文件名）

### 词典配置
- `file`: 词典文件完整路径（程序自动发现，用户选择）

### 输出配置
- `file`: 输出文件完整路径（格式从文件扩展名自动推断）
- `with_toc`: 是否包含目录

**支持的格式**：
- `.html` → html 格式
- `.pdf` → pdf 格式  
- `.jpg/.jpeg` → jpg 格式
- `.png` → png 格式

### 处理配置
- `invalid_action`: 无效词汇处理方式
- `parallel`: 是否并行处理
- `max_workers`: 最大工作线程数

### 高级配置
- `wkhtmltopdf_path`: wkhtmltopdf 路径（"auto" 自动检测）

## 向后兼容性

### 迁移策略
1. **检测旧配置**：程序启动时检查是否存在 `settings.py`
2. **自动转换**：将旧配置转换为新格式
3. **备份原配置**：保存原始配置文件
4. **用户确认**：显示转换结果，让用户确认

### 迁移工具
```python
# src/mdxscraper/migrate_config.py
def migrate_from_settings_py():
    """从 settings.py 迁移到新配置格式"""
    # 读取 settings.py
    # 转换为 TOML 格式
    # 保存到 config_latest.toml
    # 创建备份
```

## 优势总结

### 1. 配置简化
- 用户只需配置必要项目
- 智能默认值减少配置负担
- 文件路径直接指定，无需拆分

### 2. 程序智能化
- 自动发现词典文件
- 智能检测系统路径
- 动态适应不同环境

### 3. GUI 友好
- 配置结构适合图形界面
- 文件选择器直接选择文件
- 预设方案便于管理

### 4. 维护性提升
- 配置与程序逻辑分离
- 模块化设计便于维护
- 标准化配置格式

### 5. 扩展性增强
- 预设方案支持自定义
- 插件式配置管理
- 易于添加新功能

## 技术实现要点

### 1. TOML 处理（Python 3.11+）
```python
import tomllib  # Python 3.11+ 内置（只读）
import tomli_w  # 第三方写入器（写入）

# 读取配置
with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

# 写入配置（使用 tomli_w）
with open('config.toml', 'w', encoding='utf-8') as f:
    tomli_w.dump(config, f)
```

### 2. 配置验证
```python
def validate_config(config: Dict[str, Any]) -> bool:
    """验证配置的有效性"""
    # 检查必需字段
    # 验证文件路径
    # 检查值范围
    # 返回验证结果
```

### 3. 错误处理
```python
class ConfigError(Exception):
    """配置错误基类"""
    pass

class ConfigValidationError(ConfigError):
    """配置验证错误"""
    pass

class ConfigFileError(ConfigError):
    """配置文件错误"""
    pass
```

## 后续开发指引

### 1. 开发顺序
1. 先实现配置管理器基础功能
2. 再实现智能检测功能
3. 最后集成到主程序

### 2. 测试策略
1. 单元测试：配置管理器各个方法
2. 集成测试：配置加载和保存流程
3. 兼容性测试：不同操作系统和 Python 版本

### 3. 文档更新
1. 更新 API 文档
2. 更新用户指南
3. 创建迁移指南

### 4. 发布策略
1. 保持向后兼容
2. 提供迁移工具
3. 分阶段发布

---

*本文档将随着开发进度持续更新*
