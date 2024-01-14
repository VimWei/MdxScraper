#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: MdxScraper
Author: VimWei
Created: January 14, 2024

Description:
    Extract specific words from an MDX dictionary and generate PDF, HTML, or JPG files with ease.
    It's an adaptation and upgrade based on the original MdxConverter: https://github.com/noword/MdxConverter
"""

import os
import sys
import json
import argparse
from enum import IntEnum
from pathlib import Path
from datetime import datetime
from collections import OrderedDict

import imgkit  # pip install imgkit
import pdfkit  # pip install pdfkit
import openpyxl  # pip install openpyxl
from chardet import detect  # pip install chardet
from base64 import b64encode  # pip install base64
from bs4 import BeautifulSoup  # pip install bs4

# 添加mdict-query
current_script_path = Path(__file__).resolve().parent
path_to_be_added = current_script_path / "mdict-query"
sys.path.append(str(path_to_be_added))
import mdict_query

# Additional styles for HTML output
ADDITIONAL_STYLES = '''
a.lesson {font-size:120%; color: #1a237e; text-decoration: none; cursor: pointer; border-bottom: none;}
a.lesson:hover {background-color: #e3f2fd}
a.word {color: #1565c0; text-decoration: none; cursor: pointer; font-variant: normal; font-weight: normal; border-bottom: none;}
a.word:hover {background-color: #e3f2fd;}
a.invalid_word {color: #909497;}
div.main {width: 100%; height: 100%;}
div.left {width: 150px; overflow: auto; float: left; height: 100%;}
div.right {overflow-y: auto; overflow-x: hidden; padding-left: 10px; height: 100%;}
'''

# Styles for HTML output
H1_STYLE = 'color:#FFFFFF; background-color:#003366; padding-left:20px; line-height:initial;'
# H2_STYLE = 'color:#CCFFFF; background-color:#336699; padding-left:20px; line-height:initial;'
H2_STYLE = 'border: 1mm ridge rgba(111, 160, 206, .6); color:#46525F; background-color:#E3EDF5; padding:2px 2px 2px 20px; line-height:initial;'
# H2_STYLE = 'display:none;'

INVALID_WORDS_FILENAME = 'invalid_words.txt'
TEMP_FILE = 'temp.html'

# Enumeration for invalid action
class InvalidAction(IntEnum):
    Exit = 0
    Output = 1
    Collect = 2

# Function to open a file with detected encoding
def open_encoding_file(name):
    encoding = detect(open(name, 'rb').read())['encoding']
    return open(name, encoding=encoding)

# Function to retrieve words from different file types
def get_words(name):
    ext = Path(name).suffix.lower()
    return {'.xls': get_words_from_xls,
            '.xlsx': get_words_from_xls,
            '.json': get_words_from_json,
            '.txt': get_words_from_txt,
            }[ext](name)

# Function to get words from a JSON file
def get_words_from_json(name):
    return json.load(open_encoding_file(name))

# Function to get words from a text file
def get_words_from_txt(name):
    result = []
    for line in open_encoding_file(name).readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith('#'):
            result.append({'name': line.strip('#'), 'words': []})
        else:
            if len(result) == 0:
                currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
                result.append({'name': currentTime, 'words': []})
            result[-1]['words'].append(line)
    return result

# Function to get words from an Excel file
def get_words_from_xls(name):
    wb = openpyxl.load_workbook(name, read_only=True)
    result = []
    for name in wb.sheetnames:
        ws = wb[name]
        words = [row[0].value for row in ws.iter_rows(min_row=ws.min_row, max_row=ws.max_row, max_col=1)]
        words = list(filter(lambda x: x is not None and len(x) > 0, words))
        result.append({'name': name, 'words': words})
    return result

# Function to retrieve CSS from an MDX dictionary or file
def get_css(soup, mdx_path, dictionary):
    css_name = soup.head.link['href']
    css_path = Path(mdx_path) / css_name
    if css_path.exists():
        css = css_path.read_bytes()
    elif hasattr(dictionary, '_mdd_db'):
        css_key = dictionary.get_mdd_keys('*' + css_name)[0]
        css = dictionary.mdd_lookup(css_key)[0]
    else:
        css = b''
    return css.decode('utf-8')

# Function to merge CSS into the HTML soup
def merge_css(soup, mdx_path, dictionary, append_additinal_styles=True):
    try:
        css = get_css(soup, mdx_path, dictionary)
    except Exception as e:
        return soup
    if append_additinal_styles:
        css += ADDITIONAL_STYLES

    soup.head.link.decompose()
    soup.head.append(soup.new_tag('style', type='text/css'))
    soup.head.style.string = css
    return soup

# Function to determine image format based on file extension
def get_image_format_from_src(src: str) -> str:
    ext = Path(src).suffix.lower()
    if ext == '.png':
        return 'png'
    elif ext in ['.jpg', '.jpeg']:
        return 'jpeg'
    elif ext == '.gif':
        return 'gif'
    else:
        return 'png'

# Function to replace image source with base64 data in HTML soup
def grab_images(soup, dictionary):
    if not hasattr(dictionary, '_mdd_db'):
        return soup

    cache = {}
    for img in soup.find_all('img'):
        if not img.has_attr('src'):
            continue

        src = img['src']
        src_path = src.replace('/', '\\')

        if src_path in cache:
            img['src'] = cache[src_path]
            continue

        lookup_src = src_path
        if not lookup_src.startswith('\\'):
            lookup_src = '\\' + lookup_src

        # Lookup image data
        imgs = dictionary.mdd_lookup(lookup_src)
        if len(imgs) > 0:
            print(f'Got image {src}')
            image_format = get_image_format_from_src(src)
            base64_str = f'data:image/{image_format};base64,' + b64encode(imgs[0]).decode('ascii')
            cache[src_path] = base64_str
            img['src'] = base64_str

    return soup

# Function to look up a word in the MDX dictionary
def lookup(dictionary, word):
    word = word.strip()
    definitions = dictionary.mdx_lookup(word)
    if len(definitions) == 0:
        definitions = dictionary.mdx_lookup(word, ignorecase=True)
    if len(definitions) == 0:
        definitions = dictionary.mdx_lookup(word.replace('-', ''), ignorecase=True)
    if len(definitions) == 0:
        return ''
    definition = definitions[0]
    if definition.startswith('@@@LINK='):
        return dictionary.mdx_lookup(definition.replace('@@@LINK=', '').strip())[0].strip()
    else:
        return definition.strip()

# Function to verify words against the MDX dictionary
def verify_words(dictionary, lessons):
    for lesson in lessons:
        print(lesson['name'])
        for word in lesson['words']:
            print('\t', word)
            lookup(dictionary, word)

# Function to convert MDX to HTML
def mdx2html(mdx_name, input_name, output_name, invalid_action=InvalidAction.Collect, with_toc=False):
    if output_name != TEMP_FILE :
        currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_name = currentTime + "-" + output_name

    dictionary = mdict_query.IndexBuilder(mdx_name)
    lessons = get_words(input_name)

    right_soup = BeautifulSoup('<body style="font-family:Arial Unicode MS;"><div class="right"></div></body>', 'lxml')
    left_soup = BeautifulSoup('<div class="left"></div>', 'lxml')
    invalid_words = OrderedDict()

    for lesson in lessons:
        print(lesson['name'])
        h1 = right_soup.new_tag('h1', id='lesson_' + lesson['name'], style=H1_STYLE)
        h1.string = lesson['name']
        right_soup.div.append(h1)

        a = left_soup.new_tag('a', href='#lesson_' + lesson['name'], **{'class': 'lesson'})
        a.string = lesson['name']
        left_soup.div.append(a)
        left_soup.div.append(left_soup.new_tag('br'))

        invalid = False
        for word in lesson['words']:
            print('\t', word)
            result = lookup(dictionary, word)
            if len(result) == 0:  # not found
                print(f'WARNING: "{word}" not found', file=sys.stderr)
                if invalid_action == InvalidAction.Exit:
                    print('*** Exit now. Do nothing. ***')
                    sys.exit()
                elif invalid_action == InvalidAction.Output:
                    invalid = True
                    result = f'<span><b>WARNING:</b> "{word}" not found</span>'
                else:  # invalid_action == InvalidAction.Collect
                    if lesson['name'] in invalid_words:
                        invalid_words[lesson['name']].append(word)
                    else:
                        invalid_words[lesson['name']] = [word, ]
                    continue
            definition = BeautifulSoup(result, 'lxml')
            if right_soup.head is None and definition.head is not None:
                right_soup.html.insert_before(definition.head)
                right_soup.head.append(right_soup.new_tag('meta', charset='utf-8'))

            h2 = right_soup.new_tag('h2', id='word_' + word, style=H2_STYLE)
            h2.string = word
            right_soup.div.append(h2)
            right_soup.div.append(definition.body)

            a = left_soup.new_tag('a', href='#word_' + word, **{'class': 'word' + (' invalid_word' if invalid else '')})
            invalid = False
            a.string = word
            left_soup.div.append(a)
            left_soup.div.append(left_soup.new_tag('br'))

        left_soup.div.append(left_soup.new_tag('br'))

    if with_toc:
        main_div = right_soup.new_tag('div', **{'class': 'main'})
        right_soup.div.wrap(main_div)
        right_soup.div.insert_before(left_soup.div)

    right_soup = merge_css(right_soup, Path(mdx_name).parent, dictionary, with_toc)
    right_soup = grab_images(right_soup, dictionary)

    html = str(right_soup).encode('utf-8')
    html = html.replace(b'<body>', b'').replace(b'</body>', b'', html.count(b'</body>') - 1)
    open(output_name, "wb").write(html)

    if len(invalid_words) > 0:
        with open(INVALID_WORDS_FILENAME, 'w') as fp:
            for lesson, words in invalid_words.items():
                fp.write(f'#{lesson}\n')
                for word in words:
                    fp.write(word + '\n')

# Function to convert MDX to PDF
def mdx2pdf(mdx_name, input_name, output_name, invalid_action=InvalidAction.Collect):
    mdx2html(mdx_name, input_name, TEMP_FILE, invalid_action, False)

    currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_name = currentTime + "-" + output_name

    # pdfkit.from_file(TEMP_FILE, output_name)
    path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path)
    # options src: https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    pdfkit.from_file(TEMP_FILE, output_name, configuration=config,
                     options={'dpi': '150',
                              'encoding': 'UTF-8',
                              'header-left': '[title]',
                              'header-right': '[page]/[toPage]',
                              'header-spacing': '2',
                              'margin-top': '15mm',
                              'margin-bottom': '18mm',
                              'margin-left': '25mm',
                              'margin-right': '18mm',
                              'header-line': True,
                              'enable-local-file-access': True})
    os.remove(TEMP_FILE)

# Function to convert MDX to JPG
def mdx2jpg(mdx_name, input_name, output_name, invalid_action=InvalidAction.Collect):
    mdx2html(mdx_name, input_name, TEMP_FILE, invalid_action, False)

    currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_name = currentTime + "-" + output_name

    imgkit.from_file(TEMP_FILE, output_name, options={'enable-local-file-access': ''})
    os.remove(TEMP_FILE)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,)
    parser.add_argument('mdx_name', action='store', nargs=1)
    parser.add_argument('input_name', action='store', nargs=1)
    parser.add_argument('output_name', action='store', nargs='?')
    parser.add_argument('--type', action='store', choices=['pdf', 'html', 'jpg'], nargs='?')
    parser.add_argument('--invalid', action='store', type=int, default=2, choices=[0, 1, 2],
                        help='action for meeting invalid words\n'
                        '0: exit immediately\n'
                        '1: output warnning message to pdf/html\n'
                        '2: collect them to invalid_words.txt (default)')
    args = parser.parse_args()

    mdx_name = args.mdx_name[0]
    input_name = args.input_name[0]

    if args.output_name is None:
        if args.type is None:
            raise EnvironmentError('You must choose a file name or a file type')
        else:
            output_name = Path(input_name).stem + '.' + args.type
    else:
        output_name = args.output_name

    if args.type is None:
        args.type = Path(output_name).suffix[1:]

    {
        'pdf': mdx2pdf,
        'html': mdx2html,
        'jpg': mdx2jpg,
    }[args.type.lower()](mdx_name, input_name, output_name, args.invalid)
