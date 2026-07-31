"""Source-backed DSP-500-006 cold-support core tables (N-1~N-5/N-20~N-26).

The source drawings separate the cold-support definition into three layers:

* N-1/N-4: cradle and galvanized protection-shield dimensions.
* N-2/N-3/N-5: insulation layers, axial construction rules, and material data.
* N-20~N-26: pipe/insulation-to-cradle selection and allowable loads.

No item weight is released here.  The drawings do not uniquely define every
net contour, material grade, or finished development needed for fabrication.
"""

from __future__ import annotations

from copy import deepcopy


SOURCE_STANDARD = "DSP-500-006"
SOURCE_REVISION = "0"


def _cradle_key(value: object) -> str:
    raw = str(value or "").strip().upper().replace(" ", "")
    if not raw.startswith("CR"):
        raw = f"CR{raw}"
    return raw


CRADLE_RADII_MM = {
    "CR2.5": 36,
    "CR3": 44,
    "CR3.5": 51,
    "CR4": 57,
    "CR4.5": 64,
    "CR5": 70,
    "CR6": 84,
    "CR7": 97,
    "CR8": 109,
    "CR9": 122,
    "CR10": 137,
    "CR11": 149,
    "CR12": 162,
    "CR14": 178,
    "CR15": 191,
    "CR16": 203,
    "CR17": 216,
    "CR18": 229,
    "CR19": 241,
    "CR20": 254,
    "CR21": 266,
    "CR22": 279,
    "CR23": 292,
    "CR24": 304,
    "CR25": 317,
    "CR26": 330,
    "CR27": 342,
    "CR28": 355,
    "CR29": 368,
    "CR30": 381,
    "CR31": 394,
    "CR32": 407,
    "CR33": 419,
    "CR34": 433,
    "CR35": 445,
    "CR36": 458,
    "CR37": 471,
    "CR38": 483,
    "CR39": 496,
    "CR40": 509,
    "CR41": 520,
    "CR42": 533,
    "CR43": 546,
    "CR44": 558,
    "CR45": 571,
    "CR46": 584,
    "CR47": 597,
    "CR48": 609,
    "CR49": 622,
    "CR50": 635,
    "CR51": 647,
    "CR52": 660,
    "CR53": 673,
    "CR54": 685,
    "CR55": 698,
    "CR56": 711,
    "CR57": 724,
    "CR58": 735,
    "CR59": 749,
    "CR60": 762,
    "CR61": 774,
    "CR62": 787,
    "CR63": 800,
    "CR64": 812,
    "CR65": 825,
    "CR66": 838,
    "CR67": 851,
    "CR68": 863,
    "CR69": 876,
    "CR70": 889,
    "CR71": 901,
    "CR72": 914,
    "CR73": 927,
    "CR74": 939,
    "CR75": 952,
    "CR76": 965,
    "CR77": 978,
    "CR78": 991,
    "CR79": 1003,
    "CR80": 1016,
}


def _small_t1_mm(cradle_no: str) -> int | None:
    number = float(cradle_no[2:])
    if number <= 5:
        return 3
    if number <= 19:
        return 5
    if number <= 30:
        return 10
    if number <= 44:
        return 12
    return None


def _large_t1_mm(cradle_no: str) -> int | None:
    number = float(cradle_no[2:])
    if 32 <= number <= 48:
        return 10
    if 49 <= number <= 80:
        return 12
    return None


N1_LARGE_A_MM = {
    "CR32": 559,
    "CR33": 575,
    "CR34": 593,
    "CR35": 609,
    "CR36": 625,
    "CR37": 642,
    "CR38": 658,
    "CR39": 675,
    "CR40": 692,
    "CR41": 706,
    "CR42": 723,
    "CR43": 740,
    "CR44": 755,
    "CR45": 772,
    "CR46": 789,
    "CR47": 806,
    "CR48": 822,
    "CR49": 839,
    "CR50": 855,
    "CR51": 871,
    "CR52": 888,
    "CR53": 905,
    "CR54": 920,
    "CR55": 937,
    "CR56": 954,
    "CR57": 971,
    "CR58": 987,
    "CR59": 1004,
    "CR60": 1020,
    "CR61": 1036,
    "CR62": 1053,
    "CR63": 1070,
    "CR64": 1086,
    "CR65": 1103,
    "CR66": 1120,
    "CR67": 1136,
    "CR68": 1152,
    "CR69": 1169,
    "CR70": 1186,
    "CR71": 1201,
    "CR72": 1218,
    "CR73": 1235,
    "CR74": 1250,
    "CR75": 1267,
    "CR76": 1284,
    "CR77": 1301,
    "CR78": 1318,
    "CR79": 1334,
    "CR80": 1350,
}


