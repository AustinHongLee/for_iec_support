"""N-12 vessel-clip dimensional lookup.

Source: N-12 Rev.0 (clip Types 1/2) plus N-12A Rev.0 Note 2
(insulation-thickness selection).
"""

from __future__ import annotations

from copy import deepcopy

from .n12a_table import get_n12a_insulation_row


N12_COMPONENT_INFO = {
    "component_id": "N-12",
    "name_en": "VESSEL CLIPS (1 OF 2)",
    "category": "component_cold",
    "pdf_file": "N-12-VESSEL CLIPS.1.pdf",
    "engineering_standard": "DSP-500-006",
    "drawing_no": "N-12/N-12A",
    "revision": "0",
    "table_kind": "dimensional_lookup",
    "lookup_ready": True,
    "weight_ready": False,
    "transcription_status": "drawing_reverified",
}


def get_n12_component() -> dict:
    return {
        **deepcopy(N12_COMPONENT_INFO),
        "designation": "CLIP TYPE {1|2}",
        "line_size_range": "insulation thickness <= 300 mm",
        "notes": [
            "Plate thickness and dimension A come from N-12A Note 2.",
            "Clip-plate material is the same as the connected vessel material.",
        ],
    }


def get_n12_clip(clip_type, insulation_thickness_mm) -> dict | None:
    try:
        clip = int(clip_type)
    except (TypeError, ValueError):
        return None
    if clip not in {1, 2}:
        return None
    insulation = get_n12a_insulation_row(insulation_thickness_mm)
    if not insulation:
        return None
    return {
        **deepcopy(N12_COMPONENT_INFO),
        "clip_type": clip,
        "plan_layout": (
            "single radial clip"
            if clip == 1
            else "opposed pair about working point"
        ),
        "insulation_lookup": insulation,
        "A_mm": insulation["A_mm"],
        "plate_thickness_mm": insulation["plate_thickness_mm"],
        "hole_diameter_mm": 22,
        "outer_face_width_mm": 190,
        "outer_face_height_mm": 350,
        "horizontal_hole_pitch_mm": 100,
        "vertical_hole_pitch_mm": 200,
        "horizontal_edge_mm": 45,
        "cross_plate_to_hole_center_mm": 50,
        "outer_projection_mm": 25,
        "material_rule": "same as metal to which clip plate is connected",
        "weld_mm": 6,
        "fabrication_ready": False,
        "fabrication_blockers": [
            "host support must supply vessel radius, C/G and working-point placement",
            "connected-vessel material must be supplied",
        ],
    }
