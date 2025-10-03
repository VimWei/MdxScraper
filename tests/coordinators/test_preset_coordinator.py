"""Tests for PresetCoordinator"""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from mdxscraper.coordinators.preset_coordinator import PresetCoordinator
from mdxscraper.services.presets_service import PresetsService
from mdxscraper.services.settings_service import SettingsService


class FakeCombo:
    def __init__(self):
        self._items = []
        self._data = []
        self._current = -1

    def clear(self):
        self._items.clear()
        self._data.clear()
        self._current = -1

    def addItem(self, text, userData=None):
        self._items.append(text)
        self._data.append(userData)

    def count(self):
        return len(self._items)

    def itemText(self, i):
        return self._items[i]

    def itemData(self, i):
        return self._data[i]

    def setCurrentIndex(self, i):
        self._current = i

    def currentIndex(self):
        return self._current


class FakeEditor:
    def __init__(self, text=""):
        self._text = text

    def setPlainText(self, text):
        self._text = text

    def toPlainText(self):
        return self._text


class FakePresets:
    def __init__(self):
        self.store = {}

    def iter_presets(self, kind):
        items = []
        if kind == "pdf":
            items.append(("Default PDF", Path("/pdf/default.toml")))
            for k in list(self.store.keys()):
                p = Path(k)
                if p.name == "Untitled.toml" and ("pdf" in p.parts or p.parent.name == "pdf"):
                    items.append(("Untitled", p))
        if kind == "css":
            items.append(("Original CSS", Path("/css/original.toml")))
            for k in list(self.store.keys()):
                p = Path(k)
                if p.name == "Untitled.toml" and ("css" in p.parts or p.parent.name == "css"):
                    items.append(("Untitled", p))
        return items

    def load_preset_text(self, path: Path) -> str:
        return self.store.get(str(path), "text")

    def save_preset_text(self, out: Path, text: str):
        self.store[str(out)] = text

    def create_untitled_snapshot(self, kind: str, text: str) -> Path:
        p = Path(f"/snapshots/{kind}/Untitled-001.toml")
        self.store[str(p)] = text
        return p


class FakeSettings:
    def __init__(self):
        self.s = {}

    def get(self, key, default=None):
        return self.s.get(key, default)

    def set(self, key, value):
        self.s[key] = value


class FakeLog:
    def __init__(self):
        self.logs = []

    def appendLog(self, msg):
        self.logs.append(msg)


class FakeMW:
    def __init__(self, root: Path):
        self.project_root = root
        self.tab_pdf = SimpleNamespace(
            pdf_combo=FakeCombo(), pdf_editor=FakeEditor(), show_dirty=lambda x: None
        )
        self.tab_css = SimpleNamespace(
            css_combo=FakeCombo(), css_editor=FakeEditor(), show_dirty=lambda x: None
        )
        self._updating_pdf_editor = False
        self._updating_css_editor = False
        self.pdf_dirty = False
        self.css_dirty = False
        self.last_pdf_label = None
        self.last_css_label = None
        self.log_panel = FakeLog()


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture
def mock_settings():
    """Create mock SettingsService"""
    settings = Mock(spec=SettingsService)
    settings.cm = Mock()
    return settings


@pytest.fixture
def mock_presets():
    """Create mock PresetsService"""
    presets = Mock(spec=PresetsService)
    return presets


@pytest.fixture
def preset_coordinator(mock_settings, mock_presets):
    """Create PresetCoordinator instance"""
    return PresetCoordinator(mock_presets, mock_settings)


def test_preset_coordinator_initialization(preset_coordinator, mock_settings, mock_presets):
    """Test PresetCoordinator initialization"""
    assert preset_coordinator.presets == mock_presets
    assert preset_coordinator.settings == mock_settings


def test_on_pdf_preset_changed_valid(preset_coordinator, mock_presets, mock_settings):
    """Test PDF preset change with valid selection"""
    mock_mw = Mock()
    mock_mw.tab_pdf = Mock()
    mock_mw.tab_pdf.pdf_combo = Mock()
    mock_mw.tab_pdf.pdf_combo.currentIndex.return_value = 0
    mock_mw.tab_pdf.pdf_combo.itemData.return_value = "data/configs/pdf/test_preset.toml"
    mock_mw.tab_pdf.pdf_editor = Mock()
    mock_presets.load_preset_text.return_value = "pdf_preset_content"
    mock_settings.set.return_value = None
    preset_coordinator.on_pdf_preset_changed(mock_mw, "test_preset")
    mock_presets.load_preset_text.assert_called_once_with(Path("data/configs/pdf/test_preset.toml"))
    mock_mw.tab_pdf.pdf_editor.setPlainText.assert_called_once_with("pdf_preset_content")
    mock_settings.set.assert_called_once_with("pdf.preset_label", "test_preset")


