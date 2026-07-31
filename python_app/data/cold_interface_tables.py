"""Source-backed remaining DSP-500-006 cold-component data.

This module covers the final six N-series cold sheets:

* N-11 expansion bolts;
* N-13/N-14 vessel clips;
* N-15/N-16 U-bands; and
* N-19 Type-A slide plates.

The maturity is deliberately per subpart.  N-15 has a complete flat-bar
development.  N-16 also has a complete U-band development and Member-M stock
cuts, but its finished assembly still needs released joint/hardware details.
N-13/N-14 retain the exact elevation dimensions while their plan contours
remain vessel-geometry dependent.  N-19 can release the two metal rectangles
from its designation, but the PTFE product specification is not supplied.
"""

from __future__ import annotations

from copy import deepcopy
import math
import re


SOURCE_STANDARD = "DSP-500-006"
SOURCE_REVISION = "0"
CARBON_STEEL_DENSITY_KG_PER_MM3 = 7.85e-6
STAINLESS_STEEL_DENSITY_KG_PER_MM3 = 7.93e-6


def _cradle_key(value: object) -> str:
    raw = str(value or "").strip().upper().replace(" ", "")
    if not raw.startswith("CR"):
        raw = f"CR{raw}"
    return raw


N11_COMPONENT_INFO = {
    "component_id": "N-11",
    "name_en": "EXPANSION BOLT",
    "category": "component_cold",
    "pdf_file": "N-11-EXPANSION BOLT.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "dimensional_and_loading_lookup",
    "lookup_ready": True,
    "procurement_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "r_c_strength_basis_kg_cm2": 210,
    "design_safety_factor": 5,
    "n9_grout_lower_types": ["B", "E", "G", "L", "M"],
    "source_conflict": (
        "N-11 Note calls out N-9 lower Types B/E/G/L/M. N-9 Rev.0 Note 2 "
        "instead requires 25 mm grout for A/B/E/G and the sheet contains "
        "A/B/C/D/E/F/G/H/J/K/R/S but no L/M. The confirmed intersection is "
        "B/E/G; Type A is an N-9-only grout requirement."
    ),
    "fabrication_blockers": [
        "N-11 is a purchased cinch-bolt standard and supplies no manufacturer, material grade, coating, or finished unit weight",
        "the fixed-plate thickness K is supplied by the host support and is not encoded in the EB designation",
    ],
}


_N11_ROWS = (
    ("1/4", 76, 19, 32, 693, 892),
    ("3/8", 89, 32, 38, 1602, 1905),
    ("1/2", 114, 35, 57, 2312, 3300),
    ("5/8", 127, 38, 70, 3083, 4503),
    ("3/4", 152, 38, 83, 4417, 6322),
    ("7/8", 178, 57, 95, 5629, 8400),
)


N11_TABLE = {
    size: {
        **deepcopy(N11_COMPONENT_INFO),
        "designation": f"EB-{size}",
        "diameter_in": size,
        "overall_length_mm": overall_length,
        "thread_length_mm": thread_length,
        "r_c_hole_diameter_in": size,
        "r_c_hole_depth_mm": hole_depth,
        "source_tensile_loading_kg": tensile,
        "source_shear_loading_kg": shear,
        "design_tensile_at_sf5_kg": tensile / 5,
        "design_shear_at_sf5_kg": shear / 5,
        "steel_washer_included": True,
    }
    for size, overall_length, thread_length, hole_depth, tensile, shear
    in _N11_ROWS
}


def _bolt_size_key(value: object) -> str | None:
    raw = (
        str(value or "")
        .strip()
        .upper()
        .replace('"', "")
        .replace("IN", "")
        .replace(" ", "")
    )
    raw = re.sub(r"^EB-?", "", raw)
    if raw in N11_TABLE:
        return raw
    try:
        numeric = float(raw)
    except (TypeError, ValueError):
        return None
    for key in N11_TABLE:
        numerator, denominator = key.split("/")
        if math.isclose(numeric, int(numerator) / int(denominator)):
            return key
    return None


def get_n11_component() -> dict:
    return deepcopy(N11_COMPONENT_INFO)


def get_n11_by_size(size: object) -> dict | None:
    key = _bolt_size_key(size)
    row = N11_TABLE.get(key) if key else None
    return deepcopy(row) if row else None


