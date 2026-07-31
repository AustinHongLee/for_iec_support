"""M-8 Pipe Clamp Type-E source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


M8_COMPONENT_INFO = {
    "component_id": "M-8",
    "name_en": "PIPE CLAMP TYPE-E",
    "category": "component",
    "pdf_file": "M-8-PIPE CLAMP E.pdf",
    "source_drawing": (
        "單張-本案有關/中威/PIPE-CLAMP_TYPE-E_M-8.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "reference": "GRINNELL FIG. 295A OR EQ.",
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "procurement_ready": False,
    "material": "CHROME MOLYBDENUM STEEL (ASTM A387-GR.22)",
    "dimension_units": "mm unless marked inch",
    "dimension_letters": {
        "B": "source dimension B",
        "C": "clear gap between clamp ears",
        "D": "source dimension D",
        "E": "source dimension E",
        "F": "cross-bolt diameter",
        "G": "formed steel thickness x width",
        "H": "source dimension H",
    },
    "fabrication_blockers": [
        "the formed two-half clamp bend radii and flat developments are not dimensioned",
        "cross-bolt lengths/grades and the complete nut/washer scope are not supplied",
        "the drawing supplies no finished unit weight",
        "forming tolerances, heat treatment and coating are not released",
    ],
}


# line size, loads at 650/750/1000/1050 F, B, C, D, E, F, G t/w, H
_M8_ROWS = (
    (1.5, 700, 635, 450, 335, 46, 27, 124, 105, "5/8", 6, 32, 60),
    (2.0, 700, 635, 450, 335, 54, 27, 149, 130, "5/8", 6, 32, 68),
    (2.5, 700, 635, 450, 335, 59, 27, 156, 137, "5/8", 6, 32, 75),
    (3.0, 700, 635, 450, 335, 70, 27, 170, 151, "5/8", 6, 32, 89),
    (4.0, 1130, 1035, 735, 540, 86, 27, 194, 165, "3/4", 8, 51, 114),
    (5.0, 1130, 1035, 735, 540, 100, 27, 206, 178, "3/4", 8, 51, 127),
    (6.0, 1295, 1185, 840, 625, 121, 37, 252, 218, "7/8", 9, 64, 181),
    (8.0, 1295, 1185, 840, 625, 146, 37, 278, 243, "7/8", 9, 64, 181),
    (10.0, 1465, 1345, 950, 705, 179, 37, 305, 270, "1", 12, 64, 210),
)


def _line_size_label(size: float) -> str:
    return {
        1.5: "1 1/2",
        2.5: "2 1/2",
    }.get(size, f"{size:g}")


def _build_row(raw_row: tuple) -> dict:
    (
        line_size,
        load_650,
        load_750,
        load_1000,
        load_1050,
        b_mm,
        c_mm,
        d_mm,
        e_mm,
        f_diameter,
        g_thickness,
        g_width,
        h_mm,
    ) = raw_row
    return {
        **deepcopy(M8_COMPONENT_INFO),
        "designation": f"PCL-E-{_line_size_label(line_size)}B",
        "line_size_in": line_size,
        "maximum_recommended_load_kg_by_temperature_f": {
            650: load_650,
            750: load_750,
            1000: load_1000,
            1050: load_1050,
        },
        "B_mm": b_mm,
        "C_mm": c_mm,
        "D_mm": d_mm,
        "E_mm": e_mm,
        "F_cross_bolt_diameter_in": f'{f_diameter}"',
        "G_formed_steel_thickness_mm": g_thickness,
        "G_formed_steel_width_mm": g_width,
        "G_formed_steel_size_mm": f"{g_thickness} x {g_width}",
        "H_mm": h_mm,
    }


M8_TABLE = {
    raw_row[0]: _build_row(raw_row)
    for raw_row in _M8_ROWS
}


def get_m8_component() -> dict:
    return deepcopy(M8_COMPONENT_INFO)


def get_m8_by_line_size(line_size: object) -> dict | None:
    size = size_to_float(line_size)
    row = M8_TABLE.get(size) if size is not None else None
    return deepcopy(row) if row else None


def build_m8_item(line_size: object) -> dict | None:
    return get_m8_by_line_size(line_size)