def get_n1_dimensions(cradle_no: object, pipe_size_in: float) -> dict | None:
    """Return the N-1 row for the small- or large-pipe table."""
    key = _cradle_key(cradle_no)
    radius = CRADLE_RADII_MM.get(key)
    if radius is None:
        return None
    if 24 < pipe_size_in < 30:
        return None
    family = "small_pipe_24_and_under" if pipe_size_in <= 24 else "large_pipe_30_and_over"
    t1 = _small_t1_mm(key) if pipe_size_in <= 24 else _large_t1_mm(key)
    if t1 is None:
        return None
    row = {
        "component_id": "N-1",
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "cradle_no": key,
        "pipe_family": family,
        "R_mm": radius,
        "T1_mm": t1,
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": [
            "N-1 does not identify the steel cradle material grade",
            "N-1 tabulates R/T1 but does not release every host-specific net contour or flat development",
        ],
    }
    if pipe_size_in > 24:
        row.update(
            {
                "A_mm": N1_LARGE_A_MM[key],
                "B_mm": 12 if float(key[2:]) <= 48 else 16,
            }
        )
    return row


N2_LAYER_SYSTEMS = {
    25: (25, None, None),
    40: (40, None, None),
    50: (50, None, None),
    65: (65, None, None),
    75: (75, None, None),
    90: (40, 50, None),
    100: (50, 50, None),
    115: (50, 65, None),
    125: (50, 75, None),
    140: (65, 75, None),
    150: (50, 50, 50),
    165: (50, 50, 65),
    175: (50, 50, 75),
    190: (50, 65, 75),
    200: (50, 75, 75),
}


def get_n2_layer_system(total_thickness_mm: object) -> dict | None:
    try:
        thickness = int(float(total_thickness_mm))
    except (TypeError, ValueError):
        return None
    values = N2_LAYER_SYSTEMS.get(thickness)
    if not values:
        return None
    inner, middle, outer = values
    layer_count = sum(value is not None for value in values)
    return {
        "component_id": "N-2",
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "total_insulation_thickness_mm": thickness,
        "inner_layer_mm": inner,
        "middle_layer_mm": middle,
        "outer_layer_mm": outer,
        "layer_count": layer_count,
        "material": "HIGH DENSITY POLYURETHANE",
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": [
            "N-2 gives layer thicknesses but no released net volume or piece count",
            "N-2 requires the layer system to match the project cold-insulation system",
        ],
    }


def get_n3_construction(
    total_thickness_mm: object,
    cradle_length_mm: object | None = None,
) -> dict:
    """Return N-3 construction rules without inventing missing C-14 details."""
    layer = get_n2_layer_system(total_thickness_mm)
    length = None
    try:
        if cradle_length_mm is not None and float(cradle_length_mm) > 0:
            length = float(cradle_length_mm)
            if length.is_integer():
                length = int(length)
    except (TypeError, ValueError):
        length = None
    layer_count = layer["layer_count"] if layer else None
    blockers = [
        "N-3 Note 1 delegates dimensions and information not shown to C-14",
        "N-3 does not release the molded half-shell net contours or piece count",
    ]
    if layer_count == 3:
        blockers.append(
            "N-3 illustrates single- and double-layer construction only; the N-2 three-layer sequence needs project detailing"
        )
    if length is None:
        blockers.append("host cradle length L is required to resolve axial jacket/foam lengths")
    return {
        "component_id": "N-3",
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "total_insulation_thickness_mm": (
            layer["total_insulation_thickness_mm"] if layer else None
        ),
        "layer_count": layer_count,
        "construction_type": {
            1: "single_layer",
            2: "double_layer",
            3: "three_layer_requires_project_detail",
        }.get(layer_count, "unresolved_layer_system"),
        "cradle_length_L_mm": length,
        "jacket_length_mm": length + 100 if length is not None else None,
        "foam_and_vapor_barrier_length_mm": (
            length + 150 if length is not None else None
        ),
        "inner_layer_foam_length_mm": (
            length + 200
            if length is not None and layer_count and layer_count >= 2
            else None
        ),
        "lookup_ready": layer is not None,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": blockers,
    }


