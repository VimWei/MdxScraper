# MDX 词典音频提取与播放

## 概述

MdxScraper 提供了完整的音频提取 API，可以从 MDX 词典的 MDD 文件中提取音频，并支持：

- 🎵 提取单个或批量词条的音频文件
- 💾 保存音频文件到磁盘
- 🔗 生成 base64 data URI 用于直接播放
- 📄 在 HTML 中嵌入音频实现点击播放
- 🌐 支持多种音频格式（MP3, WAV, OGG, M4A 等）

## 快速开始

### 1. 提取单个词条的音频

```python
from mdxscraper import Dictionary, get_audio_info, save_audio_file

# 加载词典
with Dictionary("NHK日本語発音アクセント辞書.mdx") as dictionary:
    # 查询词条
    html = dictionary.lookup_html("あい")
    
    # 获取音频信息
    audio_infos = get_audio_info(dictionary.impl, "あい", html)
    
    # 保存音频
    for i, audio_info in enumerate(audio_infos, 1):
        print(f"格式: {audio_info.format}")
        print(f"大小: {len(audio_info.audio_data)} bytes")
        
        # 保存到文件
        save_audio_file(audio_info, f"あい_{i}.{audio_info.format}")
```

### 2. 使用命令行工具

```bash
# 提取单个词条音频
python examples/extract_audio.py あい --mdx "NHK日本語発音アクセント辞書.mdx"

# 只查看音频信息（不保存）
python examples/extract_audio.py あい --mdx "NHK日本語発音アクセント辞書.mdx" --list-only

# 批量提取
python examples/extract_audio.py --batch words.txt --mdx "NHK日本語発音アクセント辞書.mdx"
```

## API 参考

### AudioInfo

音频信息数据类，包含：

```python
@dataclass
class AudioInfo:
    word: str           # 词条
    audio_path: str     # 音频路径（MDD 中的路径）
    audio_data: bytes   # 音频二进制数据
    mime_type: str      # MIME 类型（如 audio/mpeg）
    data_uri: str       # base64 data URI（可直接用于 <audio> 标签）
    format: str         # 文件格式（mp3, wav 等）
```

### get_audio_info()

获取词条的所有音频信息。

```python
def get_audio_info(dictionary, word: str, html: str) -> list[AudioInfo]:
    """获取词条的所有音频信息.
    
    Args:
        dictionary: IndexBuilder 实例（dictionary.impl）
        word: 词条
        html: 词条的 HTML 内容
        
    Returns:
        AudioInfo 列表
    """
```

**使用示例**：

```python
from mdxscraper import Dictionary, get_audio_info

with Dictionary("dict.mdx") as dictionary:
    html = dictionary.lookup_html("hello")
    audio_infos = get_audio_info(dictionary.impl, "hello", html)
    
    for audio in audio_infos:
        print(f"路径: {audio.audio_path}")
        print(f"格式: {audio.format} ({audio.mime_type})")
        print(f"大小: {len(audio.audio_data):,} bytes")
```

### lookup_audio()

从 MDD 文件中查找音频。

```python
def lookup_audio(dictionary, audio_path: str) -> bytes | None:
    """从 MDD 文件中查找音频文件.
    
    Args:
        dictionary: IndexBuilder 实例
        audio_path: 音频文件路径
        
    Returns:
        音频二进制数据，未找到返回 None
    """
```

**使用示例**：

```python
from mdxscraper import Dictionary, lookup_audio

with Dictionary("dict.mdx") as dictionary:
    # 直接查找音频文件
    audio_data = lookup_audio(dictionary.impl, "\\sound\\hello.mp3")
    
    if audio_data:
        with open("hello.mp3", "wb") as f:
            f.write(audio_data)
```

### save_audio_file()

保存音频文件到磁盘。

```python
def save_audio_file(audio_info: AudioInfo, output_path: Path | str) -> Path:
    """保存音频文件到磁盘.
    
    Args:
        audio_info: AudioInfo 对象
        output_path: 输出文件路径
        
    Returns:
        保存的文件路径
    """
```

