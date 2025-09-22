# 核心模块 API 文档

## 概述

核心模块包含 MdxScraper 的主要功能组件，负责词典处理、文件解析、格式转换和渲染等核心业务逻辑。

## 模块结构

```
src/mdxscraper/core/
├── __init__.py
├── dictionary.py        # 词典处理
├── parser.py           # 文件解析
├── converter.py        # 格式转换
└── renderer.py         # 渲染引擎
```

## dictionary.py - 词典处理模块

### 类：DictionaryProcessor

词典处理器，封装 mdict-query 功能，提供统一的词典查询接口。

#### 初始化
```python
def __init__(self, mdx_file: Path) -> None
```
- **参数**：
  - `mdx_file` (Path): MDX 词典文件路径
- **异常**：
  - `FileNotFoundError`: 词典文件不存在
  - `ValueError`: 词典文件格式错误

#### 主要方法

##### lookup
```python
def lookup(self, word: str, ignorecase: bool = False) -> str
```
查找单词定义。

- **参数**：
  - `word` (str): 要查找的单词
  - `ignorecase` (bool): 是否忽略大小写，默认 False
- **返回**：
  - `str`: 单词定义，如果未找到返回空字符串
- **异常**：
  - `ValueError`: 输入参数无效

##### get_css
```python
def get_css(self, soup: BeautifulSoup) -> str
```
获取词典的 CSS 样式。

- **参数**：
  - `soup` (BeautifulSoup): HTML 解析对象
- **返回**：
  - `str`: CSS 样式内容
- **异常**：
  - `AttributeError`: 无法找到 CSS 文件

##### merge_css
```python
def merge_css(self, soup: BeautifulSoup, append_additional_styles: bool = True) -> BeautifulSoup
```
将 CSS 样式合并到 HTML 中。

- **参数**：
  - `soup` (BeautifulSoup): HTML 解析对象
  - `append_additional_styles` (bool): 是否添加额外样式，默认 True
- **返回**：
  - `BeautifulSoup`: 处理后的 HTML 对象

##### grab_images
```python
def grab_images(self, soup: BeautifulSoup) -> BeautifulSoup
```
将图片转换为 base64 内嵌格式。

- **参数**：
  - `soup` (BeautifulSoup): HTML 解析对象
- **返回**：
  - `BeautifulSoup`: 处理后的 HTML 对象

#### 属性

- `mdx_file` (Path): MDX 文件路径
- `dictionary` (IndexBuilder): mdict-query 词典对象
- `cache_enabled` (bool): 是否启用缓存

## parser.py - 文件解析模块

### 类：FileParser

文件解析器，负责解析不同格式的输入文件。

#### 初始化
```python
def __init__(self) -> None
```

#### 主要方法

##### parse_file
```python
def parse_file(self, file_path: Path) -> List[Dict[str, Any]]
```
解析输入文件，返回词汇列表。

- **参数**：
  - `file_path` (Path): 输入文件路径
- **返回**：
  - `List[Dict[str, Any]]`: 解析后的词汇数据
- **异常**：
  - `UnsupportedFileTypeError`: 不支持的文件类型
  - `FileParseError`: 文件解析错误

##### detect_encoding
```python
def detect_encoding(self, file_path: Path) -> str
```
检测文件编码。

- **参数**：
  - `file_path` (Path): 文件路径
- **返回**：
  - `str`: 检测到的编码格式

#### 支持的格式

- **TXT**: 纯文本文件，支持分组（以 # 开头）
- **JSON**: JSON 格式文件
- **XLSX**: Excel 文件，支持多工作表

### 函数

##### get_words_from_txt
```python
def get_words_from_txt(file_path: Path) -> List[Dict[str, Any]]
```
从文本文件解析词汇。

##### get_words_from_json
```python
def get_words_from_json(file_path: Path) -> List[Dict[str, Any]]
```
从 JSON 文件解析词汇。

##### get_words_from_xlsx
```python
def get_words_from_xlsx(file_path: Path) -> List[Dict[str, Any]]
```
从 Excel 文件解析词汇。

## converter.py - 格式转换模块

### 类：FormatConverter

格式转换器，负责将词典查询结果转换为不同输出格式。

#### 初始化
```python
def __init__(self, config: Dict[str, Any]) -> None
```
- **参数**：
  - `config` (Dict[str, Any]): 转换配置

#### 主要方法

##### convert_to_html
```python
def convert_to_html(self, lessons: List[Dict[str, Any]], 
                   dictionary: DictionaryProcessor) -> str
```
转换为 HTML 格式。

- **参数**：
  - `lessons` (List[Dict[str, Any]]): 词汇课程数据
  - `dictionary` (DictionaryProcessor): 词典处理器
- **返回**：
  - `str`: HTML 内容

##### convert_to_pdf
```python
def convert_to_pdf(self, lessons: List[Dict[str, Any]], 
                  dictionary: DictionaryProcessor, 
                  output_path: Path) -> None
```
转换为 PDF 格式。

