from __future__ import annotations

import os
import tempfile
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import imgkit
import pdfkit
from bs4 import BeautifulSoup
from PIL import Image

from mdxscraper.core.dictionary import Dictionary
from mdxscraper.core.parser import get_words
from mdxscraper.core.renderer import embed_images, merge_css
from mdxscraper.utils.path_utils import get_wkhtmltopdf_path, validate_wkhtmltopdf_for_pdf_conversion


def mdx2html(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    with_toc: bool = True,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
) -> Tuple[int, int, OrderedDict]:
    found_count = 0
    not_found_count = 0

    mdx_file = Path(mdx_file)
    dictionary = Dictionary(mdx_file)
    lessons = get_words(str(input_file))

    right_soup = BeautifulSoup('<body style="font-family:Arial Unicode MS;"><div class="right"></div></body>', 'lxml')
    right_soup.find('body').insert_before('\n')
    left_soup = BeautifulSoup('<div class="left"></div>', 'lxml')

    invalid_words = OrderedDict()

    for lesson in lessons:
        h1 = right_soup.new_tag('h1', id='lesson_' + lesson['name'])
        if h1_style:
            h1['style'] = h1_style
        h1.string = lesson['name']
        right_soup.div.append(h1)

        a = left_soup.new_tag('a', href='#lesson_' + lesson['name'], **{'class': 'lesson'})
        a.string = lesson['name']
        left_soup.div.append(a)
        left_soup.div.append(left_soup.new_tag('br'))
        left_soup.div.append('\n')

        invalid = False
        for word in lesson['words']:
            result = dictionary.lookup_html(word)
            if len(result) == 0:
                not_found_count += 1
                # Always collect invalid words and embed a warning
                if lesson['name'] in invalid_words:
                    invalid_words[lesson['name']].append(word)
                else:
                    invalid_words[lesson['name']] = [word]
                invalid = True
                # result = '<div style="padding:0 0 15px 0"><b>WARNING:</b> "' + word + '" not found</div>'
            else:
                found_count += 1

            definition = BeautifulSoup(result, 'lxml')
            if right_soup.head is None and definition.head is not None:
                right_soup.html.insert_before(definition.head)
                right_soup.head.append(right_soup.new_tag('meta', charset='utf-8'))

            new_div = right_soup.new_tag('div')
            if scrap_style:
                new_div['style'] = scrap_style
            new_div['id'] = 'word_' + word
            new_div['class'] = 'scrapedword'
            if definition.body:
                new_div.append(definition.body)
            right_soup.div.append('\n')
            right_soup.div.append(new_div)

            a = left_soup.new_tag('a', href='#word_' + word, **{'class': 'word' + (' invalid_word' if invalid else '')})
            invalid = False
            a.string = word
            left_soup.div.append(a)
            left_soup.div.append(left_soup.new_tag('br'))
            left_soup.div.append('\n')

        left_soup.div.append(left_soup.new_tag('br'))

    if with_toc:
        main_div = right_soup.new_tag('div', **{'class': 'main'})
        right_soup.div.wrap(main_div)
        right_soup.div.insert_before(left_soup.div)

    right_soup = merge_css(right_soup, mdx_file.parent, dictionary.impl, additional_styles)
    right_soup = embed_images(right_soup, dictionary.impl)

    html = str(right_soup).encode('utf-8')
    html = html.replace(b'<body>', b'').replace(b'</body>', b'', html.count(b'</body>') - 1)
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'wb') as file:
        file.write(html)

    # Return invalid_words data for caller to handle file output
    return found_count, not_found_count, invalid_words


def mdx2pdf(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    pdf_options: dict,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
    wkhtmltopdf_path: str = 'auto',
) -> tuple[int, int, OrderedDict]:
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_file = temp.name
        found, not_found, invalid_words = mdx2html(
            mdx_file, input_file, temp_file, with_toc=False,
            h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
        )

    # Validate wkhtmltopdf path before conversion
    is_valid, error_message = validate_wkhtmltopdf_for_pdf_conversion(wkhtmltopdf_path)
    if not is_valid:
        os.remove(temp_file)
        raise RuntimeError(error_message)
    
    config_path = get_wkhtmltopdf_path(wkhtmltopdf_path)
    config = pdfkit.configuration(wkhtmltopdf=config_path)
    # Ensure output directory exists
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    pdfkit.from_file(temp_file, str(output_file), configuration=config, options=pdf_options)
    os.remove(temp_file)
    return found, not_found, invalid_words


