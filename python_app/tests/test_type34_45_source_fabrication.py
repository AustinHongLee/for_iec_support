import pytest

from core.calculator import analyze_single


def _entry(result, component_id):
    return next(e for e in result.entries if e.geometry.component_id == component_id)


def test_type34_is_one_post_and_one_top_beam():
    result = analyze_single("34-L50-1010", source_profile="cw_e25_24_hp6")
    assert [e.length for e in result.entries] == [1000, 1000]
    assert [e.geometry.component_id for e in result.entries] == [
        "D39-END-POST", "D39-TOP-BEAM"
    ]


def test_type34_source_envelopes_are_separate():
    cw = analyze_single(
        "34-C150-2020", source_profile="cw_e25_24_hp6"
    )
    assert not cw.error
    assert cw.meta["issues"][0]["severity"] == "high"
    assert not analyze_single(
        "34-C150-2020", source_profile="ctci_22a_5123a"
    ).error
    assert "暫不計算" in analyze_single(
        "34-L50-1010", source_profile="ctci_20e4588"
    ).error


def test_type35_fig_b_is_one_member_not_two():
    result = analyze_single("35-C125-09B", source_profile="cw_e25_24_hp6")
    assert len(result.entries) == 1
    assert result.entries[0].quantity == 1
    assert result.entries[0].geometry.parameters["quantity"] == 1


def test_type35_source_limit_is_graded_but_missing_fig_is_hard_error():
    assert not analyze_single("35-C100-14A", source_profile="cw_e25_24_hp6").error
    overrun = analyze_single(
        "35-C100-14A", source_profile="ctci_20e4588"
    )
    assert not overrun.error
    assert overrun.meta["issues"][0]["severity"] == "high"
    assert "未提供 L50 FIG-B" in analyze_single(
        "35-L50-06B", source_profile="cw_e25_24_hp6"
    ).error


@pytest.mark.parametrize(("member", "plate_id", "holes"), [
    ("L50", "M34-LGP-C-1", 4),
    ("C125", "M34-LGP-C-6", 6),
])
def test_type36_k_bolts_follow_m34_hole_layout(member, plate_id, holes):
    result = analyze_single(f"36-{member}-05", source_profile="cw_e25_24_hp6")
    assert _entry(result, plate_id).geometry.holes.count == holes
    assert _entry(result, "D41-K-BOLT").quantity == holes


def test_type37_bom_geometry_keeps_end_cut_blocker():
    result = analyze_single("37-C125-1200A", source_profile="ctci_22a_5123a")
    assert [e.length for e in result.entries] == [1400, 1530]
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any("端切" in b for b in result.meta["fabrication"]["blockers"])


def test_type37_small_h_overrun_is_warning():
    result = analyze_single(
        "37-C125-1500A", source_profile="cw_e25_24_hp6"
    )
    assert not result.error
    assert result.meta["issues"][0]["severity"] == "warning"


def test_type39_uses_source_bolt_spec_and_all_lug_holes():
    cw = analyze_single("39-C125-500 A", source_profile="cw_e25_24_hp6")
    ctci = analyze_single("39-C125-500 A", source_profile="ctci_20e4588")
    assert _entry(cw, "D45-K-BOLT").spec == '3/4"x50'
    assert (_entry(ctci, "D45-K-BOLT").spec, _entry(ctci, "D45-K-BOLT").quantity) == (
        "M20X50", 12
    )


def test_type41_table_arrows_and_main_length_are_transcribed():
    result = analyze_single("41-7", source_profile="cw_e25_24_hp6")
    main = _entry(result, "D49-MEMBER-1")
    brace = _entry(result, "D49-MEMBER-2")
    assert (main.spec, main.length) == ("150*150*7", 1420)
    assert (brace.spec, brace.length) == ("75*75*9", 0)
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type41_accepts_explicit_brace_cut_length():
    result = analyze_single(
        "41-7", overrides={"brace_cut_length_mm": 1500},
        source_profile="cw_e25_24_hp6",
    )
    assert _entry(result, "D49-MEMBER-2").length == 1500
    assert result.meta["fabrication"]["bom_ready"] is True
    assert _entry(result, "M45-EXPANSION-BOLT").quantity == 4
    assert _entry(result, "M45-EXPANSION-BOLT").unit_weight > 0


