# MdxScraper

## 简介

**一句话：根据指定词汇，从 MDX 字典提取内容并输出为## 特点

### 核心功能（无头库 + GUI）

1. **多格式输入支持**：TXT / Markdown / JSON / Excel
2. **多格式输出支持**：HTML / PDF / JPG / PNG / WEBP
3. **全面兼容 MDX 词典**：
    * 支持多 mdd 的词典（内置并升级 mdict-query）
    * 兼容有或无 CSS 文件的词典
    * 兼容内嵌的各种图片，支持多种图片格式、img 标签多种写法等
4. **智能查询策略**：
    * 自动处理大小写
    * 自动处理连字符
    * 自动跟随 @@@LINK= 跳转
5. **跨平台**：Windows / macOS / Linux

### GUI 独有功能

4. **图形界面体验**（PySide 6）：
    * 配置选项灵活丰富：Basic、Image、CSS、PDF 等主要类别
    * 配置方案导入导出，快速切换不同场景
    * 可选备份原始词汇，数据安全有保障
    * 可选增加时间戳到输出文件名，方便文件多版本管理
    * 可选输出"无效词汇"清单，轻松改用其他词典再次查询P/PNG/JPG。**

MdxScraper 既可以作为**无头库**（Headless Library）在 Python 项目中使用，也可以作为**图形界面应用**独立运行。

![动画演示](docs/screenshot.gif)

[更多视频演示下载](docs/screencast.mp4)

## 两种使用方式

### 🎯 无头库模式（Headless Library）

直接在 Python 代码中使用，无需 GUI，适合：
- 自动化脚本
- Web 服务集成
- 批处理任务
- 命令行工具

**快速开始：**

```python
from mdxscraper import Dictionary, mdx2html

# 查询单词
with Dictionary("dict.mdx") as dict:
    result = dict.lookup_html("hello")
    print(result)

# 批量转换为 HTML
found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html"
)
print(f"找到 {found} 个词，未找到 {not_found} 个词")
```

📚 **更多示例**: 查看 [examples/](examples/) 目录，包含基础查询、批量转换、自定义样式、进度追踪等完整示例。

### 🖥️ GUI 应用模式

提供完整的图形界面，适合：
- 日常使用
- 可视化配置
- 交互式操作

**启动 GUI：**
- 命令行：`uv run mdxscraper`
- Windows：双击 `MdxScraper.vbs`

## 特点

1. 支持更多输入文件格式，包括 TXT/Markdown/JSON/Excel
2. 支持更多输出文件格式，包括 HTML/JPG/PNG/WEBP/PDF
3. 全面兼容常见 .mdx 词典：
    * 支持多 mdd 的词典（内置并升级 mdict-query）
    * 兼容有或无 CSS 文件的词典
    * 兼容内嵌的各种图片，支持多种图片格式、img 标签多种写法等
4. 采用图形界面(PySide 6)，提升智能化、增强人性化体验
    * 配置选项灵活丰富，包括 Basic、Image、CSS、PDF 等主要类别
    * 通过配置方案导入导出即可快速切换，轻松应对不同场景
    * 可选备份原始词汇，数据安全有保障
    * 可选增加时间戳到输出文件名，方便文件多版本管理
    * 可选输出“无效词汇”清单，通过它可轻松改用其他词典再次查询
5. 跨平台，兼容 Windows/MacOS/Linux

## 安装

### 方式 1：完整安装（GUI + 无头库）

适合想要使用图形界面或完整功能的用户。

1. **克隆仓库**：
   ```bash
   git clone https://github.com/VimWei/MdxScraper
   cd MdxScraper
   ```

2. **安装 uv**（Python 虚拟环境管理器）：
   ```bash
   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   
   # Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **同步环境**（包含所有依赖）：
   ```bash
   uv sync --all-extras
   ```

4. **安装 wkhtmltopdf**（可选，用于 PDF/图片输出）：
   * 访问 https://wkhtmltopdf.org/downloads.html 下载安装

### 方式 2：仅安装无头库

适合只需要在代码中使用核心功能的开发者。

```bash
# 克隆仓库
git clone https://github.com/VimWei/MdxScraper
cd MdxScraper

# 安装核心依赖（不含 GUI）
uv sync

# 或者安装为包（如果已发布到 PyPI）
# pip install mdxscraper
```

**可选依赖组合**：

```bash
# 只安装 GUI 依赖
uv sync --extra gui

# 只安装转换依赖（PDF/图片）
uv sync --extra conversion

# 安装所有功能
uv sync --all-extras
```

## 使用

### GUI 应用模式

1. **启动程序**：
    * 命令行：`uv run mdxscraper`
    * Windows：双击文件 `MdxScraper.vbs`
2. **配置参数**：主要是输入/词典/输出，其他都是高级选项
3. **点击 Scrape 按钮**：查看输出成果

### 无头库模式

#### 基础查询

```python
from mdxscraper import Dictionary

# 查询单词
with Dictionary("path/to/dict.mdx") as dict:
    html = dict.lookup_html("hello")
    if html:
        print("找到定义：", html[:100], "...")
    else:
        print("未找到")
```

#### 批量转换

```python
from mdxscraper import mdx2html, mdx2pdf, mdx2img

# 转换为 HTML
found, not_found, invalid_words = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html",
    with_toc=True,  # 包含目录
)

# 转换为 PDF（需要 wkhtmltopdf）
found, not_found, invalid_words = mdx2pdf(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.pdf",
    pdf_options={"page-size": "A4"},
)

# 转换为图片（需要 wkhtmltoimage）
found, not_found, invalid_words = mdx2img(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.png",
    img_options={"width": "800"},
)
```

#### 自定义样式

```python
from mdxscraper import mdx2html

# 添加自定义 CSS
custom_css = """
    body { font-family: Arial; }
    h1 { color: #333; }
    .scrapedword { border: 1px solid #ddd; padding: 10px; }
"""

found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html",
    additional_styles=custom_css,
)
```

#### 进度追踪

```python
from mdxscraper import mdx2html

def progress_callback(progress: int, message: str):
    print(f"[{progress}%] {message}")

found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html",
    progress_callback=progress_callback,
)
```

**📚 完整示例**：查看 [examples/](examples/) 目录获取更多使用案例。

**命令行运行示例**：
```bash
# 使用默认路径运行
uv run python examples/batch_conversion.py

# 指定自定义路径
uv run python examples/batch_conversion.py \
    --mdx-file data/mdict/my_dict.mdx \
    --input-file data/input/words.txt \
    --output-dir output

# 查看帮助
uv run python examples/batch_conversion.py --help
```

### 用户数据目录

MdxScraper 使用 `data/` 目录作为用户数据存储位置，所有用户相关的文件都存储在此目录下：

```
data/                               # 用户数据目录（可删除重建）
├── configs/                        # 配置文件目录
│   ├── config_latest.toml          # 最近一次配置方案
│   ├── pdf/                        # PDF 样式方案目录
│   ├── css/                        # CSS 样式方案目录
│   └── ...                         # 用户保存的配置方案
├── input/                          # 输入文件目录，存放待查询的词条文件
│   ├── words_to_lookup.txt         # 词条文件案例
│   └── ...                         # 用户创建的词条文件
├── output/                         # 输出文件目录，存放生成的输出文件
│   └── ...                         # 各种输出文件
└── mdict/                          # 存放 .mdx 词典文件，建议分目录存放不同词典
    ├── CC-CEDICT/                  # 中英词典
    └── ...                         # 更多词典文件
```
