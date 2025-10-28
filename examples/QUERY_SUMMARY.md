# 单词查询功能总结

## 📋 已创建的文件

### 1. `examples/query_word.py` ⭐ **推荐使用**

**最简单、最快速的单词查询工具**

- ✅ 一条命令即可查询单词并输出完整 HTML
- ✅ 内置精美的 CSS 样式（无需外部文件）
- ✅ 现代化设计：渐变色标题、响应式布局、打印优化
- ✅ 完整的 HTML5 文档结构

**使用方法**:
```bash
# 查询单词（打印到控制台）
python examples/query_word.py hello --mdx data/mdict/dict.mdx

# 保存到文件
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html
```

**特点**:
- 自动处理大小写、连字符
- 支持词典链接跳转
- 输出包含完整 CSS（约 200 行样式代码）
- 可直接在浏览器中打开，无需其他依赖

---

### 2. `examples/single_word_query.py`

**功能更丰富的高级查询工具**

提供三种模式：
1. **简单模式**: 仅输出原始 HTML（来自词典）
2. **完整模式**: HTML + CSS + 嵌入的图片（base64）
3. **自定义 CSS 模式**: 应用自定义样式

**使用方法**:
```bash
# 简单模式
python examples/single_word_query.py hello --mdx-file dict.mdx

# 完整模式（包含图片）
python examples/single_word_query.py hello --mdx-file dict.mdx --output out.html --complete

# 自定义 CSS
python examples/single_word_query.py hello --mdx-file dict.mdx --output out.html --custom-css

# 不包含图片（减小文件大小）
python examples/single_word_query.py hello --mdx-file dict.mdx --output out.html --complete --no-images
```

---

### 3. `examples/WORD_QUERY_GUIDE.md`

**完整使用指南文档**

包含内容：
- 三种查询方法的详细说明
- 完整的 CSS 代码（可复制使用）
- 实际使用示例（批量查询、Web 集成等）
- 常见问题解答
- 性能优化建议
- 自定义主题颜色示例

---

## 🎨 内置 CSS 样式特点

### 设计风格
- **现代简洁**: GitHub 风格的清爽设计
- **渐变标题**: 紫色到紫红色的渐变背景
- **圆角卡片**: 12px 圆角，柔和的阴影效果
- **响应式**: 自动适配手机、平板、桌面

### 样式覆盖
```css
- 标题样式 (h1, h2, h3)
- 段落和列表
- 链接（蓝色主题）
- 代码块（浅灰背景）
- 表格样式
- 图片（自动缩放）
- 引用块
- 打印样式优化
```

### 颜色方案
- **主色**: `#667eea` → `#764ba2` (紫色渐变)
- **文字**: `#24292f` (深灰)
- **链接**: `#0969da` (蓝色)
- **边框**: `#d0d7de` (浅灰)
- **背景**: `#f6f8fa` (极浅灰)

---

## 📊 对比三种方法

| 特性 | query_word.py | single_word_query.py | 直接调用 API |
|------|---------------|----------------------|--------------|
| **易用性** | ⭐⭐⭐⭐⭐ 最简单 | ⭐⭐⭐⭐ 较简单 | ⭐⭐⭐ 需要编码 |
| **CSS 样式** | ✅ 内置精美样式 | ✅ 多种样式选择 | ❌ 需要自己写 |
| **图片嵌入** | ❌ 不支持 | ✅ 支持 | ✅ 可以实现 |
| **自定义性** | ⭐⭐ 有限 | ⭐⭐⭐⭐⭐ 高度自定义 | ⭐⭐⭐⭐⭐ 完全自定义 |
| **文件大小** | ⭐⭐⭐⭐ 小 | ⭐⭐ 较大（如果嵌入图片） | 看实现方式 |
| **适合场景** | 快速查询、日常使用 | 完整导出、归档 | 集成到应用中 |

---

## 🚀 快速开始（3 步）

### 步骤 1: 准备词典文件
```bash
# 将你的 MDX 词典文件放到 data/mdict/ 目录
cp /path/to/your_dict.mdx data/mdict/
```

