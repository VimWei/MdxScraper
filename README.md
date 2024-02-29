# MdxScraper

## 简介

一句话：根据指定词汇，从MDX字典提取内容并输出为PDF、HTML或JPG。

详情：MdxScraper 是在 [MdxConverter](https://github.com/noword/MdxConverter) 基础上升级改造：

1. 全面提升跨平台兼容性，包括wkhtmltopdf、mdx路径名等在跨平台中的多种写法。
2. 支持同一个页面多次重复引用同一图片的情形（词典中的读音图标多次出现的情形很常见）。
3. 增加对jpg、jpeg、gif等图片的支持，原程序只支持png图片。
4. 兼容img标签的各种写法，原程序只支持一种，因此也就兼容各种词典情形。
5. 兼容无CSS文件的词典。
6. 增加PDF输出时排版的多个常见配置选项，让用户更加自由定制。
7. 升级mdict-query使其支持多mdd的词典，并将该模块内置到项目中，无需单独安装
8. 以当前时间命名文件名，避免多次输出时覆盖原有的文件。

## 用法
    usage: MdxScraper.py [-h] [--type [{pdf,html,jpg}]] [--invalid {0,1,2}] mdx_name input_name [output_name]

    positional arguments:
    mdx_name
    input_name
    output_name

    optional arguments:
    -h, --help            show this help message and exit
    --type [{pdf,html,jpg}]
    --invalid {0,1,2}     action for meeting invalid words
                            0: exit immediately
                            1: output warnning message to pdf/html
                            2: collect them to invalid_words.txt (default)

例如：MdxScraper.py 某某词典.mdx input.xlsx output.pdf

或将mdx放入子目录mdx中：MdxScraper.py "mdx\某某词典.mdx" input.txt output.pdf

## 依赖库及程序

使用了以下第三方库，请按提示进行安装

    import imgkit  # pip install imgkit
    import pdfkit  # pip install pdfkit
    import openpyxl  # pip install openpyxl
    from chardet import detect  # pip install chardet
    from base64 import b64encode  # pip install base64
    from bs4 import BeautifulSoup  # pip install bs4

转PDF用到了wkhtmltopdf，兼容各平台，按需下载安装，并修订本程序中的相关路径：

    https://wkhtmltopdf.org/downloads.html

## 输入
### txt 示例
    #Lesson 1
    hello
    world

    #Lesson 2
    python
    is
    awesome

### json 示例
```javascript
 [
 {
     "name": "Lesson 1",
     "words": [
         "hello",
         "world"
     ]
 },
 {
     "name": "Lesson 2",
     "words": [
         "python",
         "is",
         "awesome"
     ]
 }
 ]
```

### excel 示例
![](images/excel.jpg)

## 输出
### HTML
![](images/html.jpg)

### PDF
![](images/pdf.jpg)

### JPG
略
