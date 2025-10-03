from __future__ import annotations

from pathlib import Path

import pytest


def seed_defaults_and_theme(root: Path) -> None:
    d = root / "src" / "mdxscraper" / "config"
    d.mkdir(parents=True, exist_ok=True)
    (d / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n\n[pdf]\npreset_label=''\n\n[css]\npreset_label=''\n",
        encoding="utf-8",
    )
    themes = root / "src" / "mdxscraper" / "gui" / "styles" / "themes"
    themes.mkdir(parents=True, exist_ok=True)
    (themes / "default.qss").write_text(".root { }", encoding="utf-8")


@pytest.mark.usefixtures("mock_qt_application")
def test_conversion_worker_missing_fields_emits_error(monkeypatch, tmp_path: Path):
    from mdxscraper.config.config_manager import ConfigManager
    from mdxscraper.workers.conversion_worker import ConversionWorker

    cm = ConfigManager(tmp_path)
    seed_defaults_and_theme(tmp_path)
    cm.load()
    # Ensure blanks to trigger validation path
    cm.set("basic.input_file", "")
    cm.set("basic.dictionary_file", "")
    cm.set("basic.output_file", "")
    # Ensure ExportService does not do heavy work during __init__
    from mdxscraper.workers import conversion_worker as mod

    class _NoopExport:
        def __init__(self, *a, **k):
            pass

        def execute_export(self, *a, **k):
            raise AssertionError("should not be called in missing fields test")

    monkeypatch.setattr(mod, "ExportService", lambda *a, **k: _NoopExport())
    w = ConversionWorker(tmp_path, cm)

    class DummySig:
        def __init__(self):
            self.msgs = []

        def emit(self, m):
            self.msgs.append(m)

    # Replace Qt signal with dummy collector to avoid event loop issues
    dummy_err = DummySig()
    w.error_sig = dummy_err

    # Run synchronously; ensure Qt event loop exists
    w.run()

    assert dummy_err.msgs and "Missing required field" in dummy_err.msgs[0]


@pytest.mark.usefixtures("mock_qt_application")
def test_conversion_worker_success_flow(monkeypatch, tmp_path: Path):
    from mdxscraper.config.config_manager import ConfigManager
    from mdxscraper.workers.conversion_worker import ConversionWorker

    cm = ConfigManager(tmp_path)
    seed_defaults_and_theme(tmp_path)
    cm.load()

    # Provide minimal valid config
    inp = tmp_path / "data" / "input.txt"
    inp.parent.mkdir(parents=True, exist_ok=True)
    inp.write_text("# L\nword", encoding="utf-8")
    mdx = tmp_path / "data" / "dict.mdx"
    mdx.write_text("stub", encoding="utf-8")
    out = tmp_path / "data" / "out.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    cm.set("basic.input_file", str(inp))
    cm.set("basic.dictionary_file", str(mdx))
    cm.set("basic.output_file", str(out))
    # Disable timestamping and side effects that can change output path
    cm.set_output_add_timestamp(False)
    cm.set_backup_input(False)
    cm.set_save_invalid_words(False)

    # Stub ExportService before worker instantiation to avoid real service creation
    from mdxscraper.workers import conversion_worker as mod

    class StubExport:
        def __init__(self, *args, **kwargs):
            pass

        def execute_export(self, input_file, mdx_file, output_path, **kwargs):
            cb = kwargs.get("progress_callback")
            if cb:
                cb(50, "half")
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            Path(output_path).write_text("<html></html>", encoding="utf-8")
            return 1, 0, {}

    monkeypatch.setattr(mod, "ExportService", lambda *a, **k: StubExport())

    # Avoid actual copy2 by monkeypatching shutil.copy2
    import shutil

    monkeypatch.setattr(shutil, "copy2", lambda src, dst: Path(dst).write_text("copied"))

    w = ConversionWorker(tmp_path, cm)

    class DummySig2:
        def __init__(self):
            self.values = []

        def emit(self, *args):
            self.values.append(args if len(args) > 1 else args[0])

    # Replace signals with dummy collectors
    finished = DummySig2()
    logs = DummySig2()
    progresses = DummySig2()
    w.finished_sig = finished
    w.log_sig = logs
    w.progress_sig = progresses

    # Run synchronously; ensure Qt event loop exists
    w.run()

    # Signals were emitted and output created
    assert progresses.values and any(p >= 50 for p, _ in progresses.values)
    assert finished.values and "Done." in finished.values[0]
    assert out.exists()
