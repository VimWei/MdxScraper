from __future__ import annotations

from pathlib import Path
from typing import Iterator, Tuple, Dict, Optional, Any


class PresetsService:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def iter_presets(self, kind: str) -> Iterator[Tuple[str, Path]]:
        if kind == 'pdf':
            built_in = self.project_root / 'src' / 'mdxscraper' / 'config' / 'pdf_options'
            user_dir = self.project_root / 'data' / 'configs' / 'pdf'
        else:
            built_in = self.project_root / 'src' / 'mdxscraper' / 'config' / 'css_styles'
            user_dir = self.project_root / 'data' / 'configs' / 'css'

        if built_in.exists():
            for p in sorted(built_in.glob('*.toml')):
                yield f"{p.stem} [built-in]", p
        if user_dir.exists():
            for p in sorted(user_dir.glob('*.toml')):
                yield f"{p.stem}", p

    def load_preset_text(self, path: Path) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def save_preset_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    # Utilities
    def get_user_dir(self, kind: str) -> Path:
        if kind == 'pdf':
            return self.project_root / 'data' / 'configs' / 'pdf'
        else:
            return self.project_root / 'data' / 'configs' / 'css'

    def create_untitled_snapshot(self, kind: str, text: str) -> Path:
        """Create a timestamped snapshot from current Untitled content and return the file path."""
        from datetime import datetime
        user_dir = self.get_user_dir(kind).resolve()
        user_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d-%H%M')
        snap_path = user_dir / f'Untitled-{stamp}.toml'
        self.save_preset_text(snap_path, text or '')
        return snap_path

    # Parsing helpers
    def parse_pdf_preset(self, text: str) -> Dict[str, Any]:
        text = (text or '').strip()
        if not text:
            return {}
        try:
            import tomllib as _tomllib
            data = _tomllib.loads(text)
            pdf = data.get('pdf', {}) if isinstance(data, dict) else {}
            return pdf
        except Exception:
            return {}

    def parse_css_preset(self, text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        text = (text or '').strip()
        if not text:
            return None, None, None
        try:
            import tomllib as _tomllib
            data = _tomllib.loads(text)
            style = data.get('style', {}) if isinstance(data, dict) else {}
            return (
                style.get('h1_style'),
                style.get('scrap_style'),
                style.get('additional_styles'),
            )
        except Exception:
            return None, None, None


