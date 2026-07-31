"""M-9 Pipe Clamp Type-F source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M9_COMPONENT_INFO = {
    "component_id": "M-9",
    "name_en": "PIPE CLAMP TYPE-F",
    "category": "component",
    "pdf_file": "M-9-PIPE CLAMP F.pdf",
    "source_drawing": (
        "單張-本案有關/中威/PIPE-CLAMP_TYPE-F_M-9.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "reference": "GRINNELL FIG. 224 OR EQ.",
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
    },
    "fabrication_blockers": [
        "the forged/formed clamp-body contour and flat development are not fully dimensioned",
        "upper pin length/grade and the complete nut/washer scope are not supplied",
        "U-bolt developed length, threaded-end length and bend allowance are not released",
        "chrome-moly and stainless-steel grades are not specified",
        "the drawing supplies no finished unit weight",
    ],
}


# line size, loads at 750/950/1000/1050 F, C, D, E, F pin, H U-bolt, K
_M9_ROWS = (
    (4.0, 1710, 1495, 1255, 855, 27, 98, 171, "7/8", "1/2", 165),
    (6.0, 2745, 2395, 2010, 1370, 37, 138, 211, "1", "5/8", 232),
    (8.0, 2745, 2395, 2010, 1370, 37, 170, 243, "1", "5/8", 283),
    (10.0, 4105, 3585, 3010, 2000, 37, 213, 276, "1 1/8", "3/4", 346),
    (12.0, 5700, 4975, 4085, 2725, 49, 257, 327, "1 1/2", "7/8", 410),
    (14.0, 5700, 4975, 4085, 2725, 49, 283, 352, "1 1/2", "7/8", 441),
    (16.0, 5700, 4975, 4085, 2725, 49, 311, 381, "1 1/2", "7/8", 499),
)


def _build_row(raw_row: tuple) -> dict:
    (
        line_size,
        load_750,
        load_950,
        load_1000,
        load_1050,
        c_mm,
        d_mm,
        e_mm,
        f_diameter,
        h_diameter,
        k_mm,
    ) = raw_row
    return {
        **deepcopy(M9_COMPONENT_INFO),
        "designation": f"PCL-F-{line_size:g}B",
        "line_size_in": line_size,
        "maximum_recommended_load_kg_by_temperature_f": {
            750: load_750,
            950: load_950,
            1000: load_1000,
            1050: load_1050,
        },
        "C_mm": c_mm,
        "D_mm": d_mm,
        "E_mm": e_mm,
        "F_upper_cross_pin_diameter_in": f'{f_diameter}"',
        "H_u_bolt_diameter_in": f'{h_diameter}"',
        "K_overall_width_mm": k_mm,
    }


M9_TABLE = {
    raw_row[0]: _build_row(raw_row)
    for raw_row in _M9_ROWS
}


def get_m9_component() -> dict:
    return deepcopy(M9_COMPONENT_INFO)


def get_m9_by_line_size(line_size: object) -> dict | None:
    size = size_to_float(line_size)
    row = M9_TABLE.get(size) if size is not None else None
    return deepcopy(row) if row else None


def build_m9_item(line_size: object) -> dict | None:
    return get_m9_by_line_size(line_size)