### 步骤 2: 查询单词
```bash
# 最简单的方式
python examples/query_word.py hello --mdx data/mdict/your_dict.mdx --output hello.html
```

### 步骤 3: 在浏览器中打开
```bash
# Windows
start hello.html

# macOS
open hello.html

# Linux
xdg-open hello.html
```

---

## 💡 使用场景

### 场景 1: 学习笔记
快速查询单词并保存到 HTML 文件，方便复习：
```bash
python examples/query_word.py vocabulary --mdx dict.mdx --output notes/vocabulary.html
```

### 场景 2: 制作词汇卡片
批量查询单词，生成精美的 HTML 卡片：
```bash
for word in $(cat wordlist.txt); do
    python examples/query_word.py "$word" --mdx dict.mdx --output "cards/${word}.html"
done
```

### 场景 3: Web 应用集成
在 Flask/Django 中集成：
```python
from mdxscraper import Dictionary

dict = Dictionary("dict.mdx")
html = dict.lookup_html(user_input_word)
# 返回给前端显示
```

### 场景 4: Anki 卡片制作
导出为 HTML，导入到 Anki 中制作记忆卡片

### 场景 5: 离线词典 App
结合 Electron 或 Tauri 制作桌面应用

---

## 📝 完整的 CSS 代码位置

完整的 CSS 代码（约 200 行）在以下文件中：

1. **查看代码**: `examples/query_word.py` 第 77-262 行
2. **复制使用**: 见 `examples/WORD_QUERY_GUIDE.md` 的 "完整 CSS 样式代码" 部分
3. **在线查看**: 打开任何生成的 HTML 文件，在浏览器中"查看源代码"

---

## 🎯 核心代码片段

### 最简单的查询代码
```python
from mdxscraper import Dictionary

with Dictionary("dict.mdx") as dict:
    html = dict.lookup_html("hello")
    print(html)  # 输出原始 HTML
```

### 带完整 CSS 的查询
```python
from mdxscraper import Dictionary

def query_with_css(mdx_file, word):
    with Dictionary(mdx_file) as dict:
        content = dict.lookup_html(word)
        if not content:
            return None
        
        # 使用 query_word.py 中的 CSS 模板
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{word}</title>
    <style>
        /* 这里放置 CSS 代码 */
        body {{ font-family: sans-serif; }}
        /* ... 更多样式 ... */
    </style>
</head>
<body>
    <div class="container">
        <div class="word-header">
            <div class="word-title">{word}</div>
        </div>
        <div class="word-content">
            {content}
        </div>
    </div>
</body>
</html>"""
        return html
```

---

## 🔧 自定义建议

### 修改颜色主题
编辑 `query_word.py` 第 100-105 行的渐变色：

```python
# 原始（紫色）
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

# 改为蓝色
background: linear-gradient(135deg, #2E3192 0%, #1BFFFF 100%);

# 改为绿色
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

# 改为橙色
background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 100%);
```

### 调整字体大小
编辑第 85-90 行：

```python
body {
    font-size: 16px;  # 改为你喜欢的大小
    line-height: 1.6;
}
```

### 添加自定义样式
在 `</style>` 标签之前添加你的 CSS 代码。

---

## 📚 相关文档

- **主文档**: `README.md` - 项目总览
- **API 参考**: `docs/HEADLESS_API.md` - 完整 API 文档
- **快速入门**: `docs/QUICKSTART.md` - 5 分钟教程
- **示例说明**: `examples/README.md` - 所有示例列表
- **查询指南**: `examples/WORD_QUERY_GUIDE.md` - 本功能详细说明

---

## ✅ 总结

我们创建了两个强大的单词查询工具：

1. **query_word.py** - 适合日常快速查询，内置精美样式
2. **single_word_query.py** - 适合高级用户，功能更丰富

两者都提供：
- ✅ 完整的 HTML 输出（无需外部 CSS 文件）
- ✅ 现代化的设计风格
- ✅ 命令行接口，易于使用
- ✅ 支持自定义和扩展

**推荐使用 `query_word.py` 开始！** 🚀
