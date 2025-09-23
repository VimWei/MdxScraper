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

from mdxscraper.core.dictionary import Dictionary
from mdxscraper.core.enums import InvalidAction
from mdxscraper.core.parser import get_words
from mdxscraper.core.renderer import embed_images, merge_css
from mdxscraper.utils.path_utils import get_wkhtmltopdf_path


def mdx2html(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    invalid_action: InvalidAction = InvalidAction.Collect,
    with_toc: bool = True,
    h1_style: str | None = None,
    scrap_style: str | None = None,
    additional_styles: str | None = None,
) -> Tuple[int, int]:
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
                if invalid_action == InvalidAction.Exit:
                    raise SystemExit(1)
                elif invalid_action == InvalidAction.Collect:
                    if lesson['name'] in invalid_words:
                        invalid_words[lesson['name']].append(word)
                    else:
                        invalid_words[lesson['name']] = [word]
                    continue
                elif invalid_action == InvalidAction.OutputWarning:
                    invalid = True
                    result = '<div style="padding:0 0 15px 0"><b>WARNING:</b> "' + word + '" not found</div>'
                else:  # Collect_OutputWarning
                    if lesson['name'] in invalid_words:
                        invalid_words[lesson['name']].append(word)
                    else:
                        invalid_words[lesson['name']] = [word]
                    invalid = True
                    result = '<div style="padding:0 0 15px 0"><b>WARNING:</b> "' + word + '" not found</div>'
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
    with open(output_file, 'wb') as file:
        file.write(html)

    # writing invalid_words file handled by caller in new flow
    return found_count, not_found_count


def mdx2pdf(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    pdf_options: dict,
    invalid_action: InvalidAction = InvalidAction.Collect,
) -> tuple[int, int]:
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_file = temp.name
        result = mdx2html(mdx_file, input_file, temp_file, invalid_action, with_toc=False)

    config_path = get_wkhtmltopdf_path('auto')
    config = pdfkit.configuration(wkhtmltopdf=config_path)
    pdfkit.from_file(temp_file, str(output_file), configuration=config, options=pdf_options)
    os.remove(temp_file)
    return result


def mdx2jpg(
    mdx_file: str | Path,
    input_file: str | Path,
    output_file: str | Path,
    invalid_action: InvalidAction = InvalidAction.Collect,
) -> tuple[int, int]:
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as temp:
        temp_file = temp.name
        result = mdx2html(mdx_file, input_file, temp_file, invalid_action, with_toc=False)

    imgkit.from_file(temp_file, str(output_file), options={'enable-local-file-access': ''})
    os.remove(temp_file)
    return result


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


