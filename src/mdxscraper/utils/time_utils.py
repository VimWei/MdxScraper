"""时间处理工具函数"""

from datetime import timedelta


def human_readable_duration(seconds: float) -> str:
    """Convert seconds to human readable duration string.

    Args:
        seconds: Duration in seconds

    Returns:
        Human readable duration string (e.g., "01h 23m 45.123s")
    """
    time_delta = timedelta(seconds=seconds)
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes, int_seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(hours) * 3600 - int(minutes) * 60 - int(int_seconds)) * 1000)

    parts: list[str] = []
    if int(hours) > 0:
        parts.append(f"{int(hours):02d} hours")
    if int(minutes) > 0 or int(hours) > 0:
        parts.append(f"{int(minutes):02d} minutes")
    parts.append(f"{int(int_seconds):02d}.{milliseconds:03d} seconds")

    return "".join(parts)
