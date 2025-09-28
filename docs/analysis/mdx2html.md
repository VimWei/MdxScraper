逐句解读 `mdx2html` 函数（第21-132行）：

## 函数签名和参数（第21-30行）

```python
def mdx2html(
    mdx_file: str | Path,           # MDX词典文件路径
    input_file: str | Path,         # 输入单词列表文件路径
    output_file: str | Path,        # 输出HTML文件路径
    with_toc: bool = True,          # 是否生成目录
    h1_style: str | None = None,    # H1标题的CSS样式
    scrap_style: str | None = None, # 单词条目的CSS样式
    additional_styles: str | None = None, # 额外的CSS样式
    progress_callback: Optional[Callable[[int, str], None]] = None, # 进度回调函数
) -> Tuple[int, int, OrderedDict]:  # 返回：找到的单词数、未找到的单词数、无效单词字典
```

## 初始化变量（第31-32行）

```python
found_count = 0      # 在词典中找到的单词计数
not_found_count = 0  # 在词典中未找到的单词计数
```

## 文件路径处理和对象创建（第34-36行）

```python
mdx_file = Path(mdx_file)                    # 将MDX文件路径转换为Path对象
dictionary = Dictionary(mdx_file)            # 创建词典对象，用于查询单词
lessons = WordParser(str(input_file)).parse() # 使用WordParser类解析输入文件，获取课程和单词列表
```

## 进度回调（第38-39行）

```python
if progress_callback:
    progress_callback(5, "Loading dictionary and parsing input...")
```
如果有进度回调函数，报告5%的进度，表示正在加载词典和解析输入。

## 创建HTML结构（第41-43行）

```python
right_soup = BeautifulSoup('<body style="font-family:Arial Unicode MS;"><div class="right"></div></body>', 'lxml')
right_soup.find('body').insert_before('\n')
left_soup = BeautifulSoup('<div class="left"></div>', 'lxml')
```
- 创建右侧内容区域的BeautifulSoup对象，包含一个带有字体样式的body和right div
- 在body前插入换行符
- 创建左侧目录区域的BeautifulSoup对象

## 初始化处理变量（第45-47行）

```python
invalid_words = OrderedDict()  # 存储无效单词的字典，按课程分组
total_lessons = len(lessons)   # 总课程数
processed_lessons = 0          # 已处理的课程数
```

## 主处理循环（第49-104行）

### 进度报告（第50-52行）
```python
if progress_callback:
    progress = 10 + int((processed_lessons / total_lessons) * 60)
    progress_callback(progress, f"Processing lesson: {lesson['name']}")
```
计算进度（10%-70%），报告当前处理的课程名称。

### 创建课程标题（第54-58行）
```python
h1 = right_soup.new_tag('h1', id='lesson_' + lesson['name'])
if h1_style:
    h1['style'] = h1_style
h1.string = lesson['name']
right_soup.div.append(h1)
```
- 创建H1标题标签，ID为课程名
- 如果提供了H1样式，则应用
- 设置标题文本为课程名
- 将标题添加到右侧内容区域

### 创建目录链接（第60-64行）
```python
a = left_soup.new_tag('a', href='#lesson_' + lesson['name'], **{'class': 'lesson'})
a.string = lesson['name']
left_soup.div.append(a)
left_soup.div.append(left_soup.new_tag('br'))
left_soup.div.append('\n')
```
- 创建指向课程标题的链接
- 设置链接文本为课程名
- 添加链接、换行符和换行到左侧目录

### 处理单词（第66-101行）

#### 初始化无效标志（第66行）
```python
invalid = False
```

#### 单词查询循环（第67-101行）
```python
for word in lesson['words']:
    result = dictionary.lookup_html(word)  # 在词典中查找单词的HTML内容
```

#### 处理未找到的单词（第69-76行）
```python
if len(result) == 0:
    not_found_count += 1
    # Always collect invalid words and embed a warning
    if lesson['name'] in invalid_words:
        invalid_words[lesson['name']].append(word)
    else:
        invalid_words[lesson['name']] = [word]
    invalid = True
```
- 如果查询结果为空，增加未找到计数
- 将无效单词添加到对应课程的列表中
- 设置无效标志为True

