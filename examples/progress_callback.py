"""Progress callback example.

This example demonstrates how to track conversion progress using callbacks,
useful for integrating MdxScraper into other applications or CLI tools.
"""

import argparse
from pathlib import Path

from mdxscraper import mdx2html

# Default configuration
DEFAULT_MDX_FILE = Path("data/mdict/your_dictionary.mdx")
DEFAULT_INPUT_FILE = Path("data/input/words_to_lookup.txt")
DEFAULT_OUTPUT_DIR = Path("data/output")


def simple_progress_callback(progress: int, message: str):
    """Simple progress callback that prints to console."""
    # Print progress bar
    bar_length = 40
    filled = int(bar_length * progress / 100)
    bar = "█" * filled + "░" * (bar_length - filled)

    # Print on same line
    print(f"\r[{bar}] {progress}% - {message}", end="", flush=True)

    # Print newline when complete
    if progress == 100:
        print()


def detailed_progress_callback(progress: int, message: str):
    """Detailed progress callback with status messages."""
    status_icon = "⏳"
    if progress == 100:
        status_icon = "✅"
    elif progress >= 90:
        status_icon = "🎉"
    elif progress >= 50:
        status_icon = "⚡"

    print(f"{status_icon} [{progress:3d}%] {message}")


class ProgressTracker:
    """Progress tracker class for more advanced progress handling."""

    def __init__(self):
        self.start_time = None
        self.last_progress = 0

    def __call__(self, progress: int, message: str):
        """Track and display progress with timing information."""
        import time

        if self.start_time is None:
            self.start_time = time.time()

        elapsed = time.time() - self.start_time

        # Calculate estimated time remaining
        if progress > 0:
            total_time = elapsed / progress * 100
            remaining = total_time - elapsed
            eta = f"ETA: {remaining:.1f}s"
        else:
            eta = "ETA: calculating..."

        # Show progress
        bar_length = 30
        filled = int(bar_length * progress / 100)
        bar = "█" * filled + "░" * (bar_length - filled)

        print(
            f"\r[{bar}] {progress:3d}% | {elapsed:.1f}s | {eta} | {message:<40}",
            end="",
            flush=True,
        )

        if progress == 100:
            print(f"\n✅ Completed in {elapsed:.2f}s")


def progress_callback_example(mdx_file: Path, input_file: Path, output_dir: Path):
    """Demonstrate progress callback usage."""
    print("=" * 60)
    print("Progress Callback Example")
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

    # Example 1: Simple progress bar
    print("\n1️⃣  Simple Progress Bar:")
    print("-" * 60)

    output_file = output_dir / "progress_simple.html"
    found, not_found, invalid = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        progress_callback=simple_progress_callback,
    )
    print(f"   Result: {found} found, {not_found} not found")

    # Example 2: Detailed status messages
    print("\n2️⃣  Detailed Status Messages:")
    print("-" * 60)

    output_file = output_dir / "progress_detailed.html"
    found, not_found, invalid = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        progress_callback=detailed_progress_callback,
    )
    print(f"   Result: {found} found, {not_found} not found")

    # Example 3: Progress tracker with timing
    print("\n3️⃣  Progress Tracker with Timing:")
    print("-" * 60)

    output_file = output_dir / "progress_tracked.html"
    tracker = ProgressTracker()
    found, not_found, invalid = mdx2html(
        mdx_file=mdx_file,
        input_file=input_file,
        output_file=output_file,
        progress_callback=tracker,
    )
    print(f"   Result: {found} found, {not_found} not found")

    print("\n" + "=" * 60)
    print("✅ Progress callback examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Progress callback example",
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

    progress_callback_example(args.mdx_file, args.input_file, args.output_dir)
