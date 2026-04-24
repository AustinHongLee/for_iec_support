"""M-7 Pipe Clamp TYPE-D lookup table."""
from __future__ import annotations

from .m_clamp_common import build_clamp_item, build_clamp_table, get_clamp_by_line_size, get_clamp_by_type


M7_COMPONENT_INFO = {
    "component_id": "M-7",
    "name_en": "PIPE CLAMP D",
    "category": "component",
    "pdf_file": "M-7-PIPE CLAMP D.pdf",
    "drawing_file": "M-7M.DWG",
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


_RAW_M7_ROWS = [
    ('6"', '1"', 1585, 1415),
    ('8"', '1 1/8"', 2175, 1940),
    ('10"', '1 1/4"', 2490, 2225),
    ('12"', '1 3/8"', 3170, 2830),
    ('14"', '1 1/2"', 4300, 3845),
    ('16"', '1 3/4"', 4535, 4045),
    ('18"', '2"', 6255, 5582),
    ('20"', '2"', 6935, 6195),
    ('24"', '2"', 7390, 6600),
    ('28"', '2 1/4"', 8160, 0),
    ('30"', '2 1/4"', 9295, 0),
    ('32"', '2 1/2"', 10770, 0),
    ('34"', '2 1/2"', 11335, 0),
    ('36"', '2 3/4"', 12700, 0),
]


def _build_raw_row(row: tuple) -> dict:
    line_size, rod_size, load650, load750 = row
    size_token = line_size.replace('"', "")
    return {
        **M7_COMPONENT_INFO,
        "type": f"PCL-D-{size_token}B",
        "designation": f"PCL-D-{size_token}B",
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


M7_TABLE = build_clamp_table(
    [_build_raw_row(row) for row in _RAW_M7_ROWS],
    type_label="TYPE-D",
    source_component="M-7",
)


def get_m7_component() -> dict:
    return {
        **M7_COMPONENT_INFO,
        "row_count": len(M7_TABLE),
        "line_size_range": '6"~36"',
        "notes": [
            "Rod size and load values are split into m7_table.py.",
            "B/C/D/E/G/H dimensions still require full PDF transcription.",
            "Weight is intentionally not stored here; Type calculators use core.component_rules fallback if needed.",
        ],
    }


def get_m7_by_line_size(line_size) -> dict | None:
    return get_clamp_by_line_size(M7_TABLE, line_size)


def get_m7_by_type(clamp_type: str) -> dict | None:
    return get_clamp_by_type(M7_TABLE, clamp_type)


def build_m7_item(line_size) -> dict | None:
    return build_clamp_item(M7_TABLE, line_size)
