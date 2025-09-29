"""Tests for renderer functions"""

from pathlib import Path
from unittest.mock import Mock, mock_open, patch

import pytest
from bs4 import BeautifulSoup

from mdxscraper.core.renderer import embed_images, get_css, merge_css


def test_get_css_from_file():
    """Test getting CSS from file"""
    mock_soup = Mock()
    mock_soup.head.link = {'href': 'style.css'}
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    
    css_content = "body { margin: 0; }"
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_bytes", return_value=css_content.encode('utf-8')):
            result = get_css(mock_soup, mock_mdx_path, mock_dictionary)
            
            assert result == css_content


def test_get_css_from_mdd():
    """Test getting CSS from MDD database"""
    mock_soup = Mock()
    mock_soup.head.link = {'href': 'style.css'}
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.get_mdd_keys.return_value = ['style.css']
    mock_dictionary.mdd_lookup.return_value = [b"body { margin: 0; }"]
    
    with patch("pathlib.Path.exists", return_value=False):
        result = get_css(mock_soup, mock_mdx_path, mock_dictionary)
        
        assert result == "body { margin: 0; }"
        mock_dictionary.get_mdd_keys.assert_called_once_with('*style.css')
        mock_dictionary.mdd_lookup.assert_called_once_with('style.css')


def test_get_css_not_found():
    """Test getting CSS when not found"""
    mock_soup = Mock()
    mock_soup.head.link = {'href': 'style.css'}
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    mock_dictionary.get_mdd_keys.return_value = ['style.css']
    mock_dictionary.mdd_lookup.return_value = [b""]
    
    with patch("pathlib.Path.exists", return_value=False):
        result = get_css(mock_soup, mock_mdx_path, mock_dictionary)
        
        assert result == ""


def test_get_css_exception():
    """Test getting CSS when exception occurs"""
    mock_soup = Mock()
    mock_soup.head.link = {'href': 'style.css'}
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    
    with patch("pathlib.Path.exists", return_value=True):
        with patch("pathlib.Path.read_bytes", side_effect=Exception("File error")):
            # The actual function doesn't handle exceptions, so it should raise
            with pytest.raises(Exception, match="File error"):
                get_css(mock_soup, mock_mdx_path, mock_dictionary)


def test_merge_css_basic():
    """Test merging CSS with soup"""
    html_content = '<html><head><link href="style.css"></head><body></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    additional_styles = "h1 { color: red; }"
    
    with patch("mdxscraper.core.renderer.get_css", return_value="body { margin: 0; }"):
        result = merge_css(soup, mock_mdx_path, mock_dictionary, additional_styles)
        
        # Check that link was removed and style was added
        assert result.head.link is None
        assert result.head.style is not None
        assert "body { margin: 0; }" in result.head.style.string
        assert "h1 { color: red; }" in result.head.style.string


def test_merge_css_no_additional_styles():
    """Test merging CSS without additional styles"""
    html_content = '<html><head><link href="style.css"></head><body></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    
    with patch("mdxscraper.core.renderer.get_css", return_value="body { margin: 0; }"):
        result = merge_css(soup, mock_mdx_path, mock_dictionary)
        
        # Check that link was removed and style was added
        assert result.head.link is None
        assert result.head.style is not None
        assert "body { margin: 0; }" in result.head.style.string


def test_merge_css_exception():
    """Test merging CSS when exception occurs"""
    html_content = '<html><head><link href="style.css"></head><body></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_mdx_path = Path("test.mdx")
    mock_dictionary = Mock()
    
    with patch("mdxscraper.core.renderer.get_css", side_effect=Exception("CSS error")):
        result = merge_css(soup, mock_mdx_path, mock_dictionary)
        
        # Should return original soup unchanged
        assert result.head.link is not None
        assert result.head.style is None


def test_embed_images_basic():
    """Test basic image embedding"""
    html_content = '<html><body><img src="test.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", return_value="png"):
        result = embed_images(soup, mock_dictionary)
        
        img = result.find('img')
        assert img is not None
        assert img['src'].startswith('data:image/png;base64,')


