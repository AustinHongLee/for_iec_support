"""Source-backed DSP-500-006 cold base/restraint component tables.

Sources:

* N-6: special threaded base-plate assembly.
* N-7 / N-7A: two distinct special U-bolt variants selected by cradle no.
* N-8: strap selected by cradle no.
* N-8A: strap selected by bare-pipe line size.

The U-bolt rod length and rod-only weight are derivable from the source
centerline geometry.  Finished nuts, thread standard, and complete material
grades are not released, so the complete U-bolt assembly is not weight-ready.
The strap drawings give formed A/B/R/T dimensions but no released flat
development or bend allowance; strap weight must therefore remain blocked.
"""

from __future__ import annotations

from copy import deepcopy
import math


SOURCE_STANDARD = "DSP-500-006"
SOURCE_REVISION = "0"
STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def _cradle_key(value: object) -> str:
    raw = str(value or "").strip().upper().replace(" ", "")
    if not raw.startswith("CR"):
        raw = f"CR{raw}"
    return raw


N6_COMPONENT = {
    "component_id": "N-6",
    "name_en": "SPECIAL BASE PLATE",
    "category": "component_cold",
    "pdf_file": "N-6-SPECIAL BASE PLATE.pdf",
    "engineering_standard": SOURCE_STANDARD,
    "revision": SOURCE_REVISION,
    "table_kind": "single_component_geometry",
    "lookup_ready": True,
    "weight_ready": False,
    "fabrication_ready": False,
    "overall_height_mm": 200,
    "base_plate": {
        "shape": "round_plate",
        "outside_diameter_mm": 150,
        "thickness_mm": 12,
        "half_hole_diameter_mm": 10,
        "half_hole_location": "at pipe/base interface on drawing centerline",
        "material": "NOT SPECIFIED IN N-6",
    },
    "pipe_stub": {
        "nominal_size_in": 3,
        "schedule": 40,
        "source_od_callout_mm": 89,
        "material": "A53 Gr.B",
        "thread": "NATIONAL PIPE STRAIGHT THREAD",
        "cross_hole_diameter_mm": 15,
        "cross_hole_bottom_clearance_above_plate_mm": 7,
    },
    "coupling": {
        "nominal_size_in": 3,
        "class": "3000#",
        "outside_diameter_mm": 108,
        "axial_length_mm": 54,
        "thread": "FULL FEMALE NATIONAL PIPE STRAIGHT THREADS",
        "material": "NOT SPECIFIED IN N-6",
    },
    "pipe_to_plate_weld_mm": 6,
    "fabrication_blockers": [
        "N-6 gives 200 mm finished assembly height but not the pipe/coupling thread engagement needed to release the pipe cut length",
        "N-6 does not specify the round base-plate or coupling material grade",
        "the 10 mm half-hole is located at the pipe/base interface, but its circumferential orientation is not independently dimensioned",
        "the source gives no purchased 3in 3000# coupling unit weight",
    ],
}


def get_n6_component() -> dict:
    return deepcopy(N6_COMPONENT)


