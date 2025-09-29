from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QMessageBox

from mdxscraper.services.settings_service import SettingsService
from mdxscraper.utils.system_utils import open_file_or_directory


class FileCoordinator:
    """Coordinate file interactions: input/dictionary/output pickers and opening data dir."""

    def __init__(self, settings: SettingsService, project_root: Path) -> None:
        self.settings = settings
        self.project_root = project_root

    def choose_input(self, mw) -> None:
        current = mw.edit_input.text()
        fallback_dir = self.project_root / "data" / "input"
        if current:
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
            except Exception:
                start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
        else:
            start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            mw, "Select input file", start_dir, "Supported files (*.txt *.md *.json *.xlsx)"
        )
        if file:
            self.settings.set_input_file(file)
            mw.edit_input.setText(self.settings.get("basic.input_file"))
            mw.on_input_edited()

    def choose_dictionary(self, mw) -> None:
        current = mw.edit_dict.text()
        fallback_dir = self.project_root / "data" / "mdict"
        if current:
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
            except Exception:
                start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
        else:
            start_dir = str(fallback_dir if fallback_dir.exists() else self.project_root)
        file, _ = QFileDialog.getOpenFileName(
            mw, "Select MDX dictionary", start_dir, "MDX Files (*.mdx)"
        )
        if file:
            self.settings.set_dictionary_file(file)
            mw.edit_dict.setText(self.settings.get("basic.dictionary_file"))

    def choose_output(self, mw) -> None:
        current = mw.edit_output.text()
        if current:
            try:
                resolved_path = self.settings.resolve_path(current)
                if resolved_path.exists():
                    start_dir = str(resolved_path.parent)
                else:
                    output_dir = self.settings.get("output.directory", "data/output")
                    start_dir = (
                        str(Path(output_dir).resolve())
                        if Path(output_dir).exists()
                        else str(self.project_root / "data" / "output")
                    )
            except Exception:
                output_dir = self.settings.get("output.directory", "data/output")
                start_dir = (
                    str(Path(output_dir).resolve())
                    if Path(output_dir).exists()
                    else str(self.project_root / "data" / "output")
                )
        else:
            output_dir = self.settings.get("output.directory", "data/output")
            start_dir = (
                str(Path(output_dir).resolve())
                if Path(output_dir).exists()
                else str(self.project_root / "data" / "output")
            )

        default_filename = ""
        input_file = mw.edit_input.text().strip()
        if input_file:
            try:
                input_path = self.settings.resolve_path(input_file)
                default_filename = input_path.stem
            except Exception:
                pass

        filters = "HTML files (*.html);;PDF files (*.pdf);;JPG files (*.jpg);;PNG files (*.png);;WEBP files (*.webp);;All files (*.*)"
        file, _ = QFileDialog.getSaveFileName(
            mw,
            "Select output file",
            str(Path(start_dir) / (default_filename + ".html" if default_filename else "")),
            filters,
            "All files (*.*)",
        )
        if file:
            self.settings.set_output_file(file)
            mw.edit_output.setText(self.settings.get("basic.output_file"))

    def open_user_data_dir(self, mw) -> None:
        try:
            target = (self.project_root / "data").resolve()
            target.mkdir(parents=True, exist_ok=True)
            open_file_or_directory(target)
            try:
                if hasattr(mw, "tab_advanced") and hasattr(mw.tab_advanced, "edit_data_path"):
                    mw.tab_advanced.edit_data_path.setText(str(target))
            except Exception:
                pass
        except Exception as e:
            mw.log_panel.appendLog(f"❌ Failed to open data folder: {e}")

    def get_user_data_dir(self) -> Path:
        """Return the absolute user data directory path without opening UI."""
        target = (self.project_root / "data").resolve()
        target.mkdir(parents=True, exist_ok=True)
        return target
