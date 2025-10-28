# MdxScraper Headless Library - Quick Start Guide

Get started with MdxScraper as a headless library in 5 minutes.

## Installation

### Option 1: Install Core Library Only (Recommended)

For using as a headless library without GUI:

```bash
# Clone repository
git clone https://github.com/VimWei/MdxScraper
cd MdxScraper

# Install core dependencies only
uv sync
```

This installs minimal dependencies:
- beautifulsoup4 (HTML parsing)
- lxml (XML/HTML processing)
- chardet (encoding detection)
- openpyxl (Excel support)
- Pillow (image processing)

### Option 2: Install with Conversion Support

Add PDF/Image conversion capabilities:

```bash
uv sync --extra conversion
```

Additional dependencies:
- pdfkit (PDF conversion)
- imgkit (Image conversion)

**Note:** Also requires [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) system installation.

### Option 3: Full Installation

Install everything including GUI:

```bash
uv sync --all-extras
```

## 5-Minute Tutorial

### Step 1: Prepare Your Files

Create a simple word list file `words.txt`:

```text
# Basic Words
hello
world
python

# Advanced Words
dictionary
library
```

### Step 2: Basic Query

```python
# query.py
from mdxscraper import Dictionary

# Open dictionary
with Dictionary("path/to/your_dict.mdx") as dict:
    # Query a word
    result = dict.lookup_html("hello")
    
    if result:
        print("✓ Found definition:")
        print(result[:200], "...")
    else:
        print("✗ Word not found")
```

Run it:
```bash
uv run python query.py
```

### Step 3: Batch Conversion

```python
# convert.py
from pathlib import Path
from mdxscraper import mdx2html

# Setup paths
MDX_FILE = Path("path/to/your_dict.mdx")
INPUT_FILE = Path("words.txt")
OUTPUT_FILE = Path("output.html")

# Convert to HTML
found, not_found, invalid = mdx2html(
    mdx_file=MDX_FILE,
    input_file=INPUT_FILE,
    output_file=OUTPUT_FILE,
    with_toc=True,
)

print(f"✅ Complete!")
print(f"   Found: {found} words")
print(f"   Not found: {not_found} words")
print(f"   Output: {OUTPUT_FILE}")
```

Run it:
```bash
uv run python convert.py
```

### Step 4: Add Progress Tracking

```python
# convert_with_progress.py
from pathlib import Path
from mdxscraper import mdx2html

def show_progress(progress: int, message: str):
    """Simple progress display"""
    bar_length = 30
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"\r[{bar}] {progress}% - {message}", end="", flush=True)
    if progress == 100:
        print()  # New line when complete

# Convert with progress
found, not_found, invalid = mdx2html(
    mdx_file="your_dict.mdx",
    input_file="words.txt",
    output_file="output.html",
    progress_callback=show_progress,
)
```

### Step 5: Custom Styling

```python
# custom_style.py
from mdxscraper import mdx2html

# Define custom CSS
custom_css = """
    body {
        font-family: 'Arial', sans-serif;
        max-width: 900px;
        margin: 20px auto;
        padding: 20px;
        background: #f5f5f5;
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
    }
    
    .scrapedword {
        background: white;
        border-left: 4px solid #3498db;
        padding: 20px;
        margin: 15px 0;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .left a {
        color: #3498db;
        text-decoration: none;
        padding: 5px 10px;
        display: block;
        border-radius: 3px;
        transition: background 0.2s;
    }
    
    .left a:hover {
        background: #ecf0f1;
    }
"""

# Convert with custom style
found, not_found, invalid = mdx2html(
    mdx_file="your_dict.mdx",
    input_file="words.txt",
    output_file="styled_output.html",
    additional_styles=custom_css,
)

print(f"✅ Styled HTML created!")
```

## Common Use Cases

### Use Case 1: Automated Word List Processing

```python
from pathlib import Path
from mdxscraper import mdx2html

def process_word_list(input_file: Path, output_dir: Path):
    """Process a word list and save results."""
    output_file = output_dir / f"{input_file.stem}.html"
    
    found, not_found, invalid = mdx2html(
        mdx_file="dict.mdx",
        input_file=input_file,
        output_file=output_file,
    )
    
    return {
        "input": str(input_file),
        "output": str(output_file),
        "found": found,
        "not_found": not_found,
    }

# Process multiple files
input_dir = Path("input")
output_dir = Path("output")
output_dir.mkdir(exist_ok=True)

for txt_file in input_dir.glob("*.txt"):
    result = process_word_list(txt_file, output_dir)
    print(f"Processed {result['input']}: {result['found']} words found")
```

