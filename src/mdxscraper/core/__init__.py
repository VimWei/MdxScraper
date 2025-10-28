"""Core modules for headless MDX dictionary query and extraction.

This namespace provides the core functionality for querying MDX dictionaries
and converting results to various formats (HTML, PDF, images) without GUI dependencies.

Examples:
    Basic dictionary query:
        >>> from mdxscraper.core import Dictionary
        >>> with Dictionary("path/to/dict.mdx") as dict:
        ...     result = dict.lookup_html("hello")
        
    Parse input words:
        >>> from mdxscraper.core import WordParser
        >>> parser = WordParser("words.txt")
        >>> lessons = parser.parse()
        
    Convert to HTML:
        >>> from mdxscraper.core import mdx2html
        >>> found, not_found, invalid = mdx2html(
        ...     mdx_file="dict.mdx",
        ...     input_file="words.txt",
        ...     output_file="output.html"
        ... )
"""

from mdxscraper.core.converter import mdx2html, mdx2img, mdx2pdf
from mdxscraper.core.dictionary import Dictionary
from mdxscraper.core.parser import WordParser

__all__ = [
    "Dictionary",
    "WordParser",
    "mdx2html",
    "mdx2pdf",
    "mdx2img",
]
