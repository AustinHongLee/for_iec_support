"""
M-54 Strap dimensional lookup table.

Source status:
- `M-54-STRAP.pdf` is vector-outline based; text extraction returns no usable
  table.
- 2026-04-21 Codex rendered the vector PDF and transcribed the visible drawing
  table by AI visual inspection.

The drawing gives `PUBS3-{line_size}B-{fig_no}` as the designation pattern and
states material as carbon steel.  Unit weight is calculated from the developed
strap blank (`B x C x T`) with Fig.2 bolt holes subtracted.
"""
from __future__ import annotations

import math
from copy import deepcopy

from .component_size_utils import normalize_fractional_size


STEEL_DENSITY_KG_PER_MM3 = 7.85e-6
M54_MATERIAL = "Carbon Steel"
M54_FIG2_HOLE_DIA_MM = 11
M54_FIG2_HOLE_COUNT = 2

M54_COMPONENT_INFO = {
    "component_id": "M-54",
    "name_en": "STRAP",
    "category": "component",
    "pdf_file": "M-54-STRAP.pdf",
    "drawing_file": "M-54M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": True,
    "transcription_status": "ai_visual_transcribed",
}

_RAW_M54_ROWS = [
    ("PUBS3-3/4B", '3/4"', 30.0, 110, 6, 32, 13.4, 15.0, 20),
    ("PUBS3-1B", '1"', 36.6, 120, 6, 32, 16.7, 18.3, 20),
    ("PUBS3-1 1/2B", '1 1/2"', 51.6, 140, 6, 50, 24.2, 25.8, 20),
    ("PUBS3-2B", '2"', 63.6, 150, 6, 50, 30.2, 31.8, 20),
    ("PUBS3-2 1/2B", '2 1/2"', 76.0, 220, 9, 65, 36.5, 38.0, 40),
    ("PUBS3-3B", '3"', 92.0, 230, 9, 65, 44.5, 46.0, 40),
    ("PUBS3-3 1/2B", '3 1/2"', 105.0, 240, 9, 65, 50.8, 52.5, 40),
    ("PUBS3-4B", '4"', 117.6, 255, 9, 65, 57.2, 58.8, 40),
]


def _calc_weight_kg(row: dict, *, fig_no: int = 2) -> float:
    blank_area_mm2 = row["B"] * row["C"]
    if fig_no == 2:
        hole_area_mm2 = M54_FIG2_HOLE_COUNT * math.pi * (M54_FIG2_HOLE_DIA_MM / 2) ** 2
    else:
        hole_area_mm2 = 0
    volume_mm3 = max(blank_area_mm2 - hole_area_mm2, 0) * row["T"]
    return round(volume_mm3 * STEEL_DENSITY_KG_PER_MM3, 2)


M54_TABLE = {}
for _base_type, _line_size, _a, _b, _t, _c, _h, _r, _d in _RAW_M54_ROWS:
    _key = normalize_fractional_size(_line_size)
    M54_TABLE[_key] = {
        **M54_COMPONENT_INFO,
        "type": _base_type,
        "designation_base": _base_type,
        "line_size": _key,
        "dimensions_mm": {
            "A": _a,
            "B": _b,
            "T": _t,
            "C": _c,
            "H": _h,
            "R": _r,
            "D": _d,
        },
        "material": M54_MATERIAL,
        "fig_no_supported": [1, 2],
        "fig2_hole_dia_mm": M54_FIG2_HOLE_DIA_MM,
        "fig2_hole_count": M54_FIG2_HOLE_COUNT,
        "weight_status": "calculated_from_B_C_T_minus_fig2_holes",
        "source_note": "AI visual transcription from rendered vector PDF; reviewer spot-check recommended.",
    }


def get_m54_component() -> dict:
    component = deepcopy(M54_COMPONENT_INFO)
    component.update(
        {
            "row_count": len(M54_TABLE),
            "line_size_range": '3/4"~4"',
            "material": M54_MATERIAL,
            "notes": [
                "Dimension table transcribed by AI visual inspection after vector-PDF rasterization.",
                "Designation pattern from drawing note: PUBS3-{line_size}B-{fig_no}.",
                'Fig.2 includes 2-phi11 bolt holes for 3/8" expansion bolt.',
            ],
        }
    )
    return component


def get_m54_by_line_size(line_size, *, fig_no: int = 2) -> dict | None:
    row = M54_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    if fig_no not in row["fig_no_supported"]:
        return None
    item = deepcopy(row)
    item["fig_no"] = fig_no
    item["designation"] = f'{item["designation_base"]}-{fig_no}'
    item["unit_weight_kg"] = _calc_weight_kg(item["dimensions_mm"], fig_no=fig_no)
    return item


def build_m54_item(line_size, *, fig_no: int = 2) -> dict | None:
    item = get_m54_by_line_size(line_size, fig_no=fig_no)
    if not item:
        return None
    dims = item["dimensions_mm"]
    item.update(
        {
            "name": "STRAP",
            "category": "鋼板類",
            "spec": (
                f'{item["designation"]}, {item["line_size"]}, '
                f'B={dims["B"]} C={dims["C"]} T={dims["T"]}'
            ),
        }
    )
    return item
