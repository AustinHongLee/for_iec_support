from core.calculator import analyze_single


def _component(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type30_source_tables_differ():
    cw = analyze_single("30-L50-0508A", source_profile="cw_e25_24_hp6")
    assert not cw.error
    assert cw.meta["issues"][0]["severity"] == "high"
    assert not analyze_single("30-L50-0508A", source_profile="ctci_22a_5123a").error
    assert "未表列 MEMBER C100" in analyze_single("30-C100-1012A", source_profile="ctci_22a_5123a").error
    assert not analyze_single("30-C100-1012A", source_profile="ctci_20e4588").error


def test_type30_both_figures_use_h_minus_15_post_cut():
    for fig in ("A", "B"):
        result = analyze_single(f"30-L50-0306{fig}", source_profile="cw_e25_24_hp6")
        assert _component(result, "D35-MEMBER-H").length == 585
        assert _component(result, "D35-MEMBER-L").length == 300


def test_type30_l1_l2_default_and_override():
    default = analyze_single("30-L50-0306A", source_profile="cw_e25_24_hp6")
    assert (default.meta["fabrication"]["L1_mm"], default.meta["fabrication"]["L2_mm"]) == (150, 150)
    modified = analyze_single("30-L50-0306A-0201", source_profile="cw_e25_24_hp6")
    assert (modified.meta["fabrication"]["L1_mm"], modified.meta["fabrication"]["L2_mm"]) == (200, 100)
    mismatch = analyze_single(
        "30-L50-0306A-0101", source_profile="cw_e25_24_hp6"
    )
    assert not mismatch.error
    assert mismatch.meta["issues"][0]["code"] == "DESIGNATION_L1_L2_MISMATCH"
    assert mismatch.meta["fabrication"]["bom_ready"] is False


def test_type30_carries_shop_drawing_interface_blockers():
    result = analyze_single("30-L75-0710B", source_profile="cw_e25_24_hp6")
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any("existing steel" in item for item in result.meta["fabrication"]["blockers"])
