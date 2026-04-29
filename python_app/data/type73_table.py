"""
Type 73 spring strap support dimensional table (D-88/D-88A).

Source status:
- `73.pdf` is vector-outline based; text extraction returns no usable text.
- 2026-04-21 Codex rendered both pages and transcribed the visible tables by
  AI visual inspection.

The drawing references M-53 strap data and has a separate spring-coil table.
Unit weights calculated here are estimates from geometry, not source drawing
unit-weight values.
"""
from __future__ import annotations

import math
from copy import deepcopy

from .component_size_utils import (
    STEEL_DENSITY_KG_PER_MM3,
    estimate_round_bar_weight_kg,
    normalize_fractional_size,
    size_to_float,
)


TYPE73_MATERIAL = "A283-C"
SPRING_MATERIAL = "ASTM A229 Class 1"

_RAW_TYPE73_ROWS = [
    ('1"', 186, 127, 76, None, 17, '1/4"', 60, 35, "SPR02", "65X6"),
    ('1 1/2"', 202, 143, 76, None, 25, '1/4"', 60, 35, "SPR02", "65X6"),
    ('2"', 244, 171, 92, None, 30, '3/8"', 70, 40, "SPR03", "75X6"),
    ('3"', 272, 197, 92, None, 44, '3/8"', 70, 40, "SPR03", "75X6"),
    ('4"', 298, 222, 92, None, 57, '3/8"', 70, 40, "SPR03", "75X6"),
    ('6"', 396, 305, 114, 71, 84, '1/2"', 90, 55, "SPR04", "125X9"),
    ('8"', 448, 356, 114, 97, 110, '1/2"', 90, 55, "SPR04", "125X9"),
    ('10"', 502, 406, 114, 124, 137, '3/4"', 130, 70, "SPR05", "125X9"),
    ('12"', 552, 464, 114, 143, 162, '3/4"', 130, 70, "SPR05", "150X12"),
    ('14"', 584, 495, 114, 165, 178, '3/4"', 130, 70, "SPR05", "150X12"),
    ('16"', 634, 546, 114, 191, 203, '3/4"', 130, 70, "SPR05", "150X12"),
    ('18"', 686, 597, 114, 216, 229, '3/4"', 130, 70, "SPR05", "150X12"),
    ('20"', 736, 648, 114, 241, 254, '7/8"', 140, 85, "SPR06", "150X12"),
    ('24"', 838, 749, 114, 292, 305, '7/8"', 140, 85, "SPR06", "150X12"),
]

TYPE73_SPRING_TABLE = {
    "SPR02": {
        "mark": "SPR02",
        "wire_dia_mm": 2,
        "coil_id_mm": 15,
        "active_coils": 5,
        "inactive_coils": 2,
        "spring_constant_kg_per_mm": 0.7,
        "free_length_mm": 25,
        "material": SPRING_MATERIAL,
    },
    "SPR03": {
        "mark": "SPR03",
        "wire_dia_mm": 3,
        "coil_id_mm": 19,
        "active_coils": 4,
        "inactive_coils": 2,
        "spring_constant_kg_per_mm": 1.9,
        "free_length_mm": 30,
        "material": SPRING_MATERIAL,
    },
    "SPR04": {
        "mark": "SPR04",
        "wire_dia_mm": 4,
        "coil_id_mm": 24,
        "active_coils": 4,
        "inactive_coils": 2,
        "spring_constant_kg_per_mm": 2.9,
        "free_length_mm": 40,
        "material": SPRING_MATERIAL,
    },
    "SPR05": {
        "mark": "SPR05",
        "wire_dia_mm": 5,
        "coil_id_mm": 34,
        "active_coils": 3,
        "inactive_coils": 2,
        "spring_constant_kg_per_mm": 3.5,
        "free_length_mm": 55,
        "material": SPRING_MATERIAL,
    },
    "SPR06": {
        "mark": "SPR06",
        "wire_dia_mm": 6,
        "coil_id_mm": 39,
        "active_coils": 3,
        "inactive_coils": 2,
        "spring_constant_kg_per_mm": 4.7,
        "free_length_mm": 65,
        "material": SPRING_MATERIAL,
    },
}


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
