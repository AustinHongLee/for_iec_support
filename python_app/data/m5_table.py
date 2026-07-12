"""M-5 Pipe Clamp TYPE-B lookup table."""
from __future__ import annotations

from .m_clamp_common import build_clamp_item, build_clamp_table, get_clamp_by_line_size, get_clamp_by_type


M5_COMPONENT_INFO = {
    "component_id": "M-5",
    "name_en": "PIPE CLAMP B",
    "category": "component",
    "pdf_file": "M-5-PIPE CLAMP B.pdf",
    "drawing_file": "M-5M.DWG",
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


_RAW_M5_ROWS = [
    ('3"', '3/4"', 1525, 1360),
    ('4"', '7/8"', 1590, 1420),
    ('5"', '7/8"', 1590, 1420),
    ('6"', '1"', 2205, 1965),
    ('8"', '1"', 2205, 1965),
    ('10"', '1 1/4"', 2725, 2430),
    ('12"', '1 1/2"', 3930, 3510),
    ('14"', '1 1/2"', 4135, 3685),
    ('16"', '1 1/2"', 4135, 3685),
    ('18"', '2"', 6255, 0),
    ('20"', '2"', 6935, 0),
    ('24"', '2 1/4"', 7390, 0),
    ('28"', '2 1/4"', 8160, 0),
    ('30"', '2 1/2"', 9295, 0),
    ('32"', '2 1/2"', 10770, 0),
    ('34"', '2 1/2"', 11335, 0),
    ('36"', '2 3/4"', 12695, 0),
    ('42"', '2 3/4"', 15870, 0),
]


def _build_raw_row(row: tuple) -> dict:
    line_size, rod_size, load650, load750 = row
    size_token = line_size.replace('"', "")
    return {
        **M5_COMPONENT_INFO,
        "type": f"PCL-B-{size_token}B",
        "designation": f"PCL-B-{size_token}B",
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


M5_TABLE = build_clamp_table(
    [_build_raw_row(row) for row in _RAW_M5_ROWS],
    type_label="TYPE-B",
    source_component="M-5",
)


def get_m5_component() -> dict:
    return {
        **M5_COMPONENT_INFO,
        "row_count": len(M5_TABLE),
        "line_size_range": '3"~42"',
        "notes": [
            "Rod size and load values are split into m5_table.py.",
            "B/C/D/E/G/H dimensions still require full PDF transcription.",
            "Weight is intentionally not stored here; Type calculators use core.component_rules fallback if needed.",
        ],
    }


def get_m5_by_line_size(line_size) -> dict | None:
    return get_clamp_by_line_size(M5_TABLE, line_size)


def get_m5_by_type(clamp_type: str) -> dict | None:
    return get_clamp_by_type(M5_TABLE, clamp_type)


def build_m5_item(line_size) -> dict | None:
    return build_clamp_item(M5_TABLE, line_size)
