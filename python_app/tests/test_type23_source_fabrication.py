from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type23_cw_keeps_all_eight_d25_members():
    cases = {
        "L50": "50*50*6", "L65": "65*65*6", "L75": "75*75*9",
        "L100": "100*100*10", "C100": "100*50*5", "C150": "150*75*9",
        "H100": "100*100*6", "H150": "150*150*7",
    }
    for member, spec in cases.items():
        result = analyze_single(f"23-{member}-05A", source_profile="cw_e25_24_hp6")
        assert not result.error
        assert _component(result, "D25-MEMBER-M-VERTICAL").spec == spec


def test_type23_ctci_only_allows_l50_and_l75():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        assert not analyze_single("23-L75-20B", source_profile=profile).error
        rejected = analyze_single("23-C100-10A", source_profile=profile)
        assert "未表列 MEMBER C100" in rejected.error


def test_type23_source_h_limits_are_not_mixed():
    cw = analyze_single("23-L50-10A", source_profile="cw_e25_24_hp6")
    ctci = analyze_single("23-L50-10A", source_profile="ctci_22a_5123a")
    assert not cw.error
    assert cw.meta["issues"][0]["severity"] == "high"
    assert cw.meta["fabrication"]["bom_ready"] is False
    assert not ctci.error


def test_type23_ctci_fig_c_enforces_l_max():
    valid = analyze_single("23-L75-10C-08", source_profile="ctci_20e4588")
    invalid = analyze_single("23-L75-10C-09", source_profile="ctci_20e4588")
    assert not valid.error
    assert _component(valid, "D25-MEMBER-M-HORIZONTAL").length == 800
    assert not invalid.error
    assert invalid.meta["issues"][0]["severity"] == "high"


def test_type23_excessive_h_still_hard_stops():
    result = analyze_single("23-L50-11A", source_profile="cw_e25_24_hp6")
    assert result.error
    assert "有限外插護欄" in result.error


def test_type23_designation_rejects_wrong_extra_segment():
    assert analyze_single("23-L75-10A-07", source_profile="cw_e25_24_hp6").error
    assert analyze_single("23-L75-10C", source_profile="cw_e25_24_hp6").error


def test_type23_records_weld_and_no_ubolt_claim():
    result = analyze_single("23-L75-10B", source_profile="cw_e25_24_hp6")
    vertical = _component(result, "D25-MEMBER-M-VERTICAL")
    assert vertical.geometry.parameters["top_field_fillet_weld_mm"] == 6
    assert vertical.geometry.parameters["top_weld_all_around"] is True
    assert vertical.geometry.parameters["u_bolt_shown"] is False
    assert all("D-68" not in blocker for blocker in vertical.geometry.fabrication_blockers)


def test_type23_bom_ready_but_joint_and_restraint_block_fabrication():
    result = analyze_single("23-L50-05A", source_profile="ctci_22a_5123a")
    assert not result.error
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any("止滑/固定方式" in item for item in result.meta["fabrication"]["blockers"])
