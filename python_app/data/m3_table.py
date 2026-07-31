"""M-3 Adjustable Clevis source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M3_COMPONENT_INFO = {
    "component_id": "M-3",
    "name_en": "ADJUSTABLE CLEVIS",
    "category": "component",
    "pdf_file": "M-3-ADJUSTABLE CLEVIS.pdf",
    "source_drawing": (
        "單張-本案有關/中威/ADJUSTABLE-CLEVIS_M-3.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "reference": "GRINNELL FIG. 260 OR EQ.",
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "procurement_ready": False,
    "material": "CARBON STEEL, GRADE NOT SPECIFIED",
    "fabrication_blockers": [
        "M-3 is a formed purchased assembly; the drawing supplies no finished unit weight",
        "bend radii, developed strip lengths and formed-part tolerances are not dimensioned",
        "cross-bolt length/grade, nut/washer scope and finished fastener weight are not supplied",
        "carbon-steel grade and coating are not released",
    ],
}


# line size, load, upper t/w, lower t/w, A rod, B, C, D, E, F, G cross bolt
_M3_ROWS = (
    (0.5, 275, 3, 25, 3, 25, "3/8", 43, 54, 64, 22, 11, "1/4"),
    (0.75, 275, 3, 25, 3, 25, "3/8", 48, 62, 64, 25, 13, "1/4"),
    (1.0, 275, 3, 25, 3, 25, "3/8", 54, 71, 64, 32, 16, "1/4"),
    (1.25, 275, 3, 25, 3, 25, "3/8", 65, 87, 64, 44, 22, "1/4"),
    (1.5, 275, 4, 25, 3, 25, "3/8", 76, 102, 64, 54, 27, "1/4"),
    (2.0, 275, 4, 25, 3, 25, "3/8", 94, 124, 64, 75, 41, "1/4"),
    (2.5, 515, 5, 32, 5, 32, "1/2", 119, 156, 76, 97, 51, "3/8"),
    (3.0, 515, 5, 32, 5, 32, "1/2", 121, 167, 76, 98, 44, "3/8"),
    (3.5, 515, 5, 32, 5, 32, "1/2", 125, 176, 76, 103, 44, "3/8"),
    (4.0, 650, 6, 32, 5, 32, "5/8", 141, 198, 89, 114, 49, "3/8"),
    (5.0, 650, 6, 32, 5, 32, "5/8", 157, 229, 89, 130, 44, "1/2"),
    (6.0, 880, 6, 38, 5, 38, "3/4", 176, 257, 102, 143, 48, "1/2"),
    (8.0, 910, 6, 44, 5, 44, "7/8", 213, 321, 108, 178, 54, "5/8"),
    (10.0, 1635, 9, 44, 6, 44, "7/8", 251, 387, 114, 213, 57, "3/4"),
    (12.0, 1725, 9, 51, 6, 51, "7/8", 284, 446, 121, 248, 67, "3/4"),
    (14.0, 1910, 12, 51, 6, 51, "1", 316, 494, 133, 275, 75, "7/8"),
    (16.0, 2090, 12, 64, 6, 64, "1", 357, 584, 152, 316, 67, "1"),
    (18.0, 2180, 12, 64, 6, 64, "1 1/8", 394, 629, 165, 354, 95, "1"),
    (20.0, 2180, 16, 76, 9, 76, "1 1/4", 438, 695, 178, 367, 102, "1 1/4"),
    (24.0, 2180, 16, 76, 9, 76, "1 1/4", 498, 803, 191, 445, 108, "1 1/4"),
    (30.0, 2725, 19, 76, 9, 76, "1 1/4", 613, 994, 210, 556, 127, "1 5/8"),
)


def _line_size_label(size: float) -> str:
    labels = {
        0.5: "1/2",
        0.75: "3/4",
        1.25: "1 1/4",
        1.5: "1 1/2",
        2.5: "2 1/2",
        3.5: "3 1/2",
    }
    return labels.get(size, f"{size:g}")


def _build_row(raw_row: tuple) -> dict:
    (
        line_size,
        load_kg,
        upper_t,
        upper_w,
        lower_t,
        lower_w,
        rod_size,
        b_mm,
        c_mm,
        d_mm,
        e_mm,
        adjustment_f_mm,
        cross_bolt_size,
    ) = raw_row
    return {
        **deepcopy(M3_COMPONENT_INFO),
        "designation": f"ADC-{_line_size_label(line_size)}B",
        "line_size_in": line_size,
        "maximum_recommended_load_kg": load_kg,
        "upper_steel_thickness_mm": upper_t,
        "upper_steel_width_mm": upper_w,
        "lower_steel_thickness_mm": lower_t,
        "lower_steel_width_mm": lower_w,
        "A_rod_size_in": f'{rod_size}"',
        "B_inside_width_mm": b_mm,
        "C_overall_height_mm": c_mm,
        "D_top_to_pipe_center_mm": d_mm,
        "E_cross_bolt_to_pipe_center_mm": e_mm,
        "F_adjustment_mm": adjustment_f_mm,
        "G_cross_bolt_diameter_in": f'{cross_bolt_size}"',
    }


M3_TABLE = {
    raw_row[0]: _build_row(raw_row)
    for raw_row in _M3_ROWS
}


def get_m3_component() -> dict:
    return deepcopy(M3_COMPONENT_INFO)


def get_m3_by_line_size(line_size: object) -> dict | None:
    size = size_to_float(line_size)
    row = M3_TABLE.get(size) if size is not None else None
    return deepcopy(row) if row else None
