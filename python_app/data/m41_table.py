"""M-41 Lug Plate Type-P source table (HP6, Rev.1)."""

from __future__ import annotations

from copy import deepcopy

from .component_size_utils import size_to_float


_MATERIAL_CLASSES = {
    "Carbon Steel": {
        "designation_suffix": "",
        "density_kg_per_mm3": 7.85e-6,
    },
    "Alloy Steel": {
        "designation_suffix": "A",
        "density_kg_per_mm3": 7.85e-6,
    },
    "Stainless Steel": {
        "designation_suffix": "S",
        "density_kg_per_mm3": 7.93e-6,
    },
}


M41_COMPONENT_INFO = {
    "component_id": "M-41",
    "name_en": "LUG PLATE TYPE-P",
    "category": "component",
    "pdf_file": "M-41-LUG PLATE P.pdf",
    "source_drawing": (
        "單張-本案有關/中威/LUG-PLATE_TYPE-P_M-41.pdf"
    ),
    "engineering_standard": "HP6-DSD-A4-500-001",
    "project_no": "E25-24",
    "revision": "1",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "source_transcribed": True,
    "blank_weight_ready": True,
    "weight_ready": False,
    "blank_ready": True,
    "fabrication_ready": False,
    "material_classes": _MATERIAL_CLASSES,
    "fabrication_blockers": [
        "M-41 supplies only material class; released plate grade/coating is not specified",
        "the pipe-contact end preparation shows S, T/2-S and a 6 mm weld callout but does not dimension the bevel length/angle",
        "the exact three-dimensional pipe-contact fit-up and weld-preparation contour is not released",
    ],
}


# type, min size, max size, A, B, C, D, S, T, quantity
_M41_ROWS = (
    ("LGP-P-1", 3.0, 8.0, 75, 45, 30, 15, 3, 9, 4),
    ("LGP-P-2", 10.0, 12.0, 100, 60, 40, 15, 3, 12, 4),
    ("LGP-P-3", 14.0, 18.0, 120, 70, 50, 20, 5, 16, 6),
    ("LGP-P-4", 20.0, 24.0, 140, 75, 60, 20, 7, 19, 6),
)


def _build_row(raw_row: tuple, material_class: str) -> dict:
    (
        type_no,
        minimum_size,
        maximum_size,
        a_mm,
        b_mm,
        c_mm,
        d_mm,
        s_mm,
        thickness_mm,
        quantity,
    ) = raw_row
    material = _MATERIAL_CLASSES[material_class]
    gross_area_mm2 = a_mm * c_mm
    triangular_cutout_mm2 = (
        (c_mm - d_mm) * (a_mm - b_mm) / 2
    )
    net_area_mm2 = gross_area_mm2 - triangular_cutout_mm2
    weight_each_kg = (
        net_area_mm2
        * thickness_mm
        * material["density_kg_per_mm3"]
    )
    polygon_points_mm = [
        [0, 0],
        [c_mm, 0],
        [c_mm, a_mm],
        [c_mm - d_mm, a_mm],
        [0, b_mm],
    ]
    return {
        **deepcopy(M41_COMPONENT_INFO),
        "type_no": type_no,
        "designation": (
            f"{type_no}{material['designation_suffix']}"
        ),
        "line_size_min_in": minimum_size,
        "line_size_max_in": maximum_size,
        "A_height_mm": a_mm,
        "B_left_vertical_mm": b_mm,
        "C_overall_width_mm": c_mm,
        "D_top_width_mm": d_mm,
        "S_pipe_end_land_mm": s_mm,
        "T_thickness_mm": thickness_mm,
        "quantity": quantity,
        "material_class": material_class,
        "material_designation_suffix": (
            material["designation_suffix"]
        ),
        "density_kg_per_mm3": material["density_kg_per_mm3"],
        "polygon_points_mm": polygon_points_mm,
        "gross_area_mm2": gross_area_mm2,
        "triangular_cutout_area_mm2": triangular_cutout_mm2,
        "net_area_mm2": net_area_mm2,
        "calculated_blank_weight_each_kg": weight_each_kg,
        "calculated_blank_weight_total_kg": weight_each_kg * quantity,
        "pipe_end_source_callouts": {
            "S_mm": s_mm,
            "T_mm": thickness_mm,
            "groove_depth_text": "T/2-S",
            "weld_callout_mm": 6,
        },
    }


M41_TABLE = {
    row[0]: {
        material_class: _build_row(row, material_class)
        for material_class in _MATERIAL_CLASSES
    }
    for row in _M41_ROWS
}


def get_m41_component() -> dict:
    return deepcopy(M41_COMPONENT_INFO)


def get_m41_by_line_size(
    line_size: object,
    material_class: str = "Carbon Steel",
) -> dict | None:
    size = size_to_float(line_size)
    if size is None or material_class not in _MATERIAL_CLASSES:
        return None
    for raw_row in _M41_ROWS:
        if raw_row[1] <= size <= raw_row[2]:
            return deepcopy(M41_TABLE[raw_row[0]][material_class])
    return None
