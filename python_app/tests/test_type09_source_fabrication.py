import pytest

from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type09_cw_corrects_two_pipe_cut_chain_and_m43_plate_a_rule():
    result = analyze_single(
        "09-2B-05B",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    assert not result.error
    upper = _component(result, "D9-UPPER-DUMMY-LEG")
    lower = _component(result, "D9-LOWER-SUPPORTING-PIPE")
    assert upper.length == 206
    assert lower.length == 300
    assert upper.spec == '2"*SCH.40'
    assert lower.spec == '2"*SCH.40'
    assert lower.geometry.parameters["cut_formula"] == "H - 100 - 100"

    assert not any(entry.name.startswith("Plate_a_") for entry in result.entries)
    assert any(entry.name.startswith("Plate_d_") for entry in result.entries)
    assert result.meta["fabrication"]["omitted_by_type09_m43_note"] == [
        "Plate_a_無鑽孔"
    ]
    assert _component(result, "D9-ADJUSTING-BOLT").spec.startswith(
        '1-5/8"'
    )


def test_type09_straight_branch_uses_100_upper_tail():
    result = analyze_single(
        "09-3B-05H",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "straight"},
    )

    assert not result.error
    assert _component(result, "D9-UPPER-DUMMY-LEG").length == 100
    assert _component(result, "D9-LOWER-SUPPORTING-PIPE").length == 300
    assert not any(
        entry.geometry.component_id.startswith("M42-")
        for entry in result.entries
    )
    assert result.meta["fabrication"]["branch"] == "D-9/straight/M42-H"
    assert result.meta["fabrication"]["bom_ready"] is True


def test_type09_connection_must_be_explicit_for_bom_ready():
    result = analyze_single(
        "09-2B-05B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("straight/elbow" in warning for warning in result.warnings)


def test_type09_22a_has_300_to_1800_height_and_own_m42_set():
    below = analyze_single(
        "09-2B-02B",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert below.error

    upper = analyze_single(
        "09-4B-18R",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "elbow"},
    )
    assert not upper.error
    assert _component(upper, "D9-LOWER-SUPPORTING-PIPE").length == 1600
    assert _component(upper, "D9-ADJUSTING-BOLT").spec.startswith(
        '1-3/4"'
    )
    assert any(entry.name.startswith("Plate_a_") for entry in upper.entries)

    c_type = analyze_single(
        "09-2B-03C",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert not c_type.error
    assert not any(entry.name.startswith("Plate_a_") for entry in c_type.entries)


def test_type09_20e_type_c_retains_150_square_resting_plate():
    result = analyze_single(
        "09-2B-05C",
        source_profile="ctci_20e4588",
        overrides={"connection": "straight"},
    )

    assert not result.error
    plate = _component(result, "M42-PLATE-A")
    assert (plate.length, plate.width, plate.spec) == (150, 150, "9")
    assert plate.geometry.parameters["weld_per_type09_detail"] is True
    assert _component(result, "D9-ADJUSTING-BOLT").spec.startswith("M42")


@pytest.mark.parametrize(
    ("profile", "code", "severity"),
    [
        ("cw_e25_24_hp6", "09-2B-05C", "high"),
        ("ctci_20e4588", "09-2B-05R", "high"),
        ("ctci_22a_5123a", "09-2B-19B", "warning"),
    ],
)
def test_type09_grades_host_m42_and_upper_h_variances(profile, code, severity):
    result = analyze_single(
        code,
        source_profile=profile,
        overrides={"connection": "straight"},
    )

    assert not result.error
    assert result.entries
    assert result.meta["issues"][0]["severity"] == severity


def test_type09_adjusting_hardware_has_procurement_geometry_not_fake_nut_weight():
    result = analyze_single(
        "09-2B-05B",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    bolt = _component(result, "D9-ADJUSTING-BOLT")
    nuts = _component(result, "D9-HEAVY-HEX-NUT")
    assert bolt.geometry.fabrication_ready is True
    assert bolt.geometry.parameters["overall_length_mm"] == 150
    assert bolt.unit_weight == 1.58
    assert nuts.quantity == 2
    assert nuts.unit_weight == 0
    assert any("螺帽重量未計入" in warning for warning in result.warnings)
