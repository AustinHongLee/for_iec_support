"""Drawing-truth locks for the DSP-500-006 cold-support Type family."""

import pytest

from core import config_loader
from core.calculator import analyze_single
from core.source_profiles import CTCI_22A_5123A


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_letter_suffixed_type_loads_its_own_config_and_version():
    config = config_loader.load_config("109C", strict=True)

    assert config["type_id"] == "109C"
    assert config_loader.get_config_version_info("109C") == (
        "1.0",
        "2026-07-30",
    )


def test_type109c_preserves_c52_dimensions_without_inventing_member_cuts():
    result = analyze_single("109C-6B-300-500")

    assembly = _entry(result, "C52-TYPE109C-ASSEMBLY")
    params = assembly.geometry.parameters
    assert not result.error
    assert result.total_weight == 0
    assert params["line_size_in"] == 6
    assert params["B_mm"] == 300
    assert params["C_mm"] == 500
    assert params["orientation_angle_deg"] == 45
    assert not result.meta["fabrication"]["bom_ready"]


def test_type110c_accepts_explicit_orientation_override():
    result = analyze_single(
        "110C-4B-200-500",
        overrides={"orientation_angle_deg": 30},
    )

    assembly = _entry(result, "C53-TYPE110C-ASSEMBLY")
    assert not result.error
    assert result.total_weight == 0
    assert assembly.geometry.parameters["orientation_angle_deg"] == 30
    assert assembly.geometry.parameters["sections"] == [
        "L100x100x10",
        "L75x75x9",
    ]


def test_type112c_does_not_treat_the_45_degree_envelope_as_a_cut_length():
    result = analyze_single("112C-200-500")

    assembly = _entry(result, "C55-TYPE112C-ASSEMBLY")
    assert not result.error
    assert result.total_weight == 0
    assert assembly.geometry.parameters["B_mm"] == 200
    assert assembly.geometry.parameters["C_mm"] == 500
    assert any("不得用 45-degree envelope" in warning for warning in result.warnings)


def test_type113c_calculates_only_the_designation_driven_member_stock():
    result = analyze_single("113C-L75-500")

    member = _entry(result, "C56-MEMBER-M")
    connection = _entry(result, "C56-N12-N28-CONNECTION")
    assert not result.error
    assert member.length == 500
    assert member.weight_per_unit == 9.96
    assert member.unit_weight == pytest.approx(4.98)
    assert connection.unit_weight == 0
    assert connection.geometry.parameters["maximum_load_at_C_kg"] == 80
    assert not member.geometry.fabrication_ready


@pytest.mark.parametrize("designation", ["113C-L90-500", "113C-L75-0"])
def test_type113c_rejects_non_drawing_member_or_nonpositive_length(designation):
    result = analyze_single(designation)

    assert result.error
    assert result.entries == []


def test_type114c_uses_the_correct_branch_and_c_limit():
    small = analyze_single("114C-A-CR9-2B-500")
    large = analyze_single("114C-B-CR22-22B-1100")
    too_long = analyze_single("114C-B-CR22-12B-1101")

    assert not small.error
    assert _entry(
        small, "C57-C59-TYPE114C-ASSEMBLY"
    ).geometry.parameters["branch"] == "small_2_and_under"
    large_params = _entry(
        large, "C57-C59-TYPE114C-ASSEMBLY"
    ).geometry.parameters
    assert not large.error
    assert large_params["branch"] == "twelve_twenty_four"
    assert large_params["clip_reference"] == "N-14 CLIP TYPE 6"
    assert too_long.error and "<= 1100" in too_long.error


def test_type115c_splits_combined_cradle_token_and_rejects_unlisted_size():
    result = analyze_single("115C-ACR9-6B-800")
    invalid = analyze_single("115C-ACR9-5B-800")

    params = _entry(
        result, "C60-C61-TYPE115C-ASSEMBLY"
    ).geometry.parameters
    assert not result.error
    assert params["cradle_length_code"] == "A"
    assert params["cradle_no"] == "CR9"
    assert params["branch"] == "six_twenty_four"
    assert invalid.error and '5"' in invalid.error


