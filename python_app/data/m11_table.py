"""M-11 Riser Clamp Type-A source table (HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .riser_clamp_common import (
    build_riser_clamp_row,
    normalize_riser_line_size,
)


M11_COMPONENT_INFO = {
    "component_id": "M-11",
    "name_en": "RISER CLAMP TYPE-A",
    "category": "component",
    "pdf_file": "M-11-RISER CLAMP A.pdf",
    "source_drawing": (
        "單張-本案有關/中威/RISER-CLAMP_TYPE-A_M-11.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "strip_weight_ready": True,
    "weight_ready": False,
    "flat_pattern_ready": False,
    "fabrication_ready": False,
    "material": "CARBON STEEL, GRADE NOT SPECIFIED",
    "reference": "GRINNELL FIG. 261 OR EQ.",
    "fabrication_blockers": [
        "M-11 specifies carbon steel but not its released grade/coating",
        "bolt-hole diameter, hole-center locations and end corner radii are not dimensioned",
        "bend clearance/tolerance against the supported pipe is not specified",
        "bolt/nut grade, nut scope and finished fastener weight are not supplied",
    ],
}


# line size, max load, A, stock t, stock width, bolt dia, bolt length
_M11_ROWS = (
    (0.75, 115, 238, 5, 32, "3/8", 40),
    (1.0, 115, 244, 5, 32, "3/8", 40),
    (1.25, 115, 254, 6, 32, "3/8", 40),
    (1.5, 115, 264, 6, 32, "3/8", 40),
    (2.0, 115, 273, 6, 32, "7/16", 40),
    (2.5, 175, 286, 6, 32, "7/16", 40),
    (3.0, 240, 305, 6, 32, "7/16", 40),
    (3.5, 305, 330, 6, 38, "1/2", 50),
    (4.0, 370, 343, 6, 38, "1/2", 50),
    (5.0, 525, 368, 6, 51, "1/2", 50),
    (6.0, 715, 394, 6, 51, "1/2", 50),
    (8.0, 1135, 470, 9, 51, "5/8", 70),
    (10.0, 1135, 514, 9, 51, "5/8", 70),
    (12.0, 1225, 578, 12, 51, "5/8", 70),
    (14.0, 1225, 610, 12, 51, "5/8", 70),
    (16.0, 1320, 660, 16, 64, "3/4", 80),
    (18.0, 1320, 711, 16, 64, "3/4", 80),
    (20.0, 1320, 762, 16, 64, "3/4", 80),
)


M11_TABLE = {
    row[0]: build_riser_clamp_row(
        M11_COMPONENT_INFO,
        variant="A",
        line_size_in=row[0],
        maximum_recommended_load_kg=row[1],
        installed_overall_mm=row[2],
        stock_thickness_mm=row[3],
        stock_width_mm=row[4],
        bolt_diameter_in=row[5],
        bolt_length_mm=row[6],
    )
    for row in _M11_ROWS
}


def get_m11_component() -> dict:
    return deepcopy(M11_COMPONENT_INFO)


def get_m11_by_line_size(line_size: object) -> dict | None:
    key = normalize_riser_line_size(line_size)
    row = M11_TABLE.get(key) if key is not None else None
    return deepcopy(row) if row else None
