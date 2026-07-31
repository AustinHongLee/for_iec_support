from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type11_cw_uses_source_sizes_spring_and_lower_components():
    result = analyze_single(
        "11-6B-06J",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    assert not result.error
    assert _component(result, "D11-UPPER-DUMMY-PIPE").length == 229
    assert _component(result, "D11-SPRING-SPR14").quantity == 1
    assert _component(result, "D11-SPRING-SPR14").unit_weight == 1.37
    assert _component(result, "D11-FULL-THREADED-MB").spec == '1-5/8"*300L'
    assert _component(result, "D11-HEAVY-HEX-NUT").quantity == 2


def test_type11_removes_unfounded_h_minus_391_lower_pipe_formula():
    result = analyze_single(
        "11-2B-06G",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "straight"},
    )

    assert not result.error
    lower = _component(result, "D11-LOWER-SUPPORTING-PIPE")
    assert lower.length == 0
    assert lower.geometry.fabrication_ready is False
    assert "FIELD CUT TO SUIT" in lower.geometry.shape_spec
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any(
        "support_pipe_cut_length_mm" in blocker
        for blocker in lower.geometry.fabrication_blockers
    )


def test_type11_cw_can_become_bom_ready_with_explicit_field_inputs():
    result = analyze_single(
        "11-2B-06G",
        source_profile="cw_e25_24_hp6",
        overrides={
            "connection": "straight",
            "support_pipe_cut_length_mm": 420,
            "spring_installed_length_mm": 88,
            "threaded_rod_material": "A307-B GALV.",
            "heavy_hex_nut_material": "A307-B GALV.",
        },
    )

    assert not result.error
    assert _component(result, "D11-UPPER-DUMMY-PIPE").length == 100
    assert _component(result, "D11-LOWER-SUPPORTING-PIPE").length == 420
    assert result.meta["fabrication"]["bom_ready"] is True
    assert result.meta["fabrication"]["dimensions"][
        "spring_installed_length_D_mm"
    ] == 88


def test_type11_22a_requires_and_uses_installed_length_suffix():
    result = analyze_single(
        "11-2B-06G-88",
        source_profile="ctci_22a_5123a",
        overrides={
            "connection": "elbow",
            "support_pipe_cut_length_mm": 300,
        },
    )

    assert not result.error
    assert _component(result, "D11-UPPER-DUMMY-PIPE").length == 171
    rod = _component(result, "D11-FULL-THREADED-MB")
    assert (rod.spec, rod.material, rod.unit_weight) == (
        '1-3/4"*300L',
        "A307-B GALV.",
        3.65,
    )
    spring = _component(result, "D11-SPRING-SPR12")
    assert spring.geometry.parameters["installed_length_D_mm"] == 88
    assert result.meta["fabrication"]["bom_ready"] is True


def test_type11_annular_washers_use_net_geometry_and_correct_quantity():
    result = analyze_single(
        "11-2B-06G-88",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )

    assert not result.error
    washer = _component(result, "D11-WROUGHT-STEEL-WASHER")
    assert washer.quantity == 2
    assert washer.unit_weight == 0.33
    assert washer.geometry.shape_kind == "annular_plate"
    assert washer.geometry.parameters == {
        "outer_diameter_mm": 92.0,
        "inner_diameter_mm": 50.0,
        "thickness_mm": 9.0,
        "quantity": 2,
        "weight_basis": "exact annular geometry",
    }


def test_type11_22a_rejects_missing_or_invalid_installed_length():
    missing = analyze_single(
        "11-2B-06G",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert missing.error
    assert "彈簧安裝長度" in missing.error

    outside_spring_range = analyze_single(
        "11-2B-06G-70",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert outside_spring_range.error
    assert "78–100mm" in outside_spring_range.error


def test_type11_profiles_enforce_their_own_size_h_and_m42_sets():
    wrong_size = analyze_single(
        "11-6B-06G-88",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert wrong_size.error

    wrong_h = analyze_single(
        "11-2B-08G-88",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert wrong_h.error

    wrong_22a_letter = analyze_single(
        "11-2B-06J-88",
        source_profile="ctci_22a_5123a",
        overrides={"connection": "straight"},
    )
    assert wrong_22a_letter.error

    wrong_cw_letter = analyze_single(
        "11-2B-06R",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "straight"},
    )
    assert not wrong_cw_letter.error
    assert wrong_cw_letter.meta["issues"][0]["code"] == "HOST_M42_NOT_LISTED"
    assert wrong_cw_letter.meta["fabrication"]["bom_ready"] is False


def test_type11_20e_remains_blocked_without_a_d11_source_drawing():
    result = analyze_single(
        "11-2B-06G",
        source_profile="ctci_20e4588",
    )

    assert result.error
    assert "暫不計算" in result.error
    assert not result.entries