def _n4_t2_mm(cradle_no: str) -> float | None:
    number = float(cradle_no[2:])
    if number <= 12:
        return 1.6
    if 14 <= number <= 39:
        return 3.0
    if 40 <= number <= 80:
        return 5.0
    return None


def get_n4_shield(cradle_no: object, cradle_length_mm: object | None = None) -> dict | None:
    key = _cradle_key(cradle_no)
    radius = CRADLE_RADII_MM.get(key)
    t2 = _n4_t2_mm(key) if radius is not None else None
    if radius is None or t2 is None:
        return None
    length = None
    try:
        if cradle_length_mm is not None and float(cradle_length_mm) > 0:
            length = float(cradle_length_mm)
            if length.is_integer():
                length = int(length)
    except (TypeError, ValueError):
        length = None
    blockers = [
        "N-4 specifies galvanized protection shield but no steel grade or coating mass",
        "N-4 does not dimension the developed arc/edge allowance needed for a released flat pattern",
    ]
    if length is None:
        blockers.append("host steel cradle length is required for the shield axial cut")
    return {
        "component_id": "N-4",
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "shield_mark_no": key,
        "R_mm": radius,
        "T2_mm": t2,
        "axial_length_mm": length,
        "material": "GALVANIZED INSULATION PROTECTION SHIELD",
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": blockers,
    }


N5_MATERIAL_PROPERTIES = {
    160: {
        "density_lb_ft3": 10,
        "density_kg_m3": 160,
        "test_temperature_f": -256,
        "test_temperature_c": -160,
        "test_piece_foam_length_in": 6.0,
        "test_piece_foam_length_mm": 152,
        "load_at_yield_lb": 5900,
        "load_at_yield_kg": 2676,
        "load_at_1pct_deflection_lb": 2625,
        "load_at_1pct_deflection_kg": 1191,
        "compressive_strength_yield_psi": 534,
        "compressive_strength_yield_kg_cm2": 38,
        "compressive_strength_1pct_psi": 238,
        "compressive_strength_1pct_kg_cm2": 17,
        "deformation_at_yield_pct": 2.8,
        "compressive_modulus_psi": 19500,
        "compressive_modulus_kg_cm2": 1371,
        "engineering_strength_sf5_psi": 106.8,
        "engineering_strength_sf5_kg_cm2": 7.51,
        "ambient_compressive_strength_yield_psi": 129,
        "ambient_compressive_strength_yield_kg_cm2": 9.0,
    },
    224: {
        "density_lb_ft3": 14,
        "density_kg_m3": 224,
        "test_temperature_f": -256,
        "test_temperature_c": -160,
        "test_piece_foam_length_in": 6.0,
        "test_piece_foam_length_mm": 152,
        "load_at_yield_lb": 9200,
        "load_at_yield_kg": 4173,
        "load_at_1pct_deflection_lb": 3675,
        "load_at_1pct_deflection_kg": 1667,
        "compressive_strength_yield_psi": 833,
        "compressive_strength_yield_kg_cm2": 59,
        "compressive_strength_1pct_psi": 333,
        "compressive_strength_1pct_kg_cm2": 23,
        "deformation_at_yield_pct": 3.1,
        "compressive_modulus_psi": 27200,
        "compressive_modulus_kg_cm2": 1912,
        "engineering_strength_sf5_psi": 166.6,
        "engineering_strength_sf5_kg_cm2": 11.71,
        "ambient_compressive_strength_yield_psi": 223,
        "ambient_compressive_strength_yield_kg_cm2": 15.6,
    },
    320: {
        "density_lb_ft3": 20,
        "density_kg_m3": 320,
        "test_temperature_f": -256,
        "test_temperature_c": -160,
        "test_piece_foam_length_in": 6.0,
        "test_piece_foam_length_mm": 152,
        "load_at_yield_lb": 14600,
        "load_at_yield_kg": 6622,
        "load_at_1pct_deflection_lb": 4200,
        "load_at_1pct_deflection_kg": 1905,
        "compressive_strength_yield_psi": 1322,
        "compressive_strength_yield_kg_cm2": 93,
        "compressive_strength_1pct_psi": 380,
        "compressive_strength_1pct_kg_cm2": 27,
        "deformation_at_yield_pct": 3.2,
        "compressive_modulus_psi": 40000,
        "compressive_modulus_kg_cm2": 2812,
        "engineering_strength_sf5_psi": 264.4,
        "engineering_strength_sf5_kg_cm2": 18.59,
        "ambient_compressive_strength_yield_psi": 530,
        "ambient_compressive_strength_yield_kg_cm2": 37.0,
    },
}