### Use Case 2: Web Service Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mdxscraper import Dictionary
import tempfile
from pathlib import Path

app = FastAPI()

# Global dictionary instance
dict_cache = {}

class QueryRequest(BaseModel):
    dict_name: str
    word: str

@app.post("/query")
async def query_word(request: QueryRequest):
    """Query a word from dictionary."""
    # Load dictionary (with caching)
    if request.dict_name not in dict_cache:
        dict_path = Path(f"dicts/{request.dict_name}.mdx")
        if not dict_path.exists():
            raise HTTPException(404, "Dictionary not found")
        dict_cache[request.dict_name] = Dictionary(dict_path)
    
    # Query word
    dict = dict_cache[request.dict_name]
    result = dict.lookup_html(request.word)
    
    if not result:
        raise HTTPException(404, "Word not found")
    
    return {"word": request.word, "definition": result}

# Usage:
# curl -X POST http://localhost:8000/query \
#   -H "Content-Type: application/json" \
#   -d '{"dict_name": "mydict", "word": "hello"}'
```

### Use Case 3: CLI Tool

```python
#!/usr/bin/env python3
"""Simple CLI tool for dictionary queries."""

import sys
import argparse
from pathlib import Path
from mdxscraper import Dictionary, mdx2html

def cmd_query(args):
    """Query a single word."""
    with Dictionary(args.dict) as dict:
        result = dict.lookup_html(args.word)
        if result:
            print(result)
        else:
            print(f"Word not found: {args.word}", file=sys.stderr)
            sys.exit(1)

def cmd_convert(args):
    """Convert word list to HTML."""
    found, not_found, invalid = mdx2html(
        mdx_file=args.dict,
        input_file=args.input,
        output_file=args.output,
        with_toc=not args.no_toc,
    )
    print(f"Found: {found}, Not found: {not_found}")

def main():
    parser = argparse.ArgumentParser(description="MDX Dictionary Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query a word")
    query_parser.add_argument("dict", help="Path to MDX dictionary")
    query_parser.add_argument("word", help="Word to query")
    query_parser.set_defaults(func=cmd_query)
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert word list")
    convert_parser.add_argument("dict", help="Path to MDX dictionary")
    convert_parser.add_argument("input", help="Input word list")
    convert_parser.add_argument("output", help="Output HTML file")
    convert_parser.add_argument("--no-toc", action="store_true", help="Disable TOC")
    convert_parser.set_defaults(func=cmd_convert)
    
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

# Usage:
# python cli.py query dict.mdx hello
# python cli.py convert dict.mdx words.txt output.html
```

## Troubleshooting

### Problem: Dictionary file not found

```python
from pathlib import Path

mdx_file = Path("dict.mdx")
if not mdx_file.exists():
    print(f"❌ Dictionary not found: {mdx_file}")
    print(f"   Absolute path: {mdx_file.absolute()}")
    print(f"   Current directory: {Path.cwd()}")
```

### Problem: Word not found

The Dictionary class uses automatic fallback strategies:
1. Exact match
2. Case-insensitive match
3. Hyphen removal + case-insensitive
4. Follow @@@LINK= redirects

If still not found, the word may not exist in your dictionary. Try a different dictionary or check the spelling.

### Problem: PDF/Image conversion fails

Ensure wkhtmltopdf is installed:

```bash
# Check if installed
wkhtmltopdf --version

# Install on Ubuntu/Debian
sudo apt-get install wkhtmltopdf

# Install on macOS
brew install wkhtmltopdf

# Windows: Download from https://wkhtmltopdf.org/downloads.html
```

### Problem: Import errors

```python
# Verify installation
try:
    from mdxscraper import Dictionary, mdx2html
    print("✓ MdxScraper imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("   Run: uv sync")
```

## Next Steps

1. **Explore Examples**: Check out the [examples/](../examples/) directory for complete working examples
2. **Read API Docs**: See [HEADLESS_API.md](HEADLESS_API.md) for detailed API reference
3. **Customize**: Experiment with custom CSS styles and conversion options
4. **Integrate**: Use in your web services, CLI tools, or automation scripts

## Getting Help

- 📖 Documentation: [docs/](../docs/)
- 💻 Examples: [examples/](../examples/)
- 🐛 Issues: [GitHub Issues](https://github.com/VimWei/MdxScraper/issues)
- 📝 Main README: [README.md](../README.md)

Happy coding! 🎉
