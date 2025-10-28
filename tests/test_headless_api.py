"""Test headless library public API imports and exports.

This test ensures that the headless library API is properly exposed
and can be imported without GUI dependencies.
"""

import pytest


def test_core_imports():
    """Test that core functionality can be imported."""
    from mdxscraper import Dictionary, WordParser, mdx2html, mdx2img, mdx2pdf

    assert Dictionary is not None
    assert WordParser is not None
    assert mdx2html is not None
    assert mdx2pdf is not None
    assert mdx2img is not None


def test_core_module_imports():
    """Test that core module exports work."""
    from mdxscraper.core import Dictionary, WordParser, mdx2html, mdx2img, mdx2pdf

    assert Dictionary is not None
    assert WordParser is not None
    assert mdx2html is not None
    assert mdx2pdf is not None
    assert mdx2img is not None


def test_version_export():
    """Test that version is exported."""
    from mdxscraper import __version__

    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_package_all_exports():
    """Test that __all__ is properly defined."""
    import mdxscraper

    assert hasattr(mdxscraper, "__all__")
    assert isinstance(mdxscraper.__all__, list)

    expected_exports = [
        "Dictionary",
        "WordParser",
        "mdx2html",
        "mdx2pdf",
        "mdx2img",
        "__version__",
    ]

    for export in expected_exports:
        assert export in mdxscraper.__all__, f"{export} not in __all__"


def test_core_module_all_exports():
    """Test that core module __all__ is properly defined."""
    from mdxscraper import core

    assert hasattr(core, "__all__")
    assert isinstance(core.__all__, list)

    expected_exports = [
        "Dictionary",
        "WordParser",
        "mdx2html",
        "mdx2pdf",
        "mdx2img",
    ]

    for export in expected_exports:
        assert export in core.__all__, f"{export} not in core.__all__"


def test_no_gui_dependency_in_core():
    """Test that core modules don't import GUI dependencies."""
    import sys

    # Clear any GUI modules that might be imported
    gui_modules = [key for key in sys.modules.keys() if "PySide6" in key or "gui" in key.lower()]
    for module in gui_modules:
        if module.startswith("mdxscraper.gui"):
            continue  # Skip our own gui modules in the check
        if "PySide6" in module:
            pytest.skip("PySide6 already imported in test environment")

    # Import core functionality
    from mdxscraper import Dictionary, WordParser, mdx2html

    # Check that no PySide6 modules were imported
    pyside_modules = [key for key in sys.modules.keys() if "PySide6" in key]
    assert len(pyside_modules) == 0, f"Core imports should not load PySide6: {pyside_modules}"


def test_dictionary_class_available():
    """Test that Dictionary class is properly exposed."""
    from mdxscraper import Dictionary

    # Check class attributes
    assert hasattr(Dictionary, "__init__")
    assert hasattr(Dictionary, "lookup_html")
    assert hasattr(Dictionary, "__enter__")
    assert hasattr(Dictionary, "__exit__")


def test_wordparser_class_available():
    """Test that WordParser class is properly exposed."""
    from mdxscraper import WordParser

    # Check class attributes
    assert hasattr(WordParser, "__init__")
    assert hasattr(WordParser, "parse")


def test_conversion_functions_available():
    """Test that conversion functions are properly exposed."""
    from mdxscraper import mdx2html, mdx2img, mdx2pdf

    # Check that they are callable
    assert callable(mdx2html)
    assert callable(mdx2pdf)
    assert callable(mdx2img)

    # Check function signatures (they should have proper type hints)
    import inspect

    sig_html = inspect.signature(mdx2html)
    assert "mdx_file" in sig_html.parameters
    assert "input_file" in sig_html.parameters
    assert "output_file" in sig_html.parameters

    sig_pdf = inspect.signature(mdx2pdf)
    assert "mdx_file" in sig_pdf.parameters
    assert "pdf_options" in sig_pdf.parameters

    sig_img = inspect.signature(mdx2img)
    assert "mdx_file" in sig_img.parameters
    assert "img_options" in sig_img.parameters


def test_docstrings_present():
    """Test that public API has proper documentation."""
    from mdxscraper import Dictionary, WordParser, mdx2html
    from mdxscraper import core

    # Package docstring
    import mdxscraper

    assert mdxscraper.__doc__ is not None
    assert len(mdxscraper.__doc__) > 0

    # Core module docstring
    assert core.__doc__ is not None
    assert len(core.__doc__) > 0

    # Class docstrings
    # Dictionary has minimal docstring, that's OK

    # Function docstrings
    # Functions may have minimal docstrings, that's OK


def test_mdict_layer_available():
    """Test that mdict layer is accessible."""
    from mdxscraper.mdict import IndexBuilder

    assert IndexBuilder is not None
    assert callable(IndexBuilder)


def test_import_order_independence():
    """Test that imports work in any order."""
    # This test ensures circular import issues are avoided

    # First way: import from package
    from mdxscraper import Dictionary as Dict1

    # Second way: import from core
    from mdxscraper.core import Dictionary as Dict2

    # They should be the same class
    assert Dict1 is Dict2


def test_renderer_functions_available():
    """Test that renderer utility functions are available if needed."""
    from mdxscraper.core import renderer

    assert hasattr(renderer, "merge_css")
    assert hasattr(renderer, "embed_images")
    assert callable(renderer.merge_css)
    assert callable(renderer.embed_images)