def get_n5_material_properties(density_kg_m3: object) -> dict | None:
    try:
        density = int(float(density_kg_m3))
    except (TypeError, ValueError):
        return None
    row = N5_MATERIAL_PROPERTIES.get(density)
    if not row:
        return None
    result = deepcopy(row)
    result.update(
        {
            "component_id": "N-5",
            "engineering_standard": SOURCE_STANDARD,
            "revision": SOURCE_REVISION,
            "material": "MOLDED THERMAFORM",
            "sustainable_load_formula": "C * (pi * D * L) / 6",
            "formula_terms": {
                "C": "compressive strength with safety factor",
                "D": "pipe OD",
                "L": "support length",
            },
            "lookup_ready": True,
            "weight_ready": False,
            "fabrication_ready": False,
            "fabrication_blockers": [
                "N-5 is a material property sheet and does not define the finished molded support volume",
                "service temperature other than -160C requires allowable-load adjustment",
            ],
        }
    )
    return result


SMALL_PIPE_SIZES = (
    0.5,
    0.75,
    1,
    1.5,
    2,
    3,
    4,
    6,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    24,
)
SMALL_MAX_ALLOWABLE_LOAD_KG = {
    0.5: 125,
    0.75: 160,
    1: 200,
    1.5: 290,
    2: 360,
    3: 530,
    4: 685,
    6: 1005,
    8: 2730,
    10: 3400,
    12: 4030,
    14: 4430,
    16: 5060,
    18: 5695,
    20: 6330,
    24: 7595,
}


SMALL_CRADLE_BY_THICKNESS = {
    25: (2.5, 2.5, 3, 3.5, 4, 5, 6, 8, 10, 12, 15, 16, 18, 20, 22, 26),
    40: (3.5, 3.5, 4, 4.5, 5, 6, 7, 9, 11, 14, 16, 17, 19, 21, 23, 27),
    50: (4.5, 4.5, 5, 6, 6, 7, 8, 10, 12, 15, 17, 18, 20, 22, 24, 28),
    65: (6, 6, 6, 7, 7, 8, 9, 11, 14, 16, 18, 19, 21, 23, 25, 29),
    75: (7, 7, 7, 8, 8, 9, 10, 12, 15, 17, 19, 20, 22, 24, 26, 30),
    90: (8, 8, 8, 9, 9, 10, 11, 14, 16, 18, 20, 21, 23, 25, 27, 31),
    100: (9, 9, 9, 10, 10, 11, 12, 15, 17, 19, 21, 22, 24, 26, 28, 32),
    115: (None, 10, 10, 11, 11, 12, 14, 16, 18, 20, 22, 23, 25, 27, 29, 33),
    125: (None, None, 11, 12, 12, 14, 15, 17, 19, 21, 23, 24, 26, 28, 30, 34),
    140: (None, None, 12, 12, 14, 15, 16, 18, 20, 22, 24, 25, 27, 29, 31, 35),
    150: (None, None, 14, 14, 15, 16, 17, 19, 21, 23, 25, 26, 28, 30, 32, 36),
    165: (None, None, None, None, 16, 17, 18, 20, 22, 24, 26, 27, 29, 31, 33, 37),
    175: (None, None, None, None, 17, 18, 19, 21, 23, 25, 27, 28, 30, 32, 34, 38),
    190: (None, None, None, None, 18, 19, 20, 22, 24, 26, 28, 29, 31, 33, 35, 39),
    200: (None, None, None, None, 19, 20, 21, 23, 25, 27, 29, 30, 32, 34, 36, 40),
    215: (None, None, None, None, 20, 21, 22, 24, 26, 28, 30, 31, 33, 35, 37, 41),
    225: (None, None, None, None, 21, 22, 23, 25, 27, 29, 31, 32, 34, 36, 38, 42),
    240: (None, None, None, None, 22, 23, 24, 26, 28, 30, 32, 33, 35, 37, 39, 43),
    255: (None, None, None, None, 23, 24, 25, 27, 29, 31, 33, 34, 36, 38, 40, 44),
    265: (None, None, None, None, 24, 25, 26, 28, 30, 32, 34, 35, 37, 39, 41, None),
}