#### 处理找到的单词（第78-79行）
```python
else:
    found_count += 1
```
如果找到单词，增加找到计数。

#### 处理HTML内容（第81-94行）
```python
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
```
- 将查询结果解析为BeautifulSoup对象
- 如果右侧内容没有head且查询结果有head，则复制head并添加UTF-8编码meta标签
- 创建新的div容器，设置ID、类和样式
- 将查询结果的body内容添加到新div中
- 将新div添加到右侧内容区域

#### 创建单词链接（第96-101行）
```python
a = left_soup.new_tag('a', href='#word_' + word, **{'class': 'word' + (' invalid_word' if invalid else '')})
invalid = False
a.string = word
left_soup.div.append(a)
left_soup.div.append(left_soup.new_tag('br'))
left_soup.div.append('\n')
```
- 创建指向单词的链接，如果单词无效则添加'invalid_word'类
- 重置无效标志
- 设置链接文本为单词
- 添加链接、换行符和换行到左侧目录

#### 课程间分隔（第103-104行）
```python
left_soup.div.append(left_soup.new_tag('br'))
processed_lessons += 1
```
在课程间添加换行符，增加已处理课程计数。

## 生成目录（第106-109行）

```python
if with_toc:
    main_div = right_soup.new_tag('div', **{'class': 'main'})
    right_soup.div.wrap(main_div)
    right_soup.div.insert_before(left_soup.div)
```
如果需要目录：
- 创建主容器div
- 将右侧内容包装在主容器中
- 将左侧目录插入到右侧内容之前

## 合并CSS样式（第111-113行）

```python
if progress_callback:
    progress_callback(75, "Merging CSS styles...")
right_soup = merge_css(right_soup, mdx_file.parent, dictionary.impl, additional_styles)
```
报告75%进度，合并词典的CSS样式和额外样式。

## 嵌入图片（第115-117行）

```python
if progress_callback:
    progress_callback(85, "Embedding images...")
right_soup = embed_images(right_soup, dictionary.impl)
```
报告85%进度，将图片嵌入到HTML中。

## 写入HTML文件（第119-126行）

```python
if progress_callback:
    progress_callback(90, "Writing HTML file...")
html = str(right_soup).encode('utf-8')
html = html.replace(b'<body>', b'').replace(b'</body>', b'', html.count(b'</body>') - 1)
# Ensure output directory exists
Path(output_file).parent.mkdir(parents=True, exist_ok=True)
with open(output_file, 'wb') as file:
    file.write(html)
```
- 报告90%进度
- 将BeautifulSoup对象转换为UTF-8编码的字节串
- 清理多余的body标签
- 确保输出目录存在
- 将HTML内容写入文件

## 完成处理（第128-132行）

```python
if progress_callback:
    progress_callback(100, "HTML generation completed!")

# Return invalid_words data for caller to handle file output
return found_count, not_found_count, invalid_words
```
- 报告100%完成进度
- 返回找到的单词数、未找到的单词数和无效单词字典

这个函数的主要功能是将MDX词典文件中的单词定义转换为HTML格式，支持目录生成、样式定制和进度报告。

## Dictionary 类说明

`Dictionary` 类是对原有 `mdict_query.IndexBuilder` 的封装和增强，提供更智能的单词查找功能：

- **智能回退策略**：支持大小写忽略、连字符移除等多种查找策略
- **自动链接处理**：自动处理词典中的 `@@@LINK=` 链接
- **资源管理**：支持上下文管理器，自动清理资源
- **良好封装**：隐藏底层实现细节，提供简洁的API
- **向后兼容**：通过 `impl` 属性访问底层 `IndexBuilder` 实例

## WordParser 类说明

`WordParser` 是一个统一的单词解析器类，替代了原来的 `get_words` 函数，提供面向对象的文件解析方式：

- **支持多种格式**：.txt、.md、.json、.xls、.xlsx
- **自动编码检测**：使用 chardet 库自动检测文件编码
- **错误处理**：内置异常处理，解析失败时返回空列表
- **统一接口**：所有文件格式使用相同的解析接口
- **面向对象设计**：更好的封装和可扩展性