N13_COMPONENT = {
    "component_id": "N-13",
    "name_en": "VESSEL CLIPS TYPE 5",
    "category": "component_cold",
    "pdf_file": "N-13-VESSEL CLIPS.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "parametric_component_geometry",
    "designation": "CLIP TYPE 5",
    "lookup_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "vendor_scope": "VESSEL VENDOR TO FURNISH AND WELD CLIP PLATES",
    "clip_plate_quantity": 2,
    "plate_thickness_mm": 10,
    "elevation": {
        "vessel_edge_height_mm": 160,
        "projection_from_vessel_mm": 170,
        "hole_count_per_plate": 2,
        "hole_diameter_mm": 22,
        "hole_pitch_horizontal_mm": 80,
        "hole_end_margin_mm": 30,
        "support_variants": {
            "L75x75x9": {
                "free_end_depth_mm": 75,
                "top_to_hole_center_mm": 40,
                "hole_center_to_lower_edge_mm": 35,
            },
            "L100x100x10": {
                "free_end_depth_mm": 100,
                "top_to_hole_center_mm": 55,
                "hole_center_to_lower_edge_mm": 45,
            },
        },
        "weld_mm": 6,
    },
    "plan": {
        "nominal_included_angle_deg": 30,
        "minimum_clearance_mm": 10,
        "weld_mm": 6,
        "bolt_nominal_diameter_in": 0.75,
        "variable_inputs": [
            "B",
            "theta",
            "vessel Q or R",
            "insulation thickness t",
        ],
    },
    "material": "SAME AS MATERIAL TO WHICH CLIP PLATE IS CONNECTED",
    "fabrication_blockers": [
        "N-13 plan contour depends on project vessel radius Q/R, angle theta, B and insulation thickness t",
        "the host designation does not release the vessel-side curved cut or both plate working-point coordinates",
        "clip-plate material follows the connected vessel and is not a fixed grade in N-13",
    ],
}


def get_n13_component() -> dict:
    return deepcopy(N13_COMPONENT)


N14_COMPONENT = {
    "component_id": "N-14",
    "name_en": "VESSEL CLIPS TYPE 6",
    "category": "component_cold",
    "pdf_file": "N-14-VESSEL CLIPS.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "parametric_component_geometry",
    "designation": "CLIP TYPE 6",
    "lookup_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "vendor_scope": "VESSEL VENDOR TO FURNISH AND WELD CLIP PLATES",
    "clip_plate_quantity": 2,
    "plate_thickness_mm": 12,
    "elevation": {
        "vessel_edge_height_mm": 190,
        "projection_from_vessel_mm": 170,
        "support_angle_spec": "L130x130x12",
        "support_leg_depth_mm": 130,
        "free_end_plate_depth_mm": 160,
        "upper_vessel_side_offsets_mm": [18, 12],
        "hole_count_per_plate": 4,
        "hole_diameter_mm": 22,
        "bolt_nominal_diameter_in": 0.75,
        "hole_pitch_horizontal_mm": 80,
        "hole_pitch_vertical_mm": 55,
        "hole_end_margin_horizontal_mm": 30,
        "top_to_upper_hole_center_mm": 40,
        "lower_hole_center_to_lower_edge_mm": 35,
        "weld_mm": 9,
    },
    "plan": {
        "nominal_included_angle_deg": 30,
        "minimum_clearance_mm": 10,
        "weld_mm": 8,
        "variable_inputs": [
            "B",
            "theta",
            "vessel Q or R",
            "insulation thickness t",
        ],
    },
    "material": "SAME AS MATERIAL TO WHICH CLIP PLATE IS CONNECTED",
    "fabrication_blockers": [
        "N-14 plan contour depends on project vessel radius Q/R, angle theta, B and insulation thickness t",
        "the host designation does not release the vessel-side curved cut or both plate working-point coordinates",
        "clip-plate material follows the connected vessel and is not a fixed grade in N-14",
    ],
}


def get_n14_component() -> dict:
    return deepcopy(N14_COMPONENT)


N15_COMPONENT_INFO = {
    "component_id": "N-15",
    "name_en": "U-BAND 1",
    "category": "component_cold",
    "pdf_file": "N-15-U-BAND.1.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "dimensional_lookup",
    "designation": "BU-{CRADLE NO.}",
    "cradle_range": "CR2.5~CR12",
    "lookup_ready": True,
    "weight_ready": True,
    "flat_pattern_ready": True,
    "fabrication_ready": False,
    "material": "CARBON STEEL",
    "density_kg_per_mm3": CARBON_STEEL_DENSITY_KG_PER_MM3,
    "fabrication_blockers": [
        "N-15 specifies carbon steel but does not release its material grade",
    ],
}


