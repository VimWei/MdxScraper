from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


class ExportService:
    def __init__(self, settings: SettingsService, presets: PresetsService):
        self.settings = settings
        self.presets = presets

    def build_pdf_options(self, pdf_text: str) -> Dict[str, Any]:
        base = {
            "page-size": "A4",
            "margin-top": "0.75in",
            "margin-right": "0.75in",
            "margin-bottom": "0.75in",
            "margin-left": "0.75in",
            "encoding": "UTF-8",
        }
        parsed = self.presets.parse_pdf_preset(pdf_text)
        base.update(parsed)
        return base

    def build_image_options(self, output_suffix: str) -> Dict[str, Any]:
        cm = self.settings.cm
        opts: Dict[str, Any] = {}
        w = int(cm.get("image.width", 0) or 0)
        if w > 0:
            opts["width"] = str(w)
        z = float(cm.get("image.zoom", 1.0) or 1.0)
        if z and z != 1.0:
            opts["zoom"] = str(z)
        if not bool(cm.get("image.background", True)):
            opts["no-background"] = ""
        if output_suffix in (".jpg", ".jpeg"):
            opts["quality"] = int(cm.get("image.jpg.quality", 85))
        elif output_suffix == ".png":
            opts["png_optimize"] = bool(cm.get("image.png.optimize", True))
            opts["png_compress_level"] = int(cm.get("image.png.compress_level", 9))
        elif output_suffix == ".webp":
            opts["webp_quality"] = int(cm.get("image.webp.quality", 80))
            opts["webp_lossless"] = bool(cm.get("image.webp.lossless", False))
        return opts

    def parse_css_styles(self, css_text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        return self.presets.parse_css_preset(css_text)

    def execute_export(
        self,
        input_file: Path,
        mdx_file: Path,
        output_path: Path,
        pdf_text: str = "",
        css_text: str = "",
        settings_service: Optional[SettingsService] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Tuple[int, int, List[str]]:
        from mdxscraper.core.converter import mdx2html, mdx2img, mdx2pdf

        suffix = output_path.suffix.lower()
        h1_style, scrap_style, additional_styles = self.parse_css_styles(css_text)

        if suffix == ".html":
            with_toc = settings_service.get("basic.with_toc", True)
            return mdx2html(
                mdx_file,
                input_file,
                output_path,
                with_toc=with_toc,
                h1_style=h1_style,
                scrap_style=scrap_style,
                additional_styles=additional_styles,
                progress_callback=progress_callback,
            )
        elif suffix == ".pdf":
            pdf_options = self.build_pdf_options(pdf_text)
            wkhtmltopdf_path = settings_service.get("advanced.wkhtmltopdf_path", "auto")
            with_toc = settings_service.get("basic.with_toc", True)
            return mdx2pdf(
                mdx_file,
                input_file,
                output_path,
                pdf_options,
                with_toc=with_toc,
                h1_style=h1_style,
                scrap_style=scrap_style,
                additional_styles=additional_styles,
                wkhtmltopdf_path=wkhtmltopdf_path,
                progress_callback=progress_callback,
            )
        elif suffix in (".jpg", ".jpeg", ".png", ".webp"):
            img_opts = self.build_image_options(suffix)
            with_toc = settings_service.get("basic.with_toc", True)
            return mdx2img(
                mdx_file,
                input_file,
                output_path,
                img_options=img_opts,
                with_toc=with_toc,
                h1_style=h1_style,
                scrap_style=scrap_style,
                additional_styles=additional_styles,
                progress_callback=progress_callback,
            )
        else:
            raise RuntimeError(f"Unsupported output extension: {suffix}")
