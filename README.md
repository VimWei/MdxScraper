# MdxToPDF

这是一个用来从 mdx 字典中抓取所需的单词，并生成 html，pdf 或 jpg 文件的小工具。

## 加强版说明

对 [原版 MdxConverter](https://github.com/noword/MdxConverter) 做了改造加强：

1. 支持同一个页面多次重复引用同一图片的情形（词典中的读音图标多次出现的情形很常见）。
2. 增加对jpg、jpeg、gif等图片的支持，原程序只支持png图片。
3. 兼容img标签的各种写法，原程序只支持一种，因此也就兼容各种词典情形。
4. 将mdict-query直接放在MdxConverter子目录下，而不是都放在根目录下，这样可以让程序看起来更清爽。
5. 以当前时间命名文件名，避免多次输出时覆盖原有的文件。
6. 增加PDF输出时排版的多个常见配置选项，让用户更加自由定制。
7. 支持没有独立CSS的词典。

## 用法
    usage: MdxConverter.py [-h] [--type [{pdf,html,jpg}]] [--invalid {0,1,2}] mdx_name input_name [output_name]

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

    MdxConverter 某某词典.mdx input.xlsx output.pdf

可以将mdx放入子目录mdx中，这样根目录会更清爽，相应的命令则使用：

    MdxConverter "mdx\某某词典.mdx" input.txt output.pdf

## 依赖库
[mdict-query](https://github.com/mmjang/mdict-query) 本程序已包含该库原版，若有更新，直接完整替换本程序子目录mdict-query-master即可。

[BeautifulSoup4](https://pypi.org/project/beautifulsoup4)

[openpyxl](https://pypi.org/project/openpyxl)

[pdfkit](https://github.com/JazzCore/python-pdfkit)

[imgkit](https://github.com/jarrekk/imgkit)

[lxml](https://lxml.de)

[chardet](https://github.com/chardet/chardet)

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
