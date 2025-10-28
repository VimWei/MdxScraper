# MdxScraper Headless Library API Reference

Complete API documentation for using MdxScraper as a headless library without GUI.

## Table of Contents

1. [Core Classes](#core-classes)
2. [Conversion Functions](#conversion-functions)
3. [Advanced Usage](#advanced-usage)
4. [Configuration Options](#configuration-options)

---

## Core Classes

### Dictionary

Dictionary query interface with automatic fallback strategies.

#### Constructor

```python
Dictionary(mdx_file: Path | str)
```

**Parameters:**
- `mdx_file`: Path to the MDX dictionary file

**Usage:**

```python
from mdxscraper import Dictionary

# Use context manager (recommended)
with Dictionary("dict.mdx") as dict:
    result = dict.lookup_html("word")

# Or manual management
dict = Dictionary("dict.mdx")
result = dict.lookup_html("word")
# ... use dictionary ...
```

#### Methods

##### `lookup_html(word: str) -> str`

Lookup a word in the dictionary and return HTML definition.

**Parameters:**
- `word`: Word to lookup

**Returns:**
- HTML definition string, or empty string if not found

**Automatic Fallback Strategy:**
1. Exact match
2. Case-insensitive match
3. Hyphen removal + case-insensitive match
4. Follow `@@@LINK=` redirects

**Example:**

```python
with Dictionary("dict.mdx") as dict:
    # All of these will use fallback strategies
    result1 = dict.lookup_html("hello")      # Exact
    result2 = dict.lookup_html("Hello")      # Case-insensitive
    result3 = dict.lookup_html("non-word")   # Hyphen removal
```

---

### WordParser

Parse word lists from various file formats.

#### Constructor

```python
WordParser(file_path: str)
```

**Parameters:**
- `file_path`: Path to input file (TXT, Markdown, JSON, Excel)

**Supported Formats:**
- `.txt` - Text file with optional `#` headers
- `.md` - Markdown file with `#` headers
- `.json` - JSON array of `{"name": "...", "words": [...]}`
- `.xls`, `.xlsx` - Excel file (each sheet becomes a lesson)

#### Methods

##### `parse() -> List[Dict[str, Any]]`

Parse the file and return structured word lists.

**Returns:**
- List of lessons: `[{"name": "Lesson 1", "words": ["word1", "word2"]}, ...]`

**Example:**

```python
from mdxscraper import WordParser

# Parse TXT file
parser = WordParser("words.txt")
lessons = parser.parse()

for lesson in lessons:
    print(f"Lesson: {lesson['name']}")
    print(f"Words: {', '.join(lesson['words'])}")
```

**Input File Examples:**

TXT format:
```text
# Chapter 1
hello
world

# Chapter 2
python
code
```

JSON format:
```json
[
  {"name": "Chapter 1", "words": ["hello", "world"]},
  {"name": "Chapter 2", "words": ["python", "code"]}
]
```

---

## Conversion Functions

### mdx2html

Convert word list to HTML with embedded dictionary definitions.

#### Signature

```python
mdx2html(
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

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mdx_file` | `str \| Path` | required | Path to MDX dictionary file |
| `input_file` | `str \| Path` | required | Path to input word list |
| `output_file` | `str \| Path` | required | Path to output HTML file |
| `with_toc` | `bool` | `True` | Include table of contents |
| `h1_style` | `str \| None` | `None` | Custom CSS style for `<h1>` tags |
| `scrap_style` | `str \| None` | `None` | Custom CSS style for word definitions |
| `additional_styles` | `str \| None` | `None` | Additional CSS to inject |
| `progress_callback` | `Callable` | `None` | Progress callback function |

#### Returns

Tuple of `(found_count, not_found_count, invalid_words)`:
- `found_count` (int): Number of words found
- `not_found_count` (int): Number of words not found
- `invalid_words` (OrderedDict): Dictionary of `{"lesson_name": ["word1", ...]}`

#### Example

```python
from mdxscraper import mdx2html

# Basic usage
found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html"
)
print(f"Found: {found}, Not found: {not_found}")

# With custom styles
custom_css = """
    body { font-family: Arial; }
    h1 { color: #2c3e50; }
"""

found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="styled.html",
    additional_styles=custom_css
)

# With progress tracking
def on_progress(progress: int, message: str):
    print(f"[{progress}%] {message}")

found, not_found, invalid = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html",
    progress_callback=on_progress
)
```

---

### mdx2pdf

Convert word list to PDF with embedded dictionary definitions.

**Note:** Requires `wkhtmltopdf` to be installed.

#### Signature

```python
mdx2pdf(
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

#### Parameters

Same as `mdx2html`, plus:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pdf_options` | `dict` | required | PDF conversion options (see below) |
| `wkhtmltopdf_path` | `str` | `"auto"` | Path to wkhtmltopdf executable |

#### PDF Options

Common `pdf_options` keys:

```python
pdf_options = {
    "page-size": "A4",           # Paper size: A4, Letter, etc.
    "margin-top": "20mm",        # Top margin
    "margin-bottom": "20mm",     # Bottom margin
    "margin-left": "15mm",       # Left margin
    "margin-right": "15mm",      # Right margin
    "encoding": "UTF-8",         # Text encoding
    "orientation": "Portrait",   # Portrait or Landscape
    "dpi": 300,                  # Output DPI
}
```

For more options, see [wkhtmltopdf documentation](https://wkhtmltopdf.org/usage/wkhtmltopdf.txt).

#### Example

```python
from mdxscraper import mdx2pdf

pdf_options = {
    "page-size": "A4",
    "margin-top": "20mm",
    "margin-bottom": "20mm",
    "encoding": "UTF-8",
}

found, not_found, invalid = mdx2pdf(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.pdf",
    pdf_options=pdf_options,
    wkhtmltopdf_path="auto",  # Auto-detect
)
```

---

### mdx2img

Convert word list to image (PNG, JPEG, WEBP).

**Note:** Requires `wkhtmltoimage` to be installed (comes with wkhtmltopdf).

#### Signature

```python
mdx2img(
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

#### Parameters

Same as `mdx2html`, plus:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `img_options` | `dict \| None` | `None` | Image conversion options (see below) |

#### Image Options

Common `img_options` keys:

```python
# PNG options
img_options = {
    "width": "800",              # Image width in pixels
    "png_optimize": True,        # Optimize PNG
    "png_compress_level": 9,     # PNG compression (0-9)
}

# JPEG options
img_options = {
    "width": "800",
    "quality": "90",             # JPEG quality (1-100)
}

# WEBP options
img_options = {
    "width": "800",
    "webp_quality": 80,          # WEBP quality (1-100)
    "webp_lossless": False,      # Lossless compression
}
```

#### Example

```python
from mdxscraper import mdx2img

# PNG output
img_options = {
    "width": "1024",
    "png_optimize": True,
    "png_compress_level": 9,
}

found, not_found, invalid = mdx2img(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.png",
    img_options=img_options,
)

# JPEG output (change extension)
img_options = {"width": "800", "quality": "85"}
found, not_found, invalid = mdx2img(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.jpg",
    img_options=img_options,
)
```

---

## Advanced Usage

### Progress Callbacks

Track conversion progress with custom callbacks.

#### Callback Signature

```python
def progress_callback(progress: int, message: str) -> None:
    """
    Args:
        progress: Progress percentage (0-100)
        message: Status message
    """
    pass
```

#### Progress Stages

| Progress | Stage |
|----------|-------|
| 5% | Loading dictionary and parsing input |
| 10-70% | Processing lessons |
| 75% | Merging CSS styles |
| 85% | Embedding images |
| 90% | Writing HTML file |
| 80-90% | PDF/Image conversion |
| 100% | Completed |

#### Example Implementations

**Simple progress bar:**

```python
def simple_progress(progress: int, message: str):
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {progress}%", end="", flush=True)
    if progress == 100:
        print()
```

**Detailed logging:**

```python
import logging

def detailed_progress(progress: int, message: str):
    logging.info(f"[{progress:3d}%] {message}")
```

**Progress class:**

```python
class ProgressTracker:
    def __init__(self):
        self.start_time = time.time()
    
    def __call__(self, progress: int, message: str):
        elapsed = time.time() - self.start_time
        print(f"[{progress}%] {message} (elapsed: {elapsed:.1f}s)")

tracker = ProgressTracker()
mdx2html(..., progress_callback=tracker)
```

---

### Error Handling

All functions handle errors gracefully and return appropriate values.

#### Dictionary Lookup

```python
with Dictionary("dict.mdx") as dict:
    result = dict.lookup_html("word")
    if not result:
        print("Word not found")
    else:
        print("Found definition")
```

#### Conversion Functions

```python
try:
    found, not_found, invalid = mdx2html(
        mdx_file="dict.mdx",
        input_file="words.txt",
        output_file="output.html"
    )
    
    # Check results
    if not_found > 0:
        print(f"Warning: {not_found} words not found")
        for lesson, words in invalid.items():
            print(f"{lesson}: {', '.join(words)}")
            
except FileNotFoundError as e:
    print(f"File not found: {e}")
except RuntimeError as e:
    print(f"Conversion failed: {e}")
```

---

### Working with Invalid Words

Handle words that were not found in the dictionary.

```python
found, not_found, invalid_words = mdx2html(
    mdx_file="dict.mdx",
    input_file="words.txt",
    output_file="output.html"
)

# Save invalid words to a file
if invalid_words:
    with open("invalid.txt", "w", encoding="utf-8") as f:
        for lesson, words in invalid_words.items():
            f.write(f"# {lesson}\n")
            for word in words:
                f.write(f"{word}\n")
            f.write("\n")

# Try with another dictionary
if invalid_words:
    print("Trying alternative dictionary...")
    found2, not_found2, invalid2 = mdx2html(
        mdx_file="alternative_dict.mdx",
        input_file="invalid.txt",
        output_file="output_alternative.html"
    )
```

---

## Configuration Options

### Custom Styles

Apply custom CSS styles to the output HTML.

#### Inline Styles

```python
mdx2html(
    ...,
    h1_style="color: #333; font-size: 24px;",
    scrap_style="border: 1px solid #ddd; padding: 10px;"
)
```

#### Additional CSS

```python
additional_styles = """
    body {
        font-family: 'Georgia', serif;
        line-height: 1.8;
        max-width: 900px;
        margin: 0 auto;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
    }
    
    .scrapedword {
        background: #f8f9fa;
        border-radius: 4px;
        padding: 15px;
        margin: 10px 0;
    }
"""

mdx2html(..., additional_styles=additional_styles)
```

---

### Table of Contents

Control whether to include a table of contents.

```python
# With TOC (default)
mdx2html(..., with_toc=True)

# Without TOC
mdx2html(..., with_toc=False)
```

---

### PDF-Specific Options

Detailed PDF conversion options for `mdx2pdf`.

```python
pdf_options = {
    # Page setup
    "page-size": "A4",              # A4, Letter, Legal, etc.
    "orientation": "Portrait",       # Portrait or Landscape
    
    # Margins
    "margin-top": "20mm",
    "margin-bottom": "20mm",
    "margin-left": "15mm",
    "margin-right": "15mm",
    
    # Quality
    "dpi": 300,                     # Higher = better quality
    "image-dpi": 300,
    "image-quality": 94,
    
    # Headers/Footers
    "header-html": "header.html",   # Custom header
    "footer-html": "footer.html",   # Custom footer
    
    # Other
    "encoding": "UTF-8",
    "enable-local-file-access": "",
}
```

---

### Image-Specific Options

Detailed image conversion options for `mdx2img`.

```python
# PNG with optimization
img_options = {
    "width": "1024",
    "png_optimize": True,
    "png_compress_level": 9,  # Max compression
}

# JPEG with quality
img_options = {
    "width": "800",
    "quality": "90",  # High quality
}

# WEBP with lossless
img_options = {
    "width": "1200",
    "webp_lossless": True,
    "webp_quality": 100,
}
```

---

## Complete Example

Putting it all together:

```python
from pathlib import Path
from mdxscraper import Dictionary, WordParser, mdx2html

# Setup paths
MDX_FILE = Path("data/mdict/my_dict.mdx")
INPUT_FILE = Path("data/input/words.txt")
OUTPUT_DIR = Path("data/output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. Parse input file
print("Parsing input file...")
parser = WordParser(str(INPUT_FILE))
lessons = parser.parse()
print(f"Found {len(lessons)} lessons")

# 2. Test dictionary query
print("\nTesting dictionary...")
with Dictionary(MDX_FILE) as dict:
    test_word = lessons[0]['words'][0]
    result = dict.lookup_html(test_word)
    if result:
        print(f"✓ Dictionary working (tested: {test_word})")
    else:
        print(f"✗ Dictionary issue (word not found: {test_word})")

# 3. Convert with progress tracking
print("\nConverting to HTML...")

def progress_callback(progress: int, message: str):
    print(f"[{progress:3d}%] {message}")

custom_css = """
    body { 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto;
        max-width: 900px;
        margin: 20px auto;
    }
    h1 { color: #2c3e50; }
    .scrapedword { 
        border-left: 4px solid #3498db;
        padding: 15px;
        margin: 15px 0;
    }
"""

output_file = OUTPUT_DIR / "output.html"
found, not_found, invalid_words = mdx2html(
    mdx_file=MDX_FILE,
    input_file=INPUT_FILE,
    output_file=output_file,
    with_toc=True,
    additional_styles=custom_css,
    progress_callback=progress_callback,
)

# 4. Report results
print(f"\n✅ Conversion complete!")
print(f"   Output: {output_file}")
print(f"   Found: {found} words")
print(f"   Not found: {not_found} words")

if invalid_words:
    invalid_file = OUTPUT_DIR / "invalid_words.txt"
    with open(invalid_file, "w", encoding="utf-8") as f:
        for lesson, words in invalid_words.items():
            f.write(f"# {lesson}\n")
            for word in words:
                f.write(f"{word}\n")
    print(f"   Invalid words saved to: {invalid_file}")
```

---

## See Also

- [Examples Directory](../examples/): Complete working examples
- [Main README](../README.md): Project overview
- [Development Guide](../docs/Development_Guide.md): Architecture and development