SMALL_F_H_MM = {
    "CR2.5": (39, 79),
    "CR3": (47, 87),
    "CR3.5": (54, 94),
    "CR4": (60, 100),
    "CR4.5": (67, 107),
    "CR5": (73, 113),
    "CR6": (89, 129),
    "CR7": (102, 142),
    "CR8": (114, 154),
    "CR9": (127, 167),
    "CR10": (143, 183),
    "CR11": (155, 195),
    "CR12": (168, 208),
    "CR14": (184, 224),
    "CR15": (197, 237),
    "CR16": (209, 249),
    "CR17": (222, 262),
    "CR18": (235, 275),
    "CR19": (247, 287),
    "CR20": (264, 304),
    "CR21": (276, 316),
    "CR22": (289, 329),
    "CR23": (302, 342),
    "CR24": (314, 354),
    "CR25": (327, 367),
    "CR26": (340, 380),
    "CR27": (352, 392),
    "CR28": (365, 405),
    "CR29": (378, 418),
    "CR30": (391, 431),
    "CR31": (406, 446),
    "CR32": (419, 459),
    "CR33": (432, 471),
    "CR34": (445, 485),
    "CR35": (457, 497),
    "CR36": (470, 510),
    "CR37": (483, 523),
    "CR38": (495, 535),
    "CR39": (508, 548),
    "CR40": (521, 561),
    "CR41": (532, 572),
    "CR42": (545, 585),
    "CR43": (558, 598),
    "CR44": (570, 610),
}


LARGE_PIPE_SIZES = (30, 36, 42, 48, 54, 60)
LARGE_MAX_ALLOWABLE_LOAD_SOURCE_VALUE = {
    30: 49050,
    36: 58860,
    42: 68670,
    48: 78480,
    54: 88290,
    60: 98100,
}
LARGE_INSULATION_THICKNESSES_MM = (
    25,
    40,
    50,
    65,
    75,
    90,
    100,
    115,
    125,
    140,
    150,
    165,
    175,
    190,
    200,
)
LARGE_CRADLE_BY_THICKNESS = {
    25: (32, 38, 44, 50, 56, 62),
    40: (33, 39, 45, 51, 57, 63),
    50: (34, 40, 46, 52, 58, 64),
    65: (35, 41, 47, 53, 59, 65),
    75: (36, 42, 48, 54, 60, 66),
    90: (37, 43, 49, 55, 61, 67),
    100: (38, 44, 50, 56, 62, 68),
    115: (39, 45, 51, 57, 63, 69),
    125: (40, 46, 52, 58, 64, 70),
    140: (41, 47, 53, 59, 65, 71),
    150: (42, 48, 54, 60, 66, 72),
    165: (43, 49, 55, 61, 67, 73),
    175: (44, 50, 56, 62, 68, 74),
    190: (45, 51, 57, 63, 69, 75),
    200: (46, 52, 58, 64, 70, 76),
}


def _component_for_selection(pipe_size_in: float, thickness_mm: int) -> str:
    if pipe_size_in <= 24:
        if thickness_mm <= 75:
            return "N-20"
        if thickness_mm <= 140:
            return "N-21"
        if thickness_mm <= 200:
            return "N-22"
        return "N-23"
    if thickness_mm <= 75:
        return "N-24"
    if thickness_mm <= 140:
        return "N-25"
    return "N-26"


