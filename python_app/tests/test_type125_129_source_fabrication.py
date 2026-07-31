"""Drawing-truth locks for the final Chung Wei Type 125~129 wave."""

import math

import pytest

from core.calculator import analyze_single
from core.source_profiles import CTCI_22A_5123A


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type125_transcribes_and_weighs_the_d135_8_inch_ubolt():
    result = analyze_single("125-8B")

    ubolt = _entry(result, "D135-U-BOLT-ASSEMBLY")
    irod = _entry(result, "D135-I-ROD")
    assert not result.error
    assert result.total_weight > 0
    assert ubolt.unit_weight > 0
    assert ubolt.density_requires_review
    assert ubolt.geometry.parameters["pipe_od_D_mm"] == 219.1
    assert ubolt.geometry.parameters["bolt_diameter_d1"] == "1/2in"
    assert ubolt.geometry.parameters["bolt_leg_L_mm"] == 290
    assert ubolt.geometry.parameters["span_P_mm"] == 236
    assert ubolt.geometry.parameters["thread_length_A_mm"] == 90
    assert ubolt.geometry.parameters["tightening_torque_Nm"] == 20.34
    expected_developed = (
        math.pi * 236 / 2
        + 2 * (290 - 236 / 2 - 12.7 / 2)
    )
    assert ubolt.geometry.parameters["developed_length_mm"] == pytest.approx(
        expected_developed
    )
    assert (
        ubolt.geometry.parameters["developed_length_formula"]
        == "PI*P/2 + 2*(L - P/2 - d1/2)"
    )
    assert ubolt.geometry.parameters["nut_quantity_visibly_shown"] == 2
    assert irod.geometry.parameters["length_F_mm"] == 279.4
    assert irod.geometry.parameters["height_I_mm"] == 11.1
    assert irod.geometry.parameters["hole_diameter_G"] == "5/8in"
    assert irod.geometry.parameters["piece_count"] is None
    assert any("i_rod_count" in warning for warning in result.warnings)
    assert any("material class" in warning for warning in result.warnings)


def test_type125_explicit_count_and_temperature_class_drive_procurement_data():
    result = analyze_single(
        "125-10B",
        overrides={
            "i_rod_count": 3,
            "i_rod_temperature_class": "peek",
        },
    )

    ubolt = _entry(result, "D135-U-BOLT-ASSEMBLY")
    irod = _entry(result, "D135-I-ROD")
    assert not result.error
    assert ubolt.quantity == irod.quantity == 3
    assert irod.material == "THERMOPLASTIC I-ROD PEEK"
    assert irod.geometry.parameters["maximum_temperature_C"] == 249
    assert irod.geometry.parameters["single_point_load_limit_kg"] == 4540
    assert not any("i_rod_count" in warning for warning in result.warnings)
    assert not any("material class" in warning for warning in result.warnings)


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"i_rod_count": 4}, "i_rod_count"),
        ({"i_rod_temperature_class": "unknown"}, "temperature_class"),
    ],
)
def test_type125_rejects_unapproved_project_choices(overrides, message):
    result = analyze_single("125-4B", overrides=overrides)

    assert result.error and message in result.error
    assert result.entries == []


def test_type126_uses_schedule_count_and_temperature_for_the_d136_row():
    result = analyze_single(
        "126-10B",
        overrides={
            "pipe_schedule": "SCH.80",
            "i_rod_count": 2,
            "i_rod_temperature_class": "high_temp",
        },
    )

    pad = _entry(result, "D136-I-ROD-PAD")
    params = pad.geometry.parameters
    assert not result.error
    assert result.total_weight == 0
    assert pad.quantity == 2
    assert pad.material == "THERMOPLASTIC I-ROD HIGH TEMP"
    assert params["length_L_mm"] == 342.9
    assert params["width_C_mm"] == 38.1
    assert params["height_D_mm"] == 17.5
    assert params["maximum_cross_beam_spacing_m"] == 29
    assert params["single_point_load_limit_kg"] == 4540
    assert params["maximum_temperature_C"] == 171


def test_type126_preserves_missing_project_inputs_as_layout_blockers():
    result = analyze_single("126-8B")

    pad = _entry(result, "D136-I-ROD-PAD")
    assert not result.error
    assert pad.geometry.parameters["piece_count"] is None
    assert pad.geometry.parameters["maximum_cross_beam_spacing_m"] is None
    assert any("pipe_schedule" in warning for warning in result.warnings)
    assert any("material class" in warning for warning in result.warnings)
    assert not result.meta["fabrication"]["bom_ready"]


