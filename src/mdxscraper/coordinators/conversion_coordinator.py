from __future__ import annotations

from pathlib import Path
from typing import Optional

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.services.settings_service import SettingsService
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.workers.conversion_worker import ConversionWorker


class ConversionCoordinator:
    """Coordinate running conversion, progress, logs, and interruption."""

    def __init__(self, settings: SettingsService, presets: PresetsService, project_root: Path, cm: ConfigManager) -> None:
        self.settings = settings
        self.presets = presets
        self.project_root = project_root
        self.cm = cm
        self.worker: Optional[ConversionWorker] = None

    def run(self, mw) -> None:
        # sync pages to settings
        mw.cfgc.sync_all_to_config(mw)
        # autosave Untitled before run
        mw.preset_coordinator.autosave_untitled_if_needed(mw)

        mw.command_panel.btn_scrape.setEnabled(False)

        # Use editor content directly per spec
        pdf_text = mw.tab_pdf.pdf_editor.toPlainText()
        css_text = mw.tab_css.css_editor.toPlainText()

        self.worker = ConversionWorker(self.project_root, self.cm, pdf_text=pdf_text, css_text=css_text)
        self.worker.finished_sig.connect(lambda msg: self.on_finished(mw, msg))
        self.worker.error_sig.connect(lambda msg: self.on_error(mw, msg))
        self.worker.log_sig.connect(lambda text: self.on_log(mw, text))
        self.worker.progress_sig.connect(lambda p, t: self.on_progress(mw, p, t))
        mw.command_panel.setProgress(0)
        mw.command_panel.setProgressText("Starting conversion...")
        self.worker.start()

    def on_finished(self, mw, message: str) -> None:
        mw.command_panel.btn_scrape.setEnabled(True)
        mw.command_panel.setProgress(100)
        mw.command_panel.setProgressText("Conversion completed!")
        mw.log_panel.appendLog(f"✅ {message}")
        # Do not clear self.worker here to ensure any queued log_sig (e.g., duration) is delivered

    def on_error(self, mw, message: str) -> None:
        mw.command_panel.btn_scrape.setEnabled(True)
        mw.command_panel.setProgress(0)
        mw.command_panel.setProgressText("Conversion failed")
        mw.log_panel.appendLog(f"❌ Error: {message}")
        # Likewise, keep worker reference until thread fully completes

    def on_progress(self, mw, progress: int, text: str) -> None:
        mw.command_panel.setProgress(progress)
        mw.command_panel.setProgressText(text)

    def on_log(self, mw, text: str) -> None:
        # Skip redundant progress messages
        if not text.startswith("Progress:"):
            mw.log_panel.appendLog(text)

    def request_stop(self) -> None:
        if self.worker:
            self.worker.requestInterruption()


