from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type15_cw_member_and_pipe_cut_lengths_follow_d16_stack():
    result = analyze_single(
        "15-2B-1005",
        source_profile="cw_e25_24_hp6",
        overrides={"wing_plate_P_mm": 95},
    )

    assert not result.error
    pipe = _component(result, "D16-SUPPORTING-PIPE-A")
    assert pipe.length == 382
    assert pipe.geometry.parameters["cut_formula"] == "H - 2F - MEMBER_N_DEPTH"

    member = _component(result, "D16-MEMBER-N")
    assert member.name == "槽鐵"
    assert member.spec == "100*50*5"
    assert member.display_spec == "C100X50X5; CUT L=988; QTY 1"
    assert member.length == 988
    assert member.geometry.parameters["cut_formula"] == "L - 2*STOPPER_T"


def test_type15_ctci_uses_h_beam_and_reinforcement_plate():
    result = analyze_single(
        "15-4B-1030",
        source_profile="ctci_22a_5123a",
        overrides={"wing_plate_P_mm": 120},
    )

    assert not result.error
    member = _component(result, "D16-MEMBER-N")
    assert (member.name, member.spec, member.quantity) == (
        "H型鋼",
        "100*100*6",
        1,
    )
    assert member.display_spec == "H100X100X6X8; CUT L=988; QTY 1"
    reinforcement = _component(result, "D16-REINFORCEMENT-PLATE")
    assert (
        reinforcement.length,
        reinforcement.width,
        reinforcement.spec,
    ) == (84, 47, "6")

    pipe = _component(result, "D16-SUPPORTING-PIPE-A")
    assert pipe.length == 2870
    assert pipe.geometry.parameters["cut_formula"].endswith("- REINF_T")


def test_type15_22a_and_20e_keep_the_12in_f_difference():
    override = {"wing_plate_P_mm": 190}
    source_22a = analyze_single(
        "15-12B-1040",
        source_profile="ctci_22a_5123a",
        overrides=override,
    )
    source_20e = analyze_single(
        "15-12B-1040",
        source_profile="ctci_20e4588",
        overrides=override,
    )

    assert not source_22a.error
    assert not source_20e.error
    assert _component(source_22a, "D16-BASE-PLATE").spec == "16"
    assert _component(source_20e, "D16-BASE-PLATE").spec == "19"
    assert _component(source_22a, "D16-SUPPORTING-PIPE-A").length == 3759
    assert _component(source_20e, "D16-SUPPORTING-PIPE-A").length == 3753


def test_type15_source_size_boundaries_are_not_mixed():
    cw_two = analyze_single(
        "15-2B-1005",
        source_profile="cw_e25_24_hp6",
    )
    ctci_two = analyze_single(
        "15-2B-1005",
        source_profile="ctci_22a_5123a",
    )

    assert not cw_two.error
    assert ctci_two.error
    assert '未表列 2"' in ctci_two.error
    assert not ctci_two.entries


def test_type15_grades_each_source_l_h_overrun():
    cw_too_high = analyze_single(
        "15-2B-1010",
        source_profile="cw_e25_24_hp6",
    )
    ctci_too_long = analyze_single(
        "15-4B-1530",
        source_profile="ctci_22a_5123a",
    )
    ctci_too_high = analyze_single(
        "15-4B-1040",
        source_profile="ctci_20e4588",
    )

    for result in (cw_too_high, ctci_too_long, ctci_too_high):
        assert not result.error
        assert result.meta["issues"][0]["severity"] == "high"
        assert result.meta["fabrication"]["bom_ready"] is False

    excessive = analyze_single("15-2B-1099", source_profile="cw_e25_24_hp6")
    assert excessive.error
    assert "有限外插護欄" in excessive.error


def test_type15_wing_polygon_is_exact_but_p_remains_field_cut():
    estimated = analyze_single(
        "15-2B-1005",
        source_profile="cw_e25_24_hp6",
    )
    explicit = analyze_single(
        "15-2B-1005",
        source_profile="cw_e25_24_hp6",
        overrides={"wing_plate_P_mm": 95},
    )

    wing = _component(estimated, "D16-WING-PLATE")
    assert wing.geometry.net_area_mm2 == 9512.5
    assert wing.geometry.parameters["polygon_points_mm"] == [
        [0, 150.0],
        [20.0, 150.0],
        [95.0, 25.0],
        [95.0, 0],
        [10.0, 0],
        [0, 10.0],
    ]
    assert wing.geometry.fabrication_ready is False
    assert estimated.meta["fabrication"]["bom_ready"] is False

    assert _component(
        explicit, "D16-WING-PLATE"
    ).geometry.fabrication_ready is True
    assert explicit.meta["fabrication"]["bom_ready"] is True


def test_type15_stopper_uses_four_chamfer_net_area_and_qty_two():
    result = analyze_single(
        "15-4B-1030",
        source_profile="ctci_22a_5123a",
        overrides={"wing_plate_P_mm": 120},
    )

    stopper = _component(result, "D16-STOPPER-PLATE")
    assert stopper.quantity == 2
    assert stopper.geometry.net_area_mm2 == 23800
    assert len(stopper.geometry.parameters["polygon_points_mm"]) == 8


def test_type15_double_channel_keeps_assembly_spacing_blocker():
    result = analyze_single(
        "15-10B-1050",
        source_profile="cw_e25_24_hp6",
        overrides={"wing_plate_P_mm": 180},
    )

    assert not result.error
    member = _component(result, "D16-MEMBER-N")
    assert member.quantity == 2
    assert member.geometry.shape_kind == "back_to_back_double_channel"
    assert any(
        "spacing between double channels" in item
        for item in result.meta["fabrication"]["blockers"]
    )
