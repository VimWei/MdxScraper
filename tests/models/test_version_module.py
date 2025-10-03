import builtins
import io
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from mdxscraper import version as version_module


def _fake_pyproject(tmp_path: Path, content: str) -> Path:
    py = tmp_path / "pyproject.toml"
    py.write_text(content, encoding="utf-8")
    return py


def test_get_version_uses_uv_when_available(monkeypatch, tmp_path):
    class FakeCompleted:
        def __init__(self, out: str):
            self.stdout = out

    fake_run = MagicMock(return_value=FakeCompleted("5.2.3\n"))
    monkeypatch.setattr(version_module.subprocess, "run", fake_run)
    v = version_module.get_version()
    assert v == "5.2.3"
    fake_run.assert_called()


def test_get_version_falls_back_to_pyproject(monkeypatch, tmp_path):
    def raise_called(*a, **kw):
        raise FileNotFoundError()

    monkeypatch.setattr(version_module.subprocess, "run", raise_called)

    expected = 'version = "4.1.0"\n'

    real_open = builtins.open

    def fake_open(file, mode="r", *args, **kwargs):
        try:
            path_str = str(file).lower()
        except Exception:
            path_str = ""
        if "pyproject.toml" in path_str and "r" in mode:
            return io.StringIO(expected)
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    v = version_module._get_version_from_pyproject()
    assert v == "4.1.0"


def test_get_version_info_parses_semver(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "3.2.1")
    assert version_module.get_version_info() == (3, 2, 1)


def test_get_version_info_handles_prerelease(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "3.2.1-a1")
    assert version_module.get_version_info() == (3, 2, 1)


def test_is_prerelease_true(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "1.0.0rc1")
    assert version_module.is_prerelease() is True


def test_is_prerelease_false(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "1.0.0")
    assert version_module.is_prerelease() is False


def test_get_version_display(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "2.0.0")
    assert version_module.get_version_display() == "v2.0.0"


def test_get_full_version_info(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "7.8.9")
    info = version_module.get_full_version_info()
    assert info["version"] == "7.8.9"
    assert info["version_info"] == (7, 8, 9)
    assert info["display"] == "v7.8.9"
    assert info["is_prerelease"] is False
    assert info["major"] == 7 and info["minor"] == 8 and info["patch"] == 9


def test_compare_version(monkeypatch):
    monkeypatch.setattr(version_module, "get_version", lambda: "5.0.0")
    monkeypatch.setattr(version_module, "get_version_info", lambda: (5, 0, 0))
    assert version_module.compare_version("4.9.9") == 1
    assert version_module.compare_version("5.0.0") == 0
    assert version_module.compare_version("5.1.0") == -1


def test_compare_version_invalid(monkeypatch):
    monkeypatch.setattr(version_module, "get_version_info", lambda: (1, 0, 0))
    assert version_module.compare_version("invalid") == 0


def test_get_app_title(monkeypatch):
    monkeypatch.setattr(version_module, "get_version_display", lambda: "v9.9.9")
    assert version_module.get_app_title() == "MdxScraper v9.9.9"


def test_get_about_text_contains_fields(monkeypatch):
    monkeypatch.setattr(
        version_module,
        "get_full_version_info",
        lambda: {
            "version": "1.2.3",
            "version_info": (1, 2, 3),
            "display": "v1.2.3",
            "is_prerelease": False,
        },
    )
    text = version_module.get_about_text()
    assert "MdxScraper v1.2.3" in text
    assert "Version: 1.2.3" in text
    assert "Pre-release: No" in text
