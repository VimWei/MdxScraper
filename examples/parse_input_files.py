"""Input file parsing example.

This example demonstrates how to parse different input file formats
(TXT, Markdown, JSON, Excel) using MdxScraper's WordParser.
"""

from pathlib import Path

from mdxscraper import WordParser

# Configuration
EXAMPLES_DIR = Path(__file__).parent
SAMPLE_DATA_DIR = EXAMPLES_DIR / "sample_data"


def create_sample_files():
    """Create sample input files for demonstration."""
    SAMPLE_DATA_DIR.mkdir(exist_ok=True)

    # 1. Simple TXT file
    txt_file = SAMPLE_DATA_DIR / "words.txt"
    txt_file.write_text(
        """# Lesson 1: Basic Words
hello
world
python

# Lesson 2: Advanced Words
dictionary
library
framework
""",
        encoding="utf-8",
    )

    # 2. Markdown file
    md_file = SAMPLE_DATA_DIR / "words.md"
    md_file.write_text(
        """# English Vocabulary

## Chapter 1: Greetings
hello
hi
goodbye

## Chapter 2: Common Verbs
go
come
see
""",
        encoding="utf-8",
    )

    # 3. JSON file
    import json

    json_file = SAMPLE_DATA_DIR / "words.json"
    json_data = [
        {"name": "Programming Terms", "words": ["python", "java", "javascript"]},
        {"name": "Data Types", "words": ["string", "integer", "boolean"]},
    ]
    json_file.write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"✓ Sample files created in: {SAMPLE_DATA_DIR}")


def parse_txt_example():
    """Parse a TXT file."""
    print("\n📄 Parsing TXT file...")

    txt_file = SAMPLE_DATA_DIR / "words.txt"
    parser = WordParser(str(txt_file))
    lessons = parser.parse()

    print(f"✓ Found {len(lessons)} lessons:")
    for lesson in lessons:
        print(f"  - {lesson['name']}: {len(lesson['words'])} words")
        print(f"    Words: {', '.join(lesson['words'][:5])}...")


def parse_markdown_example():
    """Parse a Markdown file."""
    print("\n📝 Parsing Markdown file...")

    md_file = SAMPLE_DATA_DIR / "words.md"
    parser = WordParser(str(md_file))
    lessons = parser.parse()

    print(f"✓ Found {len(lessons)} lessons:")
    for lesson in lessons:
        print(f"  - {lesson['name']}: {len(lesson['words'])} words")
        print(f"    Words: {', '.join(lesson['words'])}")


def parse_json_example():
    """Parse a JSON file."""
    print("\n📊 Parsing JSON file...")

    json_file = SAMPLE_DATA_DIR / "words.json"
    parser = WordParser(str(json_file))
    lessons = parser.parse()

    print(f"✓ Found {len(lessons)} lessons:")
    for lesson in lessons:
        print(f"  - {lesson['name']}: {len(lesson['words'])} words")
        print(f"    Words: {', '.join(lesson['words'])}")


def parse_input_files_example():
    """Demonstrate parsing different input file formats."""
    print("=" * 60)
    print("Input File Parsing Example")
    print("=" * 60)

    # Create sample files
    create_sample_files()

    # Parse different formats
    parse_txt_example()
    parse_markdown_example()
    parse_json_example()

    print("\n" + "=" * 60)
    print("✅ Parsing examples completed!")
    print("=" * 60)

    print("\nℹ️  Note: WordParser also supports Excel files (.xls, .xlsx)")
    print("   Each sheet in the Excel file becomes a lesson.")


if __name__ == "__main__":
    parse_input_files_example()