**使用示例**：

```python
from mdxscraper import Dictionary, get_audio_info, save_audio_file
from pathlib import Path

with Dictionary("dict.mdx") as dictionary:
    html = dictionary.lookup_html("hello")
    audio_infos = get_audio_info(dictionary.impl, "hello", html)
    
    output_dir = Path("audio_output")
    output_dir.mkdir(exist_ok=True)
    
    for i, audio in enumerate(audio_infos, 1):
        output_path = output_dir / f"hello_{i}.{audio.format}"
        save_audio_file(audio, output_path)
        print(f"已保存: {output_path}")
```

### extract_audio_paths_from_html()

从 HTML 中提取所有音频路径。

```python
def extract_audio_paths_from_html(html: str) -> list[str]:
    """从 HTML 中提取所有音频路径.
    
    支持的格式:
    - <audio><source src="..."></audio>
    - <a href="sound://...">
    - <img src="sound://...">
    - entry://sound/...
    
    Args:
        html: HTML 内容
        
    Returns:
        音频路径列表
    """
```

**使用示例**：

```python
from mdxscraper import Dictionary, extract_audio_paths_from_html

with Dictionary("dict.mdx") as dictionary:
    html = dictionary.lookup_html("hello")
    audio_paths = extract_audio_paths_from_html(html)
    
    print(f"找到 {len(audio_paths)} 个音频:")
    for path in audio_paths:
        print(f"  - {path}")
```

### embed_audio_in_html()

在 HTML 中嵌入音频为 base64 data URI。

```python
def embed_audio_in_html(html: str, dictionary) -> str:
    """在 HTML 中嵌入音频为 base64 data URI.
    
    自动处理:
    - <source src="..."> 标签
    - sound:// 协议链接
    - entry://sound/ 协议
    
    Args:
        html: HTML 内容
        dictionary: IndexBuilder 实例
        
    Returns:
        嵌入音频后的 HTML
    """
```

**使用示例**：

```python
from mdxscraper import Dictionary, embed_audio_in_html

with Dictionary("dict.mdx") as dictionary:
    html = dictionary.lookup_html("hello")
    
    # 嵌入音频
    html_with_audio = embed_audio_in_html(html, dictionary.impl)
    
    # 生成完整的 HTML 文档
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>hello</title>
</head>
<body>
    {html_with_audio}
</body>
</html>"""
    
    # 保存
    Path("hello.html").write_text(full_html, encoding="utf-8")
```

## 支持的音频格式

| 格式 | 扩展名 | MIME 类型 | 浏览器支持 |
|------|--------|-----------|------------|
| MP3 | `.mp3` | `audio/mpeg` | ✅ 广泛支持 |
| WAV | `.wav` | `audio/wav` | ✅ 广泛支持 |
| OGG | `.ogg`, `.oga` | `audio/ogg` | ✅ 现代浏览器 |
| M4A | `.m4a` | `audio/mp4` | ✅ 大部分浏览器 |
| AAC | `.aac` | `audio/aac` | ✅ 现代浏览器 |
| FLAC | `.flac` | `audio/flac` | ⚠️ 部分浏览器 |
| WebM | `.webm`, `.weba` | `audio/webm` | ✅ 现代浏览器 |
| Opus | `.opus` | `audio/opus` | ✅ 现代浏览器 |

## 使用场景

### 场景 1: 单词卡片生成器

为 Anki 等记忆软件生成带发音的单词卡片。

