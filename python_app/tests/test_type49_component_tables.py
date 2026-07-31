import math

import pytest

from core.calculator import analyze_single
from data.component_table_registry import get_component_table_coverage
from data.m11_table import get_m11_by_line_size
from data.m12_table import get_m12_by_line_size
from data.m41_table import get_m41_by_line_size


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_m11_transcribes_the_full_riser_clamp_a_row():
    row = get_m11_by_line_size('3 1/2"')

    assert row["designation"] == "RCL-A-3 1/2B"
    assert row["line_size_in"] == 3.5
    assert row["pipe_od_mm"] == 101.6
    assert row["maximum_recommended_load_kg"] == 305
    assert row["installed_overall_mm"] == 330
    assert (
        row["stock_thickness_mm"],
        row["stock_width_mm"],
    ) == (6, 38)
    assert row["fastener"]["source_bolt_spec"] == '1/2"x50'
    assert row["strip_piece_quantity"] == 2
    assert row["strip_weight_ready"]
    assert not row["weight_ready"]
    assert not row["fabrication_ready"]


def test_m11_and_m12_keep_their_real_10_and_12_inch_differences():
    m11_10 = get_m11_by_line_size(10)
    m12_10 = get_m12_by_line_size(10)
    m11_12 = get_m11_by_line_size(12)
    m12_12 = get_m12_by_line_size(12)

    assert (
        m11_10["installed_overall_mm"],
        m11_10["stock_thickness_mm"],
        m11_10["fastener"]["bolt_length_mm"],
    ) == (514, 9, 70)
    assert (
        m12_10["installed_overall_mm"],
        m12_10["stock_thickness_mm"],
        m12_10["fastener"]["bolt_length_mm"],
    ) == (527, 10, 60)
    assert m11_12["stock_thickness_mm"] == 12
    assert m12_12["stock_thickness_mm"] == 13


def test_m11_calculates_only_the_two_formed_strip_weight():
    row = get_m11_by_line_size(4)
    straight_total = (
        row["installed_overall_mm"]
        - row["pipe_od_mm"]
        - 2 * row["stock_thickness_mm"]
    )
    expected_development = (
        straight_total + math.pi * row["neutral_radius_mm"]
    )
    expected_pair_weight = (
        2
        * expected_development
        * row["stock_width_mm"]
        * row["stock_thickness_mm"]
        * 7.85e-6
    )

    assert row["developed_length_each_mm"] == pytest.approx(
        expected_development
    )
    assert row["known_two_strip_weight_kg"] == pytest.approx(
        expected_pair_weight
    )
    assert row["fastener"]["finished_weight_kg"] is None
    assert not row["straight_split_released"]


def test_m12_uses_table_l_and_preserves_the_150_50_source_conflict():
    row = get_m12_by_line_size("8B")
    straight_total = (
        row["installed_overall_mm"]
        - row["pipe_od_mm"]
        - 2 * row["stock_thickness_mm"]
    )
    expected_development = straight_total + math.pi * (
        row["pipe_od_mm"] / 2 + row["stock_thickness_mm"] / 2
    )

    assert (
        row["source_sketch_left_straight_projection_mm"],
        row["source_sketch_right_straight_projection_mm"],
    ) == (150, 50)
    assert row["left_straight_projection_mm"] is None
    assert row["right_straight_projection_mm"] is None
    assert row["source_L_vs_sketch_gap_mm"] == pytest.approx(30.9)
    assert not row["straight_split_released"]
    assert row["developed_length_each_mm"] == pytest.approx(
        expected_development
    )


