import pytest

from core.calculator import analyze_single


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type08_cw_uses_outer_l_and_two_chamfered_stoppers():
    result = analyze_single(
        "08-2B-1005G",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert _entry(result, "D8-SUPPORTING-PIPE-A").length == 435
    channel = _entry(result, "D8-MEMBER-N")
    assert channel.length == 988
    assert channel.geometry.parameters["cut_formula"] == (
        "L - 2 * stopper_thickness"
    )

    stopper = _entry(result, "D8-STOPPER")
    assert stopper.quantity == 2
    assert stopper.geometry.shape_spec == "70x160x6t; 4-C10"
    assert stopper.geometry.net_area_mm2 == 11000
    assert stopper.unit_weight == 0.52

    fabrication = result.meta["fabrication"]
    assert fabrication["bom_ready"] is True
    assert fabrication["fabrication_ready"] is False
    assert "weep hole" in fabrication["blockers"][0]


def test_type08_cw_unlisted_but_source_defined_lower_component_is_high_risk():
    result = analyze_single(
        "08-2B-1005R",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert result.entries
    assert result.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type08_22a_applies_source_table_and_h_condition():
    size2 = analyze_single(
        "08-2B-0505G",
        source_profile="ctci_22a_5123a",
    )
    assert size2.error
    assert '未表列 2" supporting pipe' in size2.error

    too_long = analyze_single(
        "08-3B-0615G",
        source_profile="ctci_22a_5123a",
    )
    assert not too_long.error
    assert too_long.meta["issues"][0]["severity"] == "high"

    conditional = analyze_single(
        "08-3B-0520G",
        source_profile="ctci_22a_5123a",
    )
    assert not conditional.error
    assert any("supported line size" in item for item in conditional.warnings)
    assert any(
        "NOTE 4" in item
        for item in conditional.meta["fabrication"]["blockers"]
    )

    invalid_line = analyze_single(
        "08-3B-0520G",
        source_profile="ctci_22a_5123a",
        overrides={"supported_line_size": 3},
    )
    assert invalid_line.error
    assert '僅適用於 2" 以下' in invalid_line.error

    confirmed_line = analyze_single(
        "08-3B-0520G",
        source_profile="ctci_22a_5123a",
        overrides={"supported_line_size": 2},
    )
    assert not confirmed_line.error
    assert not any(
        "NOTE 4" in item
        for item in confirmed_line.meta["fabrication"]["blockers"]
    )


def test_type08_22a_size4_uses_800_overall_and_788_channel():
    result = analyze_single(
        "08-4B-0825R",
        source_profile="ctci_22a_5123a",
    )

    assert not result.error
    assert _entry(result, "D8-MEMBER-N").length == 788
    assert _entry(result, "D8-TOP-PLATE-B").length == 135
    assert _entry(result, "D8-STOPPER").length == 85


def test_type08_20e4588_parses_l1_l2_and_does_not_invent_stoppers():
    result = analyze_single(
        "08-3B-0515T-0203",
        source_profile="ctci_20e4588",
    )

    assert not result.error
    assert _entry(result, "D8-MEMBER-N").length == 500
    assert not any(
        entry.geometry.component_id == "D8-STOPPER"
        for entry in result.entries
    )
    channel = _entry(result, "D8-MEMBER-N")
    assert channel.geometry.parameters["support_axis_from_overall_left_mm"] == 200
    assert channel.geometry.parameters["right_span_mm"] == 300
    assert channel.geometry.parameters["placement_modified"] is True

    fabrication = result.meta["fabrication"]
    assert fabrication["branch"] == "D-8/rev-1B-multi-line"
    assert fabrication["bom_ready"] is False
    assert any("STOPPER" in item for item in fabrication["blockers"])


@pytest.mark.parametrize(
    "code",
    [
        "08-3B-0515T-0204",
        "08-3B-0515T-02",
    ],
)
def test_type08_20e4588_rejects_invalid_l1_l2(code):
    result = analyze_single(code, source_profile="ctci_20e4588")

    assert result.error
    assert not result.entries


def test_type08_other_sources_reject_legacy_l1_l2_suffix():
    result = analyze_single(
        "08-3B-0515G-0203",
        source_profile="ctci_22a_5123a",
    )

    assert result.error
    assert "未定義 L1/L2" in result.error
