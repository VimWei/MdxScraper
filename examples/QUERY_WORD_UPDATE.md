# query_word.py 更新说明

## 🎉 新功能：自动提取词典内部 CSS

`query_word.py` 已升级，现在可以**自动提取并嵌入词典内部的 CSS 样式**！

---

## ✨ 主要改进

### 1. 自动提取词典 CSS
- ✅ 自动检测并提取词典内部的 CSS 文件
- ✅ 将词典 CSS 作为 inline 样式嵌入到输出的 HTML 中
- ✅ 保留词典原有的样式效果

### 2. 自动嵌入图片
- ✅ 将词典中的图片转换为 base64 格式嵌入
- ✅ 生成的 HTML 文件完全独立，无需外部资源
- ✅ 可选择关闭图片嵌入（使用 `--no-images` 参数）

### 3. 双层 CSS 系统
输出的 HTML 包含两层 CSS：
```html
<style>
    /* ========== 词典内部 CSS ========== */
    /* 这里是从词典中提取的原始 CSS */
    
    /* ========== 自定义样式 ========== */
    /* 这里是我们添加的美化样式 */
</style>
```

---

## 📖 使用方法

### 基本用法（自动提取词典 CSS）

```bash
# 查询单词，自动提取词典内部的 CSS 和图片
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html
```

### 不嵌入图片（减小文件大小）

```bash
# 只提取 CSS，不嵌入图片
python examples/query_word.py hello --mdx data/mdict/dict.mdx --output hello.html --no-images
```

### 查看帮助

```bash
python examples/query_word.py --help
```

---

## 🔍 工作原理

### 1. CSS 提取流程

```python
# 1. 查询词条 HTML
html_content = dict.lookup_html(word)

# 2. 使用 BeautifulSoup 解析
soup = BeautifulSoup(html_content, 'lxml')

# 3. 调用 merge_css 提取词典 CSS
merged_soup = merge_css(temp_soup, mdx_file.parent, dict.impl, None)

# 4. 提取 CSS 内容
dict_css = merged_soup.head.style.string
```

### 2. 图片嵌入流程

```python
# 1. 解析 HTML 中的图片标签
temp_soup = BeautifulSoup(html_content, 'lxml')

# 2. 调用 embed_images 将图片转为 base64
embedded_soup = embed_images(temp_soup, dict.impl)

# 3. 更新 HTML 内容
html_content = str(embedded_soup.body)
```

---

## 📊 输出示例

### HTML 结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>hello</title>
    <style>
        /* ========== 词典内部 CSS ========== */
        /* 词典自带的所有 CSS 样式 */
        .entry { ... }
        .phonetic { ... }
        
        /* ========== 自定义样式 ========== */
        /* 我们添加的美化样式 */
        body {
            font-family: sans-serif;
            max-width: 900px;
            margin: 0 auto;
        }
        .word-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            /* ... */
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="word-header">
            <div class="word-title">hello</div>
        </div>
        <div class="word-content">
            <!-- 词典内容，图片已转为 base64 -->
            <div class="entry">...</div>
        </div>
    </div>
</body>
</html>
```

---

## 🎨 CSS 优先级

由于词典 CSS 在前，自定义样式在后，所以：
- ✅ 词典的原始样式会被保留
- ✅ 我们的自定义样式可以覆盖词典样式
- ✅ 如果有冲突，自定义样式优先

**示例**：
```css
/* 词典 CSS */
.entry { color: black; }