```python
from mdxscraper import Dictionary, get_audio_info
from pathlib import Path

def create_anki_card(word: str, mdx_file: Path, output_dir: Path):
    """创建 Anki 单词卡片（带音频）"""
    
    with Dictionary(mdx_file) as dictionary:
        # 查询词条
        html = dictionary.lookup_html(word)
        if not html:
            return None
        
        # 获取音频
        audio_infos = get_audio_info(dictionary.impl, word, html)
        
        # 保存音频
        audio_files = []
        for i, audio in enumerate(audio_infos, 1):
            filename = f"{word}_{i}.{audio.format}"
            audio_path = output_dir / "collection.media" / filename
            save_audio_file(audio, audio_path)
            audio_files.append(filename)
        
        # 生成 Anki 卡片格式
        card = {
            "word": word,
            "definition": html,
            "audio": audio_files,
        }
        
        return card

# 批量生成
words = ["hello", "world", "python"]
output = Path("anki_deck")
output.mkdir(exist_ok=True)

for word in words:
    card = create_anki_card(word, "dict.mdx", output)
    print(f"✅ {word}: {len(card['audio'])} 音频")
```

### 场景 2: 在线词典网站

为网站提供音频播放功能。

```python
from flask import Flask, jsonify
from mdxscraper import Dictionary, get_audio_info

app = Flask(__name__)
dictionary = Dictionary("dict.mdx")

@app.route("/api/word/<word>/audio")
def get_word_audio(word):
    """API: 获取词条的音频信息"""
    
    html = dictionary.lookup_html(word)
    if not html:
        return jsonify({"error": "Word not found"}), 404
    
    audio_infos = get_audio_info(dictionary.impl, word, html)
    
    # 返回 JSON
    return jsonify({
        "word": word,
        "audio": [
            {
                "path": audio.audio_path,
                "format": audio.format,
                "mime_type": audio.mime_type,
                "data_uri": audio.data_uri,  # 可直接用于 <audio> 标签
                "size": len(audio.audio_data),
            }
            for audio in audio_infos
        ]
    })

if __name__ == "__main__":
    app.run(debug=True)
```

前端使用：

```javascript
// 获取音频并播放
fetch(`/api/word/hello/audio`)
    .then(res => res.json())
    .then(data => {
        data.audio.forEach((audio, i) => {
            // 创建 audio 元素
            const audioEl = document.createElement('audio');
            audioEl.controls = true;
            audioEl.src = audio.data_uri;  // 使用 data URI
            document.body.appendChild(audioEl);
        });
    });
```

### 场景 3: 语音学习应用

提取所有单词的发音，用于离线学习。

```python
from mdxscraper import Dictionary, get_audio_info, save_audio_file
from pathlib import Path
import json

def extract_vocabulary_audio(words_file: Path, mdx_file: Path, output_dir: Path):
    """提取词汇表的所有音频"""
    
    # 读取词汇列表
    words = Path(words_file).read_text(encoding="utf-8").splitlines()
    
    # 准备输出目录
    audio_dir = output_dir / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    
    # 音频索引
    audio_index = {}
    
    with Dictionary(mdx_file) as dictionary:
        for i, word in enumerate(words, 1):
            print(f"[{i}/{len(words)}] {word}")
            
            html = dictionary.lookup_html(word)
            if not html:
                continue
            
            audio_infos = get_audio_info(dictionary.impl, word, html)
            if not audio_infos:
                continue
            
            # 保存音频
            word_audio = []
            for j, audio in enumerate(audio_infos, 1):
                filename = f"{word}_{j}.{audio.format}"
                audio_path = audio_dir / filename
                save_audio_file(audio, audio_path)
                
                word_audio.append({
                    "file": filename,
                    "format": audio.format,
                    "size": len(audio.audio_data),
                })
            
            audio_index[word] = word_audio
    
    # 保存索引
    index_file = output_dir / "audio_index.json"
    index_file.write_text(json.dumps(audio_index, ensure_ascii=False, indent=2))
    
    print(f"\n✅ 完成！")
    print(f"   词条数: {len(audio_index)}")
    print(f"   音频文件: {sum(len(v) for v in audio_index.values())}")
    print(f"   索引文件: {index_file}")

# 使用
extract_vocabulary_audio(
    words_file="vocabulary.txt",
    mdx_file="NHK日本語発音アクセント辞書.mdx",
    output_dir=Path("learning_materials")
)
```