def test_on_pdf_preset_changed_none(preset_coordinator, mock_presets, mock_settings):
    mock_mw = Mock()
    mock_mw.tab_pdf = Mock()
    mock_mw.tab_pdf.pdf_combo = Mock()
    mock_mw.tab_pdf.pdf_combo.currentIndex.return_value = -1
    mock_mw.tab_pdf.pdf_editor = Mock()
    preset_coordinator.on_pdf_preset_changed(mock_mw, "")


def test_on_css_preset_changed_valid(preset_coordinator, mock_presets, mock_settings):
    mock_mw = Mock()
    mock_mw.tab_css = Mock()
    mock_mw.tab_css.css_combo = Mock()
    mock_mw.tab_css.css_combo.currentIndex.return_value = 0
    mock_mw.tab_css.css_combo.itemData.return_value = "data/configs/css/test_css_preset.toml"
    mock_mw.tab_css.css_editor = Mock()
    mock_presets.load_preset_text.return_value = "css_preset_content"
    mock_settings.set.return_value = None
    preset_coordinator.on_css_preset_changed(mock_mw, "test_css_preset")
    mock_presets.load_preset_text.assert_called_once_with(
        Path("data/configs/css/test_css_preset.toml")
    )
    mock_mw.tab_css.css_editor.setPlainText.assert_called_once_with("css_preset_content")
    mock_settings.set.assert_called_once_with("css.preset_label", "test_css_preset")


def test_on_css_preset_changed_none(preset_coordinator, mock_presets, mock_settings):
    mock_mw = Mock()
    mock_mw.tab_css = Mock()
    mock_mw.tab_css.css_combo = Mock()
    mock_mw.tab_css.css_combo.currentIndex.return_value = 0
    mock_mw.tab_css.css_combo.itemData.return_value = "data/configs/css/test_css_preset.toml"
    mock_mw.tab_css.css_editor = Mock()
    preset_coordinator.on_css_preset_changed(mock_mw, "")


# Minimal fake-UI based tests below


def test_reload_presets_and_select_defaults(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    pc.reload_presets(mw, auto_select_default=True)
    assert mw.tab_pdf.pdf_combo.count() in (1, 2)
    assert mw.tab_css.css_combo.count() in (1, 2)


def test_select_label_and_load_found(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    pc.reload_presets(mw, auto_select_default=False)
    pc.select_label_and_load(mw, "pdf", "Default PDF")
    assert mw.tab_pdf.pdf_combo.currentIndex() == 0


def test_enter_untitled_state_sets_dirty(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    pc.enter_untitled_state(mw, "pdf", clear_editor=True)
    pc.enter_untitled_state(mw, "css", clear_editor=True)
    assert mw.pdf_dirty is True and mw.css_dirty is True


def test_text_changed_marks_dirty(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    pc.on_pdf_text_changed(mw)
    pc.on_css_text_changed(mw)
    assert mw.pdf_dirty is True and mw.css_dirty is True


def test_autosave_untitled_if_needed(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    mw.pdf_dirty = True
    mw.css_dirty = True
    mw.tab_pdf.pdf_editor.setPlainText("PDF")
    mw.tab_css.css_editor.setPlainText("CSS")
    pc.autosave_untitled_if_needed(mw)
    assert mw.pdf_dirty is False and mw.css_dirty is False


def test_create_snapshots_on_export(tmp_path):
    pc = PresetCoordinator(FakePresets(), FakeSettings())
    mw = FakeMW(tmp_path)
    mw.pdf_dirty = True
    mw.css_dirty = True
    mw.tab_pdf.pdf_editor.setPlainText("PDF")
    mw.tab_css.css_editor.setPlainText("CSS")
    new_pdf, new_css = pc.create_snapshots_if_needed_on_export(mw)
    assert new_pdf and new_css
