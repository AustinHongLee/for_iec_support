"""N-12A vessel-clip continuation and insulation-thickness lookup.

Source: ``N-12A-VESSEL CLIPS.2.pdf`` / DSP-500-006 / N-12A / Rev.0.
"""

from __future__ import annotations

from copy import deepcopy


N12A_COMPONENT_INFO = {
    "component_id": "N-12A",
    "name_en": "VESSEL CLIPS (2 OF 2)",
    "category": "component_cold",
    "pdf_file": "N-12A-VESSEL CLIPS.2.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-12A",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
}


N12A_INSULATION_TABLE = [
    {
        "insulation_min_mm": 0,
        "insulation_max_mm": 140,
        "plate_thickness_mm": 9,
        "A_mm": 100,
    },
    {
        "insulation_min_mm": 141,
        "insulation_max_mm": 215,
        "plate_thickness_mm": 9,
        "A_mm": 180,
    },
    {
        "insulation_min_mm": 216,
        "insulation_max_mm": 300,
        "plate_thickness_mm": 12,
        "A_mm": 260,
    },
]


def get_n12a_component() -> dict:
    return {
        **deepcopy(N12A_COMPONENT_INFO),
        "designation": "CLIP TYPE 3",
        "line_size_range": "insulation thickness <= 300 mm",
        "notes": [
            "Plate thickness and dimension A are selected by insulation thickness.",
            "Clip-plate material is the same as the connected vessel material.",
        ],
    }


def get_n12a_insulation_row(insulation_thickness_mm) -> dict | None:
    try:
        thickness = float(insulation_thickness_mm)
    except (TypeError, ValueError):
        return None
    for row in N12A_INSULATION_TABLE:
        if row["insulation_min_mm"] <= thickness <= row[
            "insulation_max_mm"
        ]:
            return {
                **deepcopy(row),
                "insulation_thickness_mm": thickness,
            }
    return None


def get_n12a_clip_type3(insulation_thickness_mm) -> dict | None:
    insulation = get_n12a_insulation_row(insulation_thickness_mm)
    if not insulation:
        return None
    return {
        **deepcopy(N12A_COMPONENT_INFO),
        "clip_type": 3,
        "insulation_lookup": insulation,
        "A_mm": insulation["A_mm"],
        "plate_thickness_mm": insulation["plate_thickness_mm"],
        "hole_diameter_mm": 22,
        "outer_width_mm": 240,
        "horizontal_hole_pitch_mm": 150,
        "horizontal_edge_mm": 45,
        "fixed_dimensions_mm": {
            "upper_vertical_steps": [50, 50, 50, 50, 50],
            "lower_height": 150,
            "lower_horizontal": [110, 60],
            "lower_brace_projection": 95,
            "lower_brace_height": 45,
            "lower_hole_edge": 60,
        },
        "material_rule": "same as metal to which clip plate is connected",
        "weld_mm": 6,
        "fabrication_ready": False,
        "fabrication_blockers": [
            "N-12A leaves D/G/C and working-point placement to the host support",
            "connected-vessel material must be supplied",
        ],
    }
