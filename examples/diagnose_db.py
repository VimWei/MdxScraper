"""诊断 MDX 数据库索引问题

用于检查非 ASCII 文件名的 MDX 词典数据库是否正确构建
"""

import argparse
import sqlite3
import sys
from pathlib import Path


def diagnose_mdx_db(mdx_file: Path):
    """诊断 MDX 数据库索引"""
    
    print("=" * 70)
    print("MDX 数据库诊断工具")
    print("=" * 70)
    
    # 检查 MDX 文件
    print(f"\n1. 检查 MDX 文件")
    print(f"   路径: {mdx_file}")
    print(f"   存在: {mdx_file.exists()}")
    print(f"   文件名包含非 ASCII: {not mdx_file.name.isascii()}")
    
    if not mdx_file.exists():
        print("❌ MDX 文件不存在！")
        return
    
    # 检查数据库文件
    db_file = mdx_file.with_suffix('.mdx.db')
    print(f"\n2. 检查数据库文件")
    print(f"   路径: {db_file}")
    print(f"   存在: {db_file.exists()}")
    
    if not db_file.exists():
        print("⚠️  数据库文件不存在，需要构建索引")
        return
    
    # 连接数据库
    print(f"\n3. 连接数据库")
    try:
        conn = sqlite3.connect(str(db_file))
        print("   ✅ 成功连接")
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return
    
    # 检查表结构
    print(f"\n4. 检查表结构")
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor]
    print(f"   表列表: {tables}")
    
    if 'MDX_INDEX' not in tables:
        print("   ❌ 缺少 MDX_INDEX 表！")
        conn.close()
        return
    
    # 检查 MDX_INDEX 表结构
    cursor = conn.execute("PRAGMA table_info(MDX_INDEX)")
    columns = [(row[1], row[2]) for row in cursor]
    print(f"\n5. MDX_INDEX 表结构")
    for i, (col_name, col_type) in enumerate(columns):
        print(f"   [{i}] {col_name} ({col_type})")
    
    expected_columns = [
        'key_text', 'file_path', 'file_pos', 'compressed_size',
        'decompressed_size', 'record_block_type', 'record_start',
        'record_end', 'offset'
    ]
    
    actual_columns = [col[0] for col in columns]
    
    print(f"\n   期望结构 (9 列):")
    for i, col in enumerate(expected_columns):
        print(f"      [{i}] {col}")
    
    print(f"\n   实际结构 ({len(actual_columns)} 列):")
    for i, (col_name, col_type) in enumerate(columns):
        match = "✅" if i < len(expected_columns) and col_name == expected_columns[i] else "❌"
        print(f"      [{i}] {col_name} ({col_type}) {match}")
    
    if len(actual_columns) != len(expected_columns):
        print(f"\n   ❌ 列数不匹配！期望 {len(expected_columns)} 列，实际 {len(actual_columns)} 列")
        print(f"   💡 建议：运行 'python examples/rebuild_index.py \"{mdx_file}\"' 重建索引")
    elif actual_columns != expected_columns:
        print(f"\n   ❌ 列名不匹配！")
        print(f"   💡 建议：运行 'python examples/rebuild_index.py \"{mdx_file}\"' 重建索引")
    else:
        print(f"\n   ✅ 表结构完全正确")
    
    # 检查索引数量
    print(f"\n6. 检查索引数量")
    cursor = conn.execute("SELECT COUNT(*) FROM MDX_INDEX")
    count = cursor.fetchone()[0]
    print(f"   词条数量: {count}")
    
    # 抽样检查前 5 条记录
    print(f"\n7. 抽样检查记录")
    cursor = conn.execute("SELECT * FROM MDX_INDEX LIMIT 5")
    for i, row in enumerate(cursor, 1):
        print(f"   记录 {i}: 字段数={len(row)}, key={row[0][:30] if row[0] else 'None'}")
        if len(row) < 9:
            print(f"      ❌ 字段不完整！期望 9 个字段，实际 {len(row)} 个")
    
    # 检查 META 表
    print(f"\n8. 检查 META 表")
    if 'META' in tables:
        cursor = conn.execute("SELECT key, substr(value, 1, 50) FROM META")
        for key, value in cursor:
            print(f"   {key}: {value}")
    else:
        print("   ⚠️  缺少 META 表")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("诊断完成")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="诊断 MDX 数据库索引问题",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "mdx",
        type=Path,
        help="MDX 词典文件路径",
    )
    args = parser.parse_args()
    
    diagnose_mdx_db(args.mdx)
