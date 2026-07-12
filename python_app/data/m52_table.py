"""
M-52 Spring Wedge dimensional lookup table.

Source status:
- The PDF is vector-outline based, so text extraction returns no usable table.
- 2026-04-21 Codex rendered the vector PDF to bitmap and transcribed the visible
  drawing table by AI visual inspection.
- This table is dimension lookup-ready, but not weight-ready because the drawing
  does not provide a complete developed-shape/weight formula.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import normalize_fractional_size, size_to_float


M52_COMPONENT_INFO = {
    "component_id": "M-52",
    "name_en": "SPRING WEDGE",
    "category": "component",
    "pdf_file": "M-52-SPRING WEDGE.pdf",
    "drawing_file": "M-52M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "ai_visual_transcribed",
}

M52_MATERIALS = {
    "wedge_pipe": "A53-B",
    "stud_bolt": "A193 GR.B-7",
    "spring": "A229",
}

_RAW_M52_ROWS = [
    ("SPRW-2B", '2"', '2"-SCH.80', 154, 295, '1/2"', 102, 57, 14, 40, 14, 6),
    ("SPRW-3B", '3"', '2"-SCH.80', 154, 295, '1/2"', 102, 57, 14, 40, 14, 6),
    ("SPRW-4B", '4"', '2"-SCH.80', 154, 295, '1/2"', 102, 57, 14, 40, 14, 6),
    ("SPRW-6B", '6"', '2"-SCH.80', 154, 345, '3/4"', 127, 57, 21, 45, 21, 10),
    ("SPRW-8B", '8"', '2"-SCH.80', 154, 345, '3/4"', 127, 57, 21, 45, 21, 10),
    ("SPRW-10B", '10"', '3"-SCH.80', 154, 470, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-12B", '12"', '3"-SCH.80', 154, 470, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-14B", '14"', '3"-SCH.80', 154, 470, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-16B", '16"', '3"-SCH.80', 154, 505, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-18B", '18"', '3"-SCH.80', 154, 505, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-20B", '20"', '3"-SCH.80', 154, 505, '3/4"', 127, 70, 21, 45, 21, 10),
    ("SPRW-24B", '24"', '3"-SCH.80', 229, 610, '1"', 190, 95, 27, 65, 27, 10),
]

M52_SPRING_DATA_GROUPS = [
    {
        "line_size_min": 2.0,
        "line_size_max": 4.0,
        "line_size_range": '2"-4"',
        "wire_dia_mm": 5,
        "inside_dia_mm": 14,
        "active_coils": 6,
        "inactive_coils": 2,
        "free_length_mm": 65,
        "spring_constant_kg_per_mm": 15,
        "install_compression_mm": 12,
    },
    {
        "line_size_min": 6.0,
        "line_size_max": 20.0,
        "line_size_range": '6"-20"',
        "wire_dia_mm": 8,
        "inside_dia_mm": 22,
        "active_coils": 5,
        "inactive_coils": 2,
        "free_length_mm": 80,
        "spring_constant_kg_per_mm": 30,
        "install_compression_mm": 12,
    },
    {
        "line_size_min": 24.0,
        "line_size_max": 24.0,
        "line_size_range": '24"',
        "wire_dia_mm": 10,
        "inside_dia_mm": 28,
        "active_coils": 4,
        "inactive_coils": 2,
        "free_length_mm": 110,
        "spring_constant_kg_per_mm": 45,
        "install_compression_mm": 25,
    },
]


def _spring_data_for_line_size(line_size) -> dict | None:
    size = size_to_float(line_size)
    if size is None:
        return None
    for group in M52_SPRING_DATA_GROUPS:
        if group["line_size_min"] <= size <= group["line_size_max"]:
            return deepcopy(group)
    return None


M52_TABLE = {}
for (
    _designation,
    _line_size,
    _pipe_size,
    _f,
    _h,
    _j,
    _k,
    _l,
    _m,
    _n,
    _p,
    _q,
) in _RAW_M52_ROWS:
    _key = normalize_fractional_size(_line_size)
    M52_TABLE[_key] = {
        **M52_COMPONENT_INFO,
        "designation": _designation,
        "type": _designation,
        "line_size": _key,
        "pipe_size": _pipe_size,
        "dimensions_mm": {
            "F": _f,
            "H": _h,
            "K": _k,
            "L": _l,
            "M": _m,
            "N": _n,
            "P": _p,
            "Q": _q,
        },
        "thread_size_j": _j,
        "spring_data": _spring_data_for_line_size(_key),
        "materials": deepcopy(M52_MATERIALS),
        "unit_weight_kg": None,
        "weight_status": "not_provided_by_pdf",
        "source_note": "AI visual transcription from rendered vector PDF; dimensions require reviewer spot-check.",
    }


def get_m52_component() -> dict:
    component = deepcopy(M52_COMPONENT_INFO)
    component.update(
        {
            "row_count": len(M52_TABLE),
            "line_size_range": '2"~24"',
            "materials": deepcopy(M52_MATERIALS),
            "notes": [
                "Dimension table transcribed by AI visual inspection after vector-PDF rasterization.",
                "Lookup-ready for dimensions and spring data; not weight-ready.",
                "No stable Type-level caller is wired to M-52 in the current repo yet.",
            ],
        }
    )
    return component


def get_m52_by_line_size(line_size) -> dict | None:
    row = M52_TABLE.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None


def get_m52_spring_data(line_size) -> dict | None:
    return _spring_data_for_line_size(line_size)


def build_m52_item(line_size) -> dict | None:
    row = get_m52_by_line_size(line_size)
    if not row:
        return None
    dims = row["dimensions_mm"]
    return {
        **row,
        "name": "SPRING WEDGE",
        "category": "彈簧類",
        "spec": (
            f'{row["designation"]}, pipe {row["pipe_size"]}, '
            f'F={dims["F"]} H={dims["H"]} J={row["thread_size_j"]}'
        ),
    }
