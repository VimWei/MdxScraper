from __future__ import annotations

from base64 import b64encode
from pathlib import Path

from bs4 import BeautifulSoup


def get_css(soup: BeautifulSoup, mdx_path: Path, dictionary) -> str:
    css_name = soup.head.link["href"]
    css_path = Path(mdx_path) / css_name
    if css_path.exists():
        css = css_path.read_bytes()
    elif hasattr(dictionary, "_mdd_db"):
        css_key = dictionary.get_mdd_keys("*" + css_name)[0]
        css = dictionary.mdd_lookup(css_key)[0]
    else:
        css = b""
    return css.decode("utf-8")


def merge_css(
    soup: BeautifulSoup, mdx_path: Path, dictionary, additional_styles: str | None = None
) -> BeautifulSoup:
    try:
        css = get_css(soup, mdx_path, dictionary)
    except Exception:
        return soup
    if additional_styles:
        css += additional_styles

    soup.head.link.decompose()
    soup.head.append(soup.new_tag("style", type="text/css"))
    soup.head.style.string = css
    return soup


def embed_images(soup: BeautifulSoup, dictionary) -> BeautifulSoup:
    if not hasattr(dictionary, "_mdd_db"):
        return soup

    cache: dict[str, str] = {}
    for img in soup.find_all("img"):
        if not img.has_attr("src"):
            continue

        src = img["src"]
        src_path = src.replace("/", "\\")

        if src_path in cache:
            img["src"] = cache[src_path]
            continue

        lookup_src = src_path
        if not lookup_src.startswith("\\"):
            lookup_src = "\\" + lookup_src

        imgs = dictionary.mdd_lookup(lookup_src)
        if len(imgs) > 0:
            from mdxscraper.utils.file_utils import get_image_format_from_src

            image_format = get_image_format_from_src(src)
            base64_str = (
                "data:image/" + image_format + ";base64," + b64encode(imgs[0]).decode("ascii")
            )
            cache[src_path] = base64_str
            img["src"] = base64_str

    return soup