def test_type126_rejects_schedule_where_d136_has_no_spacing_value():
    result = analyze_single(
        "126-2.5B",
        overrides={"pipe_schedule": "SCH40"},
    )

    assert result.error and "未提供 I-Rod cross-beam 最大間距" in result.error
    assert result.entries == []


def test_type127_keeps_unknown_c150_weight_but_calculates_exact_base_plates():
    result = analyze_single("127-15L")

    member = _entry(result, "D137-MEMBER-1")
    base = _entry(result, "D137-BASE-PLATES")
    anchors = _entry(result, "D137-EB2-ANCHORS")
    expected_one = (
        (170 * 330 - 4 * math.pi * 19**2 / 4)
        * 12
        * 7.85e-6
    )
    assert not result.error
    assert member.unit_weight == 0
    assert member.geometry.parameters["cut_length_L_mm"] == 1500
    assert "尚無核定 kg/m" in member.remark
    assert base.quantity == 2
    assert base.unit_weight == pytest.approx(expected_one, abs=0.01)
    assert base.geometry.holes.pitch_x == 90
    assert base.geometry.holes.pitch_y == 250
    assert base.geometry.holes.diameter == 19
    assert base.geometry.fabrication_ready
    assert anchors.quantity == 8
    assert anchors.unit_weight > 0
    assert anchors.geometry.parameters["weight_estimate"][
        "kind"
    ] == "expansion_bolt"
    assert result.meta["fabrication"]["assembly_dimensions"][
        "overall_support_envelope_mm"
    ] == 1600


def test_type128_calculates_c200_stock_and_exact_d138_plate_geometry():
    result = analyze_single("128-15L")

    member = _entry(result, "D138-MEMBER-1")
    base = _entry(result, "D138-BASE-PLATES")
    anchors = _entry(result, "D138-EB2-ANCHORS")
    expected_one = (
        (170 * 380 - 4 * math.pi * 19**2 / 4)
        * 12
        * 7.85e-6
    )
    assert not result.error
    assert member.weight_per_unit == 24.6
    assert member.unit_weight == pytest.approx(36.9)
    assert not member.geometry.fabrication_ready
    assert base.quantity == 2
    assert base.unit_weight == pytest.approx(expected_one, abs=0.01)
    assert base.geometry.holes.pitch_y == 300
    assert base.geometry.fabrication_ready
    assert anchors.unit_weight > 0


def test_type129_builds_two_h_sections_and_dynamic_four_hole_plates():
    result = analyze_single("129-20L-3W")

    members = _entry(result, "D139-TWIN-H-SECTIONS")
    base = _entry(result, "D139-BASE-PLATES")
    anchors = _entry(result, "D139-EB2-ANCHORS")
    expected_one = (
        (170 * 630 - 4 * math.pi * 19**2 / 4)
        * 12
        * 7.85e-6
    )
    assert not result.error
    assert members.quantity == 2
    assert members.length == 2000
    assert members.weight_per_unit == 31.5
    assert members.unit_weight == 63
    assert members.geometry.parameters["centerline_spacing_W_mm"] == 300
    assert base.quantity == 2
    assert base.width == 630
    assert base.unit_weight == pytest.approx(expected_one, abs=0.01)
    assert base.geometry.holes.pitch_x == 90
    assert base.geometry.holes.pitch_y == 550
    assert base.geometry.parameters["C_star_mm"] == 150
    assert anchors.quantity == 8
    assert anchors.unit_weight > 0
    assert any("CHANNEL" in warning for warning in result.warnings)


@pytest.mark.parametrize(
    "designation",
    [
        "127-16L",
        "128-16L",
        "129-21L-3W",
        "129-20L-2W",
    ],
)
def test_field_supports_enforce_drawing_limits(designation):
    result = analyze_single(designation)

    assert result.error
    assert result.entries == []


def test_type125_to_129_do_not_silently_run_under_unopened_ctci_source():
    result = analyze_single(
        "125-8B",
        source_profile=CTCI_22A_5123A,
    )

    assert result.error and "尚未完成" in result.error
    assert result.entries == []
