"""M-58 Type-A U-bolt dimensional lookup."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M58_COMPONENT_INFO = {
    "component_id": "M-58",
    "name_en": "TYPE-A U-BOLT",
    "category": "component",
    "pdf_file": "U-BOLT_TYPE-A_M-58.pdf",
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": True,
    "weight_calculation_location": (
        "core/types/_nonferrous_support_common.py::add_m58_ubolt"
    ),
    "transcription_status": "drawing_reverified",
}

_ROWS = {
    1.0: {"rod_dia_in": 0.25, "D": 40, "E": 55},
    1.5: {"rod_dia_in": 0.25, "D": 40, "E": 65},
    2.0: {"rod_dia_in": 0.25, "D": 40, "E": 70},
    2.5: {"rod_dia_in": 0.375, "D": 60, "E": 85},
    3.0: {"rod_dia_in": 0.375, "D": 60, "E": 90},
    4.0: {"rod_dia_in": 0.375, "D": 60, "E": 100},
    6.0: {"rod_dia_in": 0.5, "D": 70, "E": 135},
    8.0: {"rod_dia_in": 0.5, "D": 70, "E": 165},
}


def get_m58_component() -> dict:
    return {
        **deepcopy(M58_COMPONENT_INFO),
        "line_size_range": '1"~8"',
        "material": "CARBON STEEL",
        "finished_hex_nuts_per_set": 4,
        "B_rule": "actual_pipe_od_mm + 18",
        "B_dimension_basis": "inside clear distance between rod legs",
        "centerline_span_rule": "B + rod_diameter_mm",
        "developed_length_rule": (
            "pi * (B + rod_diameter_mm) / 2 + 2 * E"
        ),
    }


def get_m58_by_line_size(line_size) -> dict | None:
    size = size_to_float(line_size)
    row = _ROWS.get(size)
    if not row:
        return None
    return {
        **deepcopy(M58_COMPONENT_INFO),
        "line_size_in": size,
        "rod_dia_in": row["rod_dia_in"],
        "rod_dia_mm": row["rod_dia_in"] * 25.4,
        "dimensions_mm": {"D": row["D"], "E": row["E"]},
        "B_rule": "actual_pipe_od_mm + 18",
        "material": "CARBON STEEL",
        "finished_hex_nuts_per_set": 4,
    }
