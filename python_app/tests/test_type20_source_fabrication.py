from core.calculator import analyze_single


def _member(result):
    assert len(result.entries) == 1
    entry = result.entries[0]
    assert entry.geometry.component_id == "D22-MEMBER-M"
    return entry


def test_type20_cw_uses_its_four_member_table_and_h_limits():
    l65 = analyze_single(
        "20-L65-15A",
        source_profile="cw_e25_24_hp6",
    )
    c100 = analyze_single(
        "20-C100-30B",
        source_profile="cw_e25_24_hp6",
    )

    assert not l65.error
    assert (_member(l65).spec, _member(l65).length) == ("65*65*6", 1500)
    assert not c100.error
    assert (_member(c100).spec, _member(c100).length) == ("100*50*5", 3000)


def test_type20_ctci_uses_c125_and_rejects_cw_only_l65():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        c125 = analyze_single(
            "20-C125-20B",
            source_profile=profile,
        )
        l65 = analyze_single(
            "20-L65-10A",
            source_profile=profile,
        )

        assert not c125.error
        assert _member(c125).geometry.parameters["full_section"] == "C125X65X6X8"
        assert _member(c125).length == 2000
        assert l65.error
        assert "未表列 MEMBER L65" in l65.error


def test_type20_same_l50_height_has_different_source_risk():
    cw = analyze_single(
        "20-L50-12A",
        source_profile="cw_e25_24_hp6",
    )
    ctci = analyze_single(
        "20-L50-12A",
        source_profile="ctci_22a_5123a",
    )

    assert not cw.error
    assert not ctci.error
    assert ctci.meta["issues"][0]["severity"] == "high"
    assert ctci.meta["fabrication"]["bom_ready"] is False


def test_type20_slot_dimensions_require_explicit_non_designation_inputs():
    result = analyze_single(
        "20-L75-15B",
        source_profile="ctci_22a_5123a",
        overrides={
            "supported_line_size_in": 6,
            "u_bolt_rod_diameter_mm": 16,
        },
    )

    assert not result.error
    member = _member(result)
    params = member.geometry.parameters
    assert params["figure"] == "B"
    assert params["slot_count"] == 2
    assert params["slot_length_mm"] == 60
    assert params["slot_width_mm"] == 19
    assert params["slot_center_spacing_Z_mm"] == 184
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False


def test_type20_missing_slot_inputs_keeps_bom_but_reports_blockers():
    result = analyze_single(
        "20-L50-05A",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    member = _member(result)
    assert member.length == 500
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any("supported line size" in item for item in member.geometry.fabrication_blockers)
    assert any("rod diameter" in item for item in member.geometry.fabrication_blockers)
    assert result.warnings


def test_type20_rejects_unsupported_z_line_size_and_invalid_figure():
    unsupported_size = analyze_single(
        "20-L50-05A",
        source_profile="cw_e25_24_hp6",
        overrides={"supported_line_size_in": 5},
    )
    bad_figure = analyze_single(
        "20-L50-05C",
        source_profile="cw_e25_24_hp6",
    )

    assert unsupported_size.error
    assert "不在 Z table" in unsupported_size.error
    assert bad_figure.error
    assert "Fig A/B" in bad_figure.error


def test_type20_records_source_and_not_furnished_interfaces():
    result = analyze_single(
        "20-L50-05A",
        source_profile="ctci_20e4588",
    )

    assert not result.error
    member = _member(result)
    assert member.geometry.source_drawing.endswith(
        "中鼎/長春_Type/TYPE-20_D-22.pdf"
    )
    assert result.meta["source_profile"] == "ctci_20e4588"
    assert "STANDARD U-BOLT" in result.meta["fabrication"]["not_furnished"]