def _selection_from_cradle(
    cradle_no: str,
    pipe_size_in: float,
    thickness_mm: int | None,
) -> dict | None:
    n1 = get_n1_dimensions(cradle_no, pipe_size_in)
    if not n1:
        return None
    component_id = (
        _component_for_selection(pipe_size_in, thickness_mm)
        if thickness_mm is not None
        else None
    )
    if pipe_size_in <= 24:
        f_h = SMALL_F_H_MM.get(cradle_no)
        load_value = SMALL_MAX_ALLOWABLE_LOAD_KG.get(pipe_size_in)
        if not f_h or load_value is None:
            return None
        f_mm, h_mm = f_h
        density = 160 if pipe_size_in <= 6 else 224
        load = {
            "max_allowable_load": load_value,
            "max_allowable_load_unit": "kg",
            "max_allowable_load_kg": load_value,
        }
    else:
        load_value = LARGE_MAX_ALLOWABLE_LOAD_SOURCE_VALUE.get(
            pipe_size_in
        )
        if load_value is None:
            return None
        f_mm = n1["R_mm"] + n1["T1_mm"]
        h_mm = n1["R_mm"] + 102
        density = 320
        source_unit_labels = {
            "N-24": "kg",
            "N-25": "lb",
            "N-26": "lb",
        }
        load = {
            "max_allowable_load": load_value,
            "max_allowable_load_unit": "source_conflict",
            "max_allowable_load_source_value": load_value,
            "max_allowable_load_source_sheet": component_id,
            "max_allowable_load_source_sheet_unit_label": (
                source_unit_labels.get(component_id)
            ),
            "max_allowable_load_source_unit_labels": source_unit_labels,
            "max_allowable_load_kg": None,
            "max_allowable_load_lb": None,
            "load_selection_ready": False,
            "source_conflict": (
                "N-24 labels the shared 49050~98100 load row as kg, while "
                "N-25/N-26 label the identical values as lb; the values also "
                "equal 9810 x 5~10 and may represent force. No canonical "
                "unit conversion is released pending owner confirmation."
            ),
        }
    return {
        "component_id": component_id,
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "cradle_no": cradle_no,
        "pipe_size_in": pipe_size_in,
        "insulation_thickness_mm": thickness_mm,
        "F_mm": f_mm,
        "H_mm": h_mm,
        "polyurethane_density_kg_m3": density,
        **load,
        "allowable_load_basis": (
            "compressive strength at yield / safety factor 5 / -160C"
        ),
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": [
            "N-20~N-26 allowable load is a capacity, not component self-weight",
            *(
                [load["source_conflict"]]
                if load.get("source_conflict")
                else []
            ),
            "service temperature other than -160C requires N-5 load adjustment",
            "host C/N details are still required for released cradle contours and developments",
        ],
    }


def get_cradle_selection(
    pipe_size_in: object,
    insulation_thickness_mm: object,
) -> dict | None:
    try:
        pipe = float(pipe_size_in)
        if pipe.is_integer():
            pipe = int(pipe)
        thickness = int(float(insulation_thickness_mm))
    except (TypeError, ValueError):
        return None
    cradle_number = None
    if pipe in SMALL_PIPE_SIZES:
        values = SMALL_CRADLE_BY_THICKNESS.get(thickness)
        if values:
            cradle_number = values[SMALL_PIPE_SIZES.index(pipe)]
    elif pipe in LARGE_PIPE_SIZES and thickness in LARGE_INSULATION_THICKNESSES_MM:
        cradle_number = LARGE_CRADLE_BY_THICKNESS[thickness][
            LARGE_PIPE_SIZES.index(pipe)
        ]
    if cradle_number is None:
        return None
    cradle_no = _cradle_key(cradle_number)
    return _selection_from_cradle(cradle_no, pipe, thickness)