_N15_ROWS = (
    ("CR2.5", 50, 6, 42, 79, 96),
    ("CR3", 50, 6, 50, 87, 112),
    ("CR3.5", 50, 6, 57, 94, 126),
    ("CR4", 50, 6, 63, 100, 138),
    ("CR4.5", 50, 6, 70, 107, 152),
    ("CR5", 75, 10, 76, 113, 172),
    ("CR6", 75, 10, 92, 129, 204),
    ("CR7", 75, 10, 105, 142, 230),
    ("CR8", 75, 10, 117, 154, 254),
    ("CR9", 75, 10, 130, 167, 280),
    ("CR10", 75, 10, 146, 183, 312),
    ("CR11", 75, 10, 158, 195, 336),
    ("CR12", 75, 10, 171, 208, 362),
)


def _build_n15_row(
    cradle_no: str,
    width_mm: int,
    thickness_mm: int,
    inside_radius_mm: int,
    straight_leg_mm: int,
    outside_span_mm: int,
) -> dict:
    neutral_radius = inside_radius_mm + thickness_mm / 2
    developed_length = (
        math.pi * neutral_radius + 2 * straight_leg_mm
    )
    calculated_weight = (
        developed_length
        * width_mm
        * thickness_mm
        * CARBON_STEEL_DENSITY_KG_PER_MM3
    )
    return {
        **deepcopy(N15_COMPONENT_INFO),
        "designation": f"BU-{cradle_no}",
        "cradle_no": cradle_no,
        "D_width_mm": width_mm,
        "T_thickness_mm": thickness_mm,
        "RG_inside_radius_mm": inside_radius_mm,
        "H_straight_leg_mm": straight_leg_mm,
        "W_outside_span_mm": outside_span_mm,
        "outside_span_formula": "2 * (RG + T)",
        "neutral_radius_mm": neutral_radius,
        "developed_length_formula": "pi * (RG + T / 2) + 2 * H",
        "developed_length_mm": developed_length,
        "calculated_weight_kg": calculated_weight,
    }


N15_TABLE = {
    cradle: _build_n15_row(cradle, width, thickness, radius, height, span)
    for cradle, width, thickness, radius, height, span in _N15_ROWS
}


def get_n15_component() -> dict:
    return deepcopy(N15_COMPONENT_INFO)


def get_n15_by_cradle(cradle_no: object) -> dict | None:
    row = N15_TABLE.get(_cradle_key(cradle_no))
    return deepcopy(row) if row else None


N16_COMPONENT_INFO = {
    "component_id": "N-16",
    "name_en": "U-BAND 2",
    "category": "component_cold",
    "pdf_file": "N-16-U-BAND.2.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "dimensional_lookup",
    "designation": "BU-{CRADLE NO.}",
    "cradle_range": "CR14~CR40",
    "lookup_ready": True,
    "band_weight_ready": True,
    "band_flat_pattern_ready": True,
    "member_weight_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "material": "CARBON STEEL",
    "density_kg_per_mm3": CARBON_STEEL_DENSITY_KG_PER_MM3,
    "member_quantity": 2,
    "band_fabrication_blockers": [
        "N-15/N-16 two-sheet standard specifies carbon steel but does not release its material grade",
    ],
    "fabrication_blockers": [
        "N-15/N-16 two-sheet standard specifies carbon steel but does not release its material grade",
        "N-16 releases U-band flat development and two Member-M stock cuts, but not a complete joint preparation/weld recipe",
        "machine-bolt material/grade, nuts and finished unit weights are not specified",
        "the N-16 sheet does not independently state the released total hole/bolt quantity for every host arrangement",
    ],
}


