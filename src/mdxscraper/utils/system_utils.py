"""系统操作工具函数"""

import os
import platform
import subprocess
from pathlib import Path


def open_file_or_directory(path: Path) -> None:
    """Open file or directory using system default application.

    Args:
        path: Path to file or directory to open

    Raises:
        RuntimeError: If the system is not supported or the operation fails
    """
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif system == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        raise RuntimeError(f"Failed to open {path}: {e}")