- **参数**：
  - `lessons` (List[Dict[str, Any]]): 词汇课程数据
  - `dictionary` (DictionaryProcessor): 词典处理器
  - `output_path` (Path): 输出文件路径
- **异常**：
  - `PDFConversionError`: PDF 转换失败

##### convert_to_jpg
```python
def convert_to_jpg(self, lessons: List[Dict[str, Any]], 
                  dictionary: DictionaryProcessor, 
                  output_path: Path) -> None
```
转换为 JPG 格式。

- **参数**：
  - `lessons` (List[Dict[str, Any]]): 词汇课程数据
  - `dictionary` (DictionaryProcessor): 词典处理器
  - `output_path` (Path): 输出文件路径
- **异常**：
  - `ImageConversionError`: 图片转换失败

#### 配置选项

```python
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
```

## renderer.py - 渲染引擎模块

### 类：HTMLRenderer

HTML 渲染引擎，负责 HTML 内容的生成和样式处理。

#### 初始化
```python
def __init__(self, config: Dict[str, Any]) -> None
```
- **参数**：
  - `config` (Dict[str, Any]): 渲染配置

#### 主要方法

##### render_html
```python
def render_html(self, lessons: List[Dict[str, Any]], 
               dictionary: DictionaryProcessor) -> str
```
渲染 HTML 内容。

- **参数**：
  - `lessons` (List[Dict[str, Any]]): 词汇课程数据
  - `dictionary` (DictionaryProcessor): 词典处理器
- **返回**：
  - `str`: 渲染后的 HTML 内容

##### apply_styles
```python
def apply_styles(self, html_content: str, style_name: str = "default") -> str
```
应用样式到 HTML 内容。

- **参数**：
  - `html_content` (str): HTML 内容
  - `style_name` (str): 样式名称
- **返回**：
  - `str`: 应用样式后的 HTML 内容

##### generate_toc
```python
def generate_toc(self, lessons: List[Dict[str, Any]]) -> str
```
生成目录。

- **参数**：
  - `lessons` (List[Dict[str, Any]]): 词汇课程数据
- **返回**：
  - `str`: 目录 HTML 内容

#### 样式定义

```python
DEFAULT_STYLES = {
    'h1_style': 'color:#FFFFFF; background-color:#003366; padding-left:20px; line-height:initial;',
    'scrap_style': 'padding: 10px 0 10px 0; border-bottom: 0.5mm ridge rgba(111, 160, 206, .6);',
    'additional_styles': '''
        a.lesson {font-size:120%; color: #1a237e; text-decoration: none; cursor: pointer; border-bottom: none;}
        a.lesson:hover {background-color: #e3f2fd}
        a.word {color: #1565c0; text-decoration: none; cursor: pointer; font-variant: normal; font-weight: normal; border-bottom: none;}
        a.word:hover {background-color: #e3f2fd;}
        a.invalid_word {color: #909497;}
        div.main {width: 100%; height: 100%;}
        div.left {width: 180px; overflow: auto; float: left; height: 100%;}
        div.right {overflow-y: auto; overflow-x: hidden; padding-left: 10px; height: 100%;}
    '''
}
```

## 异常定义

### 自定义异常类

```python
class MdxScraperError(Exception):
    """MdxScraper 基础异常类"""
    pass

class UnsupportedFileTypeError(MdxScraperError):
    """不支持的文件类型异常"""
    pass

class FileParseError(MdxScraperError):
    """文件解析错误异常"""
    pass

class PDFConversionError(MdxScraperError):
    """PDF 转换错误异常"""
    pass

class ImageConversionError(MdxScraperError):
    """图片转换错误异常"""
    pass

class DictionaryError(MdxScraperError):
    """词典处理错误异常"""
    pass
```

## 使用示例

### 基本使用

```python
from pathlib import Path
from mdxscraper.core.dictionary import DictionaryProcessor
from mdxscraper.core.parser import FileParser
from mdxscraper.core.converter import FormatConverter

# 初始化组件
dictionary = DictionaryProcessor(Path("data/mdict/collins.mdx"))
parser = FileParser()
converter = FormatConverter(config)

# 解析输入文件
lessons = parser.parse_file(Path("data/input/words.txt"))

# 转换为 HTML
html_content = converter.convert_to_html(lessons, dictionary)

# 保存结果
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html_content)
```

### 错误处理

```python
from mdxscraper.core.exceptions import DictionaryError, FileParseError

try:
    dictionary = DictionaryProcessor(Path("invalid.mdx"))
except DictionaryError as e:
    print(f"词典处理错误: {e}")

try:
    lessons = parser.parse_file(Path("invalid.txt"))
except FileParseError as e:
    print(f"文件解析错误: {e}")
```

## 性能考虑

### 缓存机制
- 词典索引缓存
- 查询结果缓存
- 图片 base64 缓存

### 内存优化
- 流式处理大文件
- 延迟加载非关键资源
- 及时释放大对象

### 并发处理
- 多线程处理多个词汇
- 异步 I/O 操作
- 批量处理优化