# cradle, B, D, T, RG, H, W, L, G, I, J, K, Member M
_N16_ROWS = (
    ("CR14", 30, 75, 12, 187, 214, 398, 130, 60, 30, 15, '1/2" x 45', "L65x65x6"),
    ("CR15", 30, 75, 12, 200, 227, 424, 135, 60, 30, 15, '1/2" x 45', "L65x65x6"),
    ("CR16", 40, 75, 12, 212, 239, 448, 140, 70, 30, 15, '1/2" x 45', "L75x75x9"),
    ("CR17", 40, 75, 12, 225, 252, 474, 150, 80, 30, 15, '1/2" x 45', "L75x75x9"),
    ("CR18", 40, 90, 12, 238, 265, 500, 155, 80, 40, 15, '1/2" x 45', "L75x75x9"),
    ("CR19", 40, 90, 12, 250, 277, 524, 160, 80, 40, 15, '1/2" x 45', "L75x75x9"),
    ("CR20", 40, 90, 16, 267, 294, 566, 170, 90, 40, 19, '5/8" x 50', "L75x75x9"),
    ("CR21", 55, 90, 16, 279, 306, 590, 175, 90, 50, 19, '5/8" x 50', "L100x100x10"),
    ("CR22", 55, 100, 16, 292, 319, 616, 180, 90, 50, 19, '5/8" x 50', "L100x100x10"),
    ("CR23", 55, 100, 16, 305, 332, 642, 185, 90, 50, 19, '5/8" x 50', "L100x100x10"),
    ("CR24", 55, 100, 16, 317, 344, 666, 190, 90, 50, 19, '5/8" x 50', "L100x100x10"),
    ("CR25", 55, 100, 16, 330, 357, 692, 200, 100, 50, 19, '5/8" x 50', "L100x100x10"),
    ("CR26", 25, 130, 20, 343, 370, 726, 205, 105, 50, 19, '5/8" x 55', "C180x75x7x10.5"),
    ("CR27", 25, 130, 20, 355, 382, 750, 210, 110, 50, 19, '5/8" x 55', "C180x75x7x10.5"),
    ("CR28", 25, 130, 20, 368, 395, 776, 220, 120, 50, 19, '5/8" x 55', "C180x75x7x10.5"),
    ("CR29", 25, 130, 20, 381, 408, 802, 225, 125, 50, 19, '5/8" x 55', "C180x75x7x10.5"),
    ("CR30", 25, 130, 25, 394, 421, 838, 230, 130, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR31", 25, 130, 25, 410, 436, 870, 235, 135, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR32", 25, 130, 25, 422, 449, 894, 245, 145, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR33", 25, 130, 25, 435, 461, 920, 250, 150, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR34", 25, 130, 25, 448, 475, 946, 255, 155, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR35", 25, 130, 25, 460, 487, 970, 260, 160, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR36", 25, 130, 25, 473, 500, 996, 265, 165, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR37", 25, 130, 25, 486, 513, 1022, 275, 175, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR38", 25, 130, 25, 498, 525, 1046, 280, 180, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR39", 25, 130, 25, 511, 538, 1072, 285, 185, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
    ("CR40", 25, 130, 25, 524, 551, 1098, 290, 190, 50, 19, '5/8" x 60', "C180x75x7x10.5"),
)


_MEMBER_WEIGHT_KG_PER_M = {
    "L65x65x6": 5.91,
    "L75x75x9": 9.96,
    "L100x100x10": 15.0,
    "C180x75x7x10.5": 21.0,
}

_MEMBER_WEIGHT_BASIS = {
    "source": "python_app/data/steel_sections.py shared project lookup",
    "source_standard": None,
    "status": "project_lookup_requires_standard_confirmation",
    "note": (
        "N-16 releases member section and cut length but no kg/m. "
        "L100x100x10=15.0 and C180x75x7=21.0 are inherited project lookup "
        "values; the governing steel standard/edition is not recorded."
    ),
}


def _build_n16_row(
    cradle_no: str,
    b_mm: int,
    width_mm: int,
    thickness_mm: int,
    inside_radius_mm: int,
    h_mm: int,
    outside_span_mm: int,
    member_length_mm: int,
    g_mm: int,
    i_mm: int,
    hole_diameter_mm: int,
    machine_bolt: str,
    member_spec: str,
) -> dict:
    straight_leg = h_mm + 10
    neutral_radius = inside_radius_mm + thickness_mm / 2
    developed_length = math.pi * neutral_radius + 2 * straight_leg
    band_weight = (
        developed_length
        * width_mm
        * thickness_mm
        * CARBON_STEEL_DENSITY_KG_PER_MM3
    )
    member_weight_per_m = _MEMBER_WEIGHT_KG_PER_M[member_spec]
    member_total_weight = (
        2 * member_length_mm / 1000 * member_weight_per_m
    )
    return {
        **deepcopy(N16_COMPONENT_INFO),
        "designation": f"BU-{cradle_no}",
        "cradle_no": cradle_no,
        "B_mm": b_mm,
        "D_width_mm": width_mm,
        "T_thickness_mm": thickness_mm,
        "RG_inside_radius_mm": inside_radius_mm,
        "H_to_attachment_reference_mm": h_mm,
        "end_extension_below_H_mm": 10,
        "straight_leg_length_mm": straight_leg,
        "W_outside_span_mm": outside_span_mm,
        "outside_span_formula": "2 * (RG + T)",
        "neutral_radius_mm": neutral_radius,
        "developed_length_formula": (
            "pi * (RG + T / 2) + 2 * (H + 10)"
        ),
        "developed_length_mm": developed_length,
        "band_calculated_weight_kg": band_weight,
        "member_M": {
            "spec": member_spec,
            "quantity": 2,
            "length_each_mm": member_length_mm,
            "weight_per_m_kg": member_weight_per_m,
            "weight_basis": deepcopy(_MEMBER_WEIGHT_BASIS),
            "calculated_total_weight_kg": member_total_weight,
            "G_mm": g_mm,
            "I_mm": i_mm,
            "hole_diameter_J_mm": hole_diameter_mm,
            "machine_bolt_K": machine_bolt,
        },
        "known_steel_weight_kg": band_weight + member_total_weight,
    }


N16_TABLE = {
    row[0]: _build_n16_row(*row)
    for row in _N16_ROWS
}


def get_n16_component() -> dict:
    return deepcopy(N16_COMPONENT_INFO)


def get_n16_by_cradle(cradle_no: object) -> dict | None:
    row = N16_TABLE.get(_cradle_key(cradle_no))
    return deepcopy(row) if row else None


N19_COMPONENT_INFO = {
    "component_id": "N-19",
    "name_en": "SLIDE PLATE TYPE-A",
    "category": "component_cold",
    "pdf_file": "N-19-SLIDE PLATE A.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "parametric_designation",
    "designation": "SLP-A-{AA}{BB}-{LL}{WW}; each pair is dimension / 10 mm",
    "lookup_ready": True,
    "metal_weight_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "overall_stack_height_mm": 10,
    "upper_plate": {
        "thickness_mm": 3.6,
        "material": "STAINLESS STEEL, GRADE NOT SPECIFIED",
        "finish": "NO. 2B BOTH SIDES",
    },
    "lower_backing_plate": {
        "thickness_mm": 3.6,
        "material": "CARBON STEEL, GRADE NOT SPECIFIED",
        "ptfe_edge_margin_mm": 12,
    },
    "ptfe_slide_element": {
        "material": "PTFE, PRODUCT GRADE NOT SPECIFIED",
        "thickness_mm": None,
        "derivable_thickness_mm": 2.8,
        "derivation": "10 overall - 3.6 stainless - 3.6 carbon steel",
        "derivation_status": "source_implied_not_product_released",
    },
    "source_conflict": (
        "N-19 Note calls L/W the lower-plate dimensions, while Section B-B "
        "places L/W on the hatched PTFE element with 12 mm edge margins to "
        "the carbon-steel backing plate. Runtime retains the section-view "
        "interpretation (backing=L+24 by W+24) pending owner confirmation."
    ),
    "supporting_surface_weld": "3 mm fillet, 12 long at 100 pitch (TYP.)",
    "fabrication_blockers": [
        "N-19 gives a 10 mm overall stack but does not explicitly release PTFE sheet thickness, grade, density or bonding method",
        "the stainless and carbon-steel grades are not specified",
        "metal plates can be cut from the designation, but the complete slide assembly remains procurement/fabrication partial",
    ],
}


_N19_DESIGNATION = re.compile(
    r"^SLP-A-(\d{2})(\d{2})-(\d{2})(\d{2})$",
    re.IGNORECASE,
)


def get_n19_component() -> dict:
    return deepcopy(N19_COMPONENT_INFO)


def resolve_n19_designation(designation: object) -> dict | None:
    normalized = str(designation or "").strip().upper().replace(" ", "")
    match = _N19_DESIGNATION.fullmatch(normalized)
    if not match:
        return None
    a_mm, b_mm, l_mm, w_mm = (
        int(code) * 10
        for code in match.groups()
    )
    if min(a_mm, b_mm, l_mm, w_mm) <= 0:
        return None
    upper_weight = (
        a_mm
        * b_mm
        * 3.6
        * STAINLESS_STEEL_DENSITY_KG_PER_MM3
    )
    backing_length = l_mm + 24
    backing_width = w_mm + 24
    backing_weight = (
        backing_length
        * backing_width
        * 3.6
        * CARBON_STEEL_DENSITY_KG_PER_MM3
    )
    return {
        **deepcopy(N19_COMPONENT_INFO),
        "designation": normalized,
        "upper_plate": {
            **deepcopy(N19_COMPONENT_INFO["upper_plate"]),
            "A_length_mm": a_mm,
            "B_width_mm": b_mm,
            "calculated_weight_kg": upper_weight,
        },
        "lower_backing_plate": {
            **deepcopy(N19_COMPONENT_INFO["lower_backing_plate"]),
            "outside_length_mm": backing_length,
            "outside_width_mm": backing_width,
            "calculated_weight_kg": backing_weight,
        },
        "ptfe_slide_element": {
            **deepcopy(N19_COMPONENT_INFO["ptfe_slide_element"]),
            "L_length_mm": l_mm,
            "W_width_mm": w_mm,
        },
        "known_metal_weight_kg": upper_weight + backing_weight,
    }
