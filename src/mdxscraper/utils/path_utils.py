from __future__ import annotations

import platform
from pathlib import Path


def detect_wkhtmltopdf_path() -> str:
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
    if config_value == "auto":
        return detect_wkhtmltopdf_path()
    return config_value


