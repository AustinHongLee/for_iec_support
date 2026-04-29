"""
Shared component fallback rules.

This module is the single place for engineering estimates used when a component
table is missing or not weight-ready.  Component data files may expose source
rows; Type calculators should not invent their own fallback weights.
"""
from __future__ import annotations

from data.component_size_utils import (
    estimate_round_bar_weight_kg,
    normalize_fractional_size,
    size_to_float,
)

CLAMP_WEIGHT_MULTIPLIER = {
    "M-4": 1.00,
    "M-5": 1.08,
    "M-6": 1.18,
    "M-7": 1.28,
    "M-8": 1.45,
    "M-9": 1.70,
    "M-10": 2.00,
}

HEAVY_HEX_NUT_WEIGHT_KG = {
    '3/8"': 0.03,
    '1/2"': 0.05,
    '5/8"': 0.08,
    '3/4"': 0.12,
    '7/8"': 0.18,
    '1"': 0.25,
    '1 1/4"': 0.45,
    '1 1/2"': 0.75,
    '1 3/4"': 1.10,
    '2"': 1.50,
    '2 1/4"': 2.00,
    '2 1/2"': 2.60,
}

COMPONENT_RULE_NOTES = {
    "clamp": "Clamp weight fallback is centralized in core.component_rules and remains estimated.",
    "rod": "Rod fallback uses round-bar geometry and remains estimated.",
    "eye_nut": "Eye nut fallback uses rod-size geometry and remains estimated.",
    "m28": "M-28 fallback uses rod-size geometry and remains estimated.",
}


def estimate_clamp_weight(line_size, *, component_id: str = "M-4", multiplier: float | None = None) -> float:
    """
    Estimate clamp set weight.

    M-4 has a source-visible row but no unit-weight source column; M-5/M-6/M-7
    still use unreviewed multipliers until their own weight columns are found.
    """
    size = size_to_float(line_size) or 0.0
    normalized = normalize_fractional_size(line_size)
    multiplier = multiplier if multiplier is not None else CLAMP_WEIGHT_MULTIPLIER.get(component_id, 1.0)

    base = None
    try:
        from data.m4_table import build_m4_item

        base_item = build_m4_item(normalized)
        if base_item:
            base = base_item.get("estimated_set_weight_kg") or base_item.get("set_weight_kg")
    except Exception:
        base = None

    if not base:
        base = max(0.8, size * 0.55)
    return round(float(base) * multiplier, 2)


def component_or_estimated_clamp_weight(item: dict | None, line_size, *, component_id: str = "M-4") -> float:
    """Use a verified source weight when available; otherwise use centralized clamp estimate."""
    if item and item.get("weight_ready") and item.get("set_weight_kg") is not None:
        return float(item["set_weight_kg"])
    return estimate_clamp_weight(line_size, component_id=component_id)


def estimate_rod_weight(rod_size, length_mm: int, *, min_weight: float = 0.1) -> float:
    return round(max(min_weight, estimate_round_bar_weight_kg(rod_size, length_mm)), 2)


def estimate_eye_nut_weight(rod_size) -> float:
    return estimate_rod_weight(rod_size, 100, min_weight=0.15)


def estimate_heavy_hex_nut_weight(rod_size) -> float:
    return HEAVY_HEX_NUT_WEIGHT_KG.get(normalize_fractional_size(rod_size), 0.20)


def estimate_m28_weight(rod_size) -> float:
    return estimate_rod_weight(rod_size, 200, min_weight=0.3)


def estimate_missing_component_weight(component_id: str, *, line_size: float | None = None, rod_size: str = '1/2"') -> float:
    if component_id == "M-31":
        return 0.50
    if component_id == "M-3":
        return round(0.35 + (line_size or 1.0) * 0.12, 2)
    if component_id == "M-33":
        return round(max(0.80, (line_size or 2.0) * 0.22), 2)
    if component_id in ("M-8", "M-9", "M-10"):
        return estimate_clamp_weight(line_size or 0, component_id=component_id)
    return estimate_rod_weight(rod_size, 100)
