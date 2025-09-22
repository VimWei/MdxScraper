# MdxScraper 文档

欢迎来到 MdxScraper 的文档中心！这里包含了项目的完整文档，帮助您了解、安装、配置和使用 MdxScraper。

## 📚 文档导航

### 🚀 快速开始
- [用户指南](user_guide/README.md) - 基本使用方法和功能介绍

### 🔧 开发文档
- [开发指南](development.md) - 项目架构和开发指南
- [配置文件重构](development_config_refactor.md) - 配置文件重构设计详情
- [API 文档](api/) - 详细的 API 参考文档
  - [核心模块](api/core.md) - 核心功能模块 API
  - [配置管理](api/config.md) - 配置管理 API
  - [工具函数](api/utils.md) - 工具函数 API

### 📋 项目信息
- [更新日志](changelog.md) - 版本更新记录
- [贡献指南](CONTRIBUTING.md) - 如何参与项目开发
- [许可证](LICENSE) - 项目许可证信息

## 🎯 项目概述

MdxScraper 是一个现代化的 Python 工具，用于从 MDX 字典中提取特定词汇并生成 HTML、PDF 或 JPG 文件。项目采用模块化架构，提供图形用户界面，支持灵活的配置管理。

### ✨ 主要特性

- **🎨 图形界面**: 基于 PySide6 的现代化 GUI
- **📁 多格式支持**: 支持 txt、json、xlsx 输入格式
- **📄 多输出格式**: 支持 HTML、PDF、JPG 输出
- **⚙️ 灵活配置**: 智能的配置管理系统
- **🚀 高性能**: 并发处理和缓存机制
- **🔧 便携式**: 真正的便携式设计
- **🌍 跨平台**: 支持 Windows、macOS、Linux

### 🏗️ 技术架构

```
MdxScraper/
├── src/mdxscraper/          # 核心源代码
│   ├── config/              # 配置管理
│   ├── core/                # 核心功能
│   ├── utils/               # 工具函数
│   ├── gui/                 # 图形界面
│   └── mdict/               # 词典处理
├── data/                    # 用户数据
├── tests/                   # 测试代码
├── docs/                    # 项目文档
└── pyproject.toml          # 项目配置
```

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/VimWei/MdxScraper.git
cd MdxScraper

# 安装依赖
uv sync

# 运行程序
uv run python MdxScraper.py
```
s
### 2. 基本使用

1. **准备词汇文件**: 将词汇列表保存为 txt、json 或 xlsx 格式
2. **配置词典**: 在配置中选择要使用的 MDX 词典
3. **设置输出**: 选择输出格式和样式
4. **开始处理**: 点击开始按钮处理词汇
5. **查看结果**: 在输出目录查看生成的文件

### 3. 配置管理

- **默认配置**: 程序提供合理的默认配置
- **用户配置**: 通过 GUI 或配置文件自定义设置
- **配置方案**: 保存和切换不同的配置方案

## 📖 详细文档

### 用户文档

#### [安装指南](user_guide/installation.md)
- 系统要求
- 安装方法
- 依赖管理
- 常见问题
- 故障排除

- 配置文件结构
- 配置项详解
- 配置管理
- 配置示例
- 最佳实践

#### [用户指南](user_guide/README.md)
- 基本使用
- 高级功能
- 工作流程
- 技巧和提示
- 常见问题

### 开发文档

#### [开发指南](development.md)
- 项目架构
- 模块设计
- 技术栈
- 开发环境
- 贡献指南

#### [API 文档](api/)
- **核心模块**: 词典处理、文件解析、格式转换、渲染引擎
- **配置管理**: 配置文件的读写、验证、备份和恢复
- **工具函数**: 文件操作、GUI 工具、编码检测等

## 🔧 开发指南

### 环境设置

```bash
# 安装开发依赖
uv sync --extra dev

# 运行测试
uv run pytest

# 代码格式化
uv run black src/ tests/
uv run isort src/ tests/

# 类型检查
uv run mypy src/
```

### 项目结构

- **src/mdxscraper/**: 主要源代码
- **tests/**: 测试代码
- **docs/**: 项目文档
- **data/**: 用户数据目录

### 开发流程

1. **Fork 项目**: Fork 到个人仓库
2. **创建分支**: 创建功能分支
3. **开发功能**: 实现新功能或修复
4. **编写测试**: 添加相应的测试
5. **提交代码**: 提交代码并创建 PR
6. **代码审查**: 通过审查后合并

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 如何贡献

- **报告问题**: 使用 GitHub Issues 报告 Bug
- **功能请求**: 提交新功能建议
- **代码贡献**: 提交代码改进
- **文档改进**: 改进项目文档
- **测试**: 帮助测试新功能

### 贡献流程

1. **查看 Issues**: 查看现有的 Issues 和 PR
2. **选择任务**: 选择要贡献的任务
3. **Fork 项目**: Fork 项目到个人仓库
4. **创建分支**: 创建功能分支
5. **开发实现**: 实现功能或修复
6. **提交代码**: 提交代码并创建 PR
7. **代码审查**: 参与代码审查过程

## 📞 获取帮助

### 支持渠道

- **GitHub Issues**: 报告问题和功能请求
- **文档**: 查看完整的项目文档
- **社区**: 参与社区讨论
- **邮件**: 联系项目维护者

### 常见问题

- **安装问题**: 查看 [安装指南](user_guide/installation.md)
- **配置问题**: 通过 GUI 界面进行配置，无需查看文档
- **使用问题**: 查看 [用户指南](user_guide/README.md)
- **开发问题**: 查看 [开发指南](development.md)

## 📄 许可证

本项目采用 GPL-3.0 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢所有为 MdxScraper 项目做出贡献的开发者和用户！

### 特别感谢

- **mdict-query**: 基于 [readmdict](https://bitbucket.org/xwang/mdict-analysis) 项目
- **PySide6**: 提供现代化的 GUI 框架
- **uv**: 提供快速的 Python 包管理
- **所有贡献者**: 感谢所有代码贡献者和问题报告者

---

*最后更新: 2024-01-14*
