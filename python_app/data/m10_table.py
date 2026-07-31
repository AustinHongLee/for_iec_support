"""M-10 Pipe Clamp Type-G source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M10_COMPONENT_INFO = {
    "component_id": "M-10",
    "name_en": "PIPE CLAMP TYPE-G",
    "category": "component",
    "pdf_file": "M-10-PIPE CLAMP G.pdf",
    "source_drawing": (
        "單張-本案有關/中威/PIPE-CLAMP_TYPE-G_M-10.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "reference": "GRINNELL FIG. 246 OR EQ.",
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "procurement_ready": False,
    "material": (
        "CHROME MOLYBDENUM STEEL, EXCEPT U-BOLT WHICH IS STAINLESS STEEL"
    ),
    "dimension_units": "mm unless marked inch",
    "dimension_letters": {
        "C": "clear gap between upper clamp ears",
        "D": "source dimension D",
        "E": "pipe centerline to upper pin centerline",
        "F": "upper cross-pin diameter",
        "H": "U-bolt diameter",
        "K": "overall clamp width",
        "M": "upper clamp side-view width",
    },
    "fabrication_blockers": [
        "the forged/formed clamp-body contour and flat development are not fully dimensioned",
        "upper pin length/grade and the complete nut/washer scope are not supplied",
        "U-bolt developed length, threaded-end length and bend allowance are not released",
        "chrome-moly and stainless-steel grades are not specified",
        "the drawing supplies no finished unit weight",
    ],
}


# line size, used-on OD range, loads at 950/1000/1050/1075 F,
# C, D, E, F pin, H U-bolt, K, M
_M10_ROWS = (
    (10.0, 8, 10, 6120, 5340, 3560, 2775, 51, 232, 305, "1 1/2", "1", 391, 83),
    (12.0, 10, 12, 7480, 6760, 4505, 3510, 57, 273, 349, "1 5/8", "1 1/4", 454, 102),
    (14.0, 12, 14, 7480, 6760, 4505, 3510, 57, 292, 368, "1 5/8", "1 1/4", 486, 102),
    (16.0, 14, 16, 7480, 6760, 4505, 3510, 57, 333, 416, "1 5/8", "1 1/4", 537, 102),
    (18.0, 16, 18, 8615, 8345, 5560, 4340, 64, 368, 464, "2", "1 1/4", 613, 114),
    (20.0, 18, 20, 8615, 8345, 5560, 4340, 64, 400, 495, "2", "1 1/4", 664, 114),
    (24.0, 20, 24, 11335, 10100, 6730, 5250, 76, 464, 559, "2 1/4", "1 3/8", 781, 152),
)


def _build_row(raw_row: tuple) -> dict:
    (
        line_size,
        used_od_min,
        used_od_max,
        load_950,
        load_1000,
        load_1050,
        load_1075,
        c_mm,
        d_mm,
        e_mm,
        f_diameter,
        h_diameter,
        k_mm,
        m_mm,
    ) = raw_row
    return {
        **deepcopy(M10_COMPONENT_INFO),
        "designation": f"PCL-G-{line_size:g}B",
        "line_size_in": line_size,
        "used_on_od_pipe_size_in": {
            "min": used_od_min,
            "max": used_od_max,
        },
        "maximum_recommended_load_kg_by_temperature_f": {
            950: load_950,
            1000: load_1000,
            1050: load_1050,
            1075: load_1075,
        },
        "C_mm": c_mm,
        "D_mm": d_mm,
        "E_mm": e_mm,
        "F_upper_cross_pin_diameter_in": f'{f_diameter}"',
        "H_u_bolt_diameter_in": f'{h_diameter}"',
        "K_overall_width_mm": k_mm,
        "M_upper_side_width_mm": m_mm,
    }


M10_TABLE = {
    raw_row[0]: _build_row(raw_row)
    for raw_row in _M10_ROWS
}


def get_m10_component() -> dict:
    return deepcopy(M10_COMPONENT_INFO)


def get_m10_by_line_size(line_size: object) -> dict | None:
    size = size_to_float(line_size)
    row = M10_TABLE.get(size) if size is not None else None
    return deepcopy(row) if row else None


def build_m10_item(line_size: object) -> dict | None:
    return get_m10_by_line_size(line_size)
