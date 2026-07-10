"""Project-scoped calculation rules for PENETRATION HOLE opening reinforcement."""

from __future__ import annotations

import re

from .parser import get_lookup_value, parse_pipe_size


def parse_insulation(insulation) -> tuple[float, str]:
    """Return insulation thickness in mm and the source label used by MTO."""
    raw = str(insulation or "").strip()
    if not raw or raw in {"0", "0.0", "None"}:
        return 0.0, ""
    match = re.search(r"(\d+(?:\.\d+)?)", raw)
    if not match:
        raise ValueError(f"無法辨識保溫厚度: {insulation!r}")
    value = float(match.group(1))
    if value < 0:
        raise ValueError(f"保溫厚度不可為負值: {insulation!r}")
    return value, raw


def display_pipe_size(nominal_size) -> str:
    raw = str(nominal_size or "").strip().replace('"', "")
    return raw or "?"


def build_item_code(nominal_size, insulation) -> str:
    """Match the REV.01 SUPPORT MTO item_code.1 convention."""
    pipe_size = display_pipe_size(nominal_size)
    try:
        _, insulation_label = parse_insulation(insulation)
    except ValueError:
        insulation_label = str(insulation or "").strip()
    code = f'OPEN-{pipe_size}"'
    return f"{code}-{insulation_label}" if insulation_label else code
