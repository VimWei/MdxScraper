"""Batch conversion example.

This example demonstrates how to convert multiple word lists to HTML, PDF, and images
using MdxScraper as a headless library.
"""

import argparse
from datetime import datetime
from pathlib import Path

from mdxscraper import mdx2html, mdx2img, mdx2pdf

# Default configuration
DEFAULT_MDX_FILE = Path("data/mdict/your_dictionary.mdx")
DEFAULT_INPUT_FILE = Path("data/input/words_to_lookup.txt")
DEFAULT_OUTPUT_DIR = Path("data/output")


def convert_to_html(mdx_file: Path, input_file: Path, output_dir: Path):
    """Convert word list to HTML with table of contents."""
    print("\n📄 Converting to HTML...")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{timestamp}_{input_file.stem}.html"

    found, not_found, invalid_words = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        with_toc=True,  # Include table of contents
        h1_style="color: #333; font-size: 24px;",  # Custom heading style
        scrap_style="border: 1px solid #ddd; padding: 10px; margin: 10px 0;",
    )

    print(f"✓ HTML saved to: {output_file}")
    print(f"  Found: {found} words, Not found: {not_found} words")

    return invalid_words


def convert_to_pdf(mdx_file: Path, input_file: Path, output_dir: Path):
    """Convert word list to PDF."""
    print("\n📑 Converting to PDF...")

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{timestamp}_{input_file.stem}.pdf"

    # PDF conversion options
    pdf_options = {
        "page-size": "A4",
        "margin-top": "20mm",
        "margin-bottom": "20mm",
        "margin-left": "15mm",
        "margin-right": "15mm",
        "encoding": "UTF-8",
    }

    found, not_found, invalid_words = mdx2pdf(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        pdf_options=pdf_options,
        with_toc=True,
        wkhtmltopdf_path="auto",  # Auto-detect wkhtmltopdf
    )

    print(f"✓ PDF saved to: {output_file}")
    print(f"  Found: {found} words, Not found: {not_found} words")

    return invalid_words


def convert_to_image(mdx_file: Path, input_file: Path, output_dir: Path):
    """Convert word list to image (PNG/JPEG/WEBP)."""
    print("\n🖼️  Converting to image...")

    # You can choose different formats by changing the extension
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{timestamp}_{input_file.stem}.png"

    # Image conversion options
    img_options = {
        "width": "800",  # Image width in pixels
        "quality": "90",  # JPEG quality (1-100)
        "png_optimize": True,  # Optimize PNG
        "png_compress_level": 9,  # PNG compression (0-9)
    }

    found, not_found, invalid_words = mdx2img(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        img_options=img_options,
        with_toc=True,
    )

    print(f"✓ Image saved to: {output_file}")
    print(f"  Found: {found} words, Not found: {not_found} words")

    return invalid_words


def save_invalid_words(invalid_words: dict, input_file: Path, output_dir: Path):
    """Save invalid words to a file."""
    if not invalid_words:
        print("\n✅ All words found!")
        return

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"{timestamp}_{input_file.stem}_invalid_words.txt"
    
    print(f"\n⚠️  Saving {sum(len(v) for v in invalid_words.values())} invalid words...")

    with open(output_file, "w", encoding="utf-8") as f:
        for lesson, words in invalid_words.items():
            f.write(f"# {lesson}\n")
            for word in words:
                f.write(f"{word}\n")
            f.write("\n")

    print(f"✓ Invalid words saved to: {output_file}")


def batch_conversion_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Batch convert word list to multiple formats."""
    print("=" * 60)
    print("Batch Conversion Example")
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

    # Convert to different formats
    invalid_words_html = convert_to_html(mdx_file, input_file, output_dir)
    # invalid_words_pdf = convert_to_pdf(mdx_file, input_file, output_dir)  # Uncomment if wkhtmltopdf is installed
    # invalid_words_img = convert_to_image(mdx_file, input_file, output_dir)  # Uncomment if wkhtmltoimage is installed

    # Save invalid words
    save_invalid_words(invalid_words_html, input_file, output_dir)

    print("\n" + "=" * 60)
    print("✅ Batch conversion completed!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch conversion example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mdx",
        type=Path,
        default=DEFAULT_MDX_FILE,
        help=f"Path to MDX dictionary file (default: {DEFAULT_MDX_FILE})",
    )
    parser.add_argument(
        "--input",
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

    batch_conversion_example(args.mdx, args.input, args.output_dir)
