"""Basic MDX diction    # Check if dictionary file exists
    if not mdx_file.exists():
        print(f"❌ Dictionary file not found: {mdx_file}")
        print("   Please specify a valid MDX file path.")
        return

    # Open dictionary using context manager
    with Dictionary(mdx_file) as dict:y example.

This example demonstrates how to use MdxScraper as a headless library
to query words from an MDX dictionary.
"""

import argparse
from pathlib import Path

from mdxscraper import Dictionary

# Default paths
DEFAULT_MDX_FILE = Path("data/mdict/your_dictionary.mdx")


def basic_query_example(mdx_file: Path):
    """Basic dictionary query example."""
    print("=" * 60)
    print("Basic MDX Dictionary Query Example")
    print("=" * 60)

    # Check if dictionary file exists
    if not mdx_file.exists():
        print(f"❌ Dictionary file not found: {mdx_file}")
        print("   Please specify a valid MDX file path.")
        return

    # Open dictionary using context manager
    with Dictionary(mdx_file) as dict:
        # List of words to query
        words = ["hello", "world", "python"]

        for word in words:
            print(f"\n📖 Looking up '{word}'...")

            # Lookup word in dictionary
            result = dict.lookup_html(word)

            if result:
                # Display result (truncated for readability)
                preview = result[:200] if len(result) > 200 else result
                print(f"✓ Found definition:")
                print(f"  {preview}...")
            else:
                print(f"✗ Word not found")


def advanced_query_example(mdx_file: Path):
    """Advanced query with fallback strategies."""
    print("\n" + "=" * 60)
    print("Advanced Query with Fallback Strategies")
    print("=" * 60)

    if not mdx_file.exists():
        print(f"❌ Dictionary file not found: {mdx_file}")
        return

    with Dictionary(mdx_file) as dict:
        # The Dictionary class automatically handles:
        # 1. Exact match
        # 2. Case-insensitive match
        # 3. Hyphen removal + case-insensitive match
        # 4. @@@LINK= redirect following

        words = ["Hello", "WORLD", "non-existent"]

        for word in words:
            print(f"\n📖 Looking up '{word}'...")
            result = dict.lookup_html(word)

            if result:
                print(f"✓ Found (with automatic fallback)")
            else:
                print(f"✗ Not found after all fallback attempts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Basic MDX dictionary query example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mdx",
        type=Path,
        default=DEFAULT_MDX_FILE,
        help=f"Path to MDX dictionary file (default: {DEFAULT_MDX_FILE})",
    )
    args = parser.parse_args()

    basic_query_example(args.mdx)
    advanced_query_example(args.mdx)

    print("\n" + "=" * 60)
    print("✅ Example completed!")
    print("=" * 60)
