"""Source-locked dispatcher for Chang Chun DES-M15172 supports."""

from __future__ import annotations

from core.models import AnalysisResult

from .calculators import CALCULATORS
from .config_loader import load_config
from .parser import KNOWN_CODES, detect_code, parse_designation


def analyze(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    try:
        parsed = parse_designation(fullstring)
    except ValueError as exc:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"長春 DES-M15172: {exc}"
        return result
    config = load_config(parsed["code"])
    if config is None:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"長春 DES-M15172: 找不到 {parsed['code']} 設定檔"
        return result
    return CALCULATORS[parsed["code"]](parsed, config, overrides or {})


def can_handle(fullstring: str) -> bool:
    return detect_code(fullstring) is not None


def supported_codes() -> list[str]:
    return sorted(KNOWN_CODES)
