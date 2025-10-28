"""提取和播放 MDX 词典中的音频文件.

演示如何:
1. 从词条中提取音频信息
2. 保存音频文件到磁盘
3. 生成可直接播放的 HTML
4. 批量提取词汇表的所有音频
"""

import argparse
from pathlib import Path

from mdxscraper import Dictionary
from mdxscraper.core.audio import (
    embed_audio_in_html,
    get_audio_info,
    save_audio_file,
)

# 默认配置
DEFAULT_MDX_FILE = Path("data/mdict/NHK日本語発音アクセント辞書.mdx")
DEFAULT_OUTPUT_DIR = Path("data/audio_output")


def extract_single_audio(mdx_file: Path, word: str, output_dir: Path):
    """提取单个词条的音频.

    Args:
        mdx_file: MDX 词典文件
        word: 要查询的词条
        output_dir: 输出目录
    """
    print(f"\n{'='*70}")
    print(f"提取音频: {word}")
    print(f"{'='*70}\n")

    # 加载词典
    with Dictionary(mdx_file) as dictionary:
        # 查询词条
        html = dictionary.lookup_html(word)
        if not html:
            print(f"❌ 未找到词条: {word}")
            return

        print(f"✅ 找到词条: {word}")

        # 获取音频信息
        audio_infos = get_audio_info(dictionary.impl, word, html)

        if not audio_infos:
            print(f"⚠️  该词条没有音频文件")
            return

        print(f"\n🎵 找到 {len(audio_infos)} 个音频文件:\n")

        # 保存所有音频
        output_dir.mkdir(parents=True, exist_ok=True)

        for i, audio_info in enumerate(audio_infos, 1):
            print(f"  [{i}] {audio_info.audio_path}")
            print(f"      格式: {audio_info.format.upper()}")
            print(f"      MIME: {audio_info.mime_type}")
            print(f"      大小: {len(audio_info.audio_data):,} bytes")

            # 保存音频文件
            filename = f"{word}_{i}.{audio_info.format}"
            output_path = output_dir / filename
            save_audio_file(audio_info, output_path)
            print(f"      💾 已保存: {output_path}")

            # 生成 data URI 预览（前50字符）
            data_uri_preview = audio_info.data_uri[:50] + "..."
            print(f"      🔗 Data URI: {data_uri_preview}\n")

        # 生成可播放的 HTML
        html_with_audio = embed_audio_in_html(html, dictionary.impl)
        html_output = output_dir / f"{word}.html"

        # 完整的 HTML 文档
        full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word} - 音频发音</title>
    <style>
        body {{
            font-family: 'Hiragino Kaku Gothic Pro', 'メイリオ', Meiryo, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.8;
        }}
        audio {{
            width: 100%;
            margin: 10px 0;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <h1>{word}</h1>
    {html_with_audio}
</body>
</html>"""

        html_output.write_text(full_html, encoding="utf-8")
        print(f"📄 已生成 HTML: {html_output}")
        print(f"   可在浏览器中打开直接播放")


def batch_extract_audio(mdx_file: Path, words_file: Path, output_dir: Path):
    """批量提取词汇表的音频.

    Args:
        mdx_file: MDX 词典文件
        words_file: 词汇列表文件（每行一个词）
        output_dir: 输出目录
    """
    print(f"\n{'='*70}")
    print(f"批量提取音频")
    print(f"{'='*70}\n")

    # 读取词汇列表
    words = []
    with open(words_file, "r", encoding="utf-8") as f:
        for line in f:
            word = line.strip()
            if word and not word.startswith("#"):
                words.append(word)

    print(f"📚 词汇列表: {words_file}")
    print(f"📊 共 {len(words)} 个词条\n")

    # 加载词典
    with Dictionary(mdx_file) as dictionary:
        total_audio = 0
        found_words = 0

        for i, word in enumerate(words, 1):
            print(f"[{i}/{len(words)}] {word} ", end="")

            # 查询词条
            html = dictionary.lookup_html(word)
            if not html:
                print("❌ 未找到")
                continue

            # 获取音频信息
            audio_infos = get_audio_info(dictionary.impl, word, html)

            if not audio_infos:
                print("⚠️  无音频")
                continue

            # 保存音频
            word_dir = output_dir / word
            word_dir.mkdir(parents=True, exist_ok=True)

            for j, audio_info in enumerate(audio_infos, 1):
                filename = f"{word}_{j}.{audio_info.format}"
                output_path = word_dir / filename
                save_audio_file(audio_info, output_path)

            found_words += 1
            total_audio += len(audio_infos)
            print(f"✅ {len(audio_infos)} 个音频")

    print(f"\n{'='*70}")
    print(f"✅ 提取完成")
    print(f"   找到词条: {found_words}/{len(words)}")
    print(f"   提取音频: {total_audio} 个")
    print(f"   保存位置: {output_dir}")
    print(f"{'='*70}\n")


def list_audio_in_word(mdx_file: Path, word: str):
    """列出词条中的所有音频路径（不保存）.

    Args:
        mdx_file: MDX 词典文件
        word: 要查询的词条
    """
    print(f"\n{'='*70}")
    print(f"音频信息: {word}")
    print(f"{'='*70}\n")

    with Dictionary(mdx_file) as dictionary:
        html = dictionary.lookup_html(word)
        if not html:
            print(f"❌ 未找到词条: {word}")
            return

        audio_infos = get_audio_info(dictionary.impl, word, html)

        if not audio_infos:
            print(f"⚠️  该词条没有音频文件")
            return

        print(f"🎵 共 {len(audio_infos)} 个音频:\n")
        for i, audio_info in enumerate(audio_infos, 1):
            print(f"  [{i}] 路径: {audio_info.audio_path}")
            print(f"      格式: {audio_info.format.upper()} ({audio_info.mime_type})")
            print(f"      大小: {len(audio_info.audio_data):,} bytes")
            print(f"      可用: ✅\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="提取 MDX 词典中的音频文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:

1. 提取单个词条的音频:
   python examples/extract_audio.py hello --mdx dict.mdx

2. 只查看音频信息（不保存）:
   python examples/extract_audio.py hello --mdx dict.mdx --list-only

3. 批量提取词汇表的音频:
   python examples/extract_audio.py --batch words.txt --mdx dict.mdx

4. NHK 日语词典示例:
   python examples/extract_audio.py あい --mdx "NHK日本語発音アクセント辞書.mdx"
        """,
    )

    parser.add_argument("word", nargs="?", help="要查询的词条")

    parser.add_argument("--mdx", type=Path, default=DEFAULT_MDX_FILE, help="MDX 词典文件路径")

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument("--batch", type=Path, help="批量模式：从文件读取词汇列表")

    parser.add_argument("--list-only", action="store_true", help="只列出音频信息，不保存文件")

    args = parser.parse_args()

    # 检查 MDX 文件
    if not args.mdx.exists():
        print(f"❌ MDX 文件不存在: {args.mdx}")
        print(f"   请使用 --mdx 指定正确的词典文件路径")
        exit(1)

    # 批量模式
    if args.batch:
        if not args.batch.exists():
            print(f"❌ 词汇列表文件不存在: {args.batch}")
            exit(1)
        batch_extract_audio(args.mdx, args.batch, args.output_dir)

    # 单词查询模式
    elif args.word:
        if args.list_only:
            list_audio_in_word(args.mdx, args.word)
        else:
            extract_single_audio(args.mdx, args.word, args.output_dir)

    # 没有参数，显示帮助
    else:
        parser.print_help()
