"""Custom styles example.

This example demonstrates how to apply custom CSS styles when converting
MDX dictionary results to HTML/PDF/images.
"""

import argparse
from pathlib import Path

from mdxscraper import mdx2html

# Default configuration
DEFAULT_MDX_FILE = Path("data/mdict/your_dictionary.mdx")
DEFAULT_INPUT_FILE = Path("data/input/words_to_lookup.txt")
DEFAULT_OUTPUT_DIR = Path("data/output")


def minimal_style_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Create HTML with minimal, clean styling."""
    print("\n📄 Creating HTML with minimal style...")

    output_file = output_dir / "minimal_style.html"

    # Custom CSS for minimal design
    additional_styles = """
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }
        .scrapedword {
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 15px 0;
            border-radius: 4px;
        }
        .left a {
            color: #3498db;
            text-decoration: none;
            display: block;
            padding: 5px 0;
        }
        .left a:hover {
            color: #2980b9;
            text-decoration: underline;
        }
    """

    found, not_found, invalid_words = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        with_toc=True,
        additional_styles=additional_styles,
    )

    print(f"✓ Minimal style HTML saved to: {output_file}")
    return invalid_words


def dark_theme_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Create HTML with dark theme styling."""
    print("\n🌙 Creating HTML with dark theme...")

    output_file = output_dir / "dark_theme.html"

    # Custom CSS for dark theme
    additional_styles = """
        body {
            font-family: "Consolas", "Monaco", monospace;
            line-height: 1.6;
            color: #e0e0e0;
            background-color: #1e1e1e;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #61dafb;
            border-bottom: 2px solid #61dafb;
            padding-bottom: 10px;
            margin-top: 30px;
            text-shadow: 0 0 10px rgba(97, 218, 251, 0.5);
        }
        .scrapedword {
            background-color: #2d2d2d;
            border: 1px solid #404040;
            padding: 15px;
            margin: 15px 0;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }
        .left {
            background-color: #252525;
            padding: 15px;
            border-radius: 6px;
        }
        .left a {
            color: #61dafb;
            text-decoration: none;
            display: block;
            padding: 5px 10px;
            border-radius: 3px;
            transition: background-color 0.2s;
        }
        .left a:hover {
            background-color: #404040;
        }
        .main {
            display: flex;
            gap: 20px;
        }
        .left {
            flex: 0 0 200px;
        }
        .right {
            flex: 1;
        }
    """

    found, not_found, invalid_words = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        with_toc=True,
        additional_styles=additional_styles,
    )

    print(f"✓ Dark theme HTML saved to: {output_file}")
    return invalid_words


def print_ready_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Create HTML optimized for printing."""
    print("\n🖨️  Creating HTML optimized for printing...")

    output_file = output_dir / "print_ready.html"

    # Custom CSS for print
    additional_styles = """
        @media print {
            body {
                font-size: 12pt;
                line-height: 1.4;
            }
            .left {
                display: none;  /* Hide TOC when printing */
            }
            h1 {
                page-break-before: always;
                page-break-after: avoid;
            }
            .scrapedword {
                page-break-inside: avoid;
            }
        }
        body {
            font-family: "Times New Roman", Times, serif;
            max-width: 100%;
            margin: 0 auto;
            padding: 20mm;
        }
        h1 {
            color: #000;
            font-size: 18pt;
            border-bottom: 1px solid #000;
            padding-bottom: 5pt;
        }
        .scrapedword {
            border: 1px solid #ccc;
            padding: 10pt;
            margin: 10pt 0;
        }
    """

    found, not_found, invalid_words = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        with_toc=True,
        additional_styles=additional_styles,
    )

    print(f"✓ Print-ready HTML saved to: {output_file}")
    return invalid_words


def custom_styles_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Demonstrate various custom styling options."""
    print("=" * 60)
    print("Custom Styles Example")
    print("=" * 60)

    # Check if input files exist
    if not mdx_file.exists():
        print(f"❌ Dictionary file not found: {mdx_file}")
        print("   Please specify a valid MDX file path.")
        return

    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        print("   Please specify a valid input file path.")
        return

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate different styled versions
    minimal_style_example(mdx_file, input_file, output_dir)
    dark_theme_example(mdx_file, input_file, output_dir)
    print_ready_example(mdx_file, input_file, output_dir)

    print("\n" + "=" * 60)
    print("✅ Custom styles examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Custom styles example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mdx-file",
        type=Path,
        default=DEFAULT_MDX_FILE,
        help=f"Path to MDX dictionary file (default: {DEFAULT_MDX_FILE})",
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=DEFAULT_INPUT_FILE,
        help=f"Path to input word list file (default: {DEFAULT_INPUT_FILE})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    args = parser.parse_args()

    custom_styles_example(args.mdx_file, args.input_file, args.output_dir)
