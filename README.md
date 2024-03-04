# MdxScraper

## 简介

一句话：根据指定词汇，从MDX字典提取内容并输出为HTML、PDF或JPG。

详情：MdxScraper 是在 [MdxConverter](https://github.com/noword/MdxConverter) 基础上升级改造：

1. 提升词典兼容性：
    * 内置并升级mdict-query，支持多mdd的词典。
    * 兼容有或无CSS文件的词典。
    * 兼容html中img标签的多种写法。
    * 兼容支持png、jpg、jpeg、gif等常见图片格式。
    * 支持同一个页面多次重复引用同一图片的情形，如读音图标等。
2. 提升跨平台兼容性：
    * 文件路径名，兼容跨平台的多种的写法。
    * wkhtmltopdf安装目录，兼容跨平台的多种情形。
3. 重构程序，更加便捷、易用、强健和友好：
    * 采用配置文件方式，而非命令行参数，配合conda可以一键输出，更便捷。
    * 丰富配置选项，包括输入输出文件、词典文件、PDF排版、CSS等，更强大。
    * 增加时间戳到输出文件名，方便归档查阅所有输出文件，文件管理更方便。
    * 输出信息增加程序状态、查询统计、输出地址、耗时等信息，体验更友好。

## 安装

1. 安装以下第三方库
    * pip install imgkit
    * pip install pdfkit
    * pip install openpyxl
    * pip install chardet
    * pip install base64
    * pip install bs4

2. 安装wkhtmltopdf
    * https://wkhtmltopdf.org/downloads.html

## 使用

1. 配置参数：settings.py
2. 运行程序：python MdxScraper.py

## 高级技巧

* 上述“使用”中的第2条，在实际操作时，其实还挺麻烦的：
    1. 启动命令行：cmd 或 terminal等
    2. 查询conda环境：conda env list
    3. 激活conda环境：conda activate MdxScraper
    4. 输入命令：python MdxScraper.py
* 为简化上述步骤，可使用以下高级技巧，只要双击一个快捷键即可完成。
    - 说明1: 本技巧非必须，是可选项。
    - 说明2: 本技巧适用Window平台，其他平台同理。

1. 安装：使用miniconda配置独立的MdxScraper运行环境，避免其他程序干扰
    * 建立conda环境：conda create -n MdxScraper python
    * 进入conda环境：conda activate MdxScraper
    * 安装第三方库：同上“安装”章节
2. 配置：在程序根目录下创建快捷键Conda MdxScraper.lnk
    * 右键/属性/目标/修订并填入：
    ```
    %windir%\System32\cmd.exe "/K" C:\Users\YOURNAME\miniconda3\Scripts\activate.bat C:\Users\YOURNAME\miniconda3\envs\MdxScraper & cd c:\Apps\MdxScraperLocal\ & MdxScraper.py
    ```
    * 修订内容：请根据您的电脑配置信息，更改上述miniconda和MdxScraper的相关目录
    * 目的：双击该快捷键即可一步到位——启动命令行/激活conda中的MdxScraper环境/执行程序MdxScraper.py
3. 改进后的实际操作：
    * 配置参数：settings.py
    * 运行程序：双击快捷键Conda MdxScraper.lnk，完成

## 案例演示

* 输入（支持txt、json和excel）
    * input\words_to_lookup.txt
    * input\words_to_lookup.json
    * input\words_to_lookup.xlsx

* 输出（支持html、pdf和jpg）
    * ![html](lib/images/html.jpg)
