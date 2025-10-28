# MDX 数据库表结构兼容性

## 问题说明

不同版本的 MDX 工具（如 MDict、GoldenDict、mdict-utils 等）创建的 `.mdx.db` 文件可能使用不同的表结构，导致兼容性问题。

## 标准表结构

### MdxScraper 使用的表结构

#### MDX_INDEX 表（9 列）

| 列索引 | 列名 | 类型 | 说明 |
|--------|------|------|------|
| 0 | key_text | TEXT | 词条关键字 |
| 1 | file_path | TEXT | 文件路径（MDX 为 NULL，MDD 为文件名）|
| 2 | file_pos | INTEGER | 数据块在文件中的位置 |
| 3 | compressed_size | INTEGER | 压缩后的大小 |
| 4 | decompressed_size | INTEGER | 解压后的大小 |
| 5 | record_block_type | INTEGER | 压缩类型（0=无，1=LZO，2=ZLIB）|
| 6 | record_start | INTEGER | 记录起始位置 |
| 7 | record_end | INTEGER | 记录结束位置 |
| 8 | offset | INTEGER | 偏移量 |

#### META 表

| 列名 | 类型 | 示例值 |
|------|------|--------|
| key | TEXT | "encoding", "title", "version" |
| value | TEXT | "utf-8", "牛津词典", "1.1" |

## 常见不兼容的表结构

### 结构 A（旧版 mdict-utils，8 列）

缺少 `file_path` 列：

```sql
CREATE TABLE MDX_INDEX (
    key_text TEXT NOT NULL,
    file_pos INTEGER,
    compressed_size INTEGER,
    decompressed_size INTEGER,
    record_block_type INTEGER,
    record_start INTEGER,
    record_end INTEGER,
    offset INTEGER
)
```

### 结构 B（某些第三方工具，7 列）

缺少 `file_path` 和 `offset` 列：

```sql
CREATE TABLE MDX_INDEX (
    key_text TEXT NOT NULL,
    file_pos INTEGER,
    compressed_size INTEGER,
    decompressed_size INTEGER,
    record_block_type INTEGER,
    record_start INTEGER,
    record_end INTEGER
)
```

### 结构 C（简化版本，5 列）

仅包含基本信息：

```sql
CREATE TABLE MDX_INDEX (
    key_text TEXT NOT NULL,
    file_pos INTEGER,
    compressed_size INTEGER,
    record_start INTEGER,
    record_end INTEGER
)
```

## 兼容性检测

### 自动检测

MdxScraper 会在启动时自动检测表结构：

```python
from mdxscraper import Dictionary

# 自动检测并重建不兼容的数据库
dictionary = Dictionary("your_dictionary.mdx")
```

如果检测到不兼容，会输出：

```
Warning: Incompatible table structure in your_dictionary.mdx.db
  Expected: ['key_text', 'file_path', 'file_pos', 'compressed_size', 
             'decompressed_size', 'record_block_type', 'record_start',
             'record_end', 'offset']
  Found: ['key_text', 'file_pos', 'compressed_size', 'decompressed_size',
          'record_block_type', 'record_start', 'record_end', 'offset']
  Rebuilding with correct structure...
```

### 手动诊断

```bash
python examples/diagnose_db.py "your_dictionary.mdx"
```

输出示例：

```
======================================================================
MDX 数据库诊断工具
======================================================================

5. MDX_INDEX 表结构

   期望结构 (9 列):
      [0] key_text
      [1] file_path
      [2] file_pos
      [3] compressed_size
      [4] decompressed_size
      [5] record_block_type
      [6] record_start
      [7] record_end
      [8] offset

   实际结构 (8 列):
      [0] key_text (text) ✅
      [1] file_pos (integer) ❌
      [2] compressed_size (integer) ❌
      [3] decompressed_size (integer) ❌
      [4] record_block_type (integer) ❌
      [5] record_start (integer) ❌
      [6] record_end (integer) ❌
      [7] offset (integer) ❌

   ❌ 列数不匹配！期望 9 列，实际 8 列
   💡 建议：运行 'python examples/rebuild_index.py "your_dictionary.mdx"' 重建索引
```

## 解决方案

### 方案 1：自动重建（推荐）

MdxScraper 会自动检测并重建不兼容的数据库：

```python
from mdxscraper import Dictionary

# 首次使用会自动重建
dictionary = Dictionary("your_dictionary.mdx")
```

### 方案 2：手动重建

