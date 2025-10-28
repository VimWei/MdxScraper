# 非 ASCII 文件名支持与数据库兼容性

## 问题描述

当 MDX 词典文件名包含非 ASCII 字符（如中文、日文等）时，或者使用其他工具创建的数据库索引时，可能会遇到以下错误：

```
IndexError: tuple index out of range
```

### 常见场景

1. **非 ASCII 文件名**
   - ❌ `C:\词典\日语语音库\NHK日本語発音アクセント辞書.mdx`
   - ❌ `D:\字典\牛津高階英漢雙解詞典.mdx`

2. **不兼容的数据库**
   - 其他工具（如 mdict-utils、GoldenDict）创建的 `.mdx.db` 文件
   - 旧版本 MdxScraper 创建的数据库
   - 损坏或不完整的数据库

## 根本原因

### 1. 表结构不兼容

不同工具创建的数据库表结构可能不同：

| 工具 | 列数 | 缺失的列 |
|------|------|----------|
| MdxScraper (当前) | 9 列 | - |
| 旧版 mdict-utils | 8 列 | `file_path` |
| 某些第三方工具 | 7 列 | `file_path`, `offset` |
| 简化版本 | 5 列 | 多个列缺失 |

### 2. 版本不匹配

旧版本数据库缺少版本标识或元数据。

## 解决方案

### 方案 1：重建索引（推荐）

使用 `rebuild_index.py` 工具强制重建数据库索引：

```bash
# 重建单个词典索引
python examples/rebuild_index.py "C:\词典\NHK日本語発音アクセント辞書.mdx"
```

### 方案 2：在代码中强制重建

```python
from mdxscraper import Dictionary

# 强制重建索引
dictionary = Dictionary(
    "C:\\词典\\NHK日本語発音アクセント辞書.mdx",
    force_rebuild=True  # 强制重建索引
)

# 查询
result = dictionary.lookup("単語")
```

### 方案 3：删除旧索引文件

手动删除 `.mdx.db` 和 `.mdd.db` 文件，然后重新运行程序：

```bash
# 删除旧索引（会自动重建）
Remove-Item "C:\词典\NHK日本語発音アクセント辞書.mdx.db"
Remove-Item "C:\词典\NHK日本語発音アクセント辞書.mdd.db"

# 重新运行程序
python examples/query_word.py 単語 --mdx "C:\词典\NHK日本語発音アクセント辞書.mdx"
```

## 预防措施

### 1. 使用最新版本

确保使用最新版本的 MdxScraper，已包含增强的错误处理。

### 2. 定期重建索引

如果词典文件更新，建议重建索引：

```bash
python examples/rebuild_index.py your_dictionary.mdx
```

### 3. 诊断工具

使用诊断工具检查数据库健康状况：

```bash
python examples/diagnose_db.py your_dictionary.mdx
```

输出示例：
```
======================================================================
MDX 数据库诊断工具
======================================================================

1. 检查 MDX 文件
   路径: C:\词典\NHK日本語発音アクセント辞書.mdx
   存在: True
   文件名包含非 ASCII: True

2. 检查数据库文件
   路径: C:\词典\NHK日本語発音アクセント辞書.mdx.db
   存在: True

3. 连接数据库
   ✅ 成功连接

4. 检查表结构
   表列表: ['MDX_INDEX', 'META']

5. MDX_INDEX 表结构
   [0] key_text (text)
   [1] file_path (text)
   [2] file_pos (integer)
   [3] compressed_size (integer)
   [4] decompressed_size (integer)
   [5] record_block_type (integer)
   [6] record_start (integer)
   [7] record_end (integer)
   [8] offset (integer)
   ✅ 表结构正确

6. 检查索引数量
   词条数量: 72000

7. 抽样检查记录
   记录 1: 字段数=9, key=あ
   记录 2: 字段数=9, key=ああ
   记录 3: 字段数=9, key=ああだ
   记录 4: 字段数=9, key=ああ言えば
   记录 5: 字段数=9, key=ああ言う

8. 检查 META 表
   encoding: utf-8
   title: NHK日本語発音アクセント辞書
   version: 1.1
```

## 技术细节

### 已修复的问题

1. **SQL 注入防护**
   - 使用参数化查询
   - 安全处理特殊字符

2. **数据验证**
   - 检查查询结果完整性
   - 验证表结构

3. **错误处理**
   - 捕获 SQLite 错误
   - 提供详细错误信息
   - 优雅降级

4. **Unicode 支持**
   - 正确处理非 ASCII 路径
   - UTF-8 编码支持

### 代码示例

```python
from mdxscraper import Dictionary

# 支持各种字符的文件名
dictionaries = [
    "NHK日本語発音アクセント辞書.mdx",  # 日文
    "牛津高階英漢雙解詞典.mdx",        # 繁体中文
    "新华字典.mdx",                    # 简体中文
    "Diccionario Español.mdx",       # 西班牙文
    "Wörterbuch Deutsch.mdx",        # 德文
]

for dict_file in dictionaries:
    try:
        dictionary = Dictionary(dict_file)
        print(f"✅ {dict_file} 加载成功")
    except Exception as e:
        print(f"❌ {dict_file} 加载失败: {e}")
```

## 常见问题

### Q: 为什么会出现这个问题？

A: 旧版本的代码在创建数据库时可能没有正确处理非 ASCII 文件名，导致索引不完整。

### Q: 重建索引会丢失数据吗？

A: 不会。索引是从原始 MDX 文件重新生成的，不会影响原始数据。

### Q: 重建需要多久？

A: 取决于词典大小，通常几秒到几分钟不等。

### Q: 如何批量重建？

```python
from pathlib import Path
from mdxscraper.mdict.vendor.mdict_query import IndexBuilder

# 批量重建
dict_dir = Path("C:/词典")
for mdx_file in dict_dir.rglob("*.mdx"):
    print(f"重建索引: {mdx_file}")
    try:
        IndexBuilder(str(mdx_file), force_rebuild=True)
        print(f"  ✅ 成功")
    except Exception as e:
        print(f"  ❌ 失败: {e}")
```

## 相关文件

- `examples/rebuild_index.py` - 重建索引工具
- `examples/diagnose_db.py` - 数据库诊断工具
- `src/mdxscraper/mdict/vendor/mdict_query.py` - 核心查询模块
