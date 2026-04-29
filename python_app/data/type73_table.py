"""
Type 73 查表資料 — 資料來源: configs/type_73.json
Bridge module (2026-04-29): interface 不變，底層讀 JSON。
"""
from __future__ import annotations
import math
from copy import deepcopy
import json as _json, os as _os

from .component_size_utils import (
    STEEL_DENSITY_KG_PER_MM3 as _density_const,
    estimate_round_bar_weight_kg,
    normalize_fractional_size,
    size_to_float,
)

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_73.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# scalars
SPRING_MATERIAL = _DATA["SPRING_MATERIAL"]
STEEL_DENSITY_KG_PER_MM3 = _DATA["STEEL_DENSITY_KG_PER_MM3"]
TYPE73_MATERIAL = _DATA["TYPE73_MATERIAL"]

# private raw rows (referenced by functions)
_RAW_TYPE73_ROWS = [tuple(row) for row in _DATA["_RAW_TYPE73_ROWS"]]

# TYPE73_TABLE / TYPE73_SPRING_TABLE (dict, string key preserved as-is — pipe size strings)
TYPE73_TABLE = _DATA["TYPE73_TABLE"]
TYPE73_SPRING_TABLE = _DATA["TYPE73_SPRING_TABLE"]

# ── 原始查詢函式（interface 不變）────────────────────────

def _parse_bar_size(bar_size: str) -> tuple[float, float]:
    width, thickness = bar_size.upper().split("X", 1)
    return float(width), float(thickness)


def _estimate_flat_bar_weight_kg(length_mm: float, bar_size: str) -> float:
    width_mm, thickness_mm = _parse_bar_size(bar_size)
    return round(length_mm * width_mm * thickness_mm * STEEL_DENSITY_KG_PER_MM3, 2)


def _estimate_spring_weight_kg(spring: dict) -> float:
    wire = spring["wire_dia_mm"]
    mean_dia = spring["coil_id_mm"] + wire
    coils = spring["active_coils"] + spring["inactive_coils"]
    wire_length = math.pi * mean_dia * coils
    wire_area = math.pi * wire**2 / 4
    return round(wire_length * wire_area * STEEL_DENSITY_KG_PER_MM3, 3)


TYPE73_TABLE = {}
for (
    _line_size,
    _a,
    _b,
    _c,
    _e,
    _r,
    _bolt_dia,
    _g,
    _h,
    _spring_mark,
    _bar_size,
) in _RAW_TYPE73_ROWS:
    _key = normalize_fractional_size(_line_size)
    _designation = "PUBS2-" + _key.replace('"', "B")
    TYPE73_TABLE[_key] = {
        "line_size": _key,
        "A": _a,
        "B": _b,
        "C": _c,
        "E": _e,
        "R": _r,
        "bolt_dia": _bolt_dia,
        "G": _g,
        "H": _h,
        "spring_mark": _spring_mark,
        "steel_bar_size": _bar_size,
        "strap_designation": _designation,
        "material": TYPE73_MATERIAL,
        "bolt_arrangement": "double_bolt" if _e is not None else "single_bolt",
        "transcription_status": "ai_visual_transcribed",
    }


def get_type73_data(line_size) -> dict | None:
    row = TYPE73_TABLE.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None


def get_type73_spring_data(mark: str) -> dict | None:
    row = TYPE73_SPRING_TABLE.get(str(mark).upper())
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = _estimate_spring_weight_kg(item)
    return item


def get_type73_bolt_count(line_size) -> int:
    size = size_to_float(line_size) or 0
    return 4 if size >= 6 else 2


def build_type73_strap_item(line_size) -> dict | None:
    row = get_type73_data(line_size)
    if not row:
        return None
    return {
        "name": "STRAP",
        "spec": (
            f'{row["strap_designation"]}, A={row["A"]} B={row["B"]} C={row["C"]}, '
            f'bar={row["steel_bar_size"]}, D={row["bolt_dia"]}'
        ),
        "material": TYPE73_MATERIAL,
        "category": "鋼板類",
        "unit_weight_kg": _estimate_flat_bar_weight_kg(row["A"], row["steel_bar_size"]),
        "weight_status": "estimated_from_A_times_bar_size",
    }


def estimate_type73_stud_weight_kg(row: dict) -> float:
    return estimate_round_bar_weight_kg(row["bolt_dia"], row["G"])


def estimate_type73_gusset_weight_kg(row: dict) -> float:
    if row["E"] is None:
        return 0.0
    _, thickness = _parse_bar_size(row["steel_bar_size"])
    triangle_area = row["E"] * row["H"] / 2
    return round(triangle_area * thickness * STEEL_DENSITY_KG_PER_MM3, 2)


def list_type73_sizes() -> list[str]:
    return list(TYPE73_TABLE.keys())

