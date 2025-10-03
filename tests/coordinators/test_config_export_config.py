from __future__ import annotations

from pathlib import Path

import pytest


class StubLog:
    def __init__(self):
        self.messages = []

    def appendLog(self, m: str):
        self.messages.append(m)


class StubPresetCoord:
    def __init__(self, base: Path, to_snapshot_pdf: bool = False, to_snapshot_css: bool = False):
        self._to_pdf = to_snapshot_pdf
        self._to_css = to_snapshot_css
        self.reloaded = False
        self.selected = []
        self.autosaved = False
        self._base = base

    def autosave_untitled_if_needed(self, mw):
        self.autosaved = True

    def reload_presets(self, mw, auto_select_default: bool = False):
        self.reloaded = True

    def create_snapshots_if_needed_on_export(self, mw):
        return ("PDF_SNAP" if self._to_pdf else "", "CSS_SNAP" if self._to_css else "")

    def select_label_and_load(self, mw, kind: str, label: str):
        self.selected.append((kind, label))

    # Paths used in logging messages
    def user_pdf_dir(self) -> Path:
        p = self._base / "data" / "configs" / "pdf"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def user_css_dir(self) -> Path:
        p = self._base / "data" / "configs" / "css"
        p.mkdir(parents=True, exist_ok=True)
        return p


class StubSettings:
    def __init__(self, tmp: Path, valid: bool = True):
        self._tmp = tmp
        self._valid = valid

    class _Result:
        def __init__(self, ok: bool):
            self.is_valid = ok
            self.errors = ["e1", "e2"] if not ok else []

    def validate(self):
        return self._Result(self._valid)

    def get_config_dict(self):
        return {"pdf": {"preset_label": "P"}, "css": {"preset_label": "C"}}

    def to_relative(self, p: str | Path):
        return str(p)

    # sync helpers used by coordinator
    def get_basic_config(self):
        return object()

    def get_image_config(self):
        return object()

    def get_advanced_config(self):
        return object()

    def get_pdf_config(self):
        return object()

    def get_css_config(self):
        return object()

    def update_basic_config(self, *_):
        pass

    def update_image_config(self, *_):
        pass

    def update_advanced_config(self, *_):
        pass

    def update_pdf_config(self, *_):
        pass

    def update_css_config(self, *_):
        pass


class MW:
    def __init__(self, tmp: Path, settings, presets):
        self.tab_basic = type("T", (), {"get_config": lambda self: object()})()
        self.tab_image = type("T", (), {"get_config": lambda self: object()})()
        self.tab_advanced = type("T", (), {"get_config": lambda self: object()})()
        self.tab_pdf = type(
            "T", (), {"get_config": lambda self: object(), "show_dirty": lambda self, flag: None}
        )()
        self.tab_css = type(
            "T", (), {"get_config": lambda self: object(), "show_dirty": lambda self, flag: None}
        )()
        self.settings = settings
        self.presets = presets
        self.preset_coordinator = presets
        self.log_panel = StubLog()
        self.project_root = tmp
        self.pdf_dirty = True
        self.css_dirty = True


def test_export_config_success_with_snapshots(tmp_path: Path):
    from mdxscraper.coordinators.config_coordinator import ConfigCoordinator

    settings = StubSettings(tmp_path, valid=True)
    presets = StubPresetCoord(tmp_path, to_snapshot_pdf=True, to_snapshot_css=True)
    cc = ConfigCoordinator(settings, presets)

    mw = MW(tmp_path, settings, presets)
    out = tmp_path / "out.toml"

    cc.export_config(mw, out)

    # file created
    assert out.exists()
    # logs include exported message and frozen messages
    joined = "\n".join(mw.log_panel.messages)
    assert "Exported config" in joined
    assert "Frozen PDF Untitled" in joined and "Frozen CSS Untitled" in joined
    # preset selections after snapshot
    assert ("pdf", "PDF_SNAP") in presets.selected
    assert ("css", "CSS_SNAP") in presets.selected


def test_export_config_logs_validation_issues(tmp_path: Path):
    from mdxscraper.coordinators.config_coordinator import ConfigCoordinator

    settings = StubSettings(tmp_path, valid=False)
    presets = StubPresetCoord(tmp_path)
    cc = ConfigCoordinator(settings, presets)
    mw = MW(tmp_path, settings, presets)
    out = tmp_path / "out.toml"

    cc.export_config(mw, out)

    joined = "\n".join(mw.log_panel.messages)
    assert "Config validation issues" in joined


def test_export_config_handles_io_errors(monkeypatch, tmp_path: Path):
    from mdxscraper.coordinators.config_coordinator import ConfigCoordinator

    settings = StubSettings(tmp_path, valid=True)
    presets = StubPresetCoord(tmp_path)
    cc = ConfigCoordinator(settings, presets)
    mw = MW(tmp_path, settings, presets)
    out = tmp_path / "dir" / "no_perm" / "out.toml"

    # Simulate failure by making open raise
    def fake_open(*args, **kwargs):
        raise OSError("disk full")

    import builtins

    monkeypatch.setattr(builtins, "open", fake_open)

    cc.export_config(mw, out)

    joined = "\n".join(mw.log_panel.messages)
    assert "Failed to export config" in joined
