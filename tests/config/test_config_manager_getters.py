from __future__ import annotations

from pathlib import Path

from mdxscraper.config.config_manager import ConfigManager


def test_get_dictionary_and_output_files(tmp_path: Path) -> None:
    # Seed defaults
    defaults_dir = tmp_path / "src" / "mdxscraper" / "config"
    defaults_dir.mkdir(parents=True, exist_ok=True)
    (defaults_dir / "default_config.toml").write_text(
        "[basic]\ninput_file=''\ndictionary_file=''\noutput_file=''\n", encoding="utf-8"
    )

    cm = ConfigManager(tmp_path)
    cm.load()

    dict_path = tmp_path / "data" / "mdict" / "D.mdx"
    out_path = tmp_path / "data" / "output" / "out.html"
    dict_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    dict_path.write_text("x", encoding="utf-8")

    cm.set_dictionary_file(str(dict_path))
    cm.set_output_file(str(out_path))

    # getters return external (posix-ish) strings
    got_dict = cm.get_dictionary_file()
    got_out = cm.get_output_file()
    assert isinstance(got_dict, str) and got_dict.replace("\\", "/").endswith("data/mdict/D.mdx")
    assert isinstance(got_out, str) and got_out.replace("\\", "/").endswith("data/output/out.html")
