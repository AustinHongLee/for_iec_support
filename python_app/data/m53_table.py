"""
M-53 Strap PUBS2 dimensional lookup table.

Source status:
- The PDF is vector-outline based, so text extraction returns no usable table.
- 2026-04-21 Codex rendered the vector PDF to bitmap and transcribed the visible
  drawing table by AI visual inspection.
- This table is dimension lookup-ready, but not weight-ready because the drawing
  does not provide a direct unit-weight table.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import normalize_fractional_size


M53_COMPONENT_INFO = {
    "component_id": "M-53",
    "name_en": "STRAP PUBS2",
    "category": "component",
    "pdf_file": "M-53-STRAP PUBS2.pdf",
    "drawing_file": "M-53M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "ai_visual_transcribed",
}

M53_MATERIAL = "A283-C"

_RAW_M53_ROWS = [
    ("PUBS2-1B", '1"', 186, 127, 76, None, 17, '1/4"', 65, 6),
    ("PUBS2-1 1/2B", '1 1/2"', 202, 143, 76, None, 25, '1/4"', 65, 6),
    ("PUBS2-2B", '2"', 244, 171, 92, None, 30, '3/8"', 75, 6),
    ("PUBS2-3B", '3"', 272, 197, 92, None, 44, '3/8"', 75, 6),
    ("PUBS2-4B", '4"', 298, 222, 92, None, 57, '3/8"', 75, 6),
    ("PUBS2-6B", '6"', 396, 305, 114, 71, 84, '1/2"', 125, 9),
    ("PUBS2-8B", '8"', 448, 356, 114, 97, 110, '1/2"', 125, 9),
    ("PUBS2-10B", '10"', 502, 406, 114, 124, 137, '3/4"', 125, 9),
    ("PUBS2-12B", '12"', 552, 464, 114, 143, 162, '3/4"', 150, 12),
    ("PUBS2-14B", '14"', 584, 495, 114, 165, 178, '3/4"', 150, 12),
    ("PUBS2-16B", '16"', 634, 546, 114, 191, 203, '3/4"', 150, 12),
    ("PUBS2-18B", '18"', 686, 597, 114, 216, 229, '3/4"', 150, 12),
    ("PUBS2-20B", '20"', 736, 648, 114, 241, 254, '7/8"', 150, 12),
    ("PUBS2-24B", '24"', 838, 749, 114, 292, 305, '7/8"', 150, 12),
]

M53_TABLE = {}
for (
    _designation,
    _line_size,
    _a,
    _b,
    _c,
    _e,
    _r,
    _d,
    _f,
    _t,
) in _RAW_M53_ROWS:
    _key = normalize_fractional_size(_line_size)
    M53_TABLE[_key] = {
        **M53_COMPONENT_INFO,
        "designation": _designation,
        "type": _designation.replace("PUBS2-", ""),
        "line_size": _key,
        "dimensions_mm": {
            "A": _a,
            "B": _b,
            "C": _c,
            "E": _e,
            "R": _r,
            "F": _f,
            "T": _t,
        },
        "bolt_diameter_d": _d,
        "bar_size": f"{_f}x{_t}",
        "material": M53_MATERIAL,
        "bolt_arrangement": "double_bolt" if _e is not None else "single_bolt",
        "unit_weight_kg": None,
        "weight_status": "not_provided_by_pdf",
        "source_note": "AI visual transcription from rendered vector PDF; dimensions require reviewer spot-check.",
    }


def get_m53_component() -> dict:
    component = deepcopy(M53_COMPONENT_INFO)
    component.update(
        {
            "row_count": len(M53_TABLE),
            "line_size_range": '1"~24"',
            "material": M53_MATERIAL,
            "notes": [
                "Dimension table transcribed by AI visual inspection after vector-PDF rasterization.",
                'Drawing notes: 4" and smaller use single-bolt arrangement; 6" and larger use double-bolt arrangement.',
                "Lookup-ready for dimensions; not weight-ready.",
            ],
        }
    )
    return component


def get_m53_by_line_size(line_size) -> dict | None:
    row = M53_TABLE.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None


def build_m53_item(line_size) -> dict | None:
    row = get_m53_by_line_size(line_size)
    if not row:
        return None
    dims = row["dimensions_mm"]
    return {
        **row,
        "name": "STRAP PUBS2",
        "category": "鋼板類",
        "spec": (
            f'{row["designation"]}, A={dims["A"]} B={dims["B"]} C={dims["C"]}, '
            f'bar={row["bar_size"]}, D={row["bolt_diameter_d"]}'
        ),
    }