def get_cradle_candidates(
    cradle_no: object,
    pipe_size_in: object,
) -> list[dict]:
    """Return every source row matching the designation's CR and pipe size."""
    key = _cradle_key(cradle_no)
    try:
        pipe = float(pipe_size_in)
        if pipe.is_integer():
            pipe = int(pipe)
    except (TypeError, ValueError):
        return []
    thicknesses = (
        tuple(SMALL_CRADLE_BY_THICKNESS)
        if pipe in SMALL_PIPE_SIZES
        else LARGE_INSULATION_THICKNESSES_MM
        if pipe in LARGE_PIPE_SIZES
        else ()
    )
    rows = []
    for thickness in thicknesses:
        row = get_cradle_selection(pipe, thickness)
        if row and row["cradle_no"] == key:
            rows.append(row)
    return rows


def resolve_cradle_designation(
    cradle_no: object,
    pipe_size_in: object,
    *,
    insulation_thickness_mm: object | None = None,
) -> dict | None:
    """Resolve a CR/pipe designation, preserving multi-thickness ambiguity."""
    candidates = get_cradle_candidates(cradle_no, pipe_size_in)
    if not candidates:
        return None
    if insulation_thickness_mm is not None:
        try:
            requested = int(float(insulation_thickness_mm))
        except (TypeError, ValueError):
            return None
        for row in candidates:
            if row["insulation_thickness_mm"] == requested:
                selected = deepcopy(row)
                selected["selection_resolved"] = True
                selected["candidate_insulation_thicknesses_mm"] = [
                    candidate["insulation_thickness_mm"]
                    for candidate in candidates
                ]
                return selected
        return None
    common = deepcopy(candidates[0])
    common["candidate_insulation_thicknesses_mm"] = [
        candidate["insulation_thickness_mm"]
        for candidate in candidates
    ]
    common["candidate_source_components"] = sorted(
        {candidate["component_id"] for candidate in candidates}
    )
    common["selection_resolved"] = len(candidates) == 1
    if len(candidates) != 1:
        common["component_id"] = "/".join(common["candidate_source_components"])
        common["insulation_thickness_mm"] = None
        common["fabrication_blockers"] = [
            "CR/pipe designation maps to multiple insulation thicknesses; provide insulation_thickness_mm",
            *common["fabrication_blockers"],
        ]
    return common


def get_selection_sheet_component(component_id: str) -> dict:
    ranges = {
        "N-20": ("N-20-CRADLE NO. OF COLD SUPPORT.1.pdf", SMALL_PIPE_SIZES, (25, 40, 50, 65, 75)),
        "N-21": ("N-21-CRADLE NO. OF COLD SUPPORT.2.pdf", SMALL_PIPE_SIZES, (90, 100, 115, 125, 140)),
        "N-22": ("N-22-CRADLE NO. OF COLD SUPPORT.3.pdf", SMALL_PIPE_SIZES, (150, 165, 175, 190, 200)),
        "N-23": ("N-23-CRADLE NO. OF COLD SUPPORT.4.pdf", SMALL_PIPE_SIZES, (215, 225, 240, 255, 265)),
        "N-24": ("N-24-CRADLE NO. OF COLD SUPPORT.5.pdf", LARGE_PIPE_SIZES, (25, 40, 50, 65, 75)),
        "N-25": ("N-25-CRADLE NO. OF COLD SUPPORT.6.pdf", LARGE_PIPE_SIZES, (90, 100, 115, 125, 140)),
        "N-26": ("N-26-CRADLE NO. OF COLD SUPPORT.7.pdf", LARGE_PIPE_SIZES, (150, 165, 175, 190, 200)),
    }
    pdf_file, pipe_sizes, thicknesses = ranges[component_id]
    row_count = sum(
        get_cradle_selection(pipe, thickness) is not None
        for pipe in pipe_sizes
        for thickness in thicknesses
    )
    return {
        "component_id": component_id,
        "name_en": "CRADLE NO. OF COLD SUPPORT",
        "category": "component_cold",
        "pdf_file": pdf_file,
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "table_kind": "selection_lookup",
        "lookup_ready": True,
        "weight_ready": False,
        "source_transcribed": True,
        "pipe_sizes_in": list(pipe_sizes),
        "insulation_thicknesses_mm": list(thicknesses),
        "row_count": row_count,
        "notes": [
            "F/H/cradle mark and allowable load are source-backed",
            "allowable load is capacity rather than item self-weight",
        ],
    }
