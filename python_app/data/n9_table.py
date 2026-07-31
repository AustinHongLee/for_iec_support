"""N-9/N-10 lower-component assembly lookup.

Source: N-9 Rev.0 (arrangements and notes) plus N-10 Rev.0 (plate table).
"""

from __future__ import annotations

from copy import deepcopy

from .n10_table import get_n10_by_supporting_pipe


N9_COMPONENT_INFO = {
    "component_id": "N-9",
    "name_en": "LOWER COMPONENT OF BASE COLD SUPPORT",
    "category": "component_cold",
    "pdf_file": "N-9-LOWER COMPONENT OF BASE COLD SUPPORT.1.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-9/N-10",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
}


N9_LOWER_TYPES = {
    "A": {
        "plates": ["a"],
        "angles": 0,
        "interface": "25 mm grout",
    },
    "B": {
        "plates": ["a", "d"],
        "angles": 0,
        "interface": "25 mm grout",
    },
    "C": {
        "plates": ["a"],
        "angles": 0,
        "interface": "existing steel",
    },
    "D": {
        "plates": ["a", "e"],
        "angles": 0,
        "interface": "platform",
    },
    "E": {
        "plates": ["a", "d"],
        "angles": 2,
        "interface": "25 mm grout",
    },
    "F": {
        "plates": ["a"],
        "angles": 2,
        "interface": "existing steel",
    },
    "G": {
        "plates": ["b"],
        "angles": 0,
        "interface": "25 mm grout",
    },
    "H": {
        "plates": ["a"],
        "angles": 0,
        "interface": "foundation by civil",
    },
    "J": {
        "plates": ["b"],
        "angles": 0,
        "interface": "foundation by civil",
    },
    "K": {
        "plates": ["a"],
        "angles": 2,
        "interface": "foundation by civil",
    },
    "R": {
        "plates": ["a"],
        "angles": 0,
        "interface": "insert plate or existing steel",
    },
    "S": {
        "plates": ["a", "e"],
        "angles": 2,
        "interface": "existing steel",
    },
}


_DELETE_PLATE_A_HOST_TYPES = {"03C", "04C", "09C", "10C"}


def _plate_geometry(letter: str, row: dict) -> dict:
    thickness = row["plate_K_mm"]
    if letter == "a":
        return {
            "plate": "a",
            "length_mm": row["B_mm"],
            "width_mm": row["B_mm"],
            "thickness_mm": thickness,
            "holes": None,
        }
    if letter == "b":
        return {
            "plate": "b",
            "length_mm": row["C_mm"],
            "width_mm": row["C_mm"],
            "thickness_mm": thickness,
            "holes": {
                "count": 4,
                "diameter_mm": row["expansion_hole_H_mm"],
                "pitch_x_mm": row["D_mm"],
                "pitch_y_mm": row["D_mm"],
                "fastener": row["expansion_bolt_J"],
            },
        }
    if letter == "d":
        return {
            "plate": "d",
            "length_mm": row["E_mm"],
            "width_mm": row["E_mm"],
            "thickness_mm": thickness,
            "holes": {
                "count": 4,
                "diameter_mm": row["expansion_hole_H_mm"],
                "pitch_x_mm": row["F_mm"],
                "pitch_y_mm": row["F_mm"],
                "fastener": row["expansion_bolt_J"],
            },
        }
    if letter == "e":
        return {
            "plate": "e",
            "length_mm": row["G_mm"],
            "width_mm": row["G_mm"],
            "thickness_mm": thickness,
            "holes": None,
        }
    raise ValueError(f"unknown N-9 plate: {letter}")


def get_n9_component() -> dict:
    return {
        **deepcopy(N9_COMPONENT_INFO),
        "designation": "TYPE-{A|B|C|D|E|F|G|H|J|K|R|S}",
        "line_size_range": 'supporting pipe 1 1/2"~12"',
        "notes": [
            "Plate dimensions are supplied by N-10.",
            "For host Types 03C/04C/09C/10C, plate a is deleted in lower Type B/H.",
            "N-9/N-10 do not identify plate material.",
        ],
    }


def get_n9_lower_component(
    lower_type: str,
    supporting_pipe,
    *,
    host_type: str | None = None,
) -> dict | None:
    lower = str(lower_type).strip().upper()
    arrangement = N9_LOWER_TYPES.get(lower)
    row = get_n10_by_supporting_pipe(supporting_pipe)
    if not arrangement or not row:
        return None
    plates = list(arrangement["plates"])
    plate_a_deleted = (
        str(host_type or "").upper() in _DELETE_PLATE_A_HOST_TYPES
        and lower in {"B", "H"}
        and "a" in plates
    )
    if plate_a_deleted:
        plates.remove("a")
    return {
        **deepcopy(N9_COMPONENT_INFO),
        "lower_type": lower,
        "host_type": str(host_type or "").upper() or None,
        "supporting_pipe_size_in": row["supporting_pipe_size_in"],
        "dimension_row": row,
        "plates": [_plate_geometry(letter, row) for letter in plates],
        "plate_a_deleted_by_n9_note_1": plate_a_deleted,
        "angle_spec": (
            "L40x40x5x150 LG"
            if arrangement["angles"]
            else None
        ),
        "angle_quantity": arrangement["angles"],
        "interface": arrangement["interface"],
        "fabrication_ready": False,
        "fabrication_blockers": [
            "N-9/N-10 do not identify plate material",
            "host-support weld/interface scope must be released with the project support",
        ],
    }
