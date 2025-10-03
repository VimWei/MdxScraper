import io
import tempfile
from pathlib import Path

import pytest


def _write_temp(path: Path, data: bytes) -> None:
    path.write_bytes(data)


def test_open_encoding_file_defaults_when_no_newlines(monkeypatch):
    from mdxscraper.core.parser import WordParser, detect

    with tempfile.TemporaryDirectory() as td:
        p = Path(td, "no_newlines.txt")
        _write_temp(p, b"abcdef")  # 0 newlines triggers default path

        parser = WordParser(str(p))
        f = parser._open_encoding_file()
        try:
            assert hasattr(f, "encoding")
            assert f.encoding.lower().startswith("utf-8")
            # Ensure readable
            assert f.read() == "abcdef"
        finally:
            f.close()


@pytest.mark.parametrize(
    "detect_result, expected_encoding",
    [
        ({"encoding": "gbk", "confidence": 0.4}, "utf-8"),  # low confidence -> default
        ({"encoding": "cp1252", "confidence": 0.99}, "cp1252"),  # high confidence -> detected
    ],
)
def test_open_encoding_file_detects_or_falls_back(monkeypatch, detect_result, expected_encoding):
    from mdxscraper.core import parser

    # One or more newlines ensures detection path is used
    with tempfile.TemporaryDirectory() as td:
        p = Path(td, "with_newlines.txt")
        # bytes content doesn't matter for detection since we stub it
        _write_temp(p, b"line1\nline2\n")

        # Monkeypatch detect imported in module
        monkeypatch.setattr(parser, "detect", lambda data: detect_result)

        wp = parser.WordParser(str(p))
        f = wp._open_encoding_file()
        try:
            assert hasattr(f, "encoding")
            assert f.encoding.lower().startswith(expected_encoding)
            # Read to confirm file usable
            assert f.readline().strip() == "line1"
        finally:
            f.close()