def test_m41_calculates_the_exact_polygon_blank_and_material_suffix():
    carbon = get_m41_by_line_size(4, "Carbon Steel")
    stainless = get_m41_by_line_size(4, "Stainless Steel")
    expected_area = 75 * 30 - (30 - 15) * (75 - 45) / 2

    assert carbon["type_no"] == "LGP-P-1"
    assert carbon["designation"] == "LGP-P-1"
    assert stainless["designation"] == "LGP-P-1S"
    assert carbon["quantity"] == 4
    assert carbon["polygon_points_mm"] == [
        [0, 0],
        [30, 0],
        [30, 75],
        [15, 75],
        [0, 45],
    ]
    assert carbon["net_area_mm2"] == expected_area
    assert carbon["calculated_blank_weight_total_kg"] == pytest.approx(
        expected_area * 9 * 7.85e-6 * 4
    )
    assert (
        stainless["calculated_blank_weight_each_kg"]
        > carbon["calculated_blank_weight_each_kg"]
    )
    assert carbon["blank_ready"]
    assert not carbon["fabrication_ready"]


@pytest.mark.parametrize(
    ("size", "type_no", "quantity"),
    (
        (3, "LGP-P-1", 4),
        (10, "LGP-P-2", 4),
        (14, "LGP-P-3", 6),
        (20, "LGP-P-4", 6),
    ),
)
def test_m41_selects_the_source_ranges(size, type_no, quantity):
    row = get_m41_by_line_size(size)

    assert (row["type_no"], row["quantity"]) == (type_no, quantity)


def test_type49_accepts_the_released_d60_designation_and_translates_material():
    result = analyze_single(
        "49-4B-A(B)",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert [
        entry.geometry.component_id
        for entry in result.entries
    ] == ["M-11", "M-11-FASTENERS", "M-41"]
    assert _entry(result, "M-11").material == (
        "Carbon Steel (grade not specified)"
    )
    assert _entry(result, "M-41").geometry.parameters[
        "designation"
    ] == "LGP-P-1S"
    assert result.meta["fabrication"]["input_form"] == "released_d60"
    assert result.meta["fabrication"][
        "lug_plate_material_class"
    ] == "Stainless Steel"
    assert result.total_weight > 0


def test_type49_rejects_ambiguous_compact_codes_and_missing_rows():
    ambiguous = analyze_single(
        "49-10B",
        source_profile="cw_e25_24_hp6",
    )
    missing = analyze_single(
        "49-7B-A",
        source_profile="cw_e25_24_hp6",
    )

    assert ambiguous.error
    assert "FIG段不得省略" in ambiguous.error
    assert ambiguous.entries == []
    assert missing.error
    assert "不允許區間內插" in missing.error
    assert missing.entries == []


def test_type49_accepts_hyphenated_mixed_fraction_in_released_form():
    result = analyze_single(
        "49-1-1/2B-A",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert result.meta["fabrication"]["line_size_in"] == 1.5
    assert _entry(result, "M-11-FASTENERS").quantity == 2


def test_type49_fig_b_keeps_lug_drawing_ambiguity_unresolved():
    result = analyze_single(
        "49-10B-B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert _entry(result, "M-12-FASTENERS").quantity == 2
    ambiguity = _entry(result, "D-60-FIG-B-LUG-AMBIGUITY")
    assert ambiguity.unit_weight == 0
    assert any("NOTE 2" in warning for warning in result.warnings)


def test_type49_weight_scope_remains_explicitly_partial_for_fabrication():
    result = analyze_single(
        "49-20B-A(A)",
        source_profile="cw_e25_24_hp6",
    )
    clamp = _entry(result, "M-11")
    fastener = _entry(result, "M-11-FASTENERS")
    lug = _entry(result, "M-41")

    assert not result.error
    assert clamp.unit_weight > 0
    assert fastener.unit_weight > 0
    assert lug.unit_weight > 0
    assert not clamp.geometry.fabrication_ready
    assert not lug.geometry.fabrication_ready
    assert result.meta["fabrication"]["known_material_weight_ready"]
    assert not result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert "M-11/M-12 supplier finished-weight variance and hole deductions" in (
        result.meta["fabrication"]["excluded_weight_scope"]
    )


def test_component_registry_promotes_the_three_type49_components():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["partial_lookup"] == 3
    assert coverage["metadata_only"] == 8
