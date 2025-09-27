"""文件操作工具函数"""

from collections import OrderedDict
from pathlib import Path


def write_invalid_words_file(invalid_words: OrderedDict, output_file: str | Path) -> None:
    """Write invalid words to a text file in the same format as input files.
    
    Args:
        invalid_words: Dictionary mapping lesson names to lists of invalid words
        output_file: Path to the output file
    """
    if not invalid_words:
        return
        
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for lesson_name, words in invalid_words.items():
            f.write(f"# {lesson_name}\n")
            for word in words:
                f.write(f"{word}\n")
            f.write("\n")


def get_image_format_from_src(src: str) -> str:
    """Get image format from file source path.
    
    Args:
        src: Source path or filename
        
    Returns:
        Image format string (png, jpeg, gif, webp, svg, tiff, bmp, or jpg as default)
    """
    ext = Path(src).suffix.lower()
    if ext == '.png':
        return 'png'
    elif ext in ['.jpg', '.jpeg']:
        return 'jpeg'
    elif ext == '.gif':
        return 'gif'
    elif ext == '.webp':
        return 'webp'
    elif ext == '.svg':
        return 'svg'
    elif ext in ['.tif', '.tiff']:
        return 'tiff'
    elif ext == '.bmp':
        return 'bmp'
    else:
        return 'jpg'