```bash
# 方法 1：使用重建工具
python examples/rebuild_index.py "your_dictionary.mdx"

# 方法 2：删除旧数据库（会自动重建）
Remove-Item "your_dictionary.mdx.db"

# 方法 3：在代码中强制重建
from mdxscraper.mdict.vendor.mdict_query import IndexBuilder
IndexBuilder("your_dictionary.mdx", force_rebuild=True)
```

### 方案 3：批量升级

如果有多个词典需要升级：

```python
from pathlib import Path
from mdxscraper.mdict.vendor.mdict_query import IndexBuilder

# 批量检测和重建
dict_dir = Path("C:/词典")
for mdx_file in dict_dir.rglob("*.mdx"):
    db_file = mdx_file.with_suffix('.mdx.db')
    if db_file.exists():
        print(f"检查: {mdx_file.name}")
        try:
            # 尝试加载，如果不兼容会自动重建
            builder = IndexBuilder(str(mdx_file))
            print(f"  ✅ 兼容")
        except Exception as e:
            print(f"  ⚠️  重建: {e}")
            builder = IndexBuilder(str(mdx_file), force_rebuild=True)
```

## 版本标识

### 检查数据库版本

```python
import sqlite3

def check_db_version(db_file):
    conn = sqlite3.connect(db_file)
    try:
        cursor = conn.execute("SELECT value FROM META WHERE key='version'")
        version = cursor.fetchone()
        if version:
            print(f"数据库版本: {version[0]}")
        else:
            print("未找到版本信息（可能是旧版本）")
    except sqlite3.Error as e:
        print(f"无法读取版本: {e}")
    finally:
        conn.close()

check_db_version("your_dictionary.mdx.db")
```

### 当前版本

MdxScraper 创建的数据库版本号：`1.1`

## 预防措施

### 1. 不要混用工具

如果使用 MdxScraper，建议删除其他工具创建的 `.db` 文件：

```bash
# 查找并删除所有 .db 文件
Get-ChildItem -Path "C:\词典" -Recurse -Filter "*.mdx.db" | Remove-Item
Get-ChildItem -Path "C:\词典" -Recurse -Filter "*.mdd.db" | Remove-Item
```

### 2. 添加 .gitignore

如果词典在版本控制中，忽略数据库文件：

```gitignore
# MDX 数据库索引
*.mdx.db
*.mdd.db
*.sqlite.db
```

### 3. 定期验证

定期运行诊断工具：

```bash
# 诊断所有词典
Get-ChildItem -Path "C:\词典" -Recurse -Filter "*.mdx" | 
    ForEach-Object { python examples/diagnose_db.py $_.FullName }
```

## 技术细节

### 为什么需要 file_path 列？

`file_path` 列用于支持多 MDD 文件：

```
dictionary.mdx
dictionary.mdd      ← 主 MDD
dictionary.1.mdd    ← 额外的 MDD
dictionary.2.mdd    ← 额外的 MDD
```

每个 MDD 文件的索引都存储在同一个表中，通过 `file_path` 区分。

### 查询示例

```python
# 查询某个词条的所有索引信息
import sqlite3

conn = sqlite3.connect("dictionary.mdx.db")
cursor = conn.execute("""
    SELECT key_text, file_path, file_pos, compressed_size 
    FROM MDX_INDEX 
    WHERE key_text = 'hello'
""")

for row in cursor:
    print(f"词条: {row[0]}")
    print(f"文件: {row[1] or 'MDX'}")
    print(f"位置: {row[2]}")
    print(f"大小: {row[3]} bytes")
```

## 常见错误

### IndexError: tuple index out of range

**原因**：表结构列数不足

**解决**：重建索引

```bash
python examples/rebuild_index.py "your_dictionary.mdx"
```

### sqlite3.OperationalError: no such column

**原因**：缺少必需的列

**解决**：删除 `.db` 文件重新生成

```bash
Remove-Item "your_dictionary.mdx.db"
```

### UnicodeDecodeError

**原因**：编码不匹配

**解决**：检查 META 表中的 encoding 值

```python
import sqlite3

conn = sqlite3.connect("dictionary.mdx.db")
cursor = conn.execute("SELECT value FROM META WHERE key='encoding'")
print(cursor.fetchone())
```

## 相关资源

- [MDX 文件格式规范](https://github.com/zhansliu/writemdict/blob/master/fileformat.md)
- [readmdict 库](https://github.com/ffreemt/readmdict)
- [MDict 官方网站](https://www.mdict.cn/)
