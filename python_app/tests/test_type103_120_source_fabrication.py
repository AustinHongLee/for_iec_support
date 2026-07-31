"""Drawing-truth locks for the Type 103~120 implementation wave."""

import math

import pytest

from core.calculator import analyze_single
from core.source_profiles import CTCI_20E4588, CTCI_22A_5123A
from data.m57_table import get_m57_by_line_size
from data.m58_table import get_m58_by_line_size
from data.m59_table import get_m59_by_line_size


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type103_cw_does_not_treat_expansion_bolt_d_as_hole_diameter():
    result = analyze_single("103-1-A")

    plate = _entry(result, "D112-FOUR-HOLE-SUPPORT-PLATE")
    assert not result.error
    assert plate.unit_weight == 0
    assert plate.geometry.parameters["outside_mm"] == 180
    assert plate.geometry.parameters["hole_diameter_mm"] is None
    assert plate.geometry.holes is None
    assert not plate.geometry.fabrication_ready
    assert any("不是已核定的 drilled-hole diameter" in item for item in result.warnings)


def test_type103_20e_uses_independent_hole_column_and_two_plates_for_fig_c():
    result = analyze_single(
        "103-1-C",
        source_profile=CTCI_20E4588,
    )

    plate = _entry(result, "D112-FOUR-HOLE-SUPPORT-PLATE")
    anchors = _entry(result, "D112-ANCHOR-BOLTS")
    expected_one = (
        (180**2 - 4 * math.pi * 10**2 / 4)
        * 9
        * 7.85e-6
    )
    assert not result.error
    assert plate.quantity == 2
    assert plate.unit_weight == pytest.approx(expected_one, abs=0.01)
    assert plate.geometry.holes.diameter == 10
    assert plate.geometry.holes.pitch_x == 150
    assert anchors.quantity == 8
    assert anchors.geometry.parameters["not_furnished"] is True


def test_type103_source_rows_keep_22a_six_but_20e_stops_at_five():
    ctci22 = analyze_single(
        "103-6-A",
        source_profile=CTCI_22A_5123A,
    )
    ctci20 = analyze_single(
        "103-6-A",
        source_profile=CTCI_20E4588,
    )

    assert not ctci22.error
    assert ctci20.error and "未表列 support no. 6" in ctci20.error


def test_type104_preserves_d113_and_m52_dimensions_without_fake_weight():
    result = analyze_single("104-6B")

    assembly = _entry(result, "D113-M52-SPRING-WEDGE-ASSEMBLY")
    params = assembly.geometry.parameters
    assert not result.error
    assert result.total_weight == 0
    assert params["d113_B_mm"] == 200
    assert params["d113_C_mm"] == 135
    assert params["d113_D_mm"] == 210
    assert params["m52_designation"] == "SPRW-6B"
    assert params["m52_spring_data"]["spring_constant_kg_per_mm"] == 30


def test_type105_fig_a_member_n_differs_by_source():
    cw = analyze_single("105-L50-10A")
    ctci20 = analyze_single(
        "105-L50-10A",
        source_profile=CTCI_20E4588,
    )

    cw_n = _entry(cw, "D115-MEMBER-N")
    ctci_n = _entry(ctci20, "D115-MEMBER-N")
    assert cw_n.geometry.parameters["source_spec"] == "PL60x60x6"
    assert ctci_n.geometry.parameters["source_spec"] == "L40x40x5"
    assert cw_n.unit_weight != ctci_n.unit_weight


def test_type105_field_member_and_300_max_member_p_are_not_conflated():
    result = analyze_single("105-L75-20C")

    member_m = _entry(result, "D114-MEMBER-M")
    member_p = _entry(result, "D114-MEMBER-P")
    assert not result.error
    assert member_m.length == 2000
    assert member_m.geometry.parameters["field_fit"] is True
    assert not member_m.geometry.fabrication_ready
    assert member_p.unit_weight == 0
    assert member_p.geometry.parameters["maximum_envelope_mm"] == 300
    assert member_p.geometry.parameters["cut_length_mm"] is None


def test_type105_missing_member_p_and_unapproved_hbeam_weight_fail_safely():
    missing_p = analyze_single("105-H150-10C")
    h294 = analyze_single("105-H294-10A")

    assert missing_p.error and "Member P" in missing_p.error
    assert missing_p.entries == []
    h294_member = _entry(h294, "D114-MEMBER-M")
    assert not h294.error
    assert h294_member.unit_weight == 0
    assert "尚無核定 kg/m" in h294_member.remark


