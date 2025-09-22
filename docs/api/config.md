# 配置管理 API 文档

## 概述

配置管理模块负责处理 MdxScraper 的所有配置相关功能，包括默认配置、用户配置、配置方案的管理和持久化存储。

## 模块结构

```
src/mdxscraper/config/
├── __init__.py
├── default_config.toml      # 默认配置文件
└── config_manager.py        # 配置管理器
```

## 配置层次结构

### 1. 默认配置 (Default Configuration)
- **位置**: `src/mdxscraper/config/default_config.toml`
- **用途**: 程序内部默认配置，随程序版本更新
- **特点**: 只读，用户无法直接修改

### 2. 用户当前配置 (User Current Configuration)
- **位置**: `data/configs/config_latest.toml`
- **用途**: 用户最近使用的配置
- **特点**: 可读写，程序启动时加载

### 3. 配置方案 (Configuration Schemes)
- **位置**: `data/configs/*.toml` (除 config_latest.toml)
- **用途**: 用户保存的配置方案
- **特点**: 可读写，支持快速切换

## ConfigManager 类

### 初始化
```python
def __init__(self, base_dir: Path) -> None
```
- **参数**：
  - `base_dir` (Path): 程序根目录路径
- **功能**：初始化配置管理器，设置各配置文件的路径

### 配置获取方法

#### get_default_config
```python
def get_default_config(self) -> Dict[str, Any]
```
获取默认配置。

- **返回**：
  - `Dict[str, Any]`: 默认配置字典
- **异常**：
  - `FileNotFoundError`: 默认配置文件不存在
  - `tomllib.TOMLDecodeError`: TOML 解析错误

#### get_user_config
```python
def get_user_config(self) -> Dict[str, Any]
```
获取用户当前配置。如果用户配置不存在，则创建默认配置。

- **返回**：
  - `Dict[str, Any]`: 用户配置字典
- **功能**：
  - 首次使用时自动创建默认配置
  - 返回用户最近使用的配置

### 配置保存方法

#### save_user_config
```python
def save_user_config(self, config: Dict[str, Any]) -> None
```
保存用户当前配置。

- **参数**：
  - `config` (Dict[str, Any]): 要保存的配置字典
- **异常**：
  - `tomllib.TOMLDecodeError`: TOML 序列化错误
  - `OSError`: 文件写入错误

#### save_config_scheme
```python
def save_config_scheme(self, name: str, config: Dict[str, Any]) -> None
```
保存配置方案。

- **参数**：
  - `name` (str): 方案名称
  - `config` (Dict[str, Any]): 配置字典
- **异常**：
  - `ValueError`: 方案名称为空或包含非法字符
  - `tomllib.TOMLDecodeError`: TOML 序列化错误

### 配置方案管理

#### load_config_scheme
```python
def load_config_scheme(self, name: str) -> Dict[str, Any]
```
加载指定的配置方案。

- **参数**：
  - `name` (str): 方案名称
- **返回**：
  - `Dict[str, Any]`: 配置字典
- **异常**：
  - `FileNotFoundError`: 配置方案不存在
  - `tomllib.TOMLDecodeError`: TOML 解析错误

#### list_config_schemes
```python
def list_config_schemes(self) -> List[str]
```
列出所有可用的配置方案。

- **返回**：
  - `List[str]`: 配置方案名称列表
- **注意**：排除 `config_latest.toml`

#### apply_config_scheme
```python
def apply_config_scheme(self, name: str) -> None
```
应用配置方案到用户当前配置。

- **参数**：
  - `name` (str): 方案名称
- **功能**：
  - 加载指定方案
  - 保存为用户当前配置
- **异常**：
  - `FileNotFoundError`: 配置方案不存在

#### delete_config_scheme
```python
def delete_config_scheme(self, name: str) -> None
```
删除配置方案。

- **参数**：
  - `name` (str): 方案名称
- **异常**：
  - `FileNotFoundError`: 配置方案不存在
  - `OSError`: 文件删除错误

### 配置验证和备份

#### validate_config
```python
def validate_config(self, config: Dict[str, Any]) -> bool
```
验证配置的有效性。

- **参数**：
  - `config` (Dict[str, Any]): 要验证的配置
- **返回**：
  - `bool`: 配置是否有效
- **验证项目**：
  - 必需字段存在
  - 字段类型正确
  - 路径有效性
  - 值范围合理

#### backup_current_config
```python
def backup_current_config(self, backup_name: str = None) -> Optional[Path]
```
备份当前配置。

- **参数**：
  - `backup_name` (str, optional): 备份名称，默认使用时间戳
- **返回**：
  - `Optional[Path]`: 备份文件路径，如果备份失败返回 None

#### restore_config
```python
def restore_config(self, backup_path: Path) -> None
```
从备份恢复配置。

- **参数**：
  - `backup_path` (Path): 备份文件路径
- **异常**：
  - `FileNotFoundError`: 备份文件不存在
  - `tomllib.TOMLDecodeError`: TOML 解析错误

## 配置结构定义

