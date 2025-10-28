"""Single word query with complete HTML output.

This example demonstrates how to query a single word from an MDX dictionary
and output the complete HTML definition with embedded CSS and images.
"""

import argparse
from pathlib import Path

from mdxscraper import Dictionary
from mdxscraper.core.renderer import merge_css, embed_images


def query_single_word_simple(mdx_file: Path, word: str, output_file: Path = None):
    """Query a single word and get the raw HTML definition.
    
    Args:
        mdx_file: Path to MDX dictionary file
        word: Word to query
        output_file: Optional path to save HTML output
        
    Returns:
        HTML string of the word definition
    """
    print(f"📖 Querying word: '{word}'")
    print(f"📚 Dictionary: {mdx_file}")
    
    with Dictionary(mdx_file) as dict:
        # Get raw HTML definition
        result = dict.lookup_html(word)
        
        if not result:
            print(f"❌ Word '{word}' not found in dictionary")
            return None
        
        print(f"✅ Found definition ({len(result)} characters)")
        
        # Save to file if specified
        if output_file:
            output_file.write_text(result, encoding='utf-8')
            print(f"💾 Saved to: {output_file}")
        
        return result


def query_single_word_complete(
    mdx_file: Path, 
    word: str, 
    output_file: Path = None,
    include_css: bool = True,
    include_images: bool = True,
):
    """Query a single word and generate complete standalone HTML.
    
    Args:
        mdx_file: Path to MDX dictionary file
        word: Word to query
        output_file: Optional path to save HTML output
        include_css: Whether to merge and embed CSS
        include_images: Whether to embed images as base64
        
    Returns:
        Complete HTML string with CSS and images embedded
    """
    print(f"📖 Querying word: '{word}' (complete mode)")
    print(f"📚 Dictionary: {mdx_file}")
    
    with Dictionary(mdx_file) as dict:
        # Get raw HTML definition
        result = dict.lookup_html(word)
        
        if not result:
            print(f"❌ Word '{word}' not found in dictionary")
            return None
        
        print(f"✅ Found definition")
        
        # Build complete HTML structure
        html_parts = []
        
        # HTML header
        html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word}</title>
""".format(word=word))
        
        # Add CSS if requested
        if include_css:
            print("🎨 Merging CSS styles...")
            css_content = merge_css(str(mdx_file.parent), result)
            if css_content:
                html_parts.append(f"    <style>\n{css_content}\n    </style>\n")
        
        # Default minimal styling
        html_parts.append("""    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            background-color: #fff;
            color: #333;
        }
        .word-entry {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            background-color: #f9f9f9;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="word-entry">
        <h1>{word}</h1>
""".format(word=word))
        
        # Add word definition
        html_parts.append(result)
        
        # Close HTML
        html_parts.append("""
    </div>
</body>
</html>""")
        
        complete_html = "".join(html_parts)
        
        # Embed images if requested
        if include_images:
            print("🖼️  Embedding images...")
            complete_html = embed_images(str(mdx_file.parent), complete_html)
        
        # Save to file if specified
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(complete_html, encoding='utf-8')
            print(f"💾 Saved complete HTML to: {output_file}")
            print(f"📊 Total size: {len(complete_html):,} characters")
        
        return complete_html


def query_word_with_custom_css(
    mdx_file: Path,
    word: str,
    output_file: Path = None,
    custom_css: str = None,
):
    """Query a single word and apply custom CSS styling.
    
    Args:
        mdx_file: Path to MDX dictionary file
        word: Word to query
        output_file: Optional path to save HTML output
        custom_css: Custom CSS string to apply
        
    Returns:
        HTML string with custom CSS applied
    """
    print(f"📖 Querying word: '{word}' (custom CSS mode)")
    
    with Dictionary(mdx_file) as dict:
        result = dict.lookup_html(word)
        
        if not result:
            print(f"❌ Word '{word}' not found")
            return None
        
        # Default clean CSS if none provided
        if not custom_css:
            custom_css = """
        body {
            font-family: Georgia, serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(to bottom, #f0f0f0, #ffffff);
        }
        .word-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .word-title {
            font-size: 2.5em;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        .definition {
            font-size: 1.1em;
            color: #34495e;
        }
        """
        
        # Build HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word}</title>
    <style>
{custom_css}
    </style>
</head>
<body>
    <div class="word-container">
        <h1 class="word-title">{word}</h1>
        <div class="definition">
{result}
        </div>
    </div>
</body>
</html>"""
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(html, encoding='utf-8')
            print(f"💾 Saved to: {output_file}")
        
        return html


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Query a single word from MDX dictionary and output complete HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple query (raw HTML)
  python single_word_query.py hello

  # Save to file
  python single_word_query.py hello --output hello.html

  # Complete mode with CSS and images
  python single_word_query.py hello --output hello.html --complete

  # Custom CSS mode
  python single_word_query.py hello --output hello.html --custom-css

  # Specify dictionary
  python single_word_query.py hello --mdx-file data/mdict/dict.mdx --output out.html
        """
    )
    
    parser.add_argument(
        "word",
        help="Word to query"
    )
    
    parser.add_argument(
        "--mdx-file",
        type=Path,
        default=Path("data/mdict/your_dictionary.mdx"),
        help="Path to MDX dictionary file (default: data/mdict/your_dictionary.mdx)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output HTML file path"
    )
    
    parser.add_argument(
        "--complete",
        action="store_true",
        help="Generate complete HTML with embedded CSS and images"
    )
    
    parser.add_argument(
        "--custom-css",
        action="store_true",
        help="Apply custom CSS styling"
    )
    
    parser.add_argument(
        "--no-css",
        action="store_true",
        help="Don't include CSS (complete mode only)"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Don't embed images (complete mode only)"
    )
    
    args = parser.parse_args()
    
    # Check if dictionary exists
    if not args.mdx_file.exists():
        print(f"❌ Dictionary file not found: {args.mdx_file}")
        print("   Please specify a valid MDX file path with --mdx-file")
        return 1
    
    print("=" * 70)
    print("Single Word Query")
    print("=" * 70)
    
    # Choose mode
    if args.custom_css:
        result = query_word_with_custom_css(
            args.mdx_file,
            args.word,
            args.output
        )
    elif args.complete:
        result = query_single_word_complete(
            args.mdx_file,
            args.word,
            args.output,
            include_css=not args.no_css,
            include_images=not args.no_images
        )
    else:
        result = query_single_word_simple(
            args.mdx_file,
            args.word,
            args.output
        )
    
    if result:
        if not args.output:
            print("\n" + "=" * 70)
            print("HTML Output (first 500 characters):")
            print("=" * 70)
            print(result[:500])
            if len(result) > 500:
                print(f"\n... ({len(result) - 500} more characters)")
        
        print("\n" + "=" * 70)
        print("✅ Query completed successfully!")
        print("=" * 70)
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
