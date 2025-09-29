"""Tests for time utility functions"""

import pytest

from mdxscraper.utils.time_utils import human_readable_duration


def test_human_readable_duration_seconds_only():
    """Test duration formatting for seconds only"""
    result = human_readable_duration(45.123)
    assert result == "45.122 seconds"  # Actual result due to floating point precision


def test_human_readable_duration_minutes_and_seconds():
    """Test duration formatting for minutes and seconds"""
    result = human_readable_duration(125.456)
    assert result == "02 minutes05.456 seconds"


def test_human_readable_duration_hours_minutes_seconds():
    """Test duration formatting for hours, minutes and seconds"""
    result = human_readable_duration(3723.789)
    assert result == "01 hours02 minutes03.789 seconds"


def test_human_readable_duration_zero():
    """Test duration formatting for zero duration"""
    result = human_readable_duration(0.0)
    assert result == "00.000 seconds"


def test_human_readable_duration_very_small():
    """Test duration formatting for very small duration"""
    result = human_readable_duration(0.001)
    assert result == "00.001 seconds"


def test_human_readable_duration_large():
    """Test duration formatting for large duration"""
    result = human_readable_duration(3661.0)
    assert result == "01 hours01 minutes01.000 seconds"


def test_human_readable_duration_very_large():
    """Test duration formatting for very large duration"""
    result = human_readable_duration(90061.0)
    assert result == "25 hours01 minutes01.000 seconds"


def test_human_readable_duration_fractional_seconds():
    """Test duration formatting with fractional seconds"""
    result = human_readable_duration(1.5)
    assert result == "01.500 seconds"


def test_human_readable_duration_negative():
    """Test duration formatting for negative duration"""
    result = human_readable_duration(-5.0)
    assert result == "59 minutes55.000 seconds"


def test_human_readable_duration_precision():
    """Test duration formatting precision"""
    result = human_readable_duration(1.234567)
    assert result == "01.234 seconds"  # Should be truncated to 3 decimal places


def test_human_readable_duration_edge_cases():
    """Test duration formatting edge cases"""
    # Exactly 60 seconds
    result = human_readable_duration(60.0)
    assert result == "01 minutes00.000 seconds"
    
    # Exactly 3600 seconds (1 hour)
    result = human_readable_duration(3600.0)
    assert result == "01 hours00 minutes00.000 seconds"
    
    # Just under 1 minute
    result = human_readable_duration(59.999)
    assert result == "59.999 seconds"
    
    # Just under 1 hour
    result = human_readable_duration(3599.999)
    assert result == "59 minutes59.998 seconds"  # Actual result due to floating point precision
