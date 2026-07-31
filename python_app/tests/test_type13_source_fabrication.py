from data.m47_table import build_m47_item

from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_m47_uses_source_1_5t_and_asb_designation():
    item = build_m47_item(6)

    assert item is not None
    assert item["designation"] == "ASB-6B"
    assert item["thickness_mm"] == 1.5
    assert item["thickness_inferred"] is False
    assert item["material"] == "GARLOCK BLUE-GARD STYLE 3000 OR EQ."


def test_type13_uses_drawing_backed_m4_and_m47_components():
    result = analyze_single(
        "13-6B-05B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    clamp = _component(result, "M-4")
    assert clamp.spec == "PCL-A-6B"
    assert clamp.geometry.parameters["load_750f_kg"] == 655
    assert clamp.geometry.parameters["rod_size_a"] == '3/4"'

    gasket = _component(result, "M-47")
    assert gasket.spec == "50×529×1.5t"
    assert gasket.geometry.parameters["designation"] == "ASB-6B"
    assert gasket.geometry.parameters["thickness_mm"] == 1.5


def test_type13_removes_h_minus_100_and_corrects_double_plate_p():
    result = analyze_single(
        "13-6B-05B",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    support_pipe = _component(result, "D13-SUPPORTING-PIPE-B")
    assert support_pipe.length == 0
    assert "FIELD CUT TO SUIT" in support_pipe.geometry.shape_spec

    plate_p = _component(result, "D13-PLATE-P")
    assert (plate_p.length, plate_p.width, plate_p.spec) == (150, 75, "9")
    assert plate_p.quantity == 2
    assert plate_p.geometry.parameters["pipe_center_spacing_C_mm"] == 140

    cover = _component(result, "D13-COVER-PLATE")
    assert (cover.length, cover.width, cover.spec, cover.quantity) == (
        75,
        75,
        "6",
        1,
    )


def test_type13_explicit_field_cut_and_plate_grade_complete_bom_inputs():
    result = analyze_single(
        "13-10B-15E",
        source_profile="cw_e25_24_hp6",
        overrides={
            "support_pipe_cut_length_mm": 1300,
            "plate_material": "A36/SS400",
        },
    )

    assert not result.error
    support_pipe = _component(result, "D13-SUPPORTING-PIPE-B")
    assert support_pipe.length == 1300
    assert support_pipe.geometry.parameters["weep_hole_diameter_mm"] == 6
    assert support_pipe.geometry.parameters["weep_hole_center_offset_mm"] is None

    plate_p = _component(result, "D13-PLATE-P")
    assert (plate_p.length, plate_p.width, plate_p.spec) == (250, 105, "12")
    assert plate_p.material == "A36/SS400"
    assert plate_p.geometry.parameters["detail_A_applies"] is True
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["fabrication_ready"] is False


def test_type13_without_grade_keeps_carbon_steel_class_and_review_blocker():
    result = analyze_single(
        "13-4B-05B",
        source_profile="cw_e25_24_hp6",
        overrides={"support_pipe_cut_length_mm": 400},
    )

    assert not result.error
    assert _component(result, "D13-PLATE-P").material == "CARBON STEEL"
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any(
        "plate grade" in blocker
        for blocker in result.meta["fabrication"]["blockers"]
    )


def test_type13_grades_h_overrun_and_enforces_designation_grammar():
    too_high = analyze_single(
        "13-6B-16B",
        source_profile="cw_e25_24_hp6",
    )
    assert not too_high.error
    assert too_high.meta["issues"][0]["severity"] == "warning"

    invalid_suffix = analyze_single(
        "13-6B-05B(S)",
        source_profile="cw_e25_24_hp6",
    )
    assert invalid_suffix.error
    assert "HH+M42" in invalid_suffix.error


def test_type13_ctci_sources_remain_blocked_without_d13_drawings():
    for profile in ("ctci_22a_5123a", "ctci_20e4588"):
        result = analyze_single(
            "13-6B-05B",
            source_profile=profile,
        )
        assert result.error
        assert "暫不計算" in result.error
        assert not result.entries