def test_type108_ambiguous_supporting_pipe_requires_explicit_selection():
    result = analyze_single("108-1B-10G-A")

    pipe = _entry(result, "D119-SUPPORTING-PIPE-B")
    lower = _entry(result, "D119-M42-LOWER-COMPONENT")
    assert not result.error
    assert pipe.unit_weight == lower.unit_weight == 0
    assert len(pipe.geometry.parameters["candidate_rows"]) == 2
    assert result.meta["fabrication"]["assembly_dimensions"]["supporting_pipe"] is None


def test_type108_explicit_pipe_cut_emits_stock_weight_but_keeps_fishmouth_blocker():
    result = analyze_single(
        "108-1B-10G-C(S)",
        overrides={
            "supporting_pipe_size": 1,
            "supporting_pipe_cut_length_mm": 850,
        },
    )

    pipe = _entry(result, "D119-SUPPORTING-PIPE-B")
    brace = _entry(result, "D119-FIG-C-FLAT-BAR")
    plates = _entry(result, "D119-LUG-SPACER-ASSEMBLY")
    assert not result.error
    assert pipe.length == 850
    assert pipe.unit_weight > 0
    assert not pipe.geometry.fabrication_ready
    assert brace.geometry.parameters["cut_length_mm"] == 210
    assert brace.material == "STAINLESS STEEL MATCHING MAIN LINE"
    assert plates.geometry.parameters["lug_material"] == (
        "STAINLESS STEEL MATCHING MAIN LINE"
    )
    assert plates.geometry.parameters["spacer_material"] == (
        "CARBON STEEL GRADE TBD"
    )


def test_type110_exists_only_in_20e_and_stays_site_fit_zero_reference():
    unsupported = analyze_single("110-10A")
    ctci20 = analyze_single(
        "110-10A",
        source_profile=CTCI_20E4588,
    )

    assert unsupported.error and "尚未建立來源 profile" in unsupported.error
    assembly = _entry(ctci20, "D123-FIG-A-DITCH-SUPPORT")
    assert not ctci20.error
    assert assembly.unit_weight == 0
    assert assembly.geometry.parameters["ditch_clear_span_L_mm"] == 1000
    assert assembly.geometry.parameters["site_fit"] is True


def test_type112_calculates_only_exact_base_plate():
    result = analyze_single("112-4B")

    base = _entry(result, "D125-BASE-PLATE")
    flange = _entry(result, "D125-VALVE-FLANGE-SUPPORT-PLATES")
    assert not result.error
    assert base.geometry.parameters["cut_length_mm"] == 390
    assert base.geometry.parameters["width_W_mm"] == 229
    assert base.geometry.parameters["thickness_T2_mm"] == 9
    assert base.geometry.fabrication_ready
    assert flange.quantity == 2
    assert flange.unit_weight == 0
    assert "ANSI 150#" in flange.remark


def test_type115_plate_count_includes_both_ends_and_respects_nmax():
    result = analyze_single("115-1B-30")

    member = _entry(result, "D128-MEMBER-M")
    plates = _entry(result, "D128-PLATE-P")
    params = plates.geometry.parameters
    assert not result.error
    assert member.length == 3000
    assert plates.quantity == 4
    assert params["positions_from_start_mm"] == [0, 1000, 2000, 3000]
    assert params["actual_equal_spacing_mm"] <= params["maximum_spacing_N_mm"]
    assert result.meta["fabrication"]["bom_ready"] is True
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_m57_tables_and_type118_neutral_developments_are_drawing_based():
    row = get_m57_by_line_size(4)
    result = analyze_single("118-4B-120")

    saddle = _entry(result, "D131-M57-ROLLED-SADDLE-HALVES")
    lugs = _entry(result, "D131-M57-DRILLED-LUGS")
    bolts = _entry(result, "D131-M57-MACHINE-BOLTS")
    lining = _entry(result, "D131-RUBBER-LINING")
    assert row["dimensions_mm"] == {"W": 165, "T": 3, "A": 25, "H": 8}
    assert row["weight_ready"] is False
    assert saddle.geometry.parameters["inside_diameter_D_mm"] == 126
    assert saddle.geometry.parameters["piece_count"] == 2
    assert saddle.quantity == 2
    assert saddle.length == pytest.approx(math.pi * 129 / 2)
    assert saddle.geometry.parameters[
        "neutral_developed_total_mm"
    ] == pytest.approx(math.pi * 129)
    assert lugs.quantity == 4
    assert bolts.quantity == 2
    assert lining.quantity == 2
    assert lining.geometry.parameters[
        "each_piece_neutral_developed_length_mm"
    ] == pytest.approx(math.pi * 123 / 2)
    assert lining.geometry.parameters[
        "neutral_developed_total_mm"
    ] == pytest.approx(math.pi * 123)
    assert lining.unit_weight == 0


