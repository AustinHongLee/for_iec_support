"""
M-4 Pipe Clamp TYPE-A dimensional lookup table.

Source status:
- `M-4-PIPE CLAMP A.pdf` is vector-outline based; text extraction returns no
  usable table.
- 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
  visual inspection.

Raw table values are kept here per the component-table maintenance rule. Shared
normalization/build logic lives in `m_clamp_common.py`.
"""
from __future__ import annotations

from .m_clamp_common import build_clamp_item, build_clamp_table, get_clamp_by_line_size, get_clamp_by_type


M4_COMPONENT_INFO = {
    "component_id": "M-4",
    "name_en": "PIPE CLAMP A",
    "category": "component",
    "pdf_file": "M-4-PIPE CLAMP A.pdf",
    "drawing_file": "M-4M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "weight_ready": False,
    "transcription_status": "ai_visual_transcribed",
}


_RAW_M4_ROWS = [
    ("PCL-A-1/2B", '1/2"', 220, 200, 25, 11, 39, 25, '5/16"', "3 x 25", 39, 0.35),
    ("PCL-A-3/4B", '3/4"', 220, 200, 29, 11, 42, 29, '5/16"', "3 x 25", 42, 0.40),
    ("PCL-A-1B", '1"', 220, 200, 29, 11, 48, 35, '5/16"', "3 x 25", 42, 0.50),
    ("PCL-A-1 1/4B", '1 1/4"', 220, 200, 37, 11, 50, 37, '5/16"', "3 x 25", 50, 0.60),
    ("PCL-A-1 1/2B", '1 1/2"', 365, 325, 40, 13, 55, 41, '5/16"', "3 x 25", 56, 0.70),
    ("PCL-A-2B", '2"', 475, 420, 54, 13, 70, 54, '1/2"', "6 x 25", 70, 0.95),
    ("PCL-A-2 1/2B", '2 1/2"', 475, 420, 64, 16, 83, 67, '1/2"', "6 x 25", 79, 1.15),
    ("PCL-A-3B", '3"', 475, 420, 71, 16, 90, 75, '1/2"', "6 x 25", 87, 1.45),
    ("PCL-A-3 1/2B", '3 1/2"', 475, 420, 79, 16, 97, 81, '1/2"', "6 x 25", 95, 1.70),
    ("PCL-A-4B", '4"', 475, 420, 87, 19, 111, 92, '5/8"', "6 x 32", 106, 1.95),
    ("PCL-A-5B", '5"', 475, 420, 102, 19, 125, 106, '5/8"', "6 x 32", 121, 2.45),
    ("PCL-A-6B", '6"', 735, 655, 124, 22, 149, 127, '3/4"', "9 x 38", 146, 3.05),
    ("PCL-A-8B", '8"', 735, 655, 152, 25, 178, 156, '3/4"', "9 x 38", 175, 4.25),
    ("PCL-A-10B", '10"', 1130, 1010, 186, 25, 217, 189, '7/8"', "12 x 51", 214, 5.55),
    ("PCL-A-12B", '12"', 1130, 1010, 210, 25, 247, 214, '7/8"', "12 x 51", 238, 6.95),
    ("PCL-A-14B", '14"', 1130, 1010, 229, 29, 270, 235, '7/8"', "12 x 64", 264, 8.35),
    ("PCL-A-16B", '16"', 1130, 1010, 254, 29, 295, 260, '7/8"', "12 x 64", 289, 9.90),
    ("PCL-A-18B", '18"', 1390, 1240, 292, 32, 330, 295, '1"', "16 x 64", 327, 11.70),
    ("PCL-A-20B", '20"', 1390, 1240, 318, 35, 359, 324, '1 1/8"', "16 x 64", 352, 13.55),
    ("PCL-A-24B", '24"', 1390, 1240, 381, 41, 429, 387, '1 1/4"', "16 x 76", 422, 17.20),
]


def _build_raw_row(row: tuple) -> dict:
    designation, line_size, load650, load750, b, c, d, e, f, g, h, estimated_weight = row
    return {
        **M4_COMPONENT_INFO,
        "type": designation,
        "designation": designation,
        "line_size": line_size,
        "load_650f_kg": load650,
        "load_750f_kg": load750,
        "B": b,
        "C": c,
        "D": d,
        "E": e,
        "F": f,
        "G": g,
        "H": h,
        "rod_size_a": f,
        "estimated_set_weight_kg": estimated_weight,
        "set_weight_kg": estimated_weight,
        "set_weight_is_estimated": True,
        "weight_basis": "engineering_estimate_no_source_unit_weight",
        "half_weight_kg": round(estimated_weight / 2, 2),
    }


M4_TABLE = build_clamp_table(
    [_build_raw_row(row) for row in _RAW_M4_ROWS],
    type_label="TYPE-A",
    source_component="M-4",
)


def get_m4_component() -> dict:
    return {
        **M4_COMPONENT_INFO,
        "row_count": len(M4_TABLE),
        "line_size_range": '1/2"~24"',
        "notes": [
            "Raw B/C/D/E/F/G/H/load values are stored in m4_table.py.",
            "Set weight is estimated because the source drawing has no unit-weight column.",
        ],
    }


def get_m4_by_line_size(line_size) -> dict | None:
    return get_clamp_by_line_size(M4_TABLE, line_size)


def get_m4_by_type(clamp_type: str) -> dict | None:
    return get_clamp_by_type(M4_TABLE, clamp_type)


def build_m4_item(line_size) -> dict | None:
    return build_clamp_item(M4_TABLE, line_size)
