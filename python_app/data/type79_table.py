"""
Type 79 U-band support dimensional table (D-94).

Source status:
- `79.pdf` is vector-outline based; text extraction returns no usable text.
- 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
  visual inspection.

The drawing calls out `U-BAND SEE M-55`. Type 79 now uses `data.m55_table` for
the component-level lookup; this file remains as the original D-94 transcription
reference for regression checks.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import STEEL_DENSITY_KG_PER_MM3, normalize_fractional_size


_RAW_TYPE79_ROWS = [
    ('5"', 144.6, 330, 70.7, 105, 6, 95, 25, 9, 125, 72.3),
    ('6"', 171.6, 360, 84.2, 105, 6, 110, 25, 9, 125, 85.8),
    ('8"', 222.0, 410, 109.6, 105, 6, 135, 25, 9, 125, 111.0),
    ('10"', 276.0, 575, 136.6, 120, 9, 180, 40, 12, 150, 138.0),
    ('12"', 327.0, 620, 162.0, 120, 9, 210, 40, 12, 150, 163.5),
    ('14"', 359.0, 700, 177.8, 160, 12, 230, 50, 16, 200, 179.5),
    ('16"', 409.6, 750, 203.2, 160, 12, 260, 50, 16, 200, 204.8),
    ('18"', 460.6, 850, 228.6, 250, 16, 300, 65, 22, 300, 230.3),
    ('20"', 511.0, 900, 254.0, 250, 16, 320, 65, 22, 300, 255.5),
    ('22"', 562.0, 950, 279.4, 250, 16, 350, 65, 22, 300, 281.0),
    ('24"', 613.0, 1000, 304.8, 250, 16, 370, 65, 22, 300, 306.5),
]

TYPE79_TABLE = {}
for _line_size, _a, _b, _c, _d, _f, _h, _j, _t, _e, _r in _RAW_TYPE79_ROWS:
    _key = normalize_fractional_size(_line_size)
    TYPE79_TABLE[_key] = {
        "line_size": _key,
        "A": _a,
        "B": _b,
        "C": _c,
        "D": _d,
        "F": _f,
        "H": _h,
        "J": _j,
        "T": _t,
        "E": _e,
        "R": _r,
        "component_ref": "M-55",
        "transcription_status": "ai_visual_transcribed",
    }


def estimate_type79_uband_weight_kg(row: dict) -> float:
    return round(row["B"] * row["E"] * row["T"] * STEEL_DENSITY_KG_PER_MM3, 2)


def get_type79_data(line_size) -> dict | None:
    row = TYPE79_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = estimate_type79_uband_weight_kg(item)
    item["weight_status"] = "estimated_from_B_E_T_blank_until_M55_exists"
    return item


def list_type79_sizes() -> list[str]:
    return list(TYPE79_TABLE.keys())
