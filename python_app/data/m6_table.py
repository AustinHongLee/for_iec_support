"""M-6 Pipe Clamp TYPE-C lookup table."""
from __future__ import annotations

from .m_clamp_common import build_clamp_item, build_clamp_table, get_clamp_by_line_size, get_clamp_by_type


M6_COMPONENT_INFO = {
    "component_id": "M-6",
    "name_en": "PIPE CLAMP C",
    "category": "component",
    "pdf_file": "M-6-PIPE CLAMP C.pdf",
    "drawing_file": "M-6M.DWG",
    "engineering_standard": "E1906-DSP-500-006",
    "project": "E19-06",
    "table_kind": "partial_lookup",
    "lookup_ready": False,
    "partial_lookup_ready": True,
    "load_lookup_ready": True,
    "dimension_lookup_ready": False,
    "source_transcribed": False,
    "weight_ready": False,
    "transcription_status": "partial_pdf_transcribed",
}


_RAW_M6_ROWS = [
    ('3/4"', '3/8"', 430, 385),
    ('1"', '3/8"', 430, 385),
    ('1 1/4"', '3/8"', 430, 385),
    ('1 1/2"', '5/8"', 700, 625),
    ('2"', '5/8"', 700, 625),
    ('2 1/2"', '5/8"', 700, 625),
    ('3"', '5/8"', 700, 625),
    ('4"', '3/4"', 1135, 1015),
    ('5"', '3/4"', 1135, 1015),
    ('6"', '7/8"', 1300, 1160),
    ('8"', '7/8"', 1300, 1160),
    ('10"', '1"', 1470, 1315),
    ('12"', '1"', 1470, 1315),
    ('14"', '1 1/4"', 1955, 1745),
    ('16"', '1 1/4"', 1955, 1745),
    ('18"', '1 1/4"', 1955, 1745),
    ('20"', '1 3/8"', 2045, 1825),
    ('24"', '1 3/8"', 2495, 2225),
    ('28"', '1 1/4"', 2720, 0),
    ('30"', '1 3/8"', 3400, 0),
    ('32"', '1 1/2"', 3470, 0),
    ('34"', '1 3/4"', 4440, 0),
    ('36"', '1 3/4"', 4760, 0),
]


def _build_raw_row(row: tuple) -> dict:
    line_size, rod_size, load650, load750 = row
    size_token = line_size.replace('"', "")
    return {
        **M6_COMPONENT_INFO,
        "type": f"PCL-C-{size_token}B",
        "designation": f"PCL-C-{size_token}B",
        "line_size": line_size,
        "rod_size_a": rod_size,
        "F": rod_size,
        "load_650f_kg": load650,
        "load_750f_kg": load750 if load750 else None,
        "load_750f_status": "source_value" if load750 else "source_blank_or_not_applicable",
        "set_weight_kg": None,
        "set_weight_is_estimated": False,
        "weight_status": "not_available_partial_lookup",
    }


M6_TABLE = build_clamp_table(
    [_build_raw_row(row) for row in _RAW_M6_ROWS],
    type_label="TYPE-C",
    source_component="M-6",
)


def get_m6_component() -> dict:
    return {
        **M6_COMPONENT_INFO,
        "row_count": len(M6_TABLE),
        "line_size_range": '3/4"~36"',
        "notes": [
            "Rod size and load values are split into m6_table.py.",
            "B/C/D/E/G/H dimensions still require full PDF transcription.",
            "Weight is intentionally not stored here; Type calculators use core.component_rules fallback if needed.",
        ],
    }


def get_m6_by_line_size(line_size) -> dict | None:
    return get_clamp_by_line_size(M6_TABLE, line_size)


def get_m6_by_type(clamp_type: str) -> dict | None:
    return get_clamp_by_type(M6_TABLE, clamp_type)


def build_m6_item(line_size) -> dict | None:
    return build_clamp_item(M6_TABLE, line_size)
