from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from mdxscraper.config.config_manager import ConfigManager


class ConversionWorker(QThread):
    finished_sig = Signal(str)
    error_sig = Signal(str)
    log_sig = Signal(str)

    def __init__(self, project_root: Path, cm: ConfigManager, pdf_text: str = '', css_text: str = ''):
        super().__init__()
        self.project_root = project_root
        self.cm = cm
        self._pdf_text = pdf_text
        self._css_text = css_text

    def run(self):
        try:
            from mdxscraper.core.converter import mdx2html, mdx2pdf, mdx2img
            import time

            # Start timing
            start_time = time.time()

            cfg = self.cm._config  # Use in-memory config instead of reloading from file
            input_file = self.cm._resolve_path(cfg.get('input', {}).get('file'))
            mdx_file = self.cm._resolve_path(cfg.get('dictionary', {}).get('file'))
            output_path = self.cm._resolve_path(cfg.get('output', {}).get('file'))

            # Apply timestamp if enabled
            timestamp_enabled = self.cm.get_output_add_timestamp()
            current_time = None
            if timestamp_enabled:
                from datetime import datetime
                current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_dir = output_path.parent
                output_name = output_path.name
                output_path = output_dir / (current_time + '_' + output_name)

            suffix = output_path.suffix.lower()
            self.log_sig.emit(f"🔄 Running conversion: {mdx_file.name} -> {output_path.name}")

            # Prepare CSS styles from CSS editor
            h1_style = None
            scrap_style = None
            additional_styles = None
            css_text = (self._css_text or '').strip()
            if css_text:
                try:
                    import tomllib as _tomllib
                    data = _tomllib.loads(css_text)
                    style = data.get('style', {}) if isinstance(data, dict) else {}
                    h1_style = style.get('h1_style')
                    scrap_style = style.get('scrap_style')
                    additional_styles = style.get('additional_styles')
                except Exception as ce:
                    self.log_sig.emit(f"⚠️ CSS preset parse failed, using defaults: {ce}")

            if suffix == '.html':
                found, not_found, invalid_words = mdx2html(
                    mdx_file, input_file, output_path, with_toc=True,
                    h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
                )
            elif suffix == '.pdf':
                # Base PDF options
                pdf_options = {
                    'page-size': 'A4',
                    'margin-top': '0.75in',
                    'margin-right': '0.75in',
                    'margin-bottom': '0.75in',
                    'margin-left': '0.75in',
                    'encoding': "UTF-8",
                }
                # Merge PDF options from editor content if available
                pdf_text = (self._pdf_text or '').strip()
                if pdf_text:
                    try:
                        import tomllib as _tomllib
                        data = _tomllib.loads(pdf_text)
                        pdf = data.get('pdf', {}) if isinstance(data, dict) else {}
                        normalized = {k.replace('_', '-'): v for k, v in pdf.items()}
                        pdf_options.update(normalized)
                    except Exception as pe:
                        self.log_sig.emit(f"⚠️ PDF preset parse failed, using defaults: {pe}")
                found, not_found, invalid_words = mdx2pdf(
                    mdx_file, input_file, output_path, pdf_options,
                    h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
                )
            elif suffix in ('.jpg', '.jpeg', '.png', '.webp'):
                # Build img options from config
                img_opts = {}
                w = int(self.cm.get('output.image.width', 0) or 0)
                if w > 0:
                    img_opts['width'] = str(w)
                z = float(self.cm.get('output.image.zoom', 1.0) or 1.0)
                if z and z != 1.0:
                    img_opts['zoom'] = str(z)
                if not bool(self.cm.get('output.image.background', True)):
                    img_opts['no-background'] = ''  # will be filtered out; kept for future
                # Format-specific
                if suffix in ('.jpg', '.jpeg'):
                    img_opts['quality'] = int(self.cm.get('output.image.jpg.quality', 85))
                elif suffix == '.png':
                    img_opts['png_optimize'] = bool(self.cm.get('output.image.png.optimize', True))
                    img_opts['png_compress_level'] = int(self.cm.get('output.image.png.compress_level', 9))
                    if bool(self.cm.get('output.image.png.transparent_bg', False)):
                        # Ensure transparent background via CSS already; flag kept for clarity
                        pass
                elif suffix == '.webp':
                    img_opts['webp_quality'] = int(self.cm.get('output.image.webp.quality', 80))
                    img_opts['webp_lossless'] = bool(self.cm.get('output.image.webp.lossless', False))
                found, not_found, invalid_words = mdx2img(
                    mdx_file, input_file, output_path, img_options=img_opts,
                    h1_style=h1_style, scrap_style=scrap_style, additional_styles=additional_styles
                )
            else:
                raise RuntimeError(f"Unsupported output extension: {suffix}")

            # Backup input file to output directory if enabled
            if self.cm.get_backup_input():
                try:
                    src = Path(input_file)
                    backup_dir = output_path.parent
                    base_name = src.stem + "_backup" + src.suffix
                    if timestamp_enabled and current_time:
                        base_name = current_time + '_' + base_name
                    dest = backup_dir / base_name
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    from shutil import copy2
                    copy2(src, dest)
                    self.log_sig.emit(f"📦 Backed up input to: {dest}")
                except Exception as be:
                    self.log_sig.emit(f"⚠️ Failed to backup input: {be}")

            # Calculate success rate
            total = found + not_found
            if total > 0:
                success_rate = (found / total) * 100
                msg = f"Done. Found: {found}, Success rate: {success_rate:.1f}%"
            else:
                msg = f"Done. Found: {found}, Success rate: 0%"

            # Emit success message first
            self.finished_sig.emit(msg)

            # Write invalid words file if enabled and there are any invalid words
            if self.cm.get_save_invalid_words() and invalid_words:
                from mdxscraper.core.converter import write_invalid_words_file
                # Filename pattern: [timestamp_]input_name_invalid.txt
                input_stem = Path(input_file).stem
                base_name = f"{input_stem}_invalid.txt"
                if timestamp_enabled and current_time:
                    base_name = f"{current_time}_{base_name}"
                invalid_words_dir = output_path.parent
                invalid_words_path = invalid_words_dir / base_name
                write_invalid_words_file(invalid_words, invalid_words_path)
                self.log_sig.emit(f"📝 Invalid words saved to: {invalid_words_path}")

            # Calculate and emit duration last
            end_time = time.time()
            duration = end_time - start_time

            # Format duration in human readable format
            if duration < 1:
                duration_str = f"{duration*1000:.0f}ms"
            elif duration < 60:
                duration_str = f"{duration:.3f}s"
            else:
                minutes = int(duration // 60)
                seconds = duration % 60
                duration_str = f"{minutes}m {seconds:.1f}s"

            self.log_sig.emit(f"⏱️ The entire process took a total of {duration_str}.")
        except Exception as e:
            self.error_sig.emit(str(e))


