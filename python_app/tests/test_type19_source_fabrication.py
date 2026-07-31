from core.calculator import analyze_single


def _member(result):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == "D21-MEMBER-M"
    )


def test_type19_does_not_treat_drawing_l_as_actual_cut_length():
    result = analyze_single(
        "19-2B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    member = _member(result)
    assert (member.length, member.unit_weight, member.total_weight) == (0, 0, 0)
    assert member.geometry.parameters["drawing_L_mm"] == 600
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type19_angle_uses_measured_cut_and_detail_z_parameters():
    result = analyze_single(
        "19-2B",
        source_profile="cw_e25_24_hp6",
        overrides={"member_cut_length_mm": 720},
    )

    assert not result.error
    member = _member(result)
    assert (member.name, member.spec, member.length) == ("角鋼", "50*50*6", 720)
    assert member.unit_weight == 3.19
    assert member.geometry.parameters["slope_ratio"] == "1:1"
    assert member.geometry.parameters["lower_end_pocket_drain_cut_mm"] == 20
    assert result.meta["fabrication"]["bom_ready"] is True


def test_type19_large_branch_is_half_h_t_section_not_full_h_beam():
    result = analyze_single(
        "19-8B",
        source_profile="cw_e25_24_hp6",
        overrides={"member_cut_length_mm": 1000},
    )

    assert not result.error
    member = _member(result)
    assert member.name == "T型鋼（H型鋼剖分）"
    assert member.geometry.shape_kind == "t_section_split_from_h_beam"
    assert member.geometry.parameters["parent_section"] == "H194X150X6X9"
    assert member.weight_per_unit == 15.3
    assert member.unit_weight == 15.3
    assert member.weight_per_unit != 30.6


def test_type19_large_branch_retains_split_geometry_blocker():
    result = analyze_single(
        "19-12B",
        source_profile="cw_e25_24_hp6",
        overrides={"member_cut_length_mm": 1100},
    )

    assert not result.error
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any(
        "kerf" in blocker
        for blocker in _member(result).geometry.fabrication_blockers
    )


def test_type19_rejects_non_drawing_designation_suffix():
    result = analyze_single(
        "19-2B-06",
        source_profile="cw_e25_24_hp6",
    )

    assert result.error
    assert "只有" in result.error
    assert not result.entries


def test_type19_ctci_profiles_remain_blocked_without_drawings():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single("19-2B", source_profile=profile)
        assert result.error
        assert "暫不計算" in result.error
        assert not result.entries
