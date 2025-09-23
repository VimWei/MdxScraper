#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import tomllib

current_script_path = Path(__file__).resolve().parent
src_dir = current_script_path / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from mdxscraper.config.config_manager import ConfigManager
from mdxscraper.core.converter import mdx2html, mdx2pdf, mdx2jpg
from mdxscraper.core.enums import InvalidAction


def human_readable_duration(seconds: float) -> str:
    time_delta = timedelta(seconds=seconds)
    hours, remainder = divmod(time_delta.total_seconds(), 3600)
    minutes, int_seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(hours) * 3600 - int(minutes) * 60 - int(int_seconds)) * 1000)
    parts = []
    if int(hours) > 0:
        parts.append(f"{int(hours):02d} hours")
    if int(minutes) > 0 or int(hours) > 0:
        parts.append(f"{int(minutes):02d} minutes")
    parts.append(f"{int(int_seconds):02d}.{milliseconds:03d} seconds")
    return ''.join(parts)

if __name__ == '__main__':

    print(f'Welcome to MdxScraper：extract specific words from an MDX dictionary and generate HTML, PDF, or JPG with ease！\n')
    start_time = time.time()

    # Prefer TOML config (default from src/mdxscraper/config/default_config.toml,
    # user config from data/configs/config_latest.toml)
    cm = ConfigManager(current_script_path)
    try:
        config = cm.load()
        # Ensure required defaults populated from bundled default_config if missing
        def _ensure_defaults(conf: dict) -> dict:
            with open(cm.default_config_path, 'rb') as f:
                defaults = tomllib.load(f)
            for sect, key in [("input","file"),("dictionary","file"),("output","file")]:
                conf.setdefault(sect, {})
                if not conf[sect].get(key):
                    conf[sect][key] = defaults.get(sect, {}).get(key)
            conf.setdefault("output", {}).setdefault("with_toc", defaults.get("output", {}).get("with_toc", True))
            return conf
        config = _ensure_defaults(config or {})
        cm._config = config
        cm.save()
        # Validate config before resolving paths
        validation = cm.validate()
        if not validation.is_valid:
            print("Configuration is invalid:\n" + "\n".join(f"- {e}" for e in validation.errors))
            print("Please fix the configuration in data/configs/config_latest.toml or via GUI (uv run mdxscraper).")
            sys.exit(1)
        # resolve paths
        input_file_value = config.get('input', {}).get('file')
        dict_file_value = config.get('dictionary', {}).get('file')
        output_file_value = config.get('output', {}).get('file')
        if not input_file_value or not dict_file_value or not output_file_value:
            print("Missing required configuration fields: ensure input.file, dictionary.file, and output.file are set.")
            sys.exit(1)
        input_file = cm._resolve_path(input_file_value)
        mdx_file = cm._resolve_path(dict_file_value)
        output_path = cm._resolve_path(output_file_value)
        with_toc = bool(config.get('output', {}).get('with_toc', True))
        invalid_action_str = str(config.get('processing', {}).get('invalid_action', 'collect_warning')).lower()
        invalid_action = {
            'exit': InvalidAction.Exit,
            'collect': InvalidAction.Collect,
            'outputwarning': InvalidAction.OutputWarning,
            'collect_warning': InvalidAction.OutputWarning,
            'collect_outputwarning': InvalidAction.Collect_OutputWarning,
            'collect_output_warning': InvalidAction.Collect_OutputWarning,
        }.get(invalid_action_str, InvalidAction.Collect)
        # Derive output paths from configured output file
        output_dir = output_path.parent
        output_name = output_path.name
    except Exception:
        # If config invalid, raise to surface the issue
        raise

    currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / (currentTime + '_' + output_name)
    invalid_words_file = output_dir / (currentTime + '_' + 'invalid_words.txt')

    # backup input file beside outputs
    backup_input_file = output_dir / (currentTime + '_backup_' + Path(input_file).name)
    shutil.copy(str(input_file), str(backup_input_file))

    output_type = Path(output_file).suffix[1:]
    found, not_found = {
        'html': mdx2html,
        'pdf': lambda a,b,c,d: mdx2pdf(a,b,c, {}, d),
        'jpg': mdx2jpg,
    }[output_type](mdx_file, input_file, output_file, invalid_action)

    # Calculate success rate
    total = found + not_found
    if total > 0:
        success_rate = (found / total) * 100
        success_msg = f"Success: {found} words extracted from {Path(mdx_file).name}. Success rate: {success_rate:.1f}%. Refer to {output_file}.\n"
    else:
        success_msg = f"Success: {found} words extracted from {Path(mdx_file).name}. Success rate: 0%.\n"
    
    if found > 0 or invalid_action in [InvalidAction.OutputWarning, InvalidAction.Collect_OutputWarning]:
        print(success_msg)
    else:
        print(success_msg)
    
    if not_found > 0:
        print(f"Failure: {not_found} words not in {Path(mdx_file).name}. Check {invalid_words_file}.\n")
    else:
        print(f"Failure: {not_found} words not in {Path(mdx_file).name}.\n")

    end_time = time.time()
    duration = human_readable_duration(end_time - start_time)
    print(f"The entire process took a total of {duration}.\n")
