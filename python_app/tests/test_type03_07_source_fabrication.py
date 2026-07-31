import pytest

from core.calculator import analyze_single
from data.m37_table import get_m37_by_type


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type03_preserves_lr_estimate_but_removes_fake_ubolt_weight():
    result = analyze_single(
        "03-1B-05N",
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    assert _entry(result, "D3-VERTICAL-L75").length == 574.8
    ubolt = _entry(result, "D3-U-BOLT")
    assert (ubolt.material, ubolt.unit_weight, ubolt.weight_output) == (
        "NOT SPECIFIED IN D-3",
        0,
        0,
    )
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any(
        "彎頭半徑" in blocker
        for blocker in result.meta["fabrication"]["blockers"]
    )


def test_type03_explicit_cut_and_ubolt_procurement_overrides_are_recorded():
    result = analyze_single(
        "03-1B-05N",
        overrides={
            "vertical_cut_length_mm": 580,
            "ubolt_spec": "U10-M10-120",
            "ubolt_material": "SUS304",
            "ubolt_unit_weight_kg": 0.35,
        },
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    assert _entry(result, "D3-VERTICAL-L75").length == 580
    assert _entry(result, "D3-U-BOLT").weight_output == pytest.approx(0.35)
    assert result.meta["fabrication"]["bom_ready"] is True


def test_type03_distinguishes_member_error_envelope_warning_and_m42_risk():
    assert analyze_single("03-3B-05N", source_profile="cw_e25_24_hp6").error
    height = analyze_single("03-1B-16N", source_profile="cw_e25_24_hp6")
    m42 = analyze_single("03-1B-05A", source_profile="cw_e25_24_hp6")
    assert not height.error
    assert height.meta["issues"][0]["severity"] == "warning"
    assert not m42.error
    assert m42.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"
    assert analyze_single("03-1B-31N", source_profile="cw_e25_24_hp6").error


def test_type05_h_minus_15_and_d68_not_furnished():
    result = analyze_single(
        "05-L50-05L",
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    assert _entry(result, "D5-VERTICAL-MEMBER-M").length == 485
    assert _entry(result, "D5-HORIZONTAL-MEMBER-M").length == 130
    assert all(entry.name != "U.bolt" for entry in result.entries)
    assert result.meta["fabrication"]["not_furnished"] == [
        "STANDARD U-BOLT D-68"
    ]


def test_type05_distinguishes_member_error_envelope_warning_and_m42_risk():
    assert analyze_single("05-C100-05L", source_profile="cw_e25_24_hp6").error
    height = analyze_single("05-L50-16L", source_profile="cw_e25_24_hp6")
    m42 = analyze_single("05-L50-05N", source_profile="cw_e25_24_hp6")
    assert not height.error
    assert height.meta["issues"][0]["severity"] == "warning"
    assert not m42.error
    assert m42.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"


def test_type06_restores_m37_lug_plate_and_two_angle_bolts():
    result = analyze_single(
        "06-L50-0510-0401",
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    plate = _entry(result, "M37-LGP-F-1")
    bolt = _entry(result, "D6-K-BOLT")
    assert plate.geometry.shape_kind == "lug_plate_type_f_trapezoid"
    assert plate.geometry.holes.count == 2
    assert plate.geometry.fabrication_ready is True
    assert plate.weight_output > 0
    assert (bolt.spec, bolt.quantity) == ('5/8"X40', 2)
    assert bolt.unit_weight > 0
    assert result.meta["fabrication"]["dimensions"]["A_plus_B_equals_L"] is False
    assert any("A+B" in warning for warning in result.warnings)


def test_type06_channel_uses_four_m37_holes_and_bolts():
    result = analyze_single(
        "06-C150-0510",
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    assert _entry(result, "M37-LGP-F-6").geometry.holes.count == 4
    assert _entry(result, "D6-K-BOLT").quantity == 4
    assert result.meta["fabrication"]["dimensions"]["A_plus_B_equals_L"] is True


@pytest.mark.parametrize(
    "designation",
    ["06-C100-0510", "06-L50-1610", "06-L50-0511"],
)
def test_type06_source_limits_are_hard_stops(designation):
    assert analyze_single(
        designation,
        source_profile="cw_e25_24_hp6",
    ).error


def test_m37_row_8_matches_source_drawing_member():
    assert get_m37_by_type("LGP-F-8")["member"] == "C200*90*8"


def test_type07_source_row_and_cut_formulas_are_preserved():
    result = analyze_single(
        "07-2B-20J",
        source_profile="cw_e25_24_hp6",
    )
    assert not result.error
    assert _entry(result, "D7-SUPPORTING-PIPE-B").length == 271
    assert _entry(result, "D7-SUPPORTING-PIPE-C").length == 1782
    assert _entry(result, "D7-BASE-PLATE-E").geometry.fabrication_ready is True
    assert _entry(result, "D7-SLIDING-PLATE-F").geometry.fabrication_ready is True
    assert any(
        "weep hole" in blocker
        for blocker in result.meta["fabrication"]["blockers"]
    )


def test_type07_keeps_lower_bound_hard_and_grades_upper_and_m42():
    assert analyze_single("07-2B-15J", source_profile="cw_e25_24_hp6").error
    height = analyze_single("07-2B-35J", source_profile="cw_e25_24_hp6")
    m42 = analyze_single("07-2B-20L", source_profile="cw_e25_24_hp6")
    assert not height.error
    assert height.meta["issues"][0]["severity"] == "warning"
    assert not m42.error
    assert m42.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"


@pytest.mark.parametrize(
    ("designation", "source"),
    [
        ("03-1B-05N", "ctci_22a_5123a"),
        ("05-L50-05L", "ctci_20e4588"),
        ("06-L50-0510", "ctci_22a_5123a"),
        ("07-2B-20J", "ctci_20e4588"),
    ],
)
def test_legacy_types_do_not_fall_back_to_cw_for_ctci_sources(
    designation,
    source,
):
    assert "暫不計算" in analyze_single(
        designation,
        source_profile=source,
    ).error
