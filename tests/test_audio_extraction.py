"""测试音频提取功能的快速脚本."""

from pathlib import Path

from mdxscraper import Dictionary, extract_audio_paths_from_html, get_audio_info

# 测试用例
TEST_HTML_SAMPLES = {
    "source_tag": """
        <audio controls>
            <source src="\\sound\\hello.mp3" type="audio/mpeg">
        </audio>
    """,
    "sound_protocol": """
        <a href="sound://audio/pronunciation.mp3">🔊 播放</a>
    """,
    "entry_protocol": """
        <img src="entry://sound/word.wav" onclick="playAudio()">
    """,
    "mixed": """
        <audio controls>
            <source src="sound://audio/us.mp3">
            <source src="sound://audio/uk.mp3">
        </audio>
        <a href="sound://audio/slow.mp3">慢速</a>
    """,
}


def test_extract_paths():
    """测试从 HTML 提取音频路径."""
    print("=" * 70)
    print("测试: 提取音频路径")
    print("=" * 70)

    for name, html in TEST_HTML_SAMPLES.items():
        print(f"\n[{name}]")
        print(f"HTML: {html.strip()[:60]}...")

        paths = extract_audio_paths_from_html(html)
        print(f"找到 {len(paths)} 个音频路径:")
        for path in paths:
            print(f"  - {path}")


def test_with_real_dictionary():
    """测试真实词典（如果有的话）."""
    print("\n" + "=" * 70)
    print("测试: 真实词典")
    print("=" * 70)

    # 尝试几个可能的词典位置
    possible_dicts = [
        Path("C:/词典/日语语音库/NHK日本語発音アクセント辞書.mdx"),
        Path("data/mdict/NHK日本語発音アクセント辞書.mdx"),
        Path("E:/词典/NHK日本語発音アクセント辞書.mdx"),
    ]

    mdx_file = None
    for path in possible_dicts:
        if path.exists():
            mdx_file = path
            break

    if not mdx_file:
        print("\n⚠️  未找到 NHK 词典，跳过真实测试")
        print("   可用的词典路径:")
        for path in possible_dicts:
            print(f"   - {path}")
        return

    print(f"\n✅ 找到词典: {mdx_file}")

    # 测试词条
    test_words = ["あい", "こんにちは", "ありがとう"]

    with Dictionary(mdx_file) as dictionary:
        for word in test_words:
            print(f"\n[{word}]")

            html = dictionary.lookup_html(word)
            if not html:
                print("  ❌ 未找到词条")
                continue

            # 提取音频路径
            audio_paths = extract_audio_paths_from_html(html)
            print(f"  HTML 中的音频路径: {audio_paths}")

            # 获取音频信息
            audio_infos = get_audio_info(dictionary.impl, word, html)
            print(f"  实际找到的音频: {len(audio_infos)} 个")

            for i, audio in enumerate(audio_infos, 1):
                print(f"    [{i}] {audio.audio_path}")
                print(f"        格式: {audio.format.upper()} ({audio.mime_type})")
                print(f"        大小: {len(audio.audio_data):,} bytes")


def main():
    """运行所有测试."""
    print("\n🧪 音频功能测试\n")

    # 测试 1: 路径提取
    test_extract_paths()

    # 测试 2: 真实词典
    test_with_real_dictionary()

    print("\n" + "=" * 70)
    print("✅ 测试完成")
    print("=" * 70)
    print("\n💡 使用方法:")
    print("   python examples/extract_audio.py あい --mdx 'NHK日本語発音アクセント辞書.mdx'")
    print("   python examples/extract_audio.py --help")


if __name__ == "__main__":
    main()
