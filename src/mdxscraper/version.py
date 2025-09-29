"""Version information for MdxScraper.

This module provides version information for the MdxScraper application.
It uses uv as the primary source of version information, with fallback
to reading pyproject.toml directly.
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_version() -> str:
    """Get the current version from uv.

    Returns:
        str: The current version string (e.g., "5.0.0")

    Raises:
        RuntimeError: If version cannot be determined
    """
    try:
        # Try to get version from uv first
        result = subprocess.run(
            ["uv", "version", "--short"],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        version = result.stdout.strip()
        if version:
            return version
    except (subprocess.CalledProcessError, FileNotFoundError):
        # uv not available or failed, try fallback
        pass

    # Fallback to reading pyproject.toml directly
    return _get_version_from_pyproject()


def _get_version_from_pyproject() -> str:
    """Fallback method to read version from pyproject.toml.

    Returns:
        str: The version string from pyproject.toml

    Raises:
        RuntimeError: If version cannot be read from pyproject.toml
    """
    try:
        pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
        with open(pyproject_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("version = "):
                    # Extract version from line like: version = "5.0.0"
                    version = line.split('"')[1]
                    return version
    except (FileNotFoundError, IndexError) as e:
        pass

    raise RuntimeError("Could not determine version from uv or pyproject.toml")


def get_version_info() -> Tuple[int, ...]:
    """Get the current version as a tuple of integers.

    Returns:
        Tuple[int, ...]: Version tuple (e.g., (5, 0, 0))

    Example:
        >>> get_version_info()
        (5, 0, 0)
    """
    version_str = get_version()
    try:
        # Remove any pre-release suffixes (e.g., "5.0.0a1" -> "5.0.0")
        version_str = version_str.split("-")[0].split("+")[0]
        # Split by dots and convert to integers
        return tuple(map(int, version_str.split(".")))
    except ValueError:
        return (0, 0, 0)


def is_prerelease() -> bool:
    """Check if current version is a pre-release.

    Returns:
        bool: True if current version is a pre-release

    Example:
        >>> is_prerelease()
        False  # for version "5.0.0"
        True   # for version "5.0.0a1"
    """
    version_str = get_version()
    return any(suffix in version_str for suffix in ["a", "b", "rc", "dev"])


def get_version_display() -> str:
    """Get version string formatted for display.

    Returns:
        str: Formatted version string (e.g., "v5.0.0")
    """
    return f"v{get_version()}"


def get_full_version_info() -> dict:
    """Get comprehensive version information.

    Returns:
        dict: Dictionary containing version information

    Example:
        >>> get_full_version_info()
        {
            'version': '5.0.0',
            'version_info': (5, 0, 0),
            'display': 'v5.0.0',
            'is_prerelease': False,
            'major': 5,
            'minor': 0,
            'patch': 0
        }
    """
    version = get_version()
    version_info = get_version_info()

    return {
        "version": version,
        "version_info": version_info,
        "display": get_version_display(),
        "is_prerelease": is_prerelease(),
        "major": version_info[0] if len(version_info) > 0 else 0,
        "minor": version_info[1] if len(version_info) > 1 else 0,
        "patch": version_info[2] if len(version_info) > 2 else 0,
    }


def compare_version(other_version: str) -> int:
    """Compare current version with another version.

    Args:
        other_version: Version string to compare with

    Returns:
        int: -1 if current < other, 0 if equal, 1 if current > other

    Example:
        >>> compare_version("4.9.0")
        1  # current version (5.0.0) is greater
    """
    current_info = get_version_info()

    try:
        # Parse other version
        other_clean = other_version.split("-")[0].split("+")[0]
        other_info = tuple(map(int, other_clean.split(".")))

        # Compare tuples
        if current_info < other_info:
            return -1
        elif current_info > other_info:
            return 1
        else:
            return 0
    except ValueError:
        # If parsing fails, return 0 (equal)
        return 0


# Module-level version info for easy access
__version__ = get_version()
__version_info__ = get_version_info()


# Convenience functions for common use cases
def get_app_title() -> str:
    """Get application title with version.

    Returns:
        str: Application title (e.g., "MdxScraper v5.0.0")
    """
    return f"MdxScraper {get_version_display()}"


def get_about_text() -> str:
    """Get about text with version information.

    Returns:
        str: About text with version details
    """
    version_info = get_full_version_info()

    text = f"""MdxScraper {version_info['display']}

Version: {version_info['version']}
Build: {version_info['version_info']}
Pre-release: {'Yes' if version_info['is_prerelease'] else 'No'}

A tool for extracting content from MDX dictionaries and converting to various formats.
"""
    return text
