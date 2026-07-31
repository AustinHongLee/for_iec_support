"""N-10 lower-component plate dimensional table.

Source: ``N-10-LOWER COMPONENT OF BASE COLD SUPPORT.2.pdf`` /
DSP-500-006 / N-10 / Rev.0.
"""

from __future__ import annotations

from copy import deepcopy
import re

from .component_size_utils import size_to_float


N10_COMPONENT_INFO = {
    "component_id": "N-10",
    "name_en": "LOWER COMPONENT OF BASE COLD SUPPORT (2 OF 2)",
    "category": "component_cold",
    "pdf_file": "N-10-LOWER COMPONENT OF BASE COLD SUPPORT.2.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-10",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
}


N10_TABLE = [
    {
        "supporting_pipe_min_in": 1.5,
        "supporting_pipe_max_in": 3,
        "B_mm": 150,
        "C_mm": 180,
        "D_mm": 110,
        "E_mm": 290,
        "F_mm": 220,
        "G_mm": 200,
        "expansion_hole_H_mm": 19,
        "expansion_bolt_J": '5/8"',
        "plate_K_mm": 9,
    },
    {
        "supporting_pipe_min_in": 4,
        "supporting_pipe_max_in": 6,
        "B_mm": 230,
        "C_mm": 260,
        "D_mm": 190,
        "E_mm": 370,
        "F_mm": 300,
        "G_mm": 280,
        "expansion_hole_H_mm": 19,
        "expansion_bolt_J": '5/8"',
        "plate_K_mm": 9,
    },
    {
        "supporting_pipe_min_in": 8,
        "supporting_pipe_max_in": 8,
        "B_mm": 330,
        "C_mm": 380,
        "D_mm": 300,
        "E_mm": 490,
        "F_mm": 410,
        "G_mm": 380,
        "expansion_hole_H_mm": 22,
        "expansion_bolt_J": '3/4"',
        "plate_K_mm": 16,
    },
    {
        "supporting_pipe_min_in": 10,
        "supporting_pipe_max_in": 10,
        "B_mm": 330,
        "C_mm": 380,
        "D_mm": 300,
        "E_mm": 490,
        "F_mm": 410,
        "G_mm": 380,
        "expansion_hole_H_mm": 22,
        "expansion_bolt_J": '3/4"',
        "plate_K_mm": 16,
    },
    {
        "supporting_pipe_min_in": 12,
        "supporting_pipe_max_in": 12,
        "B_mm": 380,
        "C_mm": 500,
        "D_mm": 410,
        "E_mm": 560,
        "F_mm": 470,
        "G_mm": 430,
        "expansion_hole_H_mm": 26,
        "expansion_bolt_J": '7/8"',
        "plate_K_mm": 16,
    },
]


def _pipe_size(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    match = re.match(
        r"^\s*(\d+(?:[- ]\d+/\d+)?|\d+/\d+|\d+(?:\.\d+)?)",
        str(value),
    )
    return size_to_float(match.group(1)) if match else None


def get_n10_component() -> dict:
    return {
        **deepcopy(N10_COMPONENT_INFO),
        "line_size_range": 'supporting pipe 1 1/2"~12"',
        "designation": "dimension row selected by supporting-pipe nominal size",
        "notes": [
            "N-10 supplies plates a/b/d/e dimensions used by N-9.",
            "Material is not specified on N-9/N-10.",
        ],
    }


def get_n10_by_supporting_pipe(supporting_pipe) -> dict | None:
    size = _pipe_size(supporting_pipe)
    if size is None:
        return None
    for row in N10_TABLE:
        if row["supporting_pipe_min_in"] <= size <= row[
            "supporting_pipe_max_in"
        ]:
            return {
                **deepcopy(N10_COMPONENT_INFO),
                **deepcopy(row),
                "supporting_pipe_size_in": size,
            }
    return None
