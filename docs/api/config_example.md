# 配置管理器代码示例

## 使用内置 TOML 模块

### Python 3.12+ 配置管理器

```python
# src/mdxscraper/config/config_manager.py
import tomllib  # Python 3.11+ 内置模块
import tomli_w  # Python 3.12+ 内置模块
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.default_config_path = base_dir / "src" / "mdxscraper" / "config" / "default_config.toml"
        self.configs_dir = base_dir / "data" / "configs"
        self.latest_config_path = self.configs_dir / "config_latest.toml"
        
        # 确保目录存在
        self.configs_dir.mkdir(parents=True, exist_ok=True)
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        with open(self.default_config_path, 'rb') as f:
            return tomllib.load(f)
    
    def get_user_config(self) -> Dict[str, Any]:
        """获取用户当前配置（如果不存在则使用默认配置）"""
        if self.latest_config_path.exists():
            with open(self.latest_config_path, 'rb') as f:
                return tomllib.load(f)
        else:
            # 首次使用，创建默认配置
            default_config = self.get_default_config()
            self.save_user_config(default_config)
            return default_config
    
    def save_user_config(self, config: Dict[str, Any]) -> None:
        """保存用户当前配置"""
        with open(self.latest_config_path, 'w', encoding='utf-8') as f:
            tomli_w.dump(config, f)
    
    def save_config_scheme(self, name: str, config: Dict[str, Any]) -> None:
        """保存配置方案"""
        scheme_path = self.configs_dir / f"{name}.toml"
        with open(scheme_path, 'w', encoding='utf-8') as f:
            tomli_w.dump(config, f)
    
    def load_config_scheme(self, name: str) -> Dict[str, Any]:
        """加载配置方案"""
        scheme_path = self.configs_dir / f"{name}.toml"
        if scheme_path.exists():
            with open(scheme_path, 'rb') as f:
                return tomllib.load(f)
        else:
            raise FileNotFoundError(f"配置方案 {name} 不存在")
```

### 最终方案说明

我们采用完全内置的方案：
- **读取 TOML**: 使用 Python 3.11+ 内置的 `tomllib`
- **写入 TOML**: 使用 Python 3.12+ 内置的 `tomli_w`

这样完全不需要外部依赖，性能最佳，维护最简单。

### 使用示例

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

# 保存为配置方案
config_manager.save_config_scheme("english_pdf", config)

# 加载配置方案
pdf_config = config_manager.load_config_scheme("english_pdf")
```

## 优势总结

### 完全内置方案的优势

1. **零外部依赖**: 完全使用 Python 内置模块
2. **性能最佳**: 内置模块性能最优
3. **功能完整**: 读写功能都支持
4. **维护简单**: 无需管理外部依赖
5. **现代化**: 使用最新的 Python 特性

### 版本要求

- **Python 3.12+**: 使用 `tomllib` 读取 + `tomli_w` 写入
- **最低要求**: Python 3.12（完全内置支持）
- **外部依赖**: 无

## 推荐方案

对于 MdxScraper 项目，推荐使用 **Python 3.12+** 和完全内置方案，因为：

1. **最简洁**: 零外部依赖，最干净的依赖列表
2. **最现代**: 使用最新的 Python 特性
3. **最稳定**: 内置模块最稳定可靠
4. **最快速**: 内置模块性能最佳
5. **最易维护**: 无需担心外部库的版本兼容性
