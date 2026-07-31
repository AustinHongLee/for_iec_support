"""M-33 Lug Plate Type-B source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M33_COMPONENT_INFO = {
    "component_id": "M-33",
    "name_en": "LUG PLATE TYPE-B",
    "category": "component",
    "pdf_file": "M-33-LUG PLATE B.pdf",
    "source_drawing": (
        "單張-本案有關/中威/LUG-PLATE_TYPE-B_M-33.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "weight_ready": False,
    "blank_ready": False,
    "fabrication_ready": False,
    "material_rule": {
        "default": "CARBON STEEL, GRADE NOT SPECIFIED",
        "alloy_pipe": "SAME MATERIAL AS PIPE",
    },
    "fabrication_blockers": [
        "the exact pipe-contact contour and the 12/24 detail datum interpretation are not released as a flat profile",
        "the pipe-contact bevel/groove preparation is not fully dimensioned",
        "carbon-steel grade/coating is not released; alloy service requires an explicit lug material selection",
        "finished plate weight and weld-metal weight are not supplied",
    ],
}


# line size A, hanger rod B, C, D, E, K, R, T, S, maximum load
_M33_ROWS = (
    (2.0, "5/8", 185, 90, 320, 21, 40, 10, None, 1000),
    (3.0, "5/8", 190, 90, 295, 21, 40, 10, None, 1000),
    (4.0, "5/8", 190, 90, 295, 21, 40, 10, None, 1000),
    (6.0, "7/8", 190, 90, 295, 28, 40, 12, 6, 1700),
    (8.0, "7/8", 190, 90, 300, 28, 40, 12, 6, 1700),
    (10.0, "7/8", 185, 90, 300, 28, 40, 12, 6, 1700),
    (12.0, "7/8", 180, 90, 305, 28, 40, 12, 6, 1700),
    (14.0, "1", 160, 125, 340, 32, 50, 12, 6, 2500),
    (16.0, "1", 155, 125, 345, 32, 50, 12, 6, 2500),
    (18.0, "1", 150, 125, 345, 32, 50, 12, 6, 2500),
    (20.0, "1 1/8", 170, 125, 375, 35, 50, 16, 9, 4500),
    (24.0, "1 1/8", 185, 125, 470, 35, 50, 16, 9, 4500),
)


def _build_row(raw_row: tuple) -> dict:
    (
        line_size,
        rod_size,
        c_mm,
        d_mm,
        e_mm,
        k_mm,
        r_mm,
        thickness_mm,
        weld_s_mm,
        load_kg,
    ) = raw_row
    return {
        **deepcopy(M33_COMPONENT_INFO),
        "designation": f"LGP-B-{line_size:g}B",
        "A_line_size_in": line_size,
        "B_hanger_rod_size_in": f'{rod_size}"',
        "C_mm": c_mm,
        "D_mm": d_mm,
        "E_mm": e_mm,
        "K_mm": k_mm,
        "R_mm": r_mm,
        "T_thickness_mm": thickness_mm,
        "S_weld_size_mm": weld_s_mm,
        "maximum_recommended_load_kg": load_kg,
        "host_weld_callout": (
            "6 mm for 4 inch and smaller"
            if line_size <= 4
            else f"S={weld_s_mm} mm for 6 to 24 inch pipe"
        ),
        "pipe_contact_detail_callouts_mm": [12, 24],
    }


M33_TABLE = {
    raw_row[0]: _build_row(raw_row)
    for raw_row in _M33_ROWS
}


def get_m33_component() -> dict:
    return deepcopy(M33_COMPONENT_INFO)


def get_m33_by_line_size(line_size: object) -> dict | None:
    size = size_to_float(line_size)
    row = M33_TABLE.get(size) if size is not None else None
    return deepcopy(row) if row else None