/* 自定义 CSS */
.entry { color: #333; }  /* 这个会生效 */
```

---

## 💡 实际效果

### 运行示例

```bash
$ python examples/query_word.py hello --mdx data/mdict/oxford.mdx --output hello.html

======================================================================
📖 查询单词: hello
📚 词典: data/mdict/oxford.mdx
======================================================================
✅ 已提取词典 CSS (15234 字符)
✅ 已嵌入词典图片
✅ 已保存到: hello.html
📊 文件大小: 45,678 字符

======================================================================
✅ 查询完成!
======================================================================
```

### 输出文件特点

- **完全独立**：可以直接在浏览器中打开，无需网络或外部文件
- **样式完整**：包含词典原始样式 + 现代化美化样式
- **图片嵌入**：所有图片都转换为 base64 嵌入（可选）
- **文件较大**：由于嵌入了所有资源，文件会比较大

---

## 🔧 技术细节

### 使用的模块

```python
from bs4 import BeautifulSoup  # HTML 解析
from mdxscraper import Dictionary  # 词典查询
from mdxscraper.core.renderer import merge_css, embed_images  # CSS和图片处理
```

### 关键函数

1. **`merge_css(soup, mdx_path, dictionary, additional_styles)`**
   - 从词典中提取 CSS 文件
   - 支持从 .css 文件或 .mdd 文件中提取
   - 可以合并额外的自定义样式

2. **`embed_images(soup, dictionary)`**
   - 查找 HTML 中的所有 `<img>` 标签
   - 从词典的 .mdd 文件中提取图片数据
   - 转换为 base64 并替换 src 属性

---

## 🆚 与旧版本对比

| 特性 | 旧版本 | 新版本 |
|------|--------|--------|
| **词典 CSS** | ❌ 不包含 | ✅ 自动提取并嵌入 |
| **词典图片** | ❌ 不支持 | ✅ 自动嵌入为 base64 |
| **自定义样式** | ✅ 支持 | ✅ 支持 |
| **输出独立性** | ⚠️ 可能缺少样式 | ✅ 完全独立 |
| **文件大小** | 📉 小 | 📈 较大（但完整） |

---

## 📝 使用建议

### 何时使用图片嵌入

✅ **推荐使用**（默认）：
- 需要离线使用
- 需要分享给他人
- 需要归档保存
- 词典图片不多

❌ **不推荐使用**（`--no-images`）：
- 图片很多很大
- 只是临时查看
- 需要减小文件大小
- 不需要看图片

### 性能考虑

```bash
# 快速查看（不嵌入图片）
python examples/query_word.py hello --mdx dict.mdx --no-images

# 完整导出（嵌入所有资源）
python examples/query_word.py hello --mdx dict.mdx --output hello.html
```

---

## 🐛 故障排除

### 问题 1: 无法提取词典 CSS

**现象**：
```
ℹ️  无法提取词典 CSS: ...
```

**原因**：
- 词典可能没有 CSS 文件
- CSS 文件路径不正确

**解决**：
- 这是正常的，不影响使用
- 只是没有词典原始样式，会使用我们的自定义样式

### 问题 2: 图片显示为问号

**现象**：HTML 中图片无法显示

**原因**：
- 词典可能没有 .mdd 文件
- 图片路径不匹配

**解决**：
```bash
# 使用 --no-images 跳过图片嵌入
python examples/query_word.py hello --mdx dict.mdx --no-images
```

### 问题 3: 文件太大

**现象**：生成的 HTML 文件几 MB

**原因**：
- 图片嵌入为 base64 后会变大
- 词典 CSS 很大

**解决**：
```bash
# 方法 1: 不嵌入图片
python examples/query_word.py hello --mdx dict.mdx --no-images

# 方法 2: 压缩 HTML
gzip hello.html  # 可以减小 70-80%
```

---

## 🚀 未来计划

- [ ] 支持选择性嵌入图片（只嵌入小图）
- [ ] 支持压缩 CSS（删除注释和空白）
- [ ] 支持外部 CSS 文件（不嵌入）
- [ ] 支持批量查询多个单词
- [ ] 添加缓存机制（加快重复查询）

---

## 📚 相关文档

- **主文档**: [README.md](../README.md)
- **使用指南**: [WORD_QUERY_GUIDE.md](WORD_QUERY_GUIDE.md)
- **功能总结**: [QUERY_SUMMARY.md](QUERY_SUMMARY.md)
- **API 文档**: [../docs/HEADLESS_API.md](../docs/HEADLESS_API.md)

---

## ✅ 总结

`query_word.py` 现在是一个**功能完整的单词查询工具**：

1. ✅ 自动提取词典内部 CSS
2. ✅ 自动嵌入词典图片（base64）
3. ✅ 添加现代化美化样式
4. ✅ 生成完全独立的 HTML 文件
5. ✅ 支持灵活的命令行参数

**立即尝试**：
```bash
python examples/query_word.py hello --mdx your_dict.mdx --output hello.html
```

享受查词的乐趣！🎉