# cradle, R, rod size, B, N-7 C/D/E, N-7A C/D/E
_U_BOLT_ROWS = (
    ("CR2.5", 42, 0.25, 84, 90, 84, 126, 90, 52, 86),
    ("CR3", 50, 0.25, 100, 105, 84, 134, 106, 52, 94),
    ("CR3.5", 57, 0.25, 114, 120, 84, 141, 120, 52, 101),
    ("CR4", 63, 0.25, 126, 132, 84, 147, 132, 52, 107),
    ("CR4.5", 70, 0.25, 140, 146, 84, 154, 146, 52, 114),
    ("CR5", 76, 0.375, 152, 162, 100, 176, 162, 74, 136),
    ("CR6", 92, 0.375, 184, 194, 100, 192, 194, 74, 152),
    ("CR7", 105, 0.375, 210, 220, 100, 205, 220, 74, 165),
    ("CR8", 117, 0.375, 234, 244, 105, 222, 244, 79, 182),
    ("CR9", 130, 0.375, 260, 270, 105, 235, 270, 79, 195),
    ("CR10", 146, 0.375, 292, 302, 105, 251, 302, 79, 211),
    ("CR11", 158, 0.375, 316, 326, 105, 263, 326, 79, 223),
    ("CR12", 171, 0.375, 342, 352, 105, 276, 352, 79, 236),
    ("CR14", 187, 0.375, 374, 384, 105, 292, 384, 79, 252),
    ("CR15", 200, 0.375, 400, 410, 105, 305, 410, 79, 265),
    ("CR16", 212, 0.375, 424, 434, 105, 317, 434, 79, 277),
    ("CR17", 225, 0.375, 450, 460, 105, 330, 460, 79, 290),
    ("CR18", 238, 0.375, 476, 486, 103, 341, 486, 77, 301),
    ("CR19", 250, 0.375, 500, 510, 103, 353, 510, 77, 313),
    ("CR20", 267, 0.375, 534, 544, 103, 370, 544, 77, 330),
    ("CR21", 279, 0.375, 558, 568, 103, 382, 568, 77, 342),
    ("CR22", 292, 0.5, 584, 597, 107, 399, 597, 83, 359),
    ("CR23", 305, 0.5, 610, 623, 107, 412, 623, 83, 372),
    ("CR24", 317, 0.5, 634, 647, 107, 424, 647, 83, 384),
    ("CR25", 330, 0.5, 660, 673, 107, 437, 673, 83, 397),
    ("CR26", 343, 0.5, 686, 699, 107, 450, 699, 83, 410),
    ("CR27", 355, 0.5, 710, 723, 107, 462, 723, 83, 422),
    ("CR28", 368, 0.5, 736, 749, 107, 475, 749, 83, 435),
    ("CR29", 381, 0.5, 762, 775, 107, 488, 775, 83, 448),
)


def _build_u_bolt_row(
    *,
    component_id: str,
    cradle_no: str,
    radius_mm: int,
    rod_diameter_in: float,
    b_mm: int,
    c_mm: int,
    d_mm: int,
    e_mm: int,
) -> dict:
    rod_diameter_mm = rod_diameter_in * 25.4
    developed_length_mm = math.pi * b_mm / 2 + 2 * e_mm
    rod_weight_kg = (
        math.pi
        * rod_diameter_mm**2
        / 4
        * developed_length_mm
        * STEEL_DENSITY_KG_PER_MM3
    )
    variant = "SUB" if component_id == "N-7" else "SUB1"
    return {
        "component_id": component_id,
        "name_en": (
            "SPECIAL U-BOLT TYPE-SUB"
            if component_id == "N-7"
            else "SPECIAL U-BOLT TYPE-SUB1"
        ),
        "category": "component_cold",
        "pdf_file": (
            "N-7-SPECIAL U-BOLT SUB.pdf"
            if component_id == "N-7"
            else "N-7A-SPECIAL U-BOLT SUB1.pdf"
        ),
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        "designation": f"{variant}-{cradle_no}",
        "cradle_no": cradle_no,
        "R_mm": radius_mm,
        "rod_diameter_in": rod_diameter_in,
        "rod_diameter_mm": rod_diameter_mm,
        "B_centerline_mm": b_mm,
        "C_overall_mm": c_mm,
        "D_thread_length_mm": d_mm,
        "E_leg_to_bend_center_mm": e_mm,
        "bend_arc_deg": 180,
        "developed_length_formula": "pi * B / 2 + 2 * E",
        "rod_developed_length_mm": developed_length_mm,
        "rod_calculated_weight_kg": rod_weight_kg,
        "material": "CARBON STEEL, GALVANIZED",
        "finished_hex_nuts_per_set": 4,
        "lookup_ready": True,
        "rod_weight_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": [
            f"{component_id} specifies carbon steel and galvanizing but no material grade",
            f"{component_id} does not state thread pitch/class or the finished hex-nut standard/unit weight",
            "rod-only weight is calculated from source centerline geometry; four finished nuts remain zero-weight procurement references",
        ],
    }


N7_TABLE = {}
N7A_TABLE = {}
for (
    _cradle,
    _radius,
    _rod_in,
    _b,
    _n7_c,
    _n7_d,
    _n7_e,
    _n7a_c,
    _n7a_d,
    _n7a_e,
) in _U_BOLT_ROWS:
    N7_TABLE[_cradle] = _build_u_bolt_row(
        component_id="N-7",
        cradle_no=_cradle,
        radius_mm=_radius,
        rod_diameter_in=_rod_in,
        b_mm=_b,
        c_mm=_n7_c,
        d_mm=_n7_d,
        e_mm=_n7_e,
    )
    N7A_TABLE[_cradle] = _build_u_bolt_row(
        component_id="N-7A",
        cradle_no=_cradle,
        radius_mm=_radius,
        rod_diameter_in=_rod_in,
        b_mm=_b,
        c_mm=_n7a_c,
        d_mm=_n7a_d,
        e_mm=_n7a_e,
    )


