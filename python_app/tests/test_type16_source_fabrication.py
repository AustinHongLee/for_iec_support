from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type16_designation_builds_nominal_h_plus_c_pipe_length():
    result = analyze_single("16-2B-05", source_profile="cw_e25_24_hp6")

    assert not result.error
    pipe = _component(result, "D18-PIPE-B")
    assert pipe.length == 800
    assert pipe.total_weight > 0
    assert result.meta["fabrication"]["dimensions"]["C_overhang_mm"] == 300
    assert result.meta["fabrication"]["dimensions"]["nominal_cut_length_mm"] == 800
    assert result.meta["fabrication"]["dimensions"]["field_cut_override_mm"] is None
    assert result.meta.get("excluded_bom_components", []) == []
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("H+C=500+300=800mm" in warning for warning in result.warnings)


def test_type16_real_project_4b_03_is_600mm_not_zero():
    result = analyze_single("16-4B-03", source_profile="cw_e25_24_hp6")

    assert not result.error
    pipe = _component(result, "D18-PIPE-B")
    assert (pipe.spec, pipe.length) == ('3"*SCH.40', 600)
    assert pipe.unit_weight > 0
    assert result.total_weight > pipe.total_weight


def test_type16_ctci_fourth_segment_modifies_c_but_cw_rejects_it():
    ctci = analyze_single(
        "16-2B-04-03",
        source_profile="ctci_22a_5123a",
        overrides={
            "special_main_line": False,
            "connection_layout": "straight_side",
        },
    )
    cw = analyze_single(
        "16-2B-04-03",
        source_profile="cw_e25_24_hp6",
    )

    assert not ctci.error
    assert ctci.meta["fabrication"]["dimensions"]["H_mm"] == 400
    assert ctci.meta["fabrication"]["dimensions"]["C_overhang_mm"] == 300
    assert _component(ctci, "D18-PIPE-B").length == 700
    assert cw.error
    assert "不含 C 修改段" in cw.error


def test_type16_ctci_default_c_is_200():
    result = analyze_single(
        "16-2B-04",
        source_profile="ctci_20e4588",
        overrides={
            "special_main_line": False,
            "connection_layout": "straight_side",
        },
    )

    assert not result.error
    assert result.meta["fabrication"]["dimensions"]["C_overhang_mm"] == 200
    assert _component(result, "D18-PIPE-B").length == 600


def test_type16_special_main_line_splits_pipe_and_preserves_main_material():
    result = analyze_single(
        "16-2B-04",
        source_profile="ctci_20e4588",
        overrides={
            "dummy_pipe_cut_length_mm": 900,
            "special_main_line": True,
            "special_main_line_piece_cut_length_mm": 250,
            "main_line_material": "SUS304",
            "connection_layout": "elbow_bottom",
        },
    )

    assert not result.error
    special = _component(result, "D18-PIPE-B-SPECIAL-MAIN-LINE-SEGMENT")
    outboard = _component(result, "D18-PIPE-B-OUTBOARD-SEGMENT")
    assert (special.length, special.material) == (250, "SUS304")
    assert outboard.length == 650
    assert special.geometry.parameters["fabricated_with_main_line_in_shop"] is True


def test_type16_special_mode_requires_source_inputs():
    missing_cut = analyze_single(
        "16-2B-04",
        source_profile="ctci_22a_5123a",
        overrides={
            "dummy_pipe_cut_length_mm": 900,
            "special_main_line": True,
            "main_line_material": "SUS304",
        },
    )
    missing_material = analyze_single(
        "16-2B-04",
        source_profile="ctci_22a_5123a",
        overrides={
            "dummy_pipe_cut_length_mm": 900,
            "special_main_line": True,
            "special_main_line_piece_cut_length_mm": 250,
        },
    )

    assert "special_main_line_piece_cut_length_mm" in missing_cut.error
    assert "main_line_material" in missing_material.error


def test_type16_cover_plate_and_not_furnished_interface_are_structured():
    result = analyze_single(
        "16-24B-05",
        source_profile="cw_e25_24_hp6",
        overrides={
            "dummy_pipe_cut_length_mm": 1200,
            "special_main_line": False,
            "connection_layout": "straight_side",
        },
    )

    assert not result.error
    cover = _component(result, "D18-COVER-PLATE")
    assert (cover.length, cover.width, cover.spec) == (430, 430, "6")
    assert cover.geometry.parameters["dimension_symbol"] == "C"
    assert result.meta["fabrication"]["not_furnished"] == ["D-80 interface"]


def test_type16_bom_can_be_ready_while_attachment_cope_blocks_fabrication():
    result = analyze_single(
        "16-6B-05",
        source_profile="ctci_22a_5123a",
        overrides={
            "dummy_pipe_cut_length_mm": 1000,
            "special_main_line": False,
            "connection_layout": "straight_side",
        },
    )

    assert not result.error
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False
    assert any(
        "cope/fishmouth" in blocker
        for blocker in result.meta["fabrication"]["blockers"]
    )
