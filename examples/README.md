# MdxScraper Headless Library Examples

This directory contains examples demonstrating how to use MdxScraper as a headless library without the GUI.

## Examples Overview

### 🔧 Diagnostic Tools (诊断工具)

#### Database Diagnosis (`diagnose_db.py`)
Diagnose MDX database issues and verify table structure:
```bash
python examples/diagnose_db.py "your_dictionary.mdx"
```

**检查项目**：
- ✅ 数据库文件是否存在
- ✅ 表结构是否正确（9 列）
- ✅ 版本信息是否完整
- ✅ 索引数量和完整性

#### Rebuild Index (`rebuild_index.py`)
Force rebuild database index for incompatible or corrupted databases:
```bash
python examples/rebuild_index.py "your_dictionary.mdx"
```

**使用场景**：
- 🔧 表结构不兼容（其他工具创建的 .db 文件）
- 🔧 数据库损坏或不完整
- 🔧 非 ASCII 文件名导致的问题
- 🔧 版本升级后需要更新索引

💡 **提示**：如果遇到 `IndexError: tuple index out of range` 错误，请先运行此工具！

### 🎵 Audio Extraction (`extract_audio.py`) ⭐ NEW
Extract audio files from MDX dictionaries (perfect for NHK Japanese Dictionary):
```bash
# Extract single word audio
python examples/extract_audio.py あい --mdx "NHK日本語発音アクセント辞書.mdx"

# List audio info without saving
python examples/extract_audio.py hello --mdx dict.mdx --list-only

# Batch extract from word list
python examples/extract_audio.py --batch words.txt --mdx dict.mdx
```

**功能特点**：
- 🎵 提取单个或批量词条的音频文件
- 💾 保存音频到磁盘（MP3, WAV, OGG等）
- 🔗 生成 base64 data URI 用于网页播放
- 📄 生成可点击播放的 HTML 文件
- 🌐 支持多种音频格式

**支持的格式**：
- Audio: MP3, WAV, OGG, M4A, AAC, FLAC, WebM, Opus
- Protocol: `sound://`, `entry://sound/`, `<source>` tags

**使用场景**：
- 为 Anki 等记忆软件生成带发音的单词卡片
- 提取词典发音用于语音学习应用
- 创建离线发音库
- 网站集成音频播放功能

📖 详细文档：[AUDIO_SUPPORT.md](../docs/AUDIO_SUPPORT.md)

### 1. Basic Query (`basic_query.py`)
Demonstrates basic dictionary query operations:
- Simple word lookup
- Using context manager for proper resource handling
- Automatic fallback strategies (case-insensitive, hyphen removal, link following)

```bash
python examples/basic_query.py
```

### 📌 Quick Word Query (`query_word.py`) ⭐ NEW - 已升级
Fast single word query with complete HTML output including CSS:
- Query a single word and get complete HTML with embedded CSS
- **🎉 自动提取词典内部的 CSS 样式**（新功能）
- **🖼️ 自动嵌入词典中的图片为 base64**（新功能）
- Clean, modern styling with responsive design
- Perfect for quick lookups or integration into other tools

```bash
# Quick query with dictionary CSS and images embedded
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html

# Without images (smaller file size)
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html --no-images

# Show help
python examples/query_word.py --help
```

**特点**：
- ✅ 完全独立的 HTML 文件（包含词典 CSS + 自定义样式）
- ✅ 图片自动嵌入为 base64（可选）
- ✅ 无需外部资源，可离线使用
- 📖 详细说明：[QUERY_WORD_UPDATE.md](QUERY_WORD_UPDATE.md)

### 🔍 Advanced Single Word Query (`single_word_query.py`)
Comprehensive single word query with multiple modes:
- Simple mode: Raw HTML output
- Complete mode: HTML with embedded CSS and images
- Custom CSS mode: Apply your own styling

```bash
# Simple query
python examples/single_word_query.py hello --mdx data/mdict/dict.mdx

# Complete mode with embedded CSS and images
python examples/single_word_query.py hello --mdx data/mdict/dict.mdx --output hello.html --complete

# Custom CSS mode
python examples/single_word_query.py hello --mdx data/mdict/dict.mdx --output hello.html --custom-css
```

### 2. Batch Conversion (`batch_conversion.py`)
Shows how to convert word lists to multiple formats:
- HTML conversion with custom styles
- PDF conversion with custom options
- Image conversion (PNG/JPEG/WEBP)
- Handling invalid words

```bash
python examples/batch_conversion.py
```

### 3. Custom Styles (`custom_styles.py`)
Demonstrates applying custom CSS styles:
- Minimal clean design
- Dark theme styling
- Print-optimized styles
- Custom CSS injection

```bash
python examples/custom_styles.py
```

### 4. Parse Input Files (`parse_input_files.py`)
Shows how to parse different input formats:
- TXT files with headers
- Markdown files
- JSON files
- Excel files (not demonstrated, but supported)

