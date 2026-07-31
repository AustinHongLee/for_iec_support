"""Dispatcher for source-locked Chung Wei special supports."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from core.models import AnalysisResult

from .m26_alias import calculate as calculate_m26_alias
from .platform_opening import calculate as calculate_platform_opening
from .sps001 import calculate as calculate_sps001


_CONFIG_DIR = Path(__file__).with_name("configs")


@lru_cache(maxsize=None)
def _config(name: str) -> dict:
    with (_CONFIG_DIR / f"{name}.json").open("r", encoding="utf-8") as stream:
        return json.load(stream)


def can_handle(fullstring: str) -> bool:
    text = str(fullstring or "")
    return bool(
        re.match(r"^\s*SPS-001(?:-|$)", text, re.I)
        or re.match(r"^\s*UB1-", text, re.I)
        or re.match(r"^\s*OPEN-", text, re.I)
    )


def _dimension(token: str, suffix: str) -> int:
    text = token.strip().upper()
    if text.isdigit():
        return int(text) * 100
    match = re.fullmatch(rf"(\d+){suffix}", text)
    if match:
        return int(match.group(1))
    raise ValueError(
        f"SPS-001: {suffix}應填100mm倍數數字（例10）或明確mm（例1000{suffix}）"
    )


def _parse(fullstring: str) -> dict:
    parts = [part.strip().upper() for part in str(fullstring).split("-")]
    if len(parts) != 6 or parts[:2] != ["SPS", "001"]:
        raise ValueError("SPS-001格式應為 SPS-001-{H100/C125/H125}-{H/100}-{L/100}-{B/W}")
    member = parts[2]
    fix = parts[5]
    if member not in {"H100", "C125", "H125"}:
        raise ValueError("SPS-001構件應為 H100、C125 或 H125")
    if fix not in {"B", "W"}:
        raise ValueError("SPS-001固定方式應為 B 或 W")
    return {
        "raw": fullstring,
        "code": "SPS-001",
        "member": member,
        "H": _dimension(parts[3], "H"),
        "L": _dimension(parts[4], "L"),
        "fix": fix,
    }


def analyze(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    if re.match(r"^\s*UB1-", str(fullstring or ""), re.I):
        return calculate_m26_alias(
            fullstring,
            _config("m26-alias"),
            overrides or {},
        )
    if re.match(r"^\s*OPEN-", str(fullstring or ""), re.I):
        return calculate_platform_opening(
            fullstring,
            _config("platform-opening"),
            overrides or {},
        )
    try:
        parsed = _parse(fullstring)
    except ValueError as exc:
        result = AnalysisResult(fullstring=fullstring)
        result.error = str(exc)
        return result
    return calculate_sps001(parsed, _config("sps-001"), overrides or {})


def supported_codes() -> list[str]:
    return ["OPEN", "SPS-001", "UB1"]
