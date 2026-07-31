"""Strict parser for Chang Chun owner-standard designations."""

from __future__ import annotations

import re

from companies.eko.parser import parse_inch


KNOWN_CODES = (
    "FS15",
    "PU5",
    "S1",
    "S2",
    "SS2",
    "SS5",
    "SS6",
    "SS13",
    "SS17",
    "SS20",
)


def detect_code(fullstring: str) -> tuple[str, str] | None:
    first = str(fullstring or "").strip().split("-", 1)[0].upper()
    for code in sorted(KNOWN_CODES, key=len, reverse=True):
        if first.startswith(code):
            suffix = first[len(code):]
            if suffix.isalpha() or not suffix:
                return code, suffix
    return None


def _dimension(token: str, suffix: str) -> int | None:
    match = re.fullmatch(rf"(\d+){suffix}", token.upper())
    return int(match.group(1)) if match else None


def parse_designation(fullstring: str) -> dict:
    raw = str(fullstring or "").strip()
    detected = detect_code(raw)
    if detected is None:
        raise ValueError("不是 DES-M15172 已建檔代號")
    code, suffix = detected
    parts = [part.strip() for part in raw.split("-") if part.strip()]
    parsed = {
        "raw": raw,
        "code": code,
        "suffix": suffix,
        "variant": "",
        "fix": "",
        "serial": None,
        "pipe": None,
        "H": None,
        "H1": None,
        "L": None,
    }

    suffix_rules = {
        "FS15": (2, "HV", "ABEW"),
        "PU5": (1, "", "BEW"),
        "S1": (0, "", ""),
        "S2": (1, "ADGS", ""),
        "SS2": (1, "", "BE"),
        "SS5": (1, "", "BEW"),
        "SS6": (1, "", "BEW"),
        "SS13": (2, "SV", "BW"),
        "SS17": (1, "", "BW"),
        "SS20": (1, "", "BW"),
    }
    suffix_len, variants, fixes = suffix_rules[code]
    if len(suffix) != suffix_len:
        raise ValueError(
            f"{code}: 型式／固定方式字母數不符圖面格式"
        )
    if variants:
        parsed["variant"] = suffix[0]
        if parsed["variant"] not in variants:
            raise ValueError(
                f"{code}: 型式 {parsed['variant']!r} 應為 {list(variants)}"
            )
    if fixes:
        parsed["fix"] = suffix[-1]
        if parsed["fix"] not in fixes:
            raise ValueError(
                f"{code}: 固定方式 {parsed['fix']!r} 應為 {list(fixes)}"
            )

    bare_numbers: list[int] = []
    for token in parts[1:]:
        value = _dimension(token, "H1")
        if value is not None:
            if parsed["H1"] is not None:
                raise ValueError(f"{code}: H1 重複")
            parsed["H1"] = value
            continue
        value = _dimension(token, "H")
        if value is not None:
            if parsed["H"] is not None:
                raise ValueError(f"{code}: H 重複")
            parsed["H"] = value
            continue
        value = _dimension(token, "L")
        if value is not None:
            if parsed["L"] is not None:
                raise ValueError(f"{code}: L 重複")
            parsed["L"] = value
            continue
        if token.endswith('"'):
            if parsed["pipe"] is not None:
                raise ValueError(f"{code}: 管徑重複")
            parsed["pipe"] = parse_inch(token)
            if parsed["pipe"] is None:
                raise ValueError(f"{code}: 無法解析管徑 {token!r}")
            continue
        if code == "PU5" and token.upper().endswith("B"):
            # Project support lists use nominal-bore notation such as
            # ``1.1/2B`` where the owner drawing prints ``1.1/2"``.
            # The trailing B is a size unit, not another fixing suffix.
            if parsed["pipe"] is not None:
                raise ValueError(f"{code}: 管徑重複")
            parsed["pipe"] = parse_inch(token[:-1])
            if parsed["pipe"] is None:
                raise ValueError(f"{code}: 無法解析NB管徑 {token!r}")
            parsed.setdefault("designation_aliases", []).append(
                {
                    "raw": token,
                    "normalized": f'{parsed["pipe"]:g}"',
                    "basis": "專案清單以B表示nominal bore",
                }
            )
            continue
        if token.isdigit():
            bare_numbers.append(int(token))
            continue
        raise ValueError(f"{code}: 未識別段落 {token!r}")

    if code in {"FS15", "SS2", "SS5", "SS6"}:
        if len(bare_numbers) != 1:
            raise ValueError(f"{code}: 必須且只能指定一個序號")
        parsed["serial"] = bare_numbers[0]
    elif bare_numbers:
        raise ValueError(f"{code}: 圖面格式不接受裸數字段落")

    required = {
        "FS15": ("serial", "H"),
        "PU5": ("pipe", "L"),
        "S1": ("pipe", "H"),
        "S2": ("pipe",),
        "SS2": ("serial", "L"),
        "SS5": ("serial", "H", "L"),
        "SS6": ("serial", "H", "L"),
        "SS13": ("L",),
        "SS17": ("H", "L"),
        "SS20": ("H", "L"),
    }[code]
    missing = [field for field in required if parsed[field] is None]
    if missing:
        raise ValueError(f"{code}: 缺少必要欄位 {', '.join(missing)}")
    return parsed
