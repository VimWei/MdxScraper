# MdxScraper 版本管理指南

## 概述

本文档介绍 MdxScraper 项目的版本管理最佳实践，包括使用 `uv` 进行版本管理、标准化发布流程，以及解决版本信息不一致的问题。

## 快速开始

### 日常版本发布
```bash
# 修复版本发布（最常用）
uv run python scripts/release.py patch

# 功能版本发布
uv run python scripts/release.py minor

# 重大版本发布
uv run python scripts/release.py major
```

### 查看版本信息
```bash
# 查看当前版本
uv version

# 预览版本变化
uv version --dry-run --bump minor
```

### 在代码中使用版本
```python
from mdxscraper.version import get_version, get_app_title

version = get_version()  # "5.0.0"
title = get_app_title()  # "MdxScraper v5.0.0"
```

## 版本管理原则

### 1. 单一真实来源（Single Source of Truth）

- **主版本源**: `pyproject.toml` 中的 `[project] version` 字段
- **其他文件**: 所有其他地方的版本信息都从 `pyproject.toml` 读取
- **避免重复**: 不在多个地方硬编码版本号

### 2. 语义化版本控制（Semantic Versioning）

遵循 [SemVer](https://semver.org/) 规范：

- **主版本号 (MAJOR)**: 不兼容的 API 修改
- **次版本号 (MINOR)**: 向后兼容的功能性新增
- **修订号 (PATCH)**: 向后兼容的问题修正

示例：`5.0.0` → `5.0.1` (修复) → `5.1.0` (功能) → `6.0.0` (重大变更)

## uv 版本管理功能

### 基本命令

```bash
# 查看当前版本
uv version

# 查看版本号（仅显示版本）
uv version --short

# 设置特定版本
uv version 5.1.0

# JSON 格式输出
uv version --output-format json
```

### 自动版本升级

* 作用：仅升级 pyproject.toml 的版本号
* 副作用：默认会 re-lock 并同步环境（可用 --frozen、--no-sync 关闭）
* 不会：跑测试、校验格式、更新 changelog、提交/打 tag、推送
* 交互：无提示，直接改

```bash
# 修复版本 (5.0.0 -> 5.0.1)
uv version --bump patch

# 功能版本 (5.0.0 -> 5.1.0)
uv version --bump minor

# 重大版本 (5.0.0 -> 6.0.0)
uv version --bump major

# 预发布版本
uv version --bump alpha    # 5.0.0 -> 5.0.1a1
uv version --bump beta     # 5.0.0 -> 5.0.1b1
uv version --bump rc       # 5.0.0 -> 5.0.1rc1
uv version --bump dev      # 5.0.0 -> 5.0.1.dev1
```

### 预览模式

```bash
# 预览版本变化，不实际修改文件
uv version --dry-run --bump minor
```

## 自动化发布

### 发布脚本功能

`scripts/release.py` 会自动执行以下步骤：

1. ✅ 检查 Git 状态
2. 🧪 运行测试
3. 🔍 检查代码质量
4. 📋 预览版本变化
5. 🤔 确认发布
6. 📝 更新版本号
7. 📄 更新 changelog
8. 💾 提交更改（包含 pyproject.toml、uv.lock、docs/changelog.md）
9. 🏷️ 创建 Git 标签
10. 🚀 推送到远程

### 运行发布脚本前准备

1. 提交所有希望包含到本次发布的内容：完成从 `git add` 到 `git commit`。
2. 取消暂存（unstage）不希望纳入本次发布的所有内容（例如：`git restore --staged <path>`）。
3. 不要手动修改 `pyproject.toml` / `uv.lock` / `docs/changelog.md`：这 3 个文件无论当前是未暂存还是已暂存，都会在发布脚本运行过程中被自动更新并纳入发布提交。

### 使用发布脚本

```bash
# 修复版本发布
uv run python scripts/release.py patch

# 功能版本发布
uv run python scripts/release.py minor

# 重大版本发布
uv run python scripts/release.py major

# 预发布版本
uv run python scripts/release.py alpha
```

### 代码风格检查失败时如何处理

发布脚本在第 3 步会执行代码质量检查（对“将要发布的代码快照”进行）：

```bash
uv run black --check .
uv run isort --check-only .
```

如果出现类似提示：

```
would reformat scripts/release.py
Oh no! 💥 💔 💥
Code quality checks failed
```

直接在发布脚本的交互提示里选择 `y`，进行一键自动修复（或手动做如下操作）：

```bash
# 1) 暂存当前未暂存/未跟踪改动（仅临时保存，保留暂存区）
git stash push -u -k -m release-temp-<timestamp>

# 2) 在“发布快照”上执行自动修复
uv run isort .
uv run black .

# 3) 自动重新检查（无需人工再次运行）
uv run black --check .
uv run isort --check-only .

# 4) 对本次格式化的 .py 文件创建一个独立的“Style”提交
git add .
git commit -m "Style: format with isort/black"

# 5) 恢复你的未暂存改动，并在工作区同步一次格式（不提交）
git stash pop -q
uv run isort .
uv run black .
```

修复完成后脚本会自动重新检查（手动修复方案则需执行再次启动发布流程）；若通过将继续发布流程。这样既保证“发布提交”中的代码已通过风格检查，又让你的工作区改动与发布快照在格式上保持一致，减少后续无意义 diff。

## 版本信息统一管理

### 版本模块

`src/mdxscraper/version.py` 提供统一的版本信息获取：

```python
from mdxscraper.version import get_version, get_version_display, get_full_version_info

# 获取版本字符串
version = get_version()  # "5.0.0"

# 获取显示格式版本
display = get_version_display()  # "v5.0.0"

# 获取完整版本信息
info = get_full_version_info()
print(info['version'])        # "5.0.0"
print(info['major'])          # 5
print(info['minor'])          # 0
print(info['patch'])          # 0
print(info['is_prerelease'])  # False
```

### 在 GUI 中显示版本

```python
from mdxscraper.version import get_app_title, get_about_text

# 设置窗口标题
self.setWindowTitle(get_app_title())  # "MdxScraper v5.0.0"

# 关于对话框
about_text = get_about_text()
```

## Git 管理建议

### 应该纳入 Git 管理的文件

```bash
# 核心工具和配置
scripts/release.py              # ✅ 发布脚本
.github/workflows/              # ✅ GitHub Actions 工作流
src/mdxscraper/version.py       # ✅ 版本管理模块
docs/version_management_guide.md # ✅ 版本管理文档
```

### 立即执行的 Git 操作

```bash
# 添加版本管理相关文件
git add scripts/release.py
git add .github/workflows/
git add src/mdxscraper/version.py
git add docs/version_management_guide.md

# 提交更改
git commit -m "Add version management system

- Add automated release script (scripts/release.py)
- Add GitHub Actions workflows for release and version checking
- Add version management module (src/mdxscraper/version.py)
- Add version management documentation
- Establish single source of truth for version information"

# 推送到远程
git push origin main
```

## 故障排除

### 常见问题

#### 1. 版本信息不一致

**问题**: 不同文件中的版本号不匹配

**解决方案**:
```bash
# 检查当前版本
uv version

# 统一更新到正确版本
uv version 5.0.0  # 替换为正确版本
```

#### 2. Git 标签冲突

**问题**: 尝试创建已存在的标签

**解决方案**:
```bash
# 删除本地标签
git tag -d v5.0.0

# 删除远程标签
git push origin :refs/tags/v5.0.0

# 重新创建标签
git tag v5.0.0
git push origin v5.0.0
```

#### 3. uv 命令未找到

**问题**: 系统找不到 uv 命令

**解决方案**:
```bash
# 检查 uv 安装
uv --version

# 如果未安装，重新安装
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 调试技巧

```bash
# 详细输出版本信息
uv version --verbose

# 检查 pyproject.toml 语法
uv version --dry-run

# 验证 Git 状态
git status
git log --oneline -5
git tag -l
```

## 最佳实践总结

### ✅ 推荐做法

- 使用 `python scripts/release.py` 进行发布
- 发布前确保所有测试通过
- 及时更新 changelog.md
- 使用语义化版本号

### ❌ 避免做法

- 手动修改 pyproject.toml 中的版本号
- 跳过测试直接发布
- 忘记更新 changelog
- 使用不一致的版本号格式

## 相关资源

- [uv 官方文档](https://docs.astral.sh/uv/)
- [语义化版本控制](https://semver.org/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)

---

*最后更新: 2025-09-30*
