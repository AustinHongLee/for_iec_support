from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type22_cw_parenthesized_format_and_m42_l():
    result = analyze_single("22-L50-05(A)L", source_profile="cw_e25_24_hp6")

    assert not result.error
    assert _component(result, "D24-MEMBER-M-VERTICAL").length == 500
    assert _component(result, "D24-MEMBER-M-HORIZONTAL").length == 300
    assert _component(result, "M42-PLATE-C").length == 180
    assert _component(result, "M42-FASTENER").spec == '5/8"'


def test_type22_ctci_segmented_format_and_machine_bolt():
    result = analyze_single("22-L50-05A-L", source_profile="ctci_20e4588")

    assert not result.error
    assert _component(result, "M42-FASTENER").name == "MACH.BOLT W/ HEX NUT"
    assert _component(result, "M42-FASTENER").spec == "M16 X 40"


def test_type22_source_designation_styles_do_not_cross_parse():
    cw_with_ctci = analyze_single("22-L50-05A-L", source_profile="cw_e25_24_hp6")
    ctci_with_cw = analyze_single("22-L50-05(A)L", source_profile="ctci_22a_5123a")

    assert cw_with_ctci.error
    assert "中威第三段" in cw_with_ctci.error
    assert ctci_with_cw.error
    assert "中鼎格式" in ctci_with_cw.error


def test_type22_host_m42_subset_is_high_risk_only_when_source_m42_exists():
    cw_t = analyze_single("22-L50-05(A)T", source_profile="cw_e25_24_hp6")
    source_22a_p = analyze_single("22-L50-05A-P", source_profile="ctci_22a_5123a")
    source_20e_p = analyze_single("22-L50-05A-P", source_profile="ctci_20e4588")

    assert not cw_t.error
    assert cw_t.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"
    assert cw_t.meta["issues"][0]["severity"] == "high"
    assert "不存在於此來源 M-42 圖" in source_22a_p.error
    assert not source_20e_p.error


def test_type22_ctci_fig_c_enforces_l_max():
    boundary = analyze_single("22-L75-05C-L-08", source_profile="ctci_22a_5123a")
    too_long = analyze_single("22-L75-05C-L-09", source_profile="ctci_22a_5123a")

    assert not boundary.error
    assert _component(boundary, "D24-MEMBER-M-HORIZONTAL").length == 800
    assert not too_long.error
    assert too_long.meta["issues"][0]["severity"] == "high"
    assert too_long.meta["fabrication"]["bom_ready"] is False


def test_type22_cw_includes_c100_but_marks_missing_exact_m43_row():
    result = analyze_single("22-C100-20(B)L", source_profile="cw_e25_24_hp6")

    assert not result.error
    assert _component(result, "D24-MEMBER-M-VERTICAL").spec == "100*50*5"
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("C100未在既有M-43" in item for item in result.meta["fabrication"]["blockers"])


def test_type22_h_limit_is_graded_and_fabrication_blockers_remain():
    too_high = analyze_single("22-L50-12(A)L", source_profile="cw_e25_24_hp6")
    valid = analyze_single("22-L75-10B-T", source_profile="ctci_22a_5123a")

    assert not too_high.error
    assert too_high.meta["issues"][0]["severity"] == "high"
    assert too_high.meta["fabrication"]["bom_ready"] is False
    assert not valid.error
    assert valid.meta["fabrication"]["fabrication_ready"] is False
    assert any("D-68" in item for item in valid.meta["fabrication"]["blockers"])
