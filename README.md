# MdxScraper

## 简介

一句话：根据指定词汇，从MDX字典提取内容并输出为PDF、HTML或JPG。

详情：MdxScraper 是在 [MdxConverter](https://github.com/noword/MdxConverter) 基础上升级改造：

1. 支持同一个页面多次重复引用同一图片的情形（词典中的读音图标多次出现的情形很常见）。
2. 增加对jpg、jpeg、gif等图片的支持，原程序只支持png图片。
3. 兼容img标签的各种写法，原程序只支持一种，因此也就兼容各种词典情形。
7. 兼容无CSS文件的词典。
6. 增加PDF输出时排版的多个常见配置选项，让用户更加自由定制。
4. 将mdict-query直接放在同名子目录下，避免繁琐安装。
5. 以当前时间命名文件名，避免多次输出时覆盖原有的文件。

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

例如：

    MdxScraper 某某词典.mdx input.xlsx output.pdf

建议将mdx放入子目录mdx中，相应的命令则使用：

    MdxScraper "mdx\某某词典.mdx" input.txt output.pdf

## 依赖库安装

使用了以下第三方库，请按提示进行安装

    import imgkit  # pip install imgkit
    import pdfkit  # pip install pdfkit
    import openpyxl  # pip install openpyxl
    from chardet import detect  # pip install chardet
    from base64 import b64encode  # pip install base64
    from bs4 import BeautifulSoup  # pip install bs4

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