@pytest.mark.parametrize(
    ("designation", "figure", "interface"),
    [
        ("116C-A-CR8-1B-500A", "A", "vessel clip"),
        ("116C-B-CR8-4B-600B", "B", "vessel clip"),
        ("116C-C-CR8-6B-700C", "C", "existing surface"),
    ],
)
def test_type116c_keeps_each_source_figure_separate(
    designation, figure, interface
):
    result = analyze_single(designation)

    assembly = _entry(result, f"C62-C63-TYPE116C-FIG-{figure}")
    assert not result.error
    if figure == "A":
        assert result.total_weight > 0
    else:
        assert result.total_weight == 0
    assert assembly.geometry.parameters["figure"] == figure
    assert assembly.geometry.parameters["interface"] == interface


def test_type117c_subtracts_the_drawn_9t_end_plate_from_member_cut():
    result = analyze_single("117C-L75-200-500")

    member = _entry(result, "C64-MEMBER-M")
    plate = _entry(result, "C64-END-PLATE-N12-N28")
    assert not result.error
    assert member.length == 491
    assert member.unit_weight == pytest.approx(4.89)
    assert member.geometry.parameters["cut_formula"] == "C - 9t end plate"
    assert plate.unit_weight == 0
    assert plate.geometry.parameters["end_plate_other_side_mm"] is None


def test_type119c_selects_only_explicit_c67_nominal_sizes():
    small = analyze_single("119C-CR12-8B")
    small_intermediate = analyze_single("119C-CR12-2.1/2B")
    large = analyze_single("119C-CR20-14B")
    invalid_gap = analyze_single("119C-CR20-13B")

    small_params = _entry(
        small, "C67-TYPE119C-ASSEMBLY"
    ).geometry.parameters
    large_params = _entry(
        large, "C67-TYPE119C-ASSEMBLY"
    ).geometry.parameters
    assert small_params["member_q_section"] == "L75x75x9"
    assert _entry(
        small_intermediate, "C67-TYPE119C-ASSEMBLY"
    ).geometry.parameters["member_q_section"] == "L75x75x9"
    assert large_params["member_q_section"] == "L100x100x10"
    assert small.total_weight == small_intermediate.total_weight == large.total_weight == 0
    assert invalid_gap.error


def test_type120c_turnbuckle_boundary_and_figure_chain_follow_c68():
    at_limit = analyze_single("120C-A-CR4-2B-1/2-2000-A")
    over_limit = analyze_single("120C-A-CR4-2B-1/2-2001-B")

    a_params = _entry(
        at_limit, "C68-TYPE120C-FIG-A"
    ).geometry.parameters
    b_params = _entry(
        over_limit, "C68-TYPE120C-FIG-B"
    ).geometry.parameters
    assert not a_params["turnbuckle_required"]
    assert b_params["turnbuckle_required"]
    assert any("M-22" in item for item in a_params["hanger_chain"])
    assert any("M-23" in item for item in b_params["hanger_chain"])
    assert at_limit.total_weight == over_limit.total_weight == 0


def test_type121c_transcribes_cr42_and_calculates_two_member_q_stocks():
    result = analyze_single("121C-B-CR42-30B-G")

    members = _entry(result, "C70-MEMBER-Q-GUIDES")
    assembly = _entry(result, "C69-C70-COLD-GUIDE-ASSEMBLY")
    assert not result.error
    assert members.quantity == 2
    assert members.length == 690
    assert members.weight_per_unit == 23.8
    assert members.unit_weight == pytest.approx(16.42)
    assert result.total_weight == pytest.approx(32.84)
    assert assembly.geometry.parameters["W_mm"] == 675
    assert assembly.geometry.parameters["H_mm"] == 635
    assert assembly.geometry.parameters["h1_mm"] == 150
    assert assembly.geometry.parameters["h2_mm"] == 250


@pytest.mark.parametrize(
    "designation",
    [
        "121C-B-CR31-30B-G",
        "121C-B-CR42-29B-G",
        "121C-B-CR42-30B-A",
    ],
)
def test_type121c_enforces_cradle_pipe_and_guide_boundaries(designation):
    result = analyze_single(designation)

    assert result.error
    assert result.entries == []


def test_cold_types_do_not_silently_run_under_an_unverified_ctci_profile():
    result = analyze_single(
        "121C-B-CR42-30B-G",
        source_profile=CTCI_22A_5123A,
    )

    assert result.error and "尚未完成" in result.error
    assert result.entries == []
