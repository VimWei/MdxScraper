from __future__ import annotations

from pathlib import Path

import tomllib

from mdxscraper.config.config_manager import ConfigManager


def write_toml(path: Path, data: dict) -> None:
    import tomli_w

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(tomli_w.dumps(data))


def test_save_and_backup_and_list_and_apply_scheme(tmp_path: Path) -> None:
    project_root = tmp_path
    data_dir = project_root / "data"
    configs_dir = data_dir / "configs"

    # Provide a default config in installed package location shadow via symlink/real file
    pkg_defaults = project_root / "src" / "mdxscraper" / "config"
    pkg_defaults.mkdir(parents=True, exist_ok=True)
    default_cfg = {"basic": {"input_file": "", "dictionary_file": "", "output_file": ""}}
    write_toml(pkg_defaults / "default_config.toml", default_cfg)

    cm = ConfigManager(project_root)
    cfg = cm.load()
    # Initially will write config_latest.toml
    cm.save()
    assert (configs_dir / "config_latest.toml").is_file()

    # Create a scheme and list it
    scheme_path = configs_dir / "my_scheme.toml"
    write_toml(scheme_path, {"basic": {"input_file": "a.txt", "dictionary_file": "d.mdx", "output_file": "o.html"}})
    schemes = cm.list_schemes()
    assert "my_scheme.toml" in schemes

    # Apply scheme should load and then save to latest
    cm.apply_scheme("my_scheme.toml")
    latest = tomllib.loads((configs_dir / "config_latest.toml").read_text(encoding="utf-8"))
    assert latest["basic"]["input_file"] == "a.txt"

    # Backup should create .bak file
    backup_path = cm.backup()
    # Path.suffix would return only ".bak"; assert on the full name
    assert str(backup_path).endswith(".toml.bak")
    assert backup_path.is_file()


def test_validate_and_path_helpers(tmp_path: Path) -> None:
    project_root = tmp_path
    pkg_defaults = project_root / "src" / "mdxscraper" / "config"
    pkg_defaults.mkdir(parents=True, exist_ok=True)
    write_toml(
        pkg_defaults / "default_config.toml",
        {"basic": {"input_file": "", "dictionary_file": "", "output_file": ""}},
    )

    cm = ConfigManager(project_root)
    cm.load()

    # Set relative paths via helpers (also covers _to_external_path)
    in_file = project_root / "data" / "input" / "words.txt"
    dict_file = project_root / "data" / "mdict" / "Dict.mdx"
    out_file = project_root / "data" / "output" / "out.html"
    in_file.parent.mkdir(parents=True, exist_ok=True)
    dict_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    in_file.write_text("hello", encoding="utf-8")
    dict_file.write_text("mdx", encoding="utf-8")

    cm.set_input_file(str(in_file))
    cm.set_dictionary_file(str(dict_file))
    cm.set_output_file(str(out_file))

    # Validate should succeed and ensure output dir exists
    result = cm.validate()
    assert result.is_valid, f"unexpected errors: {result.errors}"

    # _resolve_path returns absolute path, relative preserved by getters
    assert cm.get_input_file().endswith("data/input/words.txt")
    assert cm._resolve_path(cm.get_input_file()).is_absolute()


