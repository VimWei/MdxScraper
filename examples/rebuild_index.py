"""重建 MDX 词典索引

用于修复损坏或版本不匹配的数据库索引文件
"""

import argparse
import os
from pathlib import Path


def rebuild_index(mdx_file: Path):
    """强制重建 MDX 索引"""
    
    print("=" * 70)
    print("重建 MDX 索引工具")
    print("=" * 70)
    
    if not mdx_file.exists():
        print(f"❌ MDX 文件不存在: {mdx_file}")
        return False
    
    print(f"\n📚 MDX 文件: {mdx_file}")
    
    # 删除旧的数据库文件
    db_file = mdx_file.with_suffix('.mdx.db')
    mdd_file = mdx_file.with_suffix('.mdd')
    mdd_db_file = mdx_file.with_suffix('.mdd.db')
    
    if db_file.exists():
        print(f"🗑️  删除旧索引: {db_file}")
        db_file.unlink()
    
    if mdd_db_file.exists():
        print(f"🗑️  删除旧 MDD 索引: {mdd_db_file}")
        mdd_db_file.unlink()
    
    # 导入并重建索引
    print(f"\n⚙️  重建索引中...")
    try:
        from mdxscraper.mdict.vendor.mdict_query import IndexBuilder
        
        # 强制重建索引
        builder = IndexBuilder(str(mdx_file), force_rebuild=True)
        
        print(f"\n✅ 索引重建成功！")
        print(f"   编码: {builder._encoding}")
        print(f"   标题: {builder._title}")
        print(f"   版本: {builder._version}")
        
        if builder._mdd_file:
            print(f"   MDD 文件: {builder._mdd_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 重建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="重建 MDX 词典索引",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python rebuild_index.py "C:\\词典\\NHK日本語発音アクセント辞書.mdx"
  python rebuild_index.py data/mdict/your_dictionary.mdx
        """
    )
    parser.add_argument(
        "mdx",
        type=Path,
        help="MDX 词典文件路径",
    )
    args = parser.parse_args()
    
    success = rebuild_index(args.mdx)
    exit(0 if success else 1)