```bash
python examples/parse_input_files.py
```

### 5. Progress Callback (`progress_callback.py`)
Demonstrates tracking conversion progress:
- Simple progress bar
- Detailed status messages
- Advanced progress tracker with timing
- Integration with other applications

```bash
python examples/progress_callback.py
```

## Prerequisites

Before running these examples, you need to:

1. **Install MdxScraper**:
   ```bash
   cd MdxScraper
   uv sync
   ```

2. **Prepare MDX Dictionary**:
   - Place your `.mdx` dictionary file in `data/mdict/`
   - Update the `MDX_FILE` path in each example script

3. **Prepare Input Files**:
   - Create word lists in `data/input/`
   - Or use the provided `words_to_lookup.txt`
   - Update the `INPUT_FILE` path in each example script

4. **For PDF/Image Conversion** (optional):
   - Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)
   - The tool is required for PDF and image output formats

## Running Examples

All examples now support command-line arguments for easy customization:

### Basic Usage (with default paths)
```bash
uv run python examples/basic_query.py
uv run python examples/batch_conversion.py
uv run python examples/custom_styles.py
uv run python examples/parse_input_files.py
uv run python examples/progress_callback.py
```

### With Custom Paths
```bash
# Specify custom MDX dictionary
uv run python examples/basic_query.py --mdx-file path/to/your_dict.mdx

# Specify all paths
uv run python examples/batch_conversion.py \
    --mdx-file data/mdict/my_dict.mdx \
    --input-file data/input/my_words.txt \
    --output-dir output

# Same for other examples
uv run python examples/custom_styles.py \
    --mdx-file path/to/dict.mdx \
    --input-file path/to/words.txt \
    --output-dir path/to/output
```

### Get Help
```bash
# View available command-line options
uv run python examples/basic_query.py --help
uv run python examples/batch_conversion.py --help
```

### Using UV (Recommended)
```bash
uv run python examples/basic_query.py --mdx-file data/mdict/my_dict.mdx
uv run python examples/batch_conversion.py --input-file words.txt
uv run python examples/custom_styles.py --output-dir my_output
uv run python examples/parse_input_files.py
uv run python examples/progress_callback.py
```

### Using Python Directly
```bash
python examples/basic_query.py --mdx-file data/mdict/my_dict.mdx
python examples/batch_conversion.py --help
python examples/custom_styles.py --input-file words.txt --output-dir output
```

## Integration with Your Projects

You can use MdxScraper as a library in your own projects:

```python
# Install as a dependency
# pip install mdxscraper  # (if published to PyPI)

# Or install from local directory
# pip install -e /path/to/MdxScraper

# Import and use
from mdxscraper import Dictionary, mdx2html

# Query dictionary
with Dictionary("path/to/dict.mdx") as dict:
    result = dict.lookup_html("word")

# Convert to HTML
found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html"
)
```

## API Reference

### Core Classes

#### `Dictionary`
```python
from mdxscraper import Dictionary

with Dictionary(mdx_file: Path | str) as dict:
    html = dict.lookup_html(word: str) -> str
```

#### `WordParser`
```python
from mdxscraper import WordParser

parser = WordParser(file_path: str)
lessons = parser.parse() -> List[Dict[str, Any]]
# Returns: [{"name": "Lesson 1", "words": ["word1", "word2"]}, ...]
```

### Conversion Functions

#### `mdx2html`
```python
from mdxscraper import mdx2html

found, not_found, invalid_words = mdx2html(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    with_toc: bool = True,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[int, int, OrderedDict]
```

#### `mdx2pdf`
```python
from mdxscraper import mdx2pdf

found, not_found, invalid_words = mdx2pdf(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    pdf_options: dict,
    with_toc: bool = True,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
    wkhtmltopdf_path: str = "auto",
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[int, int, OrderedDict]
```

#### `mdx2img`
```python
from mdxscraper import mdx2img

found, not_found, invalid_words = mdx2img(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    img_options: dict | None = None,
    with_toc: bool = True,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[int, int, OrderedDict]
```

## Troubleshooting

### Dictionary Not Found
- Ensure the MDX file path is correct
- Check file permissions
- Verify the file is a valid MDX dictionary

### PDF/Image Conversion Fails
- Install wkhtmltopdf from https://wkhtmltopdf.org/
- Add wkhtmltopdf to your system PATH
- Or provide the path explicitly: `wkhtmltopdf_path="/path/to/wkhtmltopdf"`

### Invalid Words
- Check if the words exist in your dictionary
- Try different dictionaries
- Use the returned `invalid_words` dict to identify missing entries

## Support

For more information, see:
- Main README: [../README.md](../README.md)
- Development Guide: [../docs/Development_Guide.md](../docs/Development_Guide.md)
- GitHub Issues: https://github.com/VimWei/MdxScraper/issues
