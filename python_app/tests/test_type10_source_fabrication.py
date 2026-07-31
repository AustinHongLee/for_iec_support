from core.calculator import analyze_single


def _component(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_type10_cw_keeps_four_bolt_branch_with_fabrication_geometry():
    result = analyze_single(
        "10-2B-05A",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    assert not result.error
    assert [entry.name for entry in result.entries] == [
        "管路",
        "管路",
        "Plate_F",
        "ADJ.BOLT",
        "HEX NUT",
        "Plate_a_無鑽孔",
    ]
    assert _component(result, "D10-UPPER-DUMMY-PIPE").length == 271
    assert _component(result, "D10-LOWER-SUPPORTING-PIPE").length == 200

    plate = _component(result, "D10-PLATE-F")
    assert plate.quantity == 2
    assert plate.geometry.parameters["hole_diameter_mm"] == 15
    assert plate.geometry.parameters["hole_pitch_x_mm"] == 100
    assert plate.geometry.parameters["edge_offset_mm"] == 35

    bolt = _component(result, "D10-ADJUSTING-BOLT")
    nuts = _component(result, "D10-HEX-NUT")
    assert (bolt.spec, bolt.quantity, bolt.unit_weight) == ("M12*160L", 4, 0.14)
    assert (nuts.spec, nuts.quantity, nuts.unit_weight) == ("M12", 16, 0)


def test_type10_cw_table_is_completed_through_50_inch():
    result = analyze_single(
        "10-50B-10G",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "straight"},
    )

    assert not result.error
    assert _component(result, "D10-UPPER-DUMMY-PIPE").length == 200
    assert _component(result, "D10-LOWER-SUPPORTING-PIPE").spec == '28"*STD.WT'
    plate = _component(result, "D10-PLATE-F")
    assert (plate.length, plate.spec) == (820, "22")
    assert _component(result, "D10-ADJUSTING-BOLT").spec == "M24*180L"


def test_type10_cw_boundary_overrun_is_warning_not_unbounded_release():
    result = analyze_single(
        "10-6B-15A",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    assert not result.error
    assert result.entries
    assert result.meta["issues"][0]["severity"] == "warning"
    assert result.meta["fabrication"]["fabrication_ready"] is False

    excessive = analyze_single(
        "10-6B-40A",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )
    assert excessive.error
    assert "有限外插護欄" in excessive.error


def test_type10_20e_is_base_washer_m1_not_cw_plate_f_branch():
    result = analyze_single(
        "10-6B-05B",
        source_profile="ctci_20e4588",
        overrides={"connection": "elbow"},
    )

    assert not result.error
    assert not any(entry.name == "Plate_F" for entry in result.entries)
    assert not any(entry.name == "ADJ.BOLT" for entry in result.entries)
    assert _component(result, "D10-UPPER-DUMMY-PIPE").length == 286
    assert _component(result, "D10-LOWER-SUPPORTING-PIPE").length == 300

    washer = _component(result, "D10-BASE-WASHER")
    assert washer.geometry.shape_kind == "annular_plate"
    assert washer.geometry.parameters == {
        "outer_diameter_F_mm": 130,
        "inner_diameter_mm": 95,
        "thickness_mm": 12,
        "weld_to_dummy_leg_mm": 6,
    }
    assert washer.unit_weight == 0.58

    m1 = _component(result, "M-1")
    assert m1.geometry.fabrication_ready is True
    assert m1.geometry.parameters["threaded_pipe_length_mm"] == 200
    assert m1.geometry.parameters["base_plate_diameter_mm"] == 150
    assert m1.geometry.parameters["drain_half_hole_diameter_mm"] == 10

    assert not any(entry.name.startswith("Plate_a_") for entry in result.entries)
    assert any(entry.name.startswith("Plate_d_") for entry in result.entries)


def test_type10_20e_type_c_retains_m42_plate_a():
    result = analyze_single(
        "10-12B-05C",
        source_profile="ctci_20e4588",
        overrides={"connection": "straight"},
    )

    assert not result.error
    assert _component(result, "D10-UPPER-DUMMY-PIPE").length == 100
    assert _component(result, "D10-BASE-WASHER").length == 180
    assert _component(result, "M42-PLATE-A").length == 230
    assert result.meta["fabrication"]["branch"].startswith(
        "D-10/single_leg_base_washer_m1"
    )


def test_type10_20e_rejects_cw_sizes_and_lower_components():
    wrong_size = analyze_single(
        "10-4B-05B",
        source_profile="ctci_20e4588",
        overrides={"connection": "straight"},
    )
    assert wrong_size.error

    wrong_m42 = analyze_single(
        "10-6B-05A",
        source_profile="ctci_20e4588",
        overrides={"connection": "straight"},
    )
    assert wrong_m42.error


def test_type10_connection_is_required_for_bom_ready():
    result = analyze_single(
        "10-2B-05A",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert result.meta["fabrication"]["bom_ready"] is False
    assert any("straight/elbow" in warning for warning in result.warnings)
