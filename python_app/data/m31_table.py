"""M-31 Steel Washer Plate source table (Chung Wei HP6, Rev.1)."""

from __future__ import annotations

import math
from copy import deepcopy

from .component_size_utils import normalize_fractional_size


_DENSITY_KG_PER_MM3 = 7.85e-6

M31_COMPONENT_INFO = {
    "component_id": "M-31",
    "name_en": "STEEL WASHER PLATE",
    "category": "component",
    "pdf_file": "M-31-STEEL WASHER PLATE.pdf",
    "source_drawing": (
        "單張-本案有關/中威/STEEL-WASHER-PLATE_M-31.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "blank_ready": True,
    "blank_weight_ready": True,
    "weight_ready": True,
    "fabrication_ready": False,
    "material": "CARBON STEEL, GRADE NOT SPECIFIED",
    "fabrication_blockers": [
        "M-31 specifies carbon steel but not its released grade/coating",
        "Type 62 FIG-A field location and weld-to-existing-steel extent require project layout confirmation",
    ],
    "source_anomalies": [
        'The Rev.1 source explicitly lists D=75 mm for SWP-3 1/2; '
        "the non-monotonic value is preserved without correction.",
    ],
}


# rod size, square side C, central hole D, plate thickness T
_M31_ROWS = (
    ("3/8", 76, 11, 6),
    ("1/2", 76, 16, 6),
    ("5/8", 76, 19, 9),
    ("3/4", 102, 22, 9),
    ("7/8", 102, 25, 12),
    ("1", 102, 32, 12),
    ("1 1/4", 127, 38, 12),
    ("1 1/2", 127, 44, 19),
    ("1 3/4", 127, 51, 19),
    ("2", 127, 57, 19),
    ("2 1/4", 152, 64, 19),
    ("2 1/2", 152, 70, 19),
    ("2 3/4", 152, 76, 19),
    ("3", 152, 83, 19),
    ("3 1/4", 152, 89, 19),
    ("3 1/2", 178, 75, 19),
    ("3 3/4", 178, 102, 19),
)


def _build_row(raw_row: tuple) -> dict:
    rod_size, side_c_mm, hole_d_mm, thickness_t_mm = raw_row
    gross_area_mm2 = side_c_mm**2
    hole_area_mm2 = math.pi * hole_d_mm**2 / 4
    net_area_mm2 = gross_area_mm2 - hole_area_mm2
    return {
        **deepcopy(M31_COMPONENT_INFO),
        "designation": f"SWP-{rod_size}",
        "rod_size_in": f'{rod_size}"',
        "C_square_side_mm": side_c_mm,
        "D_hole_diameter_mm": hole_d_mm,
        "T_thickness_mm": thickness_t_mm,
        "hole_center_x_mm": side_c_mm / 2,
        "hole_center_y_mm": side_c_mm / 2,
        "gross_area_mm2": gross_area_mm2,
        "hole_area_mm2": hole_area_mm2,
        "net_area_mm2": net_area_mm2,
        "density_kg_per_mm3": _DENSITY_KG_PER_MM3,
        "calculated_net_weight_kg": (
            net_area_mm2
            * thickness_t_mm
            * _DENSITY_KG_PER_MM3
        ),
    }


M31_TABLE = {
    normalize_fractional_size(raw_row[0]): _build_row(raw_row)
    for raw_row in _M31_ROWS
}


def get_m31_component() -> dict:
    return deepcopy(M31_COMPONENT_INFO)


def get_m31_by_rod_size(rod_size: object) -> dict | None:
    row = M31_TABLE.get(normalize_fractional_size(rod_size))
    return deepcopy(row) if row else None
