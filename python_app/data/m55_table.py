"""
M-55 U-Band dimensional lookup table.

Source status:
- `M-55-U-BAND.pdf` is vector-outline based; text extraction returns no usable
  table.
- 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
  visual inspection.

The drawing provides dimensions for `PUBD1-{line_size}B` and material as carbon
steel. It does not provide source unit-weight, so weight is calculated as a
developed blank estimate (`B x E x T`) for continuity with Type 79.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import STEEL_DENSITY_KG_PER_MM3, normalize_fractional_size


M55_MATERIAL = "Carbon Steel"

M55_COMPONENT_INFO = {
    "component_id": "M-55",
    "name_en": "U-BAND",
    "category": "component",
    "pdf_file": "M-55-U-BAND.pdf",
    "drawing_file": "M-55M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "ai_visual_transcribed",
}


_RAW_M55_ROWS = [
    ("PUBD1-5B", '5"', 144.6, 330, 70.7, 105, 6, 95, 25, 9, 125, 72.3),
    ("PUBD1-6B", '6"', 171.6, 360, 84.2, 105, 6, 110, 25, 9, 125, 85.8),
    ("PUBD1-8B", '8"', 222.0, 410, 109.6, 105, 6, 135, 25, 9, 125, 111.0),
    ("PUBD1-10B", '10"', 276.0, 575, 136.6, 120, 9, 180, 40, 12, 150, 138.0),
    ("PUBD1-12B", '12"', 327.0, 620, 162.0, 120, 9, 210, 40, 12, 150, 163.5),
    ("PUBD1-14B", '14"', 359.0, 700, 177.8, 160, 12, 230, 50, 16, 200, 179.5),
    ("PUBD1-16B", '16"', 409.6, 750, 203.2, 160, 12, 260, 50, 16, 200, 204.8),
    ("PUBD1-18B", '18"', 460.6, 850, 228.6, 250, 16, 300, 65, 22, 300, 230.3),
    ("PUBD1-20B", '20"', 511.0, 900, 254.0, 250, 16, 320, 65, 22, 300, 255.5),
    ("PUBD1-22B", '22"', 562.0, 950, 279.4, 250, 16, 350, 65, 22, 300, 281.0),
    ("PUBD1-24B", '24"', 613.0, 1000, 304.8, 250, 16, 370, 65, 22, 300, 306.5),
]


def estimate_m55_weight_kg(row: dict) -> float:
    """Estimate from B x E x T blank because source drawing has no weight column."""
    dims = row["dimensions_mm"] if "dimensions_mm" in row else row
    return round(dims["B"] * dims["E"] * dims["T"] * STEEL_DENSITY_KG_PER_MM3, 2)


M55_TABLE = {}
for _designation, _line_size, _a, _b, _c, _d, _f, _h, _j, _t, _e, _r in _RAW_M55_ROWS:
    _key = normalize_fractional_size(_line_size)
    M55_TABLE[_key] = {
        **M55_COMPONENT_INFO,
        "designation": _designation,
        "line_size": _key,
        "dimensions_mm": {
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
        },
        "material": M55_MATERIAL,
        "weight_status": "estimated_from_B_E_T_blank_no_source_weight_column",
        "source_note": "AI visual transcription from rendered vector PDF; reviewer spot-check recommended.",
    }


def get_m55_component() -> dict:
    component = deepcopy(M55_COMPONENT_INFO)
    component.update(
        {
            "row_count": len(M55_TABLE),
            "line_size_range": '5"~24"',
            "material": M55_MATERIAL,
            "notes": [
                "Dimension table transcribed by AI visual inspection after vector-PDF rasterization.",
                "Designation pattern from drawing note: PUBD1-{line_size}B.",
                "No source unit-weight column; weight is a B x E x T blank estimate.",
            ],
        }
    )
    return component


def get_m55_by_line_size(line_size) -> dict | None:
    row = M55_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = estimate_m55_weight_kg(item)
    return item


def build_m55_item(line_size) -> dict | None:
    item = get_m55_by_line_size(line_size)
    if not item:
        return None
    dims = item["dimensions_mm"]
    return {
        "component_id": "M-55",
        "name": "U-BAND",
        "spec": (
            f'{item["designation"]}, A={dims["A"]} B={dims["B"]} C={dims["C"]} '
            f'D={dims["D"]} E={dims["E"]} T={dims["T"]}'
        ),
        "material": item["material"],
        "quantity": 1,
        "unit": "PC",
        "unit_weight_kg": item["unit_weight_kg"],
        "category": "鋼板類",
        "remark": "SEE M-55; weight estimated from B x E x T blank (no source unit-weight column)",
        "source": item,
    }


def list_m55_sizes() -> list[str]:
    return list(M55_TABLE.keys())
