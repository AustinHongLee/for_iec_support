"""M-12 Riser Clamp Type-B source table (HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .riser_clamp_common import (
    build_riser_clamp_row,
    normalize_riser_line_size,
)


M12_COMPONENT_INFO = {
    "component_id": "M-12",
    "name_en": "RISER CLAMP TYPE-B",
    "category": "component",
    "pdf_file": "M-12-RISER CLAMP B.pdf",
    "source_drawing": (
        "單張-本案有關/中威/RISER-CLAMP_TYPE-B_M-12.pdf"
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
    "fabrication_blockers": [
        "M-12 specifies carbon steel but not its released grade/coating",
        "the size-specific L table conflicts with the fixed 150/50 sketch; L governs known strip weight but the individual straight-leg cuts remain unresolved",
        "bolt-hole diameter, hole-center locations and end corner radii are not dimensioned",
        "bend clearance/tolerance against the supported pipe is not specified",
        "bolt/nut grade, nut scope and finished fastener weight are not supplied",
    ],
}


# line size, max load, L, stock t, stock width, bolt dia, bolt length
_M12_ROWS = (
    (0.75, 115, 238, 5, 32, "3/8", 40),
    (1.0, 115, 244, 5, 32, "3/8", 40),
    (1.25, 115, 254, 6, 32, "3/8", 40),
    (1.5, 115, 264, 6, 32, "3/8", 40),
    (2.0, 115, 273, 6, 32, "7/16", 40),
    (2.5, 175, 286, 6, 32, "7/16", 40),
    (3.0, 240, 305, 6, 32, "7/16", 40),
    (3.5, 305, 330, 6, 38, "1/2", 40),
    (4.0, 370, 343, 6, 38, "1/2", 40),
    (5.0, 525, 368, 6, 51, "1/2", 40),
    (6.0, 715, 394, 6, 51, "1/2", 40),
    (8.0, 1135, 470, 10, 51, "5/8", 60),
    (10.0, 1135, 527, 10, 51, "5/8", 60),
    (12.0, 1225, 578, 13, 51, "5/8", 70),
    (14.0, 1225, 610, 13, 51, "5/8", 70),
    (16.0, 1320, 660, 16, 64, "3/4", 80),
    (18.0, 1320, 711, 16, 64, "3/4", 80),
    (20.0, 1320, 762, 16, 64, "3/4", 80),
)


M12_TABLE = {
    row[0]: build_riser_clamp_row(
        M12_COMPONENT_INFO,
        variant="B",
        line_size_in=row[0],
        maximum_recommended_load_kg=row[1],
        installed_overall_mm=row[2],
        stock_thickness_mm=row[3],
        stock_width_mm=row[4],
        bolt_diameter_in=row[5],
        bolt_length_mm=row[6],
        left_straight_projection_mm=150,
        right_straight_projection_mm=50,
    )
    for row in _M12_ROWS
}


def get_m12_component() -> dict:
    return deepcopy(M12_COMPONENT_INFO)


def get_m12_by_line_size(line_size: object) -> dict | None:
    key = normalize_riser_line_size(line_size)
    row = M12_TABLE.get(key) if key is not None else None
    return deepcopy(row) if row else None