### 场景 4: 集成到 query_word.py

```python
from mdxscraper import Dictionary, embed_audio_in_html
from pathlib import Path

def query_word_with_audio(word: str, mdx_file: Path, output_file: Path):
    """查询单词并生成带音频播放的 HTML"""
    
    with Dictionary(mdx_file) as dictionary:
        # 查询词条
        html = dictionary.lookup_html(word)
        if not html:
            print(f"❌ 未找到: {word}")
            return
        
        # 嵌入音频
        html_with_audio = embed_audio_in_html(html, dictionary.impl)
        
        # 完整 HTML
        full_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{word}</title>
    <style>
        body {{
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            font-family: sans-serif;
            line-height: 1.8;
        }}
        audio {{
            width: 100%;
            margin: 10px 0;
        }}
        /* 美化 sound:// 链接 */
        a[href^="data:audio"] {{
            display: inline-block;
            padding: 5px 12px;
            background: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
        }}
        a[href^="data:audio"]:hover {{
            background: #0052a3;
        }}
    </style>
    <script>
        // 点击链接播放音频
        document.addEventListener('DOMContentLoaded', function() {{
            document.querySelectorAll('a[href^="data:audio"]').forEach(link => {{
                link.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const audio = new Audio(this.href);
                    audio.play();
                }});
            }});
        }});
    </script>
</head>
<body>
    <h1>{word}</h1>
    {html_with_audio}
</body>
</html>"""
        
        # 保存
        output_file.write_text(full_html, encoding="utf-8")
        print(f"✅ 已保存: {output_file}")

# 使用
query_word_with_audio(
    word="あい",
    mdx_file=Path("NHK日本語発音アクセント辞書.mdx"),
    output_file=Path("あい.html")
)
```

## 常见问题

### Q: 如何知道词条有哪些音频文件？

```python
from mdxscraper import Dictionary, extract_audio_paths_from_html

with Dictionary("dict.mdx") as dictionary:
    html = dictionary.lookup_html("hello")
    audio_paths = extract_audio_paths_from_html(html)
    print(f"音频文件: {audio_paths}")
```

### Q: 音频文件找不到怎么办？

音频文件可能使用不同的路径格式。`lookup_audio()` 会自动尝试多种格式：

- `\sound\hello.mp3`
- `sound\hello.mp3`
- `\hello.mp3`
- `hello.mp3`

如果仍然找不到，检查 MDD 文件中的实际路径：

```python
# 列出 MDD 中的所有音频文件
keys = dictionary.impl.get_mdd_keys("*.mp3")
for key in keys[:10]:  # 显示前 10 个
    print(key)
```

### Q: 如何在网页中实现点击播放？

使用 `embed_audio_in_html()` 会自动将 `sound://` 链接转换为 data URI，然后添加 JavaScript：

```html
<script>
document.querySelectorAll('a[href^="data:audio"]').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const audio = new Audio(this.href);
        audio.play();
    });
});
</script>
```

### Q: Data URI 太长会影响性能吗？

对于单个词条，通常不会有问题。但如果批量处理：

1. **小文件**（< 100KB）：直接使用 data URI
2. **大文件**：保存到磁盘，使用文件路径

```python
# 根据文件大小选择策略
if len(audio_info.audio_data) < 100_000:
    # 使用 data URI
    use_data_uri = audio_info.data_uri
else:
    # 保存到文件
    save_audio_file(audio_info, "audio.mp3")
    use_file_path = "audio.mp3"
```

## 相关文件

- `src/mdxscraper/core/audio.py` - 音频处理核心模块
- `examples/extract_audio.py` - 命令行音频提取工具
- `src/mdxscraper/__init__.py` - 暴露的 API 接口

## 下一步

- 查看 [examples/extract_audio.py](../examples/extract_audio.py) 获取完整示例
- 集成到你的项目中使用音频 API
- 为 NHK 日语词典等语音词典提取发音