def mdx2img(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    img_options: dict | None = None,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
) -> tuple[int, int, OrderedDict]:
    """Render dictionary results to an image using wkhtmltoimage via imgkit.

    The output format is inferred from the output file suffix (.jpg/.jpeg/.png/.webp).
    Additional imgkit options can be supplied via img_options.
    """
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_file = temp.name
        found, not_found, invalid_words = mdx2html(
            mdx_file, input_file, temp_file, with_toc=False,
            h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
        )

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Build wkhtmltoimage options - whitelist only supported keys
    options = {'enable-local-file-access': ''}
    if img_options:
        # Supported wkhtmltoimage keys we allow
        allowed_keys = {"width", "zoom", "quality"}
        for k, v in img_options.items():
            if k in allowed_keys and v is not None and v != "":
                options[k] = str(v)

    suffix = output_path.suffix.lower()
    # -------- WEBP --------
    if suffix == '.webp':
        # Render to a temporary PNG first, then convert to WEBP via Pillow
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
            tmp_png_path = tmp_png.name
        try:
            imgkit.from_file(temp_file, str(tmp_png_path), options=options)
            with Image.open(tmp_png_path) as im:
                webp_quality = 80 if not img_options else int(img_options.get('webp_quality', 80))
                webp_lossless = False if not img_options else bool(img_options.get('webp_lossless', False))
                if webp_lossless:
                    im.save(str(output_path), format='WEBP', lossless=True, quality=webp_quality)
                else:
                    im.save(str(output_path), format='WEBP', quality=webp_quality, method=6)
        finally:
            try:
                os.remove(tmp_png_path)
            except Exception:
                pass
    # -------- PNG --------
    elif suffix == '.png':
        # Render to temp, then Pillow optimize and recompress
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_png:
            tmp_png_path = tmp_png.name
        try:
            imgkit.from_file(temp_file, str(tmp_png_path), options=options)
            with Image.open(tmp_png_path) as im:
                png_optimize = True if not img_options else bool(img_options.get('png_optimize', True))
                png_compress_level = 9 if not img_options else int(img_options.get('png_compress_level', 9))
                im.save(str(output_path), format='PNG', optimize=png_optimize, compress_level=png_compress_level)
        finally:
            try:
                os.remove(tmp_png_path)
            except Exception:
                pass
    # -------- JPG / JPEG --------
    elif suffix in ('.jpg', '.jpeg'):
        # Set default JPEG quality for wkhtmltoimage
        options.setdefault('quality', '85')
        imgkit.from_file(temp_file, str(output_path), options=options)
    # -------- Others (fallback to wkhtmltoimage) --------
    else:
        imgkit.from_file(temp_file, str(output_path), options=options)

    os.remove(temp_file)
    return found, not_found, invalid_words


def write_invalid_words_file(invalid_words: OrderedDict, output_file: str | Path) -> None:
    """Write invalid words to a text file in the same format as input files.
    
    Args:
        invalid_words: Dictionary mapping lesson names to lists of invalid words
        output_file: Path to the output file
    """
    if not invalid_words:
        return
        
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for lesson_name, words in invalid_words.items():
            f.write(f"# {lesson_name}\n")
            for word in words:
                f.write(f"{word}\n")
            f.write("\n")

def human_readable_duration(seconds: float) -> str:
    time_delta = timedelta(seconds=seconds)
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes, int_seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(hours) * 3600 - int(minutes) * 60 - int(int_seconds)) * 1000)

    parts: list[str] = []
    if int(hours) > 0:
        parts.append(f'{int(hours):02d} hours')
    if int(minutes) > 0 or int(hours) > 0:
        parts.append(f'{int(minutes):02d} minutes')
    parts.append(f'{int(int_seconds):02d}.{milliseconds:03d} seconds')

    return ''.join(parts)