def get_n7_by_cradle(cradle_no: object) -> dict | None:
    row = N7_TABLE.get(_cradle_key(cradle_no))
    return deepcopy(row) if row else None


def get_n7a_by_cradle(cradle_no: object) -> dict | None:
    row = N7A_TABLE.get(_cradle_key(cradle_no))
    return deepcopy(row) if row else None


_N8_ROWS = (
    ("CR5", 76, 299, 235, 10),
    ("CR6", 92, 334, 270, 10),
    ("CR7", 105, 359, 295, 10),
    ("CR8", 117, 384, 320, 10),
    ("CR9", 130, 409, 345, 10),
    ("CR10", 146, 439, 375, 10),
    ("CR11", 158, 464, 400, 10),
    ("CR12", 171, 489, 425, 10),
    ("CR14", 187, 524, 460, 10),
    ("CR15", 200, 549, 485, 10),
    ("CR16", 212, 574, 510, 10),
    ("CR17", 225, 600, 536, 12),
    ("CR18", 238, 626, 562, 12),
    ("CR19", 250, 650, 586, 12),
    ("CR20", 267, 684, 620, 12),
    ("CR21", 279, 708, 644, 12),
    ("CR22", 292, 734, 670, 16),
    ("CR23", 305, 760, 696, 16),
    ("CR24", 317, 784, 720, 16),
    ("CR25", 330, 810, 746, 16),
)


def _build_strap_row(
    *,
    component_id: str,
    selection: dict,
    radius_mm: int,
    a_mm: int,
    b_mm: int,
    thickness_mm: int,
) -> dict:
    return {
        "component_id": component_id,
        "name_en": "STRAP",
        "category": "component_cold",
        "pdf_file": (
            "N-8-STRAP-1.pdf"
            if component_id == "N-8"
            else "N-8A-STRAP-2.pdf"
        ),
        "engineering_standard": SOURCE_STANDARD,
        "revision": SOURCE_REVISION,
        **selection,
        "R_mm": radius_mm,
        "A_mm": a_mm,
        "B_hole_pitch_mm": b_mm,
        "thickness_mm": thickness_mm,
        "strap_width_mm": 100,
        "hole_count": 2,
        "hole_diameter_mm": 22,
        "hole_center_end_offset_mm": 32,
        "machine_bolt": "3/4in x 50",
        "machine_bolt_quantity": 2,
        "nut_quantity": 2,
        "material": "CARBON STEEL",
        "lookup_ready": True,
        "weight_ready": False,
        "fabrication_ready": False,
        "fabrication_blockers": [
            f"{component_id} A/B/R/T are formed dimensions; the source does not release the flat developed length or bend allowance",
            f"{component_id} specifies carbon steel but no material grade",
            f"{component_id} gives 3/4in x 50 machine-bolt size but no bolt/nut grade or unit weight",
        ],
    }


N8_TABLE = {
    cradle: _build_strap_row(
        component_id="N-8",
        selection={
            "designation": f"STR-{cradle}",
            "cradle_no": cradle,
        },
        radius_mm=radius,
        a_mm=a,
        b_mm=b,
        thickness_mm=thickness,
    )
    for cradle, radius, a, b, thickness in _N8_ROWS
}

_N8A_ROWS = {
    6: (87, 328, 264, 10),
    8: (113, 380, 316, 10),
    10: (140, 434, 370, 10),
}
N8A_TABLE = {
    line_size: _build_strap_row(
        component_id="N-8A",
        selection={
            "designation": f"STR1-{line_size}B",
            "line_size_in": line_size,
        },
        radius_mm=radius,
        a_mm=a,
        b_mm=b,
        thickness_mm=thickness,
    )
    for line_size, (radius, a, b, thickness) in _N8A_ROWS.items()
}


def get_n8_by_cradle(cradle_no: object) -> dict | None:
    row = N8_TABLE.get(_cradle_key(cradle_no))
    return deepcopy(row) if row else None


def get_n8a_by_line_size(line_size_in: object) -> dict | None:
    try:
        size = float(line_size_in)
        if size.is_integer():
            size = int(size)
    except (TypeError, ValueError):
        return None
    row = N8A_TABLE.get(size)
    return deepcopy(row) if row else None
