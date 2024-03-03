#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MdxScraper Setting

# 设置要查询的词条文件的位置，支持txt、json和excel
INPUT_PATH = 'input'
INPUT_NAME = 'words_to_lookup.txt'

# 设置要查询的词典文件的位置，支持多mdd
DICTIONARY_PATH = 'lib/mdict'
DICTIONARY_NAME = 'my_dictionary.mdx'

# 设置输出文件的位置及名称，支持html、pdf和jpg
OUTPUT_PATH = 'output'
OUTPUT_NAME = 'lookup_results.html'

# 设置无效单词的处理方式
from enum import IntEnum
class InvalidAction(IntEnum):
    Exit = 0 # 退出程序
    Collect = 1 # 收集无效单词
    OutputWarning = 2 # 输出警告信息到输出文件中
    Collect_OutputWarning = 3 # 收集无效单词，并输出警告信息
INVALID_ACTION = InvalidAction.Collect_OutputWarning
INVALID_WORDS_NAME = 'invalid_words.txt'

# 配置不同操作系统的 wkhtmltopdf 安装路径
WKHTMLTOPDF_PATHS = {
    'Windows': r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
    'Linux': '/usr/local/bin/wkhtmltopdf',
    'Linux_alt': '/usr/bin/wkhtmltopdf',
    'Darwin': '/usr/local/bin/wkhtmltopdf'
}

# 配置PDF输出选项，ref: https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
PDF_OPTIONS = {
    'dpi': '150',
    'encoding': 'UTF-8',
    'header-left': '[title]',
    'header-right': '[page]/[toPage]',
    'header-spacing': '2',
    'margin-top': '15mm',
    'margin-bottom': '18mm',
    'margin-left': '25mm',
    'margin-right': '18mm',
    'header-line': True,
    'enable-local-file-access': True
}

# 配置CSS样式
H1_STYLE = 'color:#FFFFFF; background-color:#003366; padding-left:20px; line-height:initial;'
SCRAP_STYLE ='margin: 20px 0 0 0; border-bottom: 0.2mm ridge rgba(111, 160, 206, .6);'
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