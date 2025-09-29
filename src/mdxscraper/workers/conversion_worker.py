from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QThread, Signal

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.services.export_service import ExportService
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


class ConversionWorker(QThread):
    finished_sig = Signal(str)
    error_sig = Signal(str)
    log_sig = Signal(str)
    progress_sig = Signal(int, str)  # progress percentage, status message

    def __init__(self, project_root: Path, cm: ConfigManager, pdf_text: str = '', css_text: str = ''):
        super().__init__()
        self.project_root = project_root
        self.cm = cm
        self._pdf_text = pdf_text
        self._css_text = css_text
        # Services for export pipeline
        self._settings_service = SettingsService(project_root, cm)
        self._presets_service = PresetsService(project_root)
        self._export_service = ExportService(self._settings_service, self._presets_service)

    def run(self):
        try:
            import time

            # Start timing
            start_time = time.time()

            cfg = self._settings_service.get_config_dict()  # in-memory config
            basic = cfg.get('basic', {}) if isinstance(cfg, dict) else {}
            input_val = basic.get('input_file')
            dict_val = basic.get('dictionary_file')
            output_val = basic.get('output_file')

            # Validate presence early to produce clearer errors
            if not input_val or not dict_val or not output_val:
                missing = []
                if not input_val:
                    missing.append('basic.input_file')
                if not dict_val:
                    missing.append('basic.dictionary_file')
                if not output_val:
                    missing.append('basic.output_file')
                raise ValueError('Missing required field(s): ' + ', '.join(missing))

            input_file = self._settings_service.resolve_path(input_val)
            mdx_file = self._settings_service.resolve_path(dict_val)
            output_path = self._settings_service.resolve_path(output_val)

            # Apply timestamp if enabled
            timestamp_enabled = self._settings_service.get_output_add_timestamp()
            current_time = None
            if timestamp_enabled:
                from datetime import datetime
                current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
                output_dir = output_path.parent
                output_name = output_path.name
                output_path = output_dir / (current_time + '_' + output_name)

            suffix = output_path.suffix.lower()
            self.log_sig.emit(f"🔄 Running conversion: {mdx_file.name} -> {output_path.name}")
            self.progress_sig.emit(10, "Starting conversion...")

            # Execute export via ExportService with progress callback
            def progress_callback(progress: int, message: str):
                # Scale progress from 10-90% to leave room for final steps
                scaled_progress = 10 + int((progress / 100) * 80)
                self.progress_sig.emit(scaled_progress, message)
            
            found, not_found, invalid_words = self._export_service.execute_export(
                input_file, mdx_file, output_path, pdf_text=self._pdf_text or '', css_text=self._css_text or '', 
                settings_service=self._settings_service, progress_callback=progress_callback
            )

            # Backup input file to output directory if enabled
            self.progress_sig.emit(90, "Processing backup files...")
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
                    self.log_sig.emit(f"📦 Backed up input to: {self._settings_service.to_relative(dest)}")
                except Exception as be:
                    self.log_sig.emit(f"⚠️ Failed to backup input: {be}")

            # Calculate success rate
            total = found + not_found
            if total > 0:
                success_rate = (found / total) * 100
                msg = f"Done. Found: {found}, Success rate: {success_rate:.1f}%"
            else:
                msg = f"Done. Found: {found}, Success rate: 0%"

            # Write invalid words file if enabled and there are any invalid words
            self.progress_sig.emit(95, "Saving invalid words...")
            if self.cm.get_save_invalid_words() and invalid_words:
                from mdxscraper.utils.file_utils import write_invalid_words_file

                # Filename pattern: [timestamp_]input_name_invalid.txt
                input_stem = Path(input_file).stem
                base_name = f"{input_stem}_invalid.txt"
                if timestamp_enabled and current_time:
                    base_name = f"{current_time}_{base_name}"
                invalid_words_dir = output_path.parent
                invalid_words_path = invalid_words_dir / base_name
                write_invalid_words_file(invalid_words, invalid_words_path)
                self.log_sig.emit(f"📝 Invalid words saved to: {self._settings_service.to_relative(invalid_words_path)}")

            # Emit success message after auxiliary files are handled
            self.progress_sig.emit(100, "Conversion completed!")
            self.finished_sig.emit(msg)

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

            self.log_sig.emit(f"⏱️ The entire process took a total of {duration_str}.\n")
        except Exception as e:
            self.error_sig.emit(str(e))

    


