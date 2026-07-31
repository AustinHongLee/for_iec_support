from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type14_pipe_formula_and_channel_branches_are_structured():
    small = analyze_single(
        "14-2B-1005",
        source_profile="cw_e25_24_hp6",
    )
    large = analyze_single(
        "14-10B-1005",
        source_profile="cw_e25_24_hp6",
    )

    assert not small.error
    pipe = _component(small, "D14-SUPPORTING-PIPE-A")
    assert pipe.length == 382
    assert pipe.geometry.parameters["cut_formula"] == "H - 2F - MEMBER_N_DEPTH"

    small_member = _component(small, "D14-MEMBER-N")
    assert small_member.quantity == 1
    assert small_member.length == 988
    assert small_member.geometry.parameters["cut_formula"] == "L - 2*STOPPER_T"
    large_member = _component(large, "D14-MEMBER-N")
    assert large_member.quantity == 2
    assert large_member.geometry.parameters["detail_a"] is True


def test_type14_stopper_uses_four_chamfer_net_area():
    result = analyze_single(
        "14-2B-1005",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    stopper = _component(result, "D14-STOPPER-PLATE")
    assert stopper.quantity == 2
    assert stopper.geometry.net_area_mm2 == 11000
    assert stopper.geometry.parameters["chamfer_count"] == 4
    assert stopper.geometry.parameters["chamfer_mm"] == 10
    assert stopper.unit_weight == 0.52


def test_type14_wing_p_requires_explicit_field_value_for_bom_ready():
    estimated = analyze_single(
        "14-2B-1005",
        source_profile="cw_e25_24_hp6",
    )
    explicit = analyze_single(
        "14-2B-1005",
        source_profile="cw_e25_24_hp6",
        overrides={"wing_plate_P_mm": 60},
    )

    assert not estimated.error
    wing = _component(estimated, "D14-WING-PLATE")
    assert wing.geometry.fabrication_ready is False
    assert wing.geometry.parameters["P_explicit"] is False
    assert wing.geometry.net_area_mm2 == 6887.5
    assert len(wing.geometry.parameters["polygon_points_mm"]) == 6
    assert estimated.meta["fabrication"]["bom_ready"] is False

    assert not explicit.error
    explicit_wing = _component(explicit, "D14-WING-PLATE")
    assert explicit_wing.width == 60
    assert explicit_wing.geometry.parameters["P_explicit"] is True
    assert explicit_wing.geometry.fabrication_ready is True
    assert explicit.meta["fabrication"]["bom_ready"] is True


def test_type14_base_top_and_anchor_parameters_are_source_backed():
    result = analyze_single(
        "14-6B-1035",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    base = _component(result, "D14-BASE-PLATE")
    assert base.geometry.parameters["hole_diameter_E_mm"] == 22
    assert base.geometry.parameters["hole_pitch_D_mm"] == 300

    top = _component(result, "D14-TOP-PLATE")
    assert (top.length, top.width, top.spec) == (190, 190, "16")

    anchor = _component(result, "D14-ANCHOR-BOLT-J")
    assert (anchor.spec, anchor.quantity, anchor.unit_weight) == ('3/4"', 4, 0)


def test_type14_grades_d15_l_h_envelope():
    too_high = analyze_single(
        "14-2B-1010",
        source_profile="cw_e25_24_hp6",
    )
    assert not too_high.error
    assert too_high.meta["issues"][0]["severity"] == "high"

    too_long = analyze_single(
        "14-2B-1505",
        source_profile="cw_e25_24_hp6",
    )
    assert not too_long.error
    assert too_long.meta["issues"][0]["severity"] == "high"


def test_type14_ctci_sources_remain_blocked_without_d14_drawings():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single(
            "14-2B-1005",
            source_profile=profile,
        )
        assert result.error
        assert "暫不計算" in result.error
        assert not result.entries
