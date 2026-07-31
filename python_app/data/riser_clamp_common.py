"""Shared builders for the M-11/M-12 riser-clamp source tables.

Raw drawing rows deliberately remain in ``m11_table.py`` and
``m12_table.py``.  This module only normalizes line sizes and applies the
common formed-strip geometry/weight calculation.
"""

from __future__ import annotations

from copy import deepcopy
import math

from .component_size_utils import SIZE_DISPLAY_MAP, size_to_float
from .pipe_table import get_pipe_od


CARBON_STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def normalize_riser_line_size(value: object) -> float | None:
    size = size_to_float(value)
    return round(size, 4) if size is not None else None


def build_riser_clamp_row(
    component_info: dict,
    *,
    variant: str,
    line_size_in: float,
    maximum_recommended_load_kg: int,
    installed_overall_mm: int,
    stock_thickness_mm: int,
    stock_width_mm: int,
    bolt_diameter_in: str,
    bolt_length_mm: int,
    left_straight_projection_mm: float | None = None,
    right_straight_projection_mm: float | None = None,
) -> dict:
    """Build one two-piece riser-clamp row without inventing hole geometry."""
    pipe_od_mm = get_pipe_od(line_size_in)
    neutral_radius_mm = pipe_od_mm / 2 + stock_thickness_mm / 2

    source_sketch_left_mm = left_straight_projection_mm
    source_sketch_right_mm = right_straight_projection_mm
    source_l_vs_sketch_gap_mm = None
    if source_sketch_left_mm is not None and source_sketch_right_mm is not None:
        source_sketch_total_mm = (
            source_sketch_left_mm + source_sketch_right_mm
        )
        source_l_vs_sketch_gap_mm = (
            installed_overall_mm
            - (
                source_sketch_total_mm
                + pipe_od_mm
                + 2 * stock_thickness_mm
            )
        )
    if variant == "B":
        # M-12 releases a size-specific overall L table as well as one fixed
        # 150/50 sketch.  They disagree by up to 34 mm.  The per-size table
        # governs the known strip material length, while the individual leg
        # split remains blocked pending a corrected source drawing.
        straight_total_mm = (
            installed_overall_mm
            - pipe_od_mm
            - 2 * stock_thickness_mm
        )
        left_straight_projection_mm = None
        right_straight_projection_mm = None
        straight_dimension_basis = (
            "derived from source table L, standard pipe OD and 2 x stock "
            "thickness; source sketch 150/50 conflicts with table L"
        )
        straight_split_released = False
    elif (
        left_straight_projection_mm is None
        or right_straight_projection_mm is None
    ):
        # M-11 only dimensions installed overall A.  Its view is symmetric,
        # so retain A exactly and expose the derived split as non-released.
        straight_total_mm = (
            installed_overall_mm
            - pipe_od_mm
            - 2 * stock_thickness_mm
        )
        left_straight_projection_mm = straight_total_mm / 2
        right_straight_projection_mm = straight_total_mm / 2
        straight_dimension_basis = (
            "derived symmetric split from source A, standard pipe OD and "
            "2 x stock thickness; not directly dimensioned"
        )
        straight_split_released = False
    else:
        straight_total_mm = (
            left_straight_projection_mm
            + right_straight_projection_mm
        )
        straight_dimension_basis = "direct source dimensions"
        straight_split_released = True

    developed_length_each_mm = (
        straight_total_mm + math.pi * neutral_radius_mm
    )
    strip_weight_each_kg = (
        developed_length_each_mm
        * stock_width_mm
        * stock_thickness_mm
        * CARBON_STEEL_DENSITY_KG_PER_MM3
    )
    calculated_installed_overall_mm = (
        straight_total_mm + pipe_od_mm + 2 * stock_thickness_mm
    )

    blockers = list(component_info["fabrication_blockers"])
    if not straight_split_released:
        if variant == "B":
            blockers.append(
                "M-12 size-specific table L conflicts with the fixed "
                "150/50 sketch dimensions; table L governs known strip "
                "material weight, but the two straight-leg cuts are not "
                "fabrication-released"
            )
        else:
            blockers.append(
                "M-11 dimensions only overall A; the symmetric straight-leg "
                "split is derived and is not a released fabrication dimension"
            )

    return {
        **deepcopy(component_info),
        "designation": (
            f"RCL-{variant}-"
            f"{SIZE_DISPLAY_MAP[line_size_in].replace(chr(34), '')}B"
        ),
        "variant": variant,
        "line_size_in": line_size_in,
        "pipe_od_mm": pipe_od_mm,
        "maximum_recommended_load_kg": maximum_recommended_load_kg,
        "installed_overall_dimension_name": (
            "A" if variant == "A" else "L"
        ),
        "installed_overall_mm": installed_overall_mm,
        "calculated_installed_overall_mm": (
            calculated_installed_overall_mm
        ),
        "installed_overall_reconstruction_delta_mm": (
            installed_overall_mm - calculated_installed_overall_mm
        ),
        "stock_thickness_mm": stock_thickness_mm,
        "stock_width_mm": stock_width_mm,
        "strip_piece_quantity": 2,
        "inner_bend_radius_mm": pipe_od_mm / 2,
        "neutral_radius_mm": neutral_radius_mm,
        "left_straight_projection_mm": left_straight_projection_mm,
        "right_straight_projection_mm": right_straight_projection_mm,
        "source_sketch_left_straight_projection_mm": (
            source_sketch_left_mm
        ),
        "source_sketch_right_straight_projection_mm": (
            source_sketch_right_mm
        ),
        "source_L_vs_sketch_gap_mm": source_l_vs_sketch_gap_mm,
        "straight_projection_total_mm": straight_total_mm,
        "straight_dimension_basis": straight_dimension_basis,
        "straight_split_released": straight_split_released,
        "developed_length_formula": (
            "left straight + right straight + "
            "pi * (pipe OD / 2 + stock thickness / 2)"
        ),
        "developed_length_each_mm": developed_length_each_mm,
        "calculated_strip_weight_each_kg": strip_weight_each_kg,
        "known_two_strip_weight_kg": 2 * strip_weight_each_kg,
        "fastener": {
            "source_bolt_spec": (
                f'{bolt_diameter_in}"x{bolt_length_mm}'
            ),
            "bolt_diameter_in": bolt_diameter_in,
            "bolt_length_mm": bolt_length_mm,
            "assembly_positions_shown": 2,
            "hole_diameter_mm": None,
            "hole_center_locations_mm": None,
            "finished_weight_kg": None,
        },
        "fabrication_blockers": blockers,
    }
