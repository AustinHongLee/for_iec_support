"""M-59 Type-A U-band dimensional lookup."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M59_COMPONENT_INFO = {
    "component_id": "M-59",
    "name_en": "TYPE-A U-BAND",
    "category": "component",
    "pdf_file": "U-BAND_TYPE-A_M-59.pdf",
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": True,
    "weight_calculation_location": (
        "core/types/_nonferrous_support_common.py::add_m59_uband"
    ),
    "transcription_status": "drawing_reverified",
}

_ROWS = {
    10.0: {"D": 100, "T": 6, "G": 9},
    12.0: {"D": 100, "T": 6, "G": 9},
    14.0: {"D": 100, "T": 6, "G": 9},
    16.0: {"D": 100, "T": 6, "G": 9},
    18.0: {"D": 100, "T": 6, "G": 12},
    20.0: {"D": 100, "T": 6, "G": 12},
    24.0: {"D": 150, "T": 9, "G": 12},
    26.0: {"D": 150, "T": 9, "G": 15},
    28.0: {"D": 150, "T": 9, "G": 15},
    30.0: {"D": 150, "T": 9, "G": 15},
    32.0: {"D": 150, "T": 9, "G": 15},
}


def get_m59_component() -> dict:
    return {
        **deepcopy(M59_COMPONENT_INFO),
        "line_size_range": '10"~32"',
        "material": "CARBON STEEL GALVANIZED",
        "rules": {
            "R": "actual_pipe_od_mm / 2 + G + 3",
            "H": "R - 3",
            "W": "2 * (R + T)",
        },
    }


def get_m59_by_line_size(line_size) -> dict | None:
    size = size_to_float(line_size)
    row = _ROWS.get(size)
    if not row:
        return None
    return {
        **deepcopy(M59_COMPONENT_INFO),
        "line_size_in": size,
        "dimensions_mm": deepcopy(row),
        "material": "CARBON STEEL GALVANIZED",
        "rules": {
            "R": "actual_pipe_od_mm / 2 + G + 3",
            "H": "R - 3",
            "W": "2 * (R + T)",
        },
    }
