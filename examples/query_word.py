#!/usr/bin/env python
"""快速查询单个词汇并输出完整 HTML（含 CSS、图片和音频）

使用方法:
    python query_word.py <word> [--mdx FILE] [--output FILE]

示例:
    # 查询单词并打印到控制台
    python query_word.py hello
    
    # 指定词典文件
    python query_word.py hello --mdx data/mdict/my_dict.mdx
    
    # 保存到文件
    python query_word.py hello --output hello.html
    
    # 完整示例（包含音频和图片）
    python query_word.py hello --mdx data/mdict/dict.mdx --output result.html
    
    # NHK 日语词典示例（包含发音）
    python query_word.py あい --mdx "NHK日本語発音アクセント辞書.mdx" --output あい.html
    
    # 不嵌入图片和音频（减小文件大小）
    python query_word.py hello --mdx dict.mdx --output hello.html --no-images --no-audio

功能特点:
    ✅ 自动提取词典内部 CSS 样式
    ✅ 自动嵌入图片为 base64（可选）
    ✅ 自动嵌入音频为 base64（可选）
    ✅ 生成独立的 HTML 文件，可离线使用
    ✅ 美化的音频播放按钮，点击即可播放
    ✅ 支持多种音频格式（MP3, WAV, OGG 等）
"""

import argparse
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from mdxscraper import Dictionary
from mdxscraper.core.renderer import merge_css, embed_images
from mdxscraper.core.audio import embed_audio_in_html, extract_audio_paths_from_html


