"""
Type 77 saddle support dimensional table (D-92).

Source status:
- `77.pdf` is vector-outline based; text extraction returns no usable text.
- 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
  visual inspection.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import STEEL_DENSITY_KG_PER_MM3, normalize_fractional_size


_RAW_TYPE77_ROWS = [
    ('26"', 200, 35, 600, 12, 650),
    ('28"', 200, 35, 600, 12, 650),
    ('30"', 250, 40, 650, 12, 700),
    ('32"', 250, 40, 650, 12, 700),
    ('34"', 250, 45, 750, 12, 750),
    ('36"', 250, 45, 750, 12, 750),
    ('40"', 300, 50, 850, 16, 800),
]

TYPE77_TABLE = {}
for _line_size, _a, _b, _c, _t, _h in _RAW_TYPE77_ROWS:
    _key = normalize_fractional_size(_line_size)
    TYPE77_TABLE[_key] = {
        "line_size": _key,
        "A": _a,
        "B": _b,
        "C": _c,
        "T": _t,
        "H": _h,
        "material_note": "identical or similar to pipe material",
        "transcription_status": "ai_visual_transcribed",
    }


def estimate_type77_saddle_weight_kg(row: dict) -> float:
    # Conservative bounding rectangle estimate for the side-plate envelope plus bottom strip.
    side_plate_area = row["C"] * row["H"]
    bottom_strip_area = row["A"] * row["B"]
    return round((side_plate_area + bottom_strip_area) * row["T"] * STEEL_DENSITY_KG_PER_MM3, 2)


def get_type77_data(line_size) -> dict | None:
    row = TYPE77_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = estimate_type77_saddle_weight_kg(item)
    item["weight_status"] = "estimated_from_saddle_bounding_geometry"
    return item


def list_type77_sizes() -> list[str]:
    return list(TYPE77_TABLE.keys())
