import os
import tempfile
from pathlib import Path

import pytest


@pytest.mark.parametrize("inner_progress, expected_scaled", [(0, 0), (50, 40), (100, 80)])
def test_mdx2pdf_progress_scaling(monkeypatch, inner_progress, expected_scaled):
    # Import inside test to ensure monkeypatch targets correct module objects
    from mdxscraper.core import converter

    # Capture outer progress calls
    reported = []

    def outer_progress(pct: int, msg: str):
        reported.append((pct, msg))

    # Stub mdx2html to invoke provided progress_callback with inner_progress
    def fake_mdx2html(*args, **kwargs):
        cb = kwargs.get("progress_callback")
        if cb:
            cb(inner_progress, "inner")
        # found, not_found, invalid_words
        return 1, 0, {}

    monkeypatch.setattr(converter, "mdx2html", fake_mdx2html)

    # Bypass wkhtmltopdf validation and conversion
    monkeypatch.setattr(
        converter, "validate_wkhtmltopdf_for_pdf_conversion", lambda path: (True, "")
    )
    monkeypatch.setattr(converter, "get_wkhtmltopdf_path", lambda path: "wkhtmltopdf")

    class DummyConfig:
        pass

    def fake_configuration(**kwargs):  # pdfkit.configuration
        return DummyConfig()

    # Simulate pdfkit module functions
    class DummyPdfKit:
        @staticmethod
        def configuration(**kwargs):
            return fake_configuration(**kwargs)

        @staticmethod
        def from_file(*args, **kwargs):
            return True

    monkeypatch.setattr(converter, "pdfkit", DummyPdfKit)

    # Avoid actual file deletion during the test
    monkeypatch.setattr(os, "remove", lambda path: None)

    with tempfile.TemporaryDirectory() as td:
        mdx = Path(td, "dict.mdx")
        mdx.write_text("dummy")
        input_file = Path(td, "input.txt")
        input_file.write_text("# Lesson\nword")
        output_file = Path(td, "out.pdf")

        converter.mdx2pdf(
            mdx_file=str(mdx),
            input_file=str(input_file),
            output_file=str(output_file),
            pdf_options={},
            progress_callback=outer_progress,
        )

    # First part of progress comes from scaled HTML callback
    assert any(p == expected_scaled for p, _ in reported)


@pytest.mark.parametrize("inner_progress, expected_scaled", [(0, 0), (50, 40), (100, 80)])
def test_mdx2img_progress_scaling(monkeypatch, inner_progress, expected_scaled):
    from mdxscraper.core import converter

    reported = []

    def outer_progress(pct: int, msg: str):
        reported.append((pct, msg))

    def fake_mdx2html(*args, **kwargs):
        cb = kwargs.get("progress_callback")
        if cb:
            cb(inner_progress, "inner")
        return 1, 0, {}

    monkeypatch.setattr(converter, "mdx2html", fake_mdx2html)

    # Fake imgkit to avoid running wkhtmltoimage
    class DummyImgKit:
        @staticmethod
        def from_file(*args, **kwargs):
            return True

    monkeypatch.setattr(converter, "imgkit", DummyImgKit)

    # Ensure temporary file cleanup doesn't error if already removed
    monkeypatch.setattr(os, "remove", lambda path: None)

    with tempfile.TemporaryDirectory() as td:
        mdx = Path(td, "dict.mdx")
        mdx.write_text("dummy")
        input_file = Path(td, "input.txt")
        input_file.write_text("# Lesson\nword")
        output_file = Path(td, "out.jpg")  # choose JPG path for simpler branch

        converter.mdx2img(
            mdx_file=str(mdx),
            input_file=str(input_file),
            output_file=str(output_file),
            img_options={},
            progress_callback=outer_progress,
        )

    assert any(p == expected_scaled for p, _ in reported)