def test_type119_small_branch_uses_m58_and_exact_two_hole_plate():
    result = analyze_single("119-4B-120")

    ubolt = _entry(result, "D132-M58-U-BOLT")
    plate = _entry(result, "D132-TWO-HOLE-PLATE")
    assert not result.error
    m58 = get_m58_by_line_size(4)
    assert m58["dimensions_mm"] == {"D": 60, "E": 100}
    assert m58["weight_ready"] is True
    b_inside = 120 + 18
    centerline_span = b_inside + m58["rod_dia_mm"]
    expected_dev = math.pi * centerline_span / 2 + 2 * 100
    assert ubolt.length == pytest.approx(expected_dev)
    assert ubolt.geometry.parameters["inside_clear_B_mm"] == b_inside
    assert ubolt.geometry.parameters[
        "centerline_span_mm"
    ] == pytest.approx(centerline_span)
    assert plate.geometry.parameters["hole_pitch_P_mm"] == 148
    assert plate.geometry.parameters["plate_length_mm"] == 188
    assert result.meta["fabrication"]["branch"].startswith("M-58")


def test_type119_large_branch_uses_m59_flat_development():
    result = analyze_single("119-12B-320")

    band = _entry(result, "D132-M59-U-BAND")
    assert not result.error
    m59 = get_m59_by_line_size(12)
    assert m59["dimensions_mm"] == {
        "D": 100,
        "T": 6,
        "G": 9,
    }
    assert m59["weight_ready"] is True
    assert band.material == "CARBON STEEL GALVANIZED"
    assert band.geometry.parameters["inside_radius_R_mm"] == 172
    assert band.geometry.parameters["straight_leg_H_mm"] == 169
    assert band.geometry.parameters[
        "neutral_developed_length_mm"
    ] == pytest.approx(math.pi * 175 + 2 * 169)
    assert result.meta["fabrication"]["branch"] == "M-59 U-BAND"


def test_type119_rejects_size_not_drawn_before_adding_partial_entries():
    result = analyze_single("119-0.75B-25")

    assert result.error and '未表列 0.75"' in result.error
    assert result.entries == []


@pytest.mark.parametrize(
    ("designation", "expected_e", "expected_f", "expected_h"),
    [
        ("120-4B-120", 76, 12, 8),
        ("120-12B-320", 188, 21, 14),
    ],
)
def test_type120_preserves_anchor_dimensions_but_blocks_composite_collar(
    designation, expected_e, expected_f, expected_h
):
    result = analyze_single(designation)

    collar = _entry(result, "D134-ANCHOR-COLLAR-ASSEMBLY")
    collar_bolts = _entry(result, "D134-COLLAR-MACHINE-BOLTS")
    saddle = _entry(result, "D133-M57-ROLLED-SADDLE-HALVES")
    params = collar.geometry.parameters
    assert not result.error
    assert collar.unit_weight == 0
    assert params["E_mm"] == expected_e
    assert params["F_mm"] == expected_f
    assert params["bolt_hole_H_mm"] == expected_h
    expected_bolt = (
        "1/4in x 40mm"
        if designation.startswith("120-4")
        else "1/2in x 60mm"
    )
    assert params["collar_machine_bolt_J"] == expected_bolt
    assert params["collar_machine_bolt_quantity"] == 2
    assert collar_bolts.spec.startswith(expected_bolt)
    assert collar_bolts.quantity == 2
    assert "A36" not in collar.material
    assert "SS400" not in collar.material
    assert saddle.unit_weight == 0
    assert "CUT 3MM FOR WELD" in saddle.remark
    if designation.startswith("120-12"):
        band = _entry(result, "D133-M59-U-BAND")
        assert band.unit_weight == 0
        assert "CUT TO SUIT" in band.remark
    assert collar.geometry.fabrication_blockers
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_non_default_source_profiles_are_open_only_for_reviewed_types():
    type103 = analyze_single(
        "103-1-A",
        source_profile=CTCI_22A_5123A,
    )
    type105 = analyze_single(
        "105-L50-10A",
        source_profile=CTCI_20E4588,
    )
    unsupported_104 = analyze_single(
        "104-2B",
        source_profile=CTCI_22A_5123A,
    )

    assert type103.meta["source_profile_rule_status"] == "partial"
    assert type105.meta["source_profile_rule_status"] == "partial"
    assert unsupported_104.error and "尚未完成" in unsupported_104.error
