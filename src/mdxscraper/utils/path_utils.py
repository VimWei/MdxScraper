from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path

# In-memory cache for current session only (portable-friendly)
_session_cache = {"detected_path": None, "is_valid": None, "message": None}


def detect_wkhtmltopdf_path() -> str:
    """Detect wkhtmltopdf path"""
    system = platform.system()
    candidates: list[str]
    if system == "Windows":
        candidates = [
            r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
            r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        ]
    elif system == "Linux":
        candidates = [
            "/usr/local/bin/wkhtmltopdf",
            "/usr/bin/wkhtmltopdf",
        ]
    elif system == "Darwin":
        candidates = [
            "/usr/local/bin/wkhtmltopdf",
            "/opt/homebrew/bin/wkhtmltopdf",
        ]
    else:
        candidates = []

    for c in candidates:
        if Path(c).is_file():
            return c

    # Fallback to PATH
    return "wkhtmltopdf"


def get_wkhtmltopdf_path(config_value: str) -> str:
    # Treat both "auto" and empty string as auto-detect for backward compatibility
    if config_value in ("auto", ""):
        return detect_wkhtmltopdf_path()
    return config_value


def validate_wkhtmltopdf_path(path: str) -> tuple[bool, str]:
    """
    Validate if wkhtmltopdf is available at the given path.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not path:
        return False, "No path specified"

    # Check if file exists (for absolute paths)
    if Path(path).is_absolute():
        if not Path(path).is_file():
            return False, f"File not found: {path}"

    # Try to run wkhtmltopdf --version to check if it's working
    try:
        result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_info = (
                result.stdout.strip().split("\n")[0] if result.stdout else "Unknown version"
            )
            return True, f"✓ {version_info}"
        else:
            return False, f"Command failed (exit code: {result.returncode})"
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, f"Executable not found: {path}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_auto_detect_status() -> tuple[bool, str, str]:
    """
    Get the status of auto-detection with session caching.

    Returns:
        tuple[bool, str, str]: (is_successful, detected_path, status_message)
    """
    # Check if we have a cached result in this session
    if _session_cache["detected_path"] is not None:
        return (
            _session_cache["is_valid"],
            _session_cache["detected_path"],
            _session_cache["message"],
        )

    # Perform fresh detection and validation
    detected_path = detect_wkhtmltopdf_path()
    is_valid, message = validate_wkhtmltopdf_path(detected_path)

    # Cache the result for this session
    _session_cache["detected_path"] = detected_path
    _session_cache["is_valid"] = is_valid
    _session_cache["message"] = message

    return is_valid, detected_path, message


def clear_auto_detect_cache():
    """Clear the session cache to force fresh detection"""
    global _session_cache
    _session_cache = {"detected_path": None, "is_valid": None, "message": None}


def force_auto_detect():
    """Force a fresh auto-detection, ignoring session cache"""
    clear_auto_detect_cache()
    return get_auto_detect_status()


def validate_wkhtmltopdf_for_pdf_conversion(config_path: str) -> tuple[bool, str]:
    """
    Validate wkhtmltopdf path specifically for PDF conversion.
    This is called at runtime when actually converting to PDF.

    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if not config_path or config_path in ("auto", ""):
        # Try auto-detect
        detected_path = detect_wkhtmltopdf_path()
        if detected_path == "wkhtmltopdf":
            return (
                False,
                "wkhtmltopdf not found in system PATH. Please install wkhtmltopdf or specify the path manually in Advanced settings.",
            )
        config_path = detected_path

    # Validate the path
    is_valid, message = validate_wkhtmltopdf_path(config_path)
    if not is_valid:
        return (
            False,
            f"wkhtmltopdf validation failed: {message}. Please check the path in Advanced settings.",
        )

    return True, ""
