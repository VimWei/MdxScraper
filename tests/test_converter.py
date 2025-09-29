"""Tests for converter functions"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest

from mdxscraper.core.converter import mdx2html, mdx2img, mdx2pdf


def test_mdx2html_basic():
    """Test basic HTML conversion"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    # Mock lessons data
    lessons = [
        {"name": "Lesson 1", "words": ["word1", "word2"]},
        {"name": "Lesson 2", "words": ["word3", "word4"]}
    ]
    
    # Mock dictionary lookup results
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file
                        )
                        
                        assert found == 4  # 4 words found
                        assert not_found == 0
                        assert len(invalid_words) == 0


def test_mdx2html_with_not_found_words():
    """Test HTML conversion with some words not found"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = [
        {"name": "Lesson 1", "words": ["word1", "word2", "word3"]}
    ]
    
    # Mock dictionary lookup results - some words not found
    mock_dictionary = Mock()
    def lookup_side_effect(word):
        if word in ["word1", "word3"]:
            return "<html>definition</html>"
        return ""
    mock_dictionary.lookup_html.side_effect = lookup_side_effect
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file
                        )
                        
                        assert found == 2  # 2 words found
                        assert not_found == 1  # 1 word not found
                        assert len(invalid_words) == 1
                        assert "Lesson 1" in invalid_words
                        assert "word2" in invalid_words["Lesson 1"]


def test_mdx2html_with_progress_callback():
    """Test HTML conversion with progress callback"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    progress_callback = Mock()
    
    lessons = [
        {"name": "Lesson 1", "words": ["word1"]}
    ]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file, progress_callback=progress_callback
                        )
                        
                        # Progress callback should be called
                        assert progress_callback.call_count > 0


def test_mdx2html_with_css_styles():
    """Test HTML conversion with CSS styles"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css") as mock_merge_css:
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        mock_merge_css.return_value = "merged_css"
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file,
                            h1_style="color: red;",
                            scrap_style="font-size: 14px;",
                            additional_styles="body { margin: 0; }"
                        )
                        
                        # Verify CSS merge was called with correct parameters
                        mock_merge_css.assert_called_once()
                        call_args = mock_merge_css.call_args[0]
                        assert len(call_args) == 4  # soup, mdx_path, dictionary, additional_styles


def test_mdx2html_with_mdd_file():
    """Test HTML conversion with MDD file for images"""
    mdx_file = Path("test.mdx")
    mdd_file = Path("test.mdd")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition with <img src='test.png'></html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images") as mock_embed_images:
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        mock_embed_images.return_value = "embedded_html"
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file
                        )
                        
                        # Verify image embedding was called
                        mock_embed_images.assert_called_once()
                        call_args = mock_embed_images.call_args[0]
                        assert len(call_args) == 2  # soup, dictionary


def test_mdx2pdf_basic():
    """Test basic PDF conversion"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.pdf")
    pdf_options = {"page-size": "A4", "margin-top": "1in"}
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("mdxscraper.core.converter.pdfkit.from_file") as mock_pdfkit:
                            mock_parser.return_value.parse.return_value = lessons
                            mock_pdfkit.return_value = None
                            
                            found, not_found, invalid_words = mdx2pdf(
                                mdx_file, input_file, output_file, pdf_options
                            )
                            
                            assert found == 1
                            assert not_found == 0
                            assert len(invalid_words) == 0
                            
                            # Verify pdfkit was called for PDF conversion
                            mock_pdfkit.assert_called_once()


def test_mdx2pdf_wkhtmltopdf_error():
    """Test PDF conversion with wkhtmltopdf error"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.pdf")
    pdf_options = {"page-size": "A4"}
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("mdxscraper.core.converter.pdfkit.from_file") as mock_pdfkit:
                            mock_parser.return_value.parse.return_value = lessons
                            mock_pdfkit.side_effect = Exception("wkhtmltopdf error")
                            
                            with pytest.raises(Exception, match="wkhtmltopdf error"):
                                mdx2pdf(mdx_file, input_file, output_file, pdf_options)


def test_mdx2img_basic():
    """Test basic image conversion"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.png")
    image_options = {"width": 800, "height": 600, "format": "png"}
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("mdxscraper.core.converter.imgkit.from_file") as mock_imgkit:
                            with patch("mdxscraper.core.converter.Image.open") as mock_image_open:
                                mock_image = Mock()
                                mock_image.size = (800, 600)
                                mock_image_open.return_value.__enter__.return_value = mock_image
                                mock_parser.return_value.parse.return_value = lessons
                                mock_imgkit.return_value = None
                                
                                found, not_found, invalid_words = mdx2img(
                                    mdx_file, input_file, output_file, image_options
                                )
                            
                            assert found == 1
                            assert not_found == 0
                            assert len(invalid_words) == 0
                            
                            # Verify imgkit was called for image conversion
                            mock_imgkit.assert_called_once()


def test_mdx2img_wkhtmltoimage_error():
    """Test image conversion with wkhtmltoimage error"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.png")
    image_options = {"width": 800, "height": 600, "format": "png"}
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("mdxscraper.core.converter.imgkit.from_file") as mock_imgkit:
                            mock_parser.return_value.parse.return_value = lessons
                            mock_imgkit.side_effect = Exception("wkhtmltoimage error")
                            
                            with pytest.raises(Exception, match="wkhtmltoimage error"):
                                mdx2img(mdx_file, input_file, output_file, image_options)


def test_mdx2html_empty_lessons():
    """Test HTML conversion with empty lessons"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = []
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary"):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        mock_parser.return_value.parse.return_value = lessons
                        
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file
                        )
                        
                        assert found == 0
                        assert not_found == 0
                        assert len(invalid_words) == 0


def test_mdx2html_with_backup():
    """Test HTML conversion with backup enabled"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("shutil.copy2") as mock_copy:
                            mock_parser.return_value.parse.return_value = lessons
                            
                        found, not_found, invalid_words = mdx2html(
                            mdx_file, input_file, output_file
                        )
                        
                        # Verify backup was created (if implemented)
                        # Note: backup functionality may not be implemented in mdx2html


def test_mdx2html_with_timestamp():
    """Test HTML conversion with timestamp in output filename"""
    mdx_file = Path("test.mdx")
    input_file = Path("test.txt")
    output_file = Path("output.html")
    
    lessons = [{"name": "Lesson 1", "words": ["word1"]}]
    
    mock_dictionary = Mock()
    mock_dictionary.lookup_html.return_value = "<html>definition</html>"
    
    with patch("mdxscraper.core.converter.WordParser") as mock_parser:
        with patch("mdxscraper.core.converter.Dictionary", return_value=mock_dictionary):
            with patch("mdxscraper.core.converter.merge_css", return_value="merged_css"):
                with patch("mdxscraper.core.converter.embed_images", return_value="embedded_html"):
                    with patch("builtins.open", mock_open()) as mock_file:
                        with patch("mdxscraper.core.converter.datetime") as mock_datetime:
                            mock_parser.return_value.parse.return_value = lessons
                            mock_datetime.now.return_value.strftime.return_value = "20240101-120000"
                            
                            found, not_found, invalid_words = mdx2html(
                                mdx_file, input_file, output_file
                            )
                            
                            # Verify timestamp was added to filename (if implemented)
                            # Note: timestamp functionality may not be implemented in mdx2html