def test_type42_keeps_trunnion_procurement_as_blocker():
    result = analyze_single("42-8B-C125-500 A", source_profile="cw_e25_24_hp6")
    assert _entry(result, "D50-TRUNNION").unit_weight == 0
    assert _entry(result, "D50-M-BOLT").unit_weight > 0
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("schedule" in b for b in result.meta["fabrication"]["blockers"])


def test_type43_20e_excludes_not_furnished_trunnion():
    result = analyze_single("43-8B-C125-500 A", source_profile="ctci_20e4588")
    assert all(e.name != "TRUNNION" for e in result.entries)
    assert result.meta["fabrication"]["not_furnished"] == ["TRUNNION PIPE"]
    assert (_entry(result, "D51-K-BOLT").spec, _entry(result, "D51-K-BOLT").quantity) == (
        "M20X50", 12
    )


def test_type43_cw_retains_trunnion_without_invented_weight():
    result = analyze_single("43-8B-C125-500 A", source_profile="cw_e25_24_hp6")
    assert _entry(result, "D51-TRUNNION").unit_weight == 0
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type44_expands_the_four_member_frame():
    result = analyze_single("44-8B-C100-800 A", source_profile="cw_e25_24_hp6")
    assert (_entry(result, "D53-LONGITUDINAL").length, _entry(result, "D53-LONGITUDINAL").quantity) == (916, 2)
    assert (_entry(result, "D53-TRANSVERSE").length, _entry(result, "D53-TRANSVERSE").quantity) == (232, 2)
    assert _entry(result, "D53-CLIP-PLATE").quantity == 2
    assert _entry(result, "D53-M-BOLT").quantity == 2


def test_type44_adds_brace_only_at_drawing_threshold():
    low = analyze_single("44-8B-C100-1199 A", source_profile="cw_e25_24_hp6")
    high = analyze_single("44-8B-C100-1200 A", source_profile="cw_e25_24_hp6")
    assert all(e.geometry.component_id != "D53-L50-BRACE" for e in low.entries)
    assert _entry(high, "D53-L50-BRACE").length == 1016


def test_type45_unbraced_frame_has_two_m34_plates_and_no_detail_y():
    result = analyze_single("45-8B-C100-800 A", source_profile="cw_e25_24_hp6")
    assert (_entry(result, "D54-LONGITUDINAL").length, _entry(result, "D54-LONGITUDINAL").quantity) == (746, 2)
    assert _entry(result, "M34-LGP-C-4").quantity == 2
    assert _entry(result, "D54-DETAIL-Z-K-BOLT").quantity == 8
    assert all(e.geometry.component_id != "D54-DETAIL-Y-K-BOLT" for e in result.entries)


def test_type45_braced_frame_adds_detail_y_lug_and_bolts():
    result = analyze_single("45-8B-C100-1200 A", source_profile="cw_e25_24_hp6")
    assert _entry(result, "D54-L50-BRACE").length == 1008
    assert _entry(result, "M36-LGP-E-4").quantity == 1
    assert _entry(result, "D54-DETAIL-Y-K-BOLT").quantity == 4
    assert _entry(result, "D54-DETAIL-Y-K-BOLT").spec == '5/8"x40'


@pytest.mark.parametrize("type_id", ["36", "41", "42", "44", "45"])
def test_types_without_ctci_drawings_are_source_gated(type_id):
    sample = {
        "36": "36-L50-05", "41": "41-1", "42": "42-8B-C125-500 A",
        "44": "44-8B-C100-800 A", "45": "45-8B-C100-800 A",
    }[type_id]
    assert "暫不計算" in analyze_single(
        sample, source_profile="ctci_22a_5123a"
    ).error
