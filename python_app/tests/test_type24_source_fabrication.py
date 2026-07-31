from core.calculator import analyze_single


def _member(result):
    assert len(result.entries) == 1
    return result.entries[0]


def test_type24_cw_member_rows_and_limits():
    l50 = analyze_single("24-L50-10", source_profile="cw_e25_24_hp6")
    l75 = analyze_single("24-L75-15", source_profile="cw_e25_24_hp6")
    assert not l50.error and (_member(l50).spec, _member(l50).length) == ("50*50*6", 1000)
    assert not l75.error and (_member(l75).spec, _member(l75).length) == ("75*75*9", 1500)


def test_type24_small_h_overrun_is_warning():
    result = analyze_single("24-L50-11", source_profile="cw_e25_24_hp6")
    assert not result.error
    assert result.entries
    assert result.meta["issues"][0]["severity"] == "warning"


def test_type24_ctci_profiles_remain_blocked_without_d26():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single("24-L50-05", source_profile=profile)
        assert result.error
        assert not result.entries


def test_type24_records_selected_mounting_orientation():
    result = analyze_single(
        "24-L50-05",
        source_profile="cw_e25_24_hp6",
        overrides={"mounting_orientation": "wall_cantilever"},
    )
    assert not result.error
    assert _member(result).geometry.parameters["mounting_orientation"] == "wall_cantilever"
    assert all("安裝方向" not in item for item in result.meta["fabrication"]["blockers"])


def test_type24_rejects_orientation_not_shown_on_d26():
    result = analyze_single(
        "24-L50-05",
        source_profile="cw_e25_24_hp6",
        overrides={"mounting_orientation": "floor"},
    )
    assert result.error
    assert "mounting_orientation" in result.error


def test_type24_bom_ready_but_d68_holes_block_fabrication():
    result = analyze_single("24-L50-05", source_profile="cw_e25_24_hp6")
    member = _member(result)
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert member.geometry.parameters["supported_line_center_from_free_end_mm"] == 100
    assert member.geometry.parameters["field_fillet_weld_mm"] == 6
    assert any("D-68" in item for item in member.geometry.fabrication_blockers)
