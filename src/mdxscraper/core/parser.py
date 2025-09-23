from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import openpyxl
from chardet import detect


def open_encoding_file(name: str, default_encoding: str = "utf-8"):
    with open(name, "rb") as f:
        raw_data = f.read()
    if raw_data.count(b"\n") < 1:
        encoding = default_encoding
    else:
        detection_result = detect(raw_data)
        encoding = detection_result["encoding"]
        confidence = detection_result.get("confidence", 0)
        if confidence < 0.5:
            encoding = default_encoding
    return open(name, encoding=encoding, errors="ignore")


def get_words(name: str) -> List[Dict[str, Any]]:
    ext = Path(name).suffix.lower()
    return {
        ".xls": get_words_from_xls,
        ".xlsx": get_words_from_xls,
        ".json": get_words_from_json,
        ".txt": get_words_from_txt,
        ".md": get_words_from_txt,
    }[ext](name)


def get_words_from_json(name: str):
    return json.load(open_encoding_file(name))


def get_words_from_txt(name: str):
    result = []
    for line in open_encoding_file(name).readlines():
        line = line.strip()
        if len(line) == 0:
            continue
        if line.startswith("#"):
            result.append({"name": line.strip("#"), "words": []})
        else:
            if len(result) == 0:
                currentTime = datetime.now().strftime("%Y%m%d-%H%M%S")
                result.append({"name": currentTime, "words": []})
            result[-1]["words"].append(line)
    return result


def get_words_from_xls(name: str):
    wb = openpyxl.load_workbook(name, read_only=True)
    result = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        words = [row[0].value for row in ws.iter_rows(min_row=ws.min_row, max_row=ws.max_row, max_col=1)]
        words = list(filter(lambda x: x is not None and len(x) > 0, words))
        result.append({"name": sheet_name, "words": words})
    return result


