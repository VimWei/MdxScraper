#!/usr/bin/env python
# -*- coding: utf-8 -*-
# MdxScraper settings

# 设置要查询的词条文件的位置，支持txt、json和excel
INPUT_PATH = 'input'
INPUT_NAME = 'words_to_lookup.txt'

# 设置词典文件的存放位置
DICTIONARY_PATH = 'lib/mdict'
# 定义可用词典列表，可以使用子目录
dictionaries = {
    "Chinese": [
        '汉字源流大字典/汉字源流大字典.mdx',
        '现代汉语规范词典/现代汉语规范词典2.mdx',
        '现代汉语大词典/现代汉语大词典（图文综合版）.mdx',
        '汉语辞海/汉语辞海20190923重排.mdx',
    ],
    "English": [
        '简明英汉增强升级必应版/concise-bing.mdx',
        'Collins COBUILD 8th/Collins COBUILD 8th.mdx',
        '牛津小学生英汉双解词典/OxfordPrimary.mdx',
        'Longman Active Study Dictionary/LASD 5th.mdx',
        '朗文当代高级英语辞典/朗文当代高级英语辞典4th.mdx',
        '普通高中英语课程标准词汇简明字典/《词汇表》简明字典2023版国庆节.mdx',
    ],
    "Others": [
        '牛津外研社英汉汉英词典/Oxford·FLTRP EC-CE Dictionary.mdx',
        'CC-CEDICT/CC-CEDICT 230908.mdx',
        'my_dictionary.mdx',
    ],
}
# 选择要查询的词典：类别（需要引号）和编号（从零开始）
DICTIONARY_NAME = dictionaries['English'][3]

# 设置输出文件的位置
OUTPUT_PATH = 'output'
# 设置输出文件名，支持html、pdf和jpg；若为空，则采用'输入文件名.html'
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
SCRAP_STYLE ='padding: 10px 0 10px 0; border-bottom: 0.5mm ridge rgba(111, 160, 206, .6);'
ADDITIONAL_STYLES = '''
a.lesson {font-size:120%; color: #1a237e; text-decoration: none; cursor: pointer; border-bottom: none;}
a.lesson:hover {background-color: #e3f2fd}
a.word {color: #1565c0; text-decoration: none; cursor: pointer; font-variant: normal; font-weight: normal; border-bottom: none;}
a.word:hover {background-color: #e3f2fd;}
a.invalid_word {color: #909497;}
div.main {width: 100%; height: 100%;}
div.left {width: 180px; overflow: auto; float: left; height: 100%;}
div.right {overflow-y: auto; overflow-x: hidden; padding-left: 10px; height: 100%;}
'''