### 完整配置结构
```toml
# 输入配置
[input]
path = "data/input"                    # 输入文件目录
file = "words_to_lookup.txt"           # 输入文件名
encoding = "auto"                      # 文件编码

# 词典配置
[dictionary]
type = "English"                       # 词典类型
order = 0                              # 词典序号
path = "data/mdict"                    # 词典目录
cache = true                           # 是否启用缓存

# 输出配置
[output]
path = "data/output"                   # 输出目录
format = "html"                        # 输出格式 (html/pdf/jpg)
with_toc = true                        # 是否包含目录
style = "default"                      # 样式名称

# 处理配置
[processing]
invalid_action = "collect_warning"     # 无效词汇处理方式
parallel = true                        # 是否并行处理
max_workers = 4                        # 最大工作线程数

# GUI 配置
[gui]
window_size = [1200, 800]              # 窗口大小
theme = "light"                        # 主题 (light/dark)
language = "zh_CN"                     # 界面语言
auto_save = true                       # 自动保存配置
show_toolbar = true                    # 显示工具栏
show_statusbar = true                  # 显示状态栏
```

### 配置验证规则

```python
CONFIG_SCHEMA = {
    "input": {
        "path": {"type": "string", "required": True},
        "file": {"type": "string", "required": True},
        "encoding": {"type": "string", "default": "auto"}
    },
    "dictionary": {
        "type": {"type": "string", "required": True, "choices": ["Chinese", "English", "Others"]},
        "order": {"type": "integer", "required": True, "min": 0},
        "path": {"type": "string", "required": True},
        "cache": {"type": "boolean", "default": True}
    },
    "output": {
        "path": {"type": "string", "required": True},
        "format": {"type": "string", "required": True, "choices": ["html", "pdf", "jpg"]},
        "with_toc": {"type": "boolean", "default": True},
        "style": {"type": "string", "default": "default"}
    },
    "processing": {
        "invalid_action": {"type": "string", "required": True, "choices": ["exit", "collect", "warning", "collect_warning"]},
        "parallel": {"type": "boolean", "default": True},
        "max_workers": {"type": "integer", "default": 4, "min": 1, "max": 16}
    },
    "gui": {
        "window_size": {"type": "list", "length": 2, "items": {"type": "integer", "min": 400}},
        "theme": {"type": "string", "choices": ["light", "dark"]},
        "language": {"type": "string", "default": "zh_CN"},
        "auto_save": {"type": "boolean", "default": True},
        "show_toolbar": {"type": "boolean", "default": True},
        "show_statusbar": {"type": "boolean", "default": True}
    }
}
```

## 使用示例

### 基本使用

```python
from pathlib import Path
from mdxscraper.config.config_manager import ConfigManager

# 初始化配置管理器
config_manager = ConfigManager(Path("."))

# 获取用户配置
config = config_manager.get_user_config()

# 修改配置
config["output"]["format"] = "pdf"
config["processing"]["max_workers"] = 8

# 保存配置
config_manager.save_user_config(config)
```

### 配置方案管理

```python
# 保存当前配置为方案
config_manager.save_config_scheme("english_basic", config)

# 列出所有方案
schemes = config_manager.list_config_schemes()
print(f"可用方案: {schemes}")

# 应用方案
config_manager.apply_config_scheme("english_basic")

# 删除方案
config_manager.delete_config_scheme("old_scheme")
```

### 配置验证和备份

```python
# 验证配置
if config_manager.validate_config(config):
    print("配置有效")
else:
    print("配置无效")

# 备份配置
backup_path = config_manager.backup_current_config("before_update")
print(f"配置已备份到: {backup_path}")

# 恢复配置
config_manager.restore_config(backup_path)
```

### 错误处理

```python
from mdxscraper.config.exceptions import ConfigError, ConfigValidationError

try:
    config = config_manager.get_user_config()
except ConfigError as e:
    print(f"配置错误: {e}")

try:
    config_manager.save_config_scheme("", config)
except ConfigValidationError as e:
    print(f"配置验证错误: {e}")
```

## 配置迁移

### 从旧版本迁移

```python
def migrate_from_old_config(self, old_config_path: Path) -> None:
    """
    从旧版本配置文件迁移到新格式
    """
    # 读取旧配置
    old_config = self._load_old_config(old_config_path)
    
    # 转换为新格式
    new_config = self._convert_to_new_format(old_config)
    
    # 验证新配置
    if self.validate_config(new_config):
        self.save_user_config(new_config)
        print("配置迁移成功")
    else:
        print("配置迁移失败：新配置无效")
```

## 性能优化

### 配置缓存
- 内存中缓存配置对象
- 文件修改时间检查
- 按需重新加载

### 并发安全
- 文件锁机制
- 原子写入操作
- 配置变更通知

## 扩展性

### 插件配置
```python
# 支持插件配置扩展
def register_plugin_config(self, plugin_name: str, config_schema: Dict) -> None:
    """注册插件配置模式"""
    pass

def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
    """获取插件配置"""
    pass
```

### 环境变量支持
```python
# 支持环境变量覆盖配置
def apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
    """应用环境变量覆盖"""
    pass
```