def test_embed_images_no_mdd_db():
    """Test image embedding when no MDD database"""
    html_content = '<html><body><img src="test.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    # No _mdd_db attribute
    mock_dictionary.mdd_lookup.return_value = []
    
    result = embed_images(soup, mock_dictionary)
    
    # Should return original soup unchanged
    img = result.find('img')
    assert img is not None
    assert img['src'] == "test.png"


def test_embed_images_multiple_images():
    """Test embedding multiple images"""
    html_content = '''
    <html><body>
        <img src="image1.png" alt="image1">
        <img src="image2.jpg" alt="image2">
        <img src="image3.gif" alt="image3">
    </body></html>
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    def get_format_side_effect(src):
        if "png" in src:
            return "png"
        elif "jpg" in src:
            return "jpeg"
        elif "gif" in src:
            return "gif"
        return "png"
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", side_effect=get_format_side_effect):
        result = embed_images(soup, mock_dictionary)
        
        imgs = result.find_all('img')
        assert len(imgs) == 3
        assert imgs[0]['src'].startswith('data:image/png;base64,')
        assert imgs[1]['src'].startswith('data:image/jpeg;base64,')
        assert imgs[2]['src'].startswith('data:image/gif;base64,')


def test_embed_images_no_src_attribute():
    """Test image embedding with no src attribute"""
    html_content = '<html><body><img alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    
    result = embed_images(soup, mock_dictionary)
    
    # Should return original soup unchanged
    img = result.find('img')
    assert img is not None
    assert 'src' not in img.attrs


def test_embed_images_image_not_found():
    """Test image embedding when image not found in MDD"""
    html_content = '<html><body><img src="nonexistent.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = []  # No images found
    
    result = embed_images(soup, mock_dictionary)
    
    # Should return original soup unchanged
    img = result.find('img')
    assert img is not None
    assert img['src'] == "nonexistent.png"


def test_embed_images_caching():
    """Test image embedding caching"""
    html_content = '''
    <html><body>
        <img src="test.png" alt="test1">
        <img src="test.png" alt="test2">
    </body></html>
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", return_value="png"):
        result = embed_images(soup, mock_dictionary)
        
        # mdd_lookup should only be called once due to caching
        assert mock_dictionary.mdd_lookup.call_count == 1
        
        imgs = result.find_all('img')
        assert len(imgs) == 2
        # Both images should have the same base64 data
        assert imgs[0]['src'] == imgs[1]['src']


def test_embed_images_path_normalization():
    """Test image embedding with path normalization"""
    html_content = '<html><body><img src="/test/image.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", return_value="png"):
        result = embed_images(soup, mock_dictionary)
        
        # Check that path was normalized (forward slashes to backslashes)
        mock_dictionary.mdd_lookup.assert_called_once()
        call_args = mock_dictionary.mdd_lookup.call_args[0][0]
        assert call_args == "\\test\\image.png"


def test_embed_images_relative_path():
    """Test image embedding with relative path"""
    html_content = '<html><body><img src="images/test.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", return_value="png"):
        result = embed_images(soup, mock_dictionary)
        
        # Check that relative path was handled correctly
        mock_dictionary.mdd_lookup.assert_called_once()
        call_args = mock_dictionary.mdd_lookup.call_args[0][0]
        assert call_args == "\\images\\test.png"


def test_embed_images_base64_encoding():
    """Test that images are properly base64 encoded"""
    html_content = '<html><body><img src="test.png" alt="test"></body></html>'
    soup = BeautifulSoup(html_content, 'html.parser')
    
    mock_dictionary = Mock()
    mock_dictionary._mdd_db = True
    mock_dictionary.mdd_lookup.return_value = [b"fake_image_data"]
    
    with patch("mdxscraper.utils.file_utils.get_image_format_from_src", return_value="png"):
        result = embed_images(soup, mock_dictionary)
        
        img = result.find('img')
        assert img is not None
        assert img['src'].startswith('data:image/png;base64,')
        
        # Check that the base64 data is present
        import base64
        expected_b64 = base64.b64encode(b"fake_image_data").decode('ascii')
        assert expected_b64 in img['src']