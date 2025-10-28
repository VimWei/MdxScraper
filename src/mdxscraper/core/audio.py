"""Audio extraction and handling for MDX dictionaries.

This module provides functions to extract audio files from MDD files and
return them as base64-encoded data URIs for direct playback or saving.
"""

from __future__ import annotations

import re
from base64 import b64encode
from pathlib import Path
from typing import NamedTuple


class AudioInfo(NamedTuple):
    """Information about an audio file extracted from dictionary."""

    word: str  # 词条
    audio_path: str  # 音频路径（原始）
    audio_data: bytes  # 音频二进制数据
    mime_type: str  # MIME 类型
    data_uri: str  # base64 data URI
    format: str  # 文件格式（mp3, wav等）


def get_mime_type_from_filename(filename: str) -> str:
    """根据文件扩展名返回 MIME 类型."""

    ext = filename.lower().split(".")[-1]
    mime_types = {
        # Audio formats
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
        "m4a": "audio/mp4",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "webm": "audio/webm",
        "opus": "audio/opus",
        "weba": "audio/webm",
        "spx": "audio/ogg",  # Speex format (浏览器支持有限)
        # Video formats (某些词典可能包含视频发音)
        "mp4": "video/mp4",
        "ogv": "video/ogg",
        "webm": "video/webm",
    }
    return mime_types.get(ext, "audio/mpeg")


def extract_audio_paths_from_html(html: str) -> list[str]:
    """从 HTML 中提取所有音频路径.

    支持的格式:
    - <audio><source src="..."></audio>
    - <a href="sound://...">
    - <img src="sound://...">  # 某些词典用 img 标签触发音频
    - entry://sound/...

    Args:
        html: HTML 内容

    Returns:
        音频路径列表
    """
    paths = []

    # 1. <source src="..."> 标签
    source_pattern = r'<source\s+[^>]*src=["\'](.*?)["\']'
    paths.extend(re.findall(source_pattern, html, re.IGNORECASE))

    # 2. sound:// 协议
    sound_protocol_pattern = r'(?:href|src)=["\']*sound://([^"\'\s>]+)'
    sound_paths = re.findall(sound_protocol_pattern, html, re.IGNORECASE)
    paths.extend(sound_paths)

    # 3. entry://sound/ 协议
    entry_sound_pattern = r'entry://sound/([^"\'\s>]+)'
    entry_paths = re.findall(entry_sound_pattern, html, re.IGNORECASE)
    paths.extend(entry_paths)

    # 4. 直接的音频文件路径 (*.mp3, *.wav等)
    audio_ext_pattern = r'(?:href|src)=["\']([^"\']*\.(?:mp3|wav|ogg|m4a|aac|flac))["\']'
    audio_ext_paths = re.findall(audio_ext_pattern, html, re.IGNORECASE)
    paths.extend(audio_ext_paths)

    # 去重并清理
    unique_paths = []
    seen = set()
    for path in paths:
        # 移除 sound:// 等协议前缀
        clean_path = path.replace("sound://", "").replace("entry://sound/", "")
        if clean_path and clean_path not in seen:
            unique_paths.append(clean_path)
            seen.add(clean_path)

    return unique_paths


def lookup_audio(dictionary, audio_path: str) -> bytes | None:
    """从 MDD 文件中查找音频文件.

    Args:
        dictionary: IndexBuilder 实例
        audio_path: 音频文件路径

    Returns:
        音频二进制数据，如果未找到返回 None
    """
    if not hasattr(dictionary, "_mdd_db"):
        return None

    # 标准化路径
    lookup_path = audio_path.replace("/", "\\")

    # 尝试不同的路径格式
    search_paths = [
        lookup_path,
        "\\" + lookup_path if not lookup_path.startswith("\\") else lookup_path,
        lookup_path.lstrip("\\"),
    ]

    # 如果路径中包含 sound 或 audio 目录，也尝试移除
    if "sound" in lookup_path.lower() or "audio" in lookup_path.lower():
        filename = Path(lookup_path).name
        search_paths.append("\\" + filename)
        search_paths.append(filename)

    for path in search_paths:
        try:
            results = dictionary.mdd_lookup(path)
            if results and len(results) > 0:
                return results[0]
        except Exception:
            continue

    return None


def get_audio_info(dictionary, word: str, html: str) -> list[AudioInfo]:
    """获取词条的所有音频信息.

    Args:
        dictionary: IndexBuilder 实例
        word: 词条
        html: 词条的 HTML 内容

    Returns:
        AudioInfo 列表，包含所有找到的音频文件信息
    """
    audio_infos = []
    audio_paths = extract_audio_paths_from_html(html)

    for audio_path in audio_paths:
        audio_data = lookup_audio(dictionary, audio_path)
        if audio_data:
            file_format = audio_path.split(".")[-1].lower()
            mime_type = get_mime_type_from_filename(audio_path)
            data_uri = f"data:{mime_type};base64,{b64encode(audio_data).decode('ascii')}"

            audio_infos.append(
                AudioInfo(
                    word=word,
                    audio_path=audio_path,
                    audio_data=audio_data,
                    mime_type=mime_type,
                    data_uri=data_uri,
                    format=file_format,
                )
            )

    return audio_infos


def save_audio_file(audio_info: AudioInfo, output_path: Path | str) -> Path:
    """保存音频文件到磁盘.

    Args:
        audio_info: AudioInfo 对象
        output_path: 输出文件路径

    Returns:
        保存的文件路径
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(audio_info.audio_data)

    return output_path


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
    if not hasattr(dictionary, "_mdd_db"):
        return html

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    cache: dict[str, str] = {}

    # 1. 处理 <source> 标签
    for source in soup.find_all("source"):
        if not source.has_attr("src"):
            continue

        src = source["src"]
        # 跳过已经是 data URI 的
        if src.startswith("data:"):
            continue

        src_clean = src.replace("sound://", "").replace("entry://sound/", "")

        if src_clean in cache:
            source["src"] = cache[src_clean]
            continue

        audio_data = lookup_audio(dictionary, src_clean)
        if audio_data:
            mime_type = get_mime_type_from_filename(src_clean)
            data_uri = f"data:{mime_type};base64,{b64encode(audio_data).decode('ascii')}"
            cache[src_clean] = data_uri
            source["src"] = data_uri

    # 2. 处理 sound:// 链接
    for link in soup.find_all("a", href=True):
        href = link["href"]
        if href.startswith("sound://") or href.startswith("entry://sound/"):
            src_clean = href.replace("sound://", "").replace("entry://sound/", "")

            if src_clean in cache:
                link["href"] = cache[src_clean]
                continue

            audio_data = lookup_audio(dictionary, src_clean)
            if audio_data:
                mime_type = get_mime_type_from_filename(src_clean)
                data_uri = f"data:{mime_type};base64,{b64encode(audio_data).decode('ascii')}"
                cache[src_clean] = data_uri
                link["href"] = data_uri

    # 3. 处理 <img> 标签中的 sound:// (某些词典用这种方式)
    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("sound://") or src.startswith("entry://sound/"):
            src_clean = src.replace("sound://", "").replace("entry://sound/", "")

            if src_clean in cache:
                img["src"] = cache[src_clean]
                continue

            audio_data = lookup_audio(dictionary, src_clean)
            if audio_data:
                mime_type = get_mime_type_from_filename(src_clean)
                data_uri = f"data:{mime_type};base64,{b64encode(audio_data).decode('ascii')}"
                cache[src_clean] = data_uri
                img["src"] = data_uri

    return str(soup)
