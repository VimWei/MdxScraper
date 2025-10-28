# 单词查询快速指南

## 快速开始

### 方法 1: 使用 query_word.py (推荐 - 最简单)

这是最快捷的方式，一条命令即可获得完整的 HTML 输出（包含完整的 CSS 样式）。

```bash
# 基本用法（需要指定词典文件）
python examples/query_word.py hello --mdx data/mdict/your_dict.mdx

# 保存到文件
python examples/query_word.py hello --mdx data/mdict/your_dict.mdx --output hello.html

# 使用 uv 运行
uv run python examples/query_word.py hello --mdx data/mdict/your_dict.mdx
```

**输出特点**:
- ✅ 完整的 HTML5 文档结构
- ✅ 内嵌现代化 CSS 样式（无需外部文件）
- ✅ 响应式设计，支持移动端
- ✅ 优雅的渐变色标题
- ✅ 打印友好
- ✅ 支持深色/浅色主题

### 方法 2: 使用 single_word_query.py (功能更丰富)

提供多种模式选择：

```bash
# 简单模式 - 仅获取原始 HTML
python examples/single_word_query.py hello --mdx-file data/mdict/dict.mdx

# 完整模式 - 包含 CSS 和嵌入图片
python examples/single_word_query.py hello \
    --mdx-file data/mdict/dict.mdx \
    --output hello.html \
    --complete

# 自定义 CSS 模式
python examples/single_word_query.py hello \
    --mdx-file data/mdict/dict.mdx \
    --output hello.html \
    --custom-css

# 查看所有选项
python examples/single_word_query.py --help
```

### 方法 3: Python 代码直接调用

```python
from pathlib import Path
from mdxscraper import Dictionary

# 打开词典
mdx_file = Path("data/mdict/your_dict.mdx")
with Dictionary(mdx_file) as dict:
    # 查询单词
    html = dict.lookup_html("hello")
    
    if html:
        print("找到定义:")
        print(html)
    else:
        print("未找到该单词")
```

## 完整 CSS 样式代码

如果你想在自己的项目中使用相同的样式，这里是完整的 CSS 代码：

```css
/* 基础重置 */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

/* 主体样式 */
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    line-height: 1.6;
    color: #24292f;
    background-color: #ffffff;
    padding: 20px;
}

/* 容器 */
.container {
    max-width: 900px;
    margin: 0 auto;
}

/* 单词标题区域 */
.word-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    border-radius: 12px 12px 0 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.word-title {
    font-size: 2.5em;
    font-weight: 700;
    margin-bottom: 10px;
}

/* 词条内容区域 */
.word-content {
    background: #ffffff;
    border: 1px solid #d0d7de;
    border-top: none;
    border-radius: 0 0 12px 12px;
    padding: 30px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* 标题样式 */
.word-content h1 {
    font-size: 1.8em;
    color: #1f2328;
    border-bottom: 2px solid #d0d7de;
    padding-bottom: 10px;
    margin: 20px 0 15px 0;
}

.word-content h2 {
    font-size: 1.5em;
    color: #1f2328;
    margin: 15px 0 10px 0;
}

/* 链接样式 */
.word-content a {
    color: #0969da;
    text-decoration: none;
}

.word-content a:hover {
    text-decoration: underline;
}

/* 代码样式 */
.word-content code {
    background: #f6f8fa;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
}

/* 响应式设计 */
@media (max-width: 768px) {
    body {
        padding: 10px;
    }
    
    .word-header {
        padding: 20px;
    }
    
    .word-title {
        font-size: 2em;
    }
}
```

## 实际使用示例

### 示例 1: 快速查询并在浏览器中打开

```bash
# Windows
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html
start hello.html

# macOS
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html
open hello.html

# Linux
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html
xdg-open hello.html
```

### 示例 2: 批量查询多个单词

```bash
# 创建批处理脚本
cat > query_words.sh << 'EOF'
#!/bin/bash
WORDS=("hello" "world" "python" "dictionary")
MDX="data/mdict/my_dict.mdx"

for word in "${WORDS[@]}"; do
    echo "Querying: $word"
    python examples/query_word.py "$word" --mdx "$MDX" --output "output/${word}.html"
done
EOF

chmod +x query_words.sh
./query_words.sh
```

### 示例 3: 集成到 Web 应用

```python
from flask import Flask, request, jsonify
from pathlib import Path
from mdxscraper import Dictionary

app = Flask(__name__)
mdx_file = Path("data/mdict/dict.mdx")
dict_cache = Dictionary(mdx_file)

@app.route('/query/<word>')
def query_word(word):
    html = dict_cache.lookup_html(word)
    if html:
        return jsonify({
            'word': word,
            'html': html,
            'found': True
        })
    else:
        return jsonify({
            'word': word,
            'found': False
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
```

## 常见问题

### Q: 如何修改 CSS 样式？

**A:** 编辑 `examples/query_word.py` 文件中的 `<style>` 部分，或使用 `single_word_query.py` 的 `--custom-css` 模式。

### Q: 如何处理词典中的图片？

**A:** 使用 `single_word_query.py --complete` 模式会自动将图片转换为 base64 嵌入。

### Q: 输出文件太大怎么办？

**A:** 
- 使用简单模式（不嵌入图片）
- 压缩 HTML: `python -m htmlmin input.html output.html`
- 使用 gzip 压缩: `gzip output.html`

### Q: 如何自定义颜色主题？

**A:** 修改 CSS 中的颜色变量：

```css
/* 蓝色主题 */
.word-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 绿色主题 */
.word-header {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

/* 红色主题 */
.word-header {
    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
}
```

## 性能提示

1. **缓存词典对象**: 如果需要查询多个单词，重用同一个 `Dictionary` 对象
2. **使用简单模式**: 如果不需要完整样式，使用原始 HTML 输出更快
3. **按需加载图片**: 大型词典的图片可能很大，仅在需要时嵌入

## 相关文档

- [主 README](../README.md) - 项目总览
- [API 文档](../docs/HEADLESS_API.md) - 完整 API 参考
- [快速入门](../docs/QUICKSTART.md) - 5 分钟教程
- [更多示例](README.md) - 所有示例列表
