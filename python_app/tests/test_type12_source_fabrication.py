from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type12_cw_uses_double_plate_p_and_one_cover_plate():
    result = analyze_single(
        "12-6B-05B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    support_pipe = _component(result, "D12-SUPPORTING-PIPE-B")
    assert support_pipe.length == 0
    assert support_pipe.geometry.fabrication_ready is False

    plate_p = _component(result, "D12-PLATE-P")
    assert (plate_p.length, plate_p.width, plate_p.spec) == (150, 75, "9")
    assert plate_p.quantity == 2
    assert plate_p.geometry.parameters["pipe_center_spacing_C_mm"] == 140

    cover = _component(result, "D12-COVER-PLATE")
    assert (cover.length, cover.width, cover.spec, cover.quantity) == (
        75,
        75,
        "6",
        1,
    )


def test_type12_removes_unfounded_h_minus_100_pipe_formula():
    result = analyze_single(
        "12-2B-05G",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    support_pipe = _component(result, "D12-SUPPORTING-PIPE-B")
    assert support_pipe.length == 0
    assert "FIELD CUT TO SUIT" in support_pipe.geometry.shape_spec
    assert result.meta["fabrication"]["dimensions"][
        "supporting_pipe_cut_length_mm"
    ] is None
    assert result.meta["fabrication"]["bom_ready"] is False


def test_type12_explicit_field_cut_and_material_grade_complete_bom_inputs():
    result = analyze_single(
        "12-8B-12E(A)",
        source_profile="cw_e25_24_hp6",
        overrides={
            "support_pipe_cut_length_mm": 1080,
            "plate_material": "A387-22",
        },
    )

    assert not result.error
    support_pipe = _component(result, "D12-SUPPORTING-PIPE-B")
    assert support_pipe.length == 1080
    assert support_pipe.geometry.parameters["weep_hole_diameter_mm"] == 6
    assert support_pipe.geometry.parameters["weep_hole_center_offset_mm"] is None

    plate_p = _component(result, "D12-PLATE-P")
    assert plate_p.material == "A387-22"
    assert plate_p.geometry.parameters["plate_material_class"] == "ALLOY STEEL"
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False


def test_type12_suffix_keeps_source_material_class_without_inventing_grade():
    carbon = analyze_single(
        "12-4B-05B",
        source_profile="cw_e25_24_hp6",
    )
    alloy = analyze_single(
        "12-4B-05B(A)",
        source_profile="cw_e25_24_hp6",
    )
    stainless = analyze_single(
        "12-4B-05B(S)",
        source_profile="cw_e25_24_hp6",
    )

    assert _component(carbon, "D12-PLATE-P").material == "CARBON STEEL"
    assert _component(alloy, "D12-PLATE-P").material == "ALLOY STEEL"
    assert _component(stainless, "D12-PLATE-P").material == "STAINLESS STEEL"
    assert all(
        result.meta["fabrication"]["bom_ready"] is False
        for result in (carbon, alloy, stainless)
    )


def test_type12_large_size_retains_detail_a_parameters():
    result = analyze_single(
        "12-10B-15B",
        source_profile="cw_e25_24_hp6",
        overrides={
            "support_pipe_cut_length_mm": 1300,
            "plate_material": "A36/SS400",
        },
    )

    assert not result.error
    plate_p = _component(result, "D12-PLATE-P")
    assert (plate_p.length, plate_p.width, plate_p.spec) == (250, 105, "12")
    assert plate_p.geometry.parameters["detail_A_applies"] is True
    assert plate_p.geometry.parameters["pipe_center_spacing_C_mm"] == 240


def test_type12_grades_h_overrun_and_enforces_material_suffix_grammar():
    too_high = analyze_single(
        "12-6B-16B",
        source_profile="cw_e25_24_hp6",
    )
    assert not too_high.error
    assert too_high.meta["issues"][0]["severity"] == "warning"

    invalid_suffix = analyze_single(
        "12-6B-05B(X)",
        source_profile="cw_e25_24_hp6",
    )
    assert invalid_suffix.error
    assert "(A)/(S)" in invalid_suffix.error


def test_type12_ctci_sources_remain_blocked_without_d12_drawings():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single(
            "12-6B-05B",
            source_profile=profile,
        )
        assert result.error
        assert "暫不計算" in result.error
        assert not result.entries