def query_word(
    mdx_file: Path,
    word: str,
    output_file: Path = None,
    embed_dict_images: bool = True,
    embed_dict_audio: bool = True,
) -> str:
    """查询单个词汇并返回完整 HTML
    
    Args:
        mdx_file: MDX 词典文件路径
        word: 要查询的单词
        output_file: 可选的输出文件路径
        embed_dict_images: 是否嵌入词典中的图片（base64）
        embed_dict_audio: 是否嵌入词典中的音频（base64）
        
    Returns:
        包含完整 CSS 的 HTML 字符串
    """
    
    # 打开词典
    with Dictionary(mdx_file) as dict:
        # 查询单词（自动处理大小写、连字符等）
        html_content = dict.lookup_html(word)
        
        if not html_content:
            print(f"❌ 未找到单词: {word}", file=sys.stderr)
            return None
        
        # 使用 BeautifulSoup 解析 HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 尝试提取词典内部的 CSS
        dict_css = ""
        try:
            # 检查原始 HTML 是否包含 link 标签引用 CSS
            if '<link' in html_content.lower():
                # 创建完整的 HTML 结构供 merge_css 处理
                temp_html = f"<html><head>{html_content}</head><body></body></html>"
                temp_soup = BeautifulSoup(temp_html, 'lxml')
                
                # 调用 merge_css 提取并合并 CSS
                merged_soup = merge_css(temp_soup, mdx_file.parent, dict.impl, None)
                
                # 提取合并后的 CSS
                if merged_soup.head and merged_soup.head.style:
                    dict_css = merged_soup.head.style.string or ""
                    if dict_css:
                        print(f"✅ 已提取词典 CSS ({len(dict_css)} 字符)")
            else:
                print(f"ℹ️  词典内容未包含 CSS 引用")
        except Exception as e:
            print(f"ℹ️  无法提取词典 CSS: {e}")
            import traceback
            traceback.print_exc()
        
        # 如果需要嵌入图片
        if embed_dict_images:
            try:
                temp_soup = BeautifulSoup(f"<html><body>{html_content}</body></html>", 'lxml')
                embedded_soup = embed_images(temp_soup, dict.impl)
                # 更新 html_content
                html_content = str(embedded_soup.body)
                html_content = html_content.replace('<body>', '').replace('</body>', '')
                print(f"✅ 已嵌入词典图片")
            except Exception as e:
                print(f"ℹ️  无法嵌入图片: {e}")
        
        # 如果需要嵌入音频
        audio_count = 0
        has_unsupported_format = False
        if embed_dict_audio:
            try:
                # 先检查是否有音频
                audio_paths = extract_audio_paths_from_html(html_content)
                if audio_paths:
                    print(f"🔍 发现 {len(audio_paths)} 个音频路径")
                    
                    # 检查是否有不支持的格式
                    unsupported_formats = []
                    for path in audio_paths:
                        if path.lower().endswith('.spx'):
                            unsupported_formats.append('SPX')
                            has_unsupported_format = True
                    
                    if unsupported_formats:
                        print(f"⚠️  警告: 发现 {len(unsupported_formats)} 个 SPX 格式音频")
                        print(f"   SPX (Speex) 格式在现代浏览器中支持有限")
                        print(f"   建议: 使用 extract_audio.py 导出并转换为 MP3/OGG 格式")
                    
                    # 嵌入音频（转换为 base64 data URI）
                    html_content = embed_audio_in_html(html_content, dict.impl)
                    audio_count = len(audio_paths)
                    print(f"✅ 已嵌入 {audio_count} 个音频文件")
                else:
                    print(f"ℹ️  词条中未发现音频文件")
            except Exception as e:
                print(f"ℹ️  无法嵌入音频: {e}")
                import traceback
                traceback.print_exc()
        
        # 构建完整的 HTML 文档
        full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word}</title>
    <style>
        /* ========== 词典内部 CSS ========== */
        {dict_css}

        /* ========== 自定义样式 ========== */
        /* 基础样式 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}

        /* 音频播放样式 */
        audio {{
            width: 100%;
            max-width: 400px;
            margin: 10px 0;
            outline: none;
        }}

        /* 美化 sound:// 链接为播放按钮 */
        a[href^="data:audio"] {{
            display: inline-block;
            padding: 6px 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 5px 5px 5px 0;
        }}

        a[href^="data:audio"]:hover {{
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: translateY(-2px);
        }}

        a[href^="data:audio"]:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* 添加播放图标 */
        a[href^="data:audio"]::before {{
            content: '🔊 ';
            margin-right: 4px;
        }}

        /* 响应式设计 */
        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}
        }}
    </style>
    <script>
        // 点击链接播放音频
        document.addEventListener('DOMContentLoaded', function() {{
            // 处理所有音频链接
            document.querySelectorAll('a[href^="data:audio"]').forEach(function(link) {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    
                    // 创建并播放音频
                    const audio = new Audio(this.href);
                    
                    // 添加播放状态指示
                    const originalText = this.textContent;
                    this.textContent = '▶ ' + originalText.replace('🔊 ', '');
                    
                    audio.play().then(function() {{
                        console.log('音频播放中...');
                    }}).catch(function(error) {{
                        console.error('音频播放失败:', error);
                        alert('音频播放失败，请检查浏览器设置');
                    }});
                    
                    // 播放结束后恢复
                    audio.addEventListener('ended', function() {{
                        link.textContent = originalText;
                    }});
                    
                    // 发生错误时恢复
                    audio.addEventListener('error', function() {{
                        link.textContent = originalText;
                    }});
                }});
            }});
            
            // 统计音频数量
            const audioLinks = document.querySelectorAll('a[href^="data:audio"]').length;
            const audioElements = document.querySelectorAll('audio').length;
            if (audioLinks + audioElements > 0) {{
                console.log(`📊 页面包含 ${{audioLinks}} 个音频链接和 ${{audioElements}} 个音频元素`);
            }}
        }});
    </script>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # 保存到文件（如果指定）
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(full_html, encoding='utf-8')
            print(f"✅ 已保存到: {output_file}")
            print(f"📊 文件大小: {len(full_html):,} 字符")
        
        return full_html


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="查询 MDX 词典中的单个词汇并输出完整 HTML",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "word",
        help="要查询的单词"
    )
    
    parser.add_argument(
        "--mdx",
        type=Path,
        default=Path("data/mdict/your_dictionary.mdx"),
        help="MDX 词典文件路径 (默认: data/mdict/your_dictionary.mdx)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="输出 HTML 文件路径（不指定则打印到控制台）"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="不嵌入词典中的图片（减小文件大小）"
    )
    
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="不嵌入词典中的音频（减小文件大小）"
    )
    
    args = parser.parse_args()
    
    # 检查词典文件是否存在
    if not args.mdx.exists():
        print(f"❌ 词典文件不存在: {args.mdx}", file=sys.stderr)
        print(f"   当前目录: {Path.cwd()}", file=sys.stderr)
        print(f"   请使用 --mdx 指定正确的词典文件路径", file=sys.stderr)
        return 1
    
    print("=" * 70)
    print(f"📖 查询单词: {args.word}")
    print(f"📚 词典: {args.mdx}")
    print("=" * 70)
    
    # 执行查询
    result = query_word(
        args.mdx,
        args.word,
        args.output,
        embed_dict_images=not args.no_images,
        embed_dict_audio=not args.no_audio,
    )
    
    if result:
        if not args.output:
            # 如果没有指定输出文件，打印部分内容到控制台
            print("\n" + "=" * 70)
            print("HTML 输出预览（前 1000 字符）:")
            print("=" * 70)
            print(result[:1000])
            if len(result) > 1000:
                print(f"\n... (还有 {len(result) - 1000:,} 个字符)")
            print("\n提示: 使用 --output 参数保存到文件")
        
        print("\n" + "=" * 70)
        print("✅ 查询完成!")
        print("=" * 70)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
