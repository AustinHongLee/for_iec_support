"""M-57 non-ferrous pipe saddle dimensional table.

Source: Chung Wei ``NON-FERROUS-PIPE-SADDLE_M-57.pdf`` / Rev.1.
The source defines the saddle diameter from the manufacturer's actual pipe OD,
so callers must supply that OD rather than infer an ASME steel-pipe OD.
"""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M57_COMPONENT_INFO = {
    "component_id": "M-57",
    "name_en": "NON-FERROUS PIPE SADDLE",
    "category": "component",
    "pdf_file": "NON-FERROUS-PIPE-SADDLE_M-57.pdf",
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
}

_GROUPS = [
    {
        "min": 0.5,
        "max": 4.0,
        "W": 165,
        "T": 3,
        "A": 25,
        "H": 8,
        "J": '1/4"x30mm',
    },
    {
        "min": 6.0,
        "max": 8.0,
        "W": 165,
        "T": 3,
        "A": 25,
        "H": 11,
        "J": '3/8"x40mm',
    },
    {
        "min": 10.0,
        "max": 16.0,
        "W": 330,
        "T": 6,
        "A": 40,
        "H": 14,
        "J": '1/2"x60mm',
    },
    {
        "min": 18.0,
        "max": 24.0,
        "W": 500,
        "T": 9,
        "A": 40,
        "H": 18,
        "J": '5/8"x80mm',
    },
    {
        "min": 26.0,
        "max": 32.0,
        "W": 600,
        "T": 12,
        "A": 50,
        "H": 21,
        "J": '3/4"x100mm',
    },
]

_DRAWN_SIZES = {
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    2.5,
    3.0,
    4.0,
    6.0,
    8.0,
    10.0,
    12.0,
    14.0,
    16.0,
    18.0,
    20.0,
    24.0,
    26.0,
    28.0,
    30.0,
    32.0,
}


def get_m57_component() -> dict:
    return {
        **deepcopy(M57_COMPONENT_INFO),
        "line_size_range": '1/2"~32"',
        "materials": {
            "plate": "CARBON STEEL",
            "bolt": "A307 Gr.B",
            "nut": "A563 Gr.A",
        },
        "notes": [
            "D = manufacturer pipe OD + 6 mm.",
            "Two half-saddles and four A×A drilled lugs form one set.",
            "The four lugs form two opposed bolt-and-nut joints.",
        ],
    }


def get_m57_by_line_size(line_size) -> dict | None:
    size = size_to_float(line_size)
    if size is None or size not in _DRAWN_SIZES:
        return None
    for group in _GROUPS:
        if group["min"] <= size <= group["max"]:
            return {
                **deepcopy(M57_COMPONENT_INFO),
                "line_size_in": size,
                "dimensions_mm": {
                    key: group[key] for key in ("W", "T", "A", "H")
                },
                "machine_bolt_J": group["J"],
                "machine_bolt_quantity": 2,
                "lug_plate_quantity": 4,
                "saddle_inside_diameter_rule": "actual_pipe_od_mm + 6",
                "materials": {
                    "plate": "CARBON STEEL",
                    "bolt": "A307 Gr.B",
                    "nut": "A563 Gr.A",
                },
            }
    return None
