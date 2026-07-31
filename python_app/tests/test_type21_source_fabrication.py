from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type21_cw_retains_l65_and_its_h_limit():
    result = analyze_single(
        "21-L65-15A",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    vertical = _component(result, "D23-MEMBER-M-VERTICAL")
    horizontal = _component(result, "D23-MEMBER-M-HORIZONTAL")
    assert (vertical.spec, vertical.length) == ("65*65*6", 1500)
    assert horizontal.length == 300


def test_type21_ctci_rejects_cw_only_l65():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single(
            "21-L65-10A",
            source_profile=profile,
        )

        assert result.error
        assert "未表列 MEMBER L65" in result.error
        assert not result.entries


def test_type21_source_specific_h_limit_is_high_risk():
    cw = analyze_single(
        "21-L75-20B",
        source_profile="cw_e25_24_hp6",
    )
    ctci = analyze_single(
        "21-L75-20B",
        source_profile="ctci_22a_5123a",
    )

    assert not cw.error
    assert not ctci.error
    assert ctci.meta["issues"][0]["severity"] == "high"
    assert ctci.meta["fabrication"]["bom_ready"] is False


def test_type21_ctci_fig_c_enforces_member_l_max():
    l50_too_long = analyze_single(
        "21-L50-05C-06",
        source_profile="ctci_22a_5123a",
    )
    l75_boundary = analyze_single(
        "21-L75-05C-08",
        source_profile="ctci_20e4588",
    )
    l75_too_long = analyze_single(
        "21-L75-05C-09",
        source_profile="ctci_20e4588",
    )

    assert not l50_too_long.error
    assert l50_too_long.meta["issues"][0]["severity"] == "high"
    assert not l75_boundary.error
    assert _component(l75_boundary, "D23-MEMBER-M-HORIZONTAL").length == 800
    assert not l75_too_long.error
    assert l75_too_long.meta["issues"][0]["severity"] == "high"


def test_type21_designation_rejects_extra_or_missing_l_segment():
    a_with_l = analyze_single(
        "21-L50-05A-07",
        source_profile="cw_e25_24_hp6",
    )
    c_without_l = analyze_single(
        "21-L50-05C",
        source_profile="cw_e25_24_hp6",
    )

    assert a_with_l.error
    assert "Fig.A/B 不得有第四段" in a_with_l.error
    assert c_without_l.error
    assert "Fig.C 需且只能有第四段" in c_without_l.error


def test_type21_designated_h_is_used_as_field_cut_and_bom_is_ready():
    result = analyze_single(
        "21-L50-05B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    vertical = _component(result, "D23-MEMBER-M-VERTICAL")
    horizontal = _component(result, "D23-MEMBER-M-HORIZONTAL")
    assert (vertical.length, horizontal.length) == (500, 500)
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert all(entry.material_canonical_id for entry in result.entries)


def test_type21_retains_shop_drawing_blockers_and_source_trace():
    result = analyze_single(
        "21-L75-10C-07",
        source_profile="ctci_20e4588",
    )

    assert not result.error
    horizontal = _component(result, "D23-MEMBER-M-HORIZONTAL")
    assert horizontal.geometry.source_drawing.endswith(
        "中鼎/長春_Type/TYPE-21_D-23.pdf"
    )
    assert horizontal.geometry.parameters[
        "supported_line_center_from_free_end_mm"
    ] == 100
    assert horizontal.geometry.parameters["base_field_fillet_weld_mm"] == 6
    assert horizontal.geometry.parameters["u_bolt_furnished"] is False
    assert any(
        "D-68 U-bolt孔徑與孔距" in blocker
        for blocker in horizontal.geometry.fabrication_blockers
    )
