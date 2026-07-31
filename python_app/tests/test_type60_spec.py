import math

import pytest

from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows


def test_type58_d69_row_and_holes_are_drawing_backed():
    result = analyze_single("58-4B-A")

    assert not result.error
    assert [entry.name for entry in result.entries] == [
        "STEEL PLATE",
        "M-26 U-BOLT ROD",
        "M-26 FINISHED HEX NUTS",
    ]
    plate = result.entries[0]
    rod = result.entries[1]
    nuts = result.entries[2]
    assert (plate.spec, plate.length, plate.width, plate.quantity) == (
        "9", 200, 65, 1,
    )
    assert (plate.geometry.holes.count, plate.geometry.holes.diameter) == (2, 14)
    assert plate.geometry.holes.pitch_x == 129
    assert rod.length == pytest.approx(math.pi * 116 / 2 + 2 * 108)
    assert rod.unit_weight > 0
    assert nuts.quantity == 4
    assert nuts.unit_weight > 0


def test_type58_fig_b_records_source_weld_x():
    result = analyze_single("58-4B-B")

    assert not result.error
    assert result.meta["fabrication"]["installation"]["fig_b_fillet_weld_mm"] == 5
    assert result.entries[0].geometry.parameters["fig_b_fillet_weld_mm"] == 5


def test_type48_spec_handles_fractional_size_and_material_suffix():
    result = analyze_single("48-1/2B(B)")

    assert not result.error
    entry = result.entries[0]
    assert (entry.name, entry.spec, entry.length, entry.width, entry.quantity) == (
        "PLATE", "6", 150, 100, 1,
    )
    assert entry.material == "Stainless Steel"
    assert entry.geometry.component_id == "D59-OFFSET-PLATE"
    assert entry.geometry.shape_kind == "bent_offset_plate_blank"
    assert entry.geometry.parameters["upper_leg_mm"] == 100
    assert entry.geometry.parameters["lower_offset_mm"] == 20
    assert result.meta["fabrication"]["blank_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_type57_m26_metadata_and_invalid_mode_hard_stop():
    slide = analyze_single("57-2B-A")
    fixed = analyze_single("57-2B-B")
    invalid = analyze_single("57-2B-Z")

    assert not slide.error
    assert [entry.name for entry in slide.entries] == [
        "M-26 U-BOLT ROD",
        "M-26 FINISHED HEX NUTS",
    ]
    rod, nuts = slide.entries
    assert rod.material == "CARBON STEEL (GRADE NOT SPECIFIED IN M-26)"
    assert rod.geometry.parameters["C_overall_mm"] == 71
    assert rod.length == pytest.approx(math.pi * 62 / 2 + 2 * 74)
    assert rod.unit_weight > 0
    assert nuts.quantity == 4
    assert nuts.unit_weight > 0
    assert not slide.meta["fabrication"]["fabrication_ready"]
    assert not fixed.error
    assert invalid.error
    assert invalid.entries == []


def test_m26_project_quantity_scales_rod_weight_and_nuts_once_only():
    project = analyze_project_rows(
        [
            ProjectInputRow("57-2B-A", quantity=3),
            ProjectInputRow("58-4B-B", quantity=2),
        ],
        source_profile="cw_e25_24_hp6",
    )

    assert not project.errors
    for row_result in project.rows:
        single = row_result.single_result
        scaled = row_result.scaled_result
        support_qty = row_result.input_row.quantity
        assert scaled.total_weight == pytest.approx(
            single.total_weight * support_qty
        )
        rod_single = next(
            entry for entry in single.entries
            if entry.geometry.shape_kind == "u_bolt_round_bar"
        )
        rod_scaled = next(
            entry for entry in scaled.entries
            if entry.geometry.shape_kind == "u_bolt_round_bar"
        )
        nuts_single = next(
            entry for entry in single.entries
            if entry.geometry.shape_kind == "purchased_finished_hex_nut"
        )
        nuts_scaled = next(
            entry for entry in scaled.entries
            if entry.geometry.shape_kind == "purchased_finished_hex_nut"
        )
        assert rod_scaled.quantity == rod_single.quantity * support_qty
        assert rod_scaled.weight_output == pytest.approx(
            rod_single.weight_output * support_qty
        )
        assert nuts_scaled.quantity == 4 * support_qty
        assert nuts_scaled.weight_output == pytest.approx(
            nuts_single.weight_output * support_qty
        )

    assert project.total_weight == pytest.approx(
        sum(row.scaled_result.total_weight for row in project.rows)
    )


def test_m26_carbon_steel_truth_is_not_overwritten_by_upper_material_override():
    result = analyze_single(
        "57-2B-A",
        overrides={"upper_material": "SUS316"},
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert all(
        entry.material == "CARBON STEEL (GRADE NOT SPECIFIED IN M-26)"
        for entry in result.entries
    )


def test_type60_fig_a_uses_two_base_and_four_loftable_wing_plates():
    result = analyze_single("60-20B-A")

    assert not result.error
    assert [(entry.name, entry.spec, entry.length, entry.width, entry.quantity) for entry in result.entries] == [
        ("SIDE SUPPORT BASE PLATE", "12", 120, 340, 2),
        ("SIDE SUPPORT WING PLATE", "12", 200, 120, 4),
    ]
    assert result.meta["fabrication"]["assembly_dimensions"] == {
        "A": 200, "B": 120, "C": 60, "D": 340,
        "E": 240, "F": None, "T": 12,
    }
    assert all(entry.material == "A283 Gr.C" for entry in result.entries)
    assert result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_type60_fig_b_uses_exact_d71_row_and_blocks_shape_export():
    result = analyze_single("60-20B-B")

    assert not result.error
    assert [(entry.name, entry.length, entry.width, entry.quantity) for entry in result.entries] == [
        ("SIDE SUPPORT BASE PLATE", 150, 260, 2),
        ("SIDE SUPPORT WING PLATE", 0, 0, 4),
    ]
    wing = result.entries[1]
    assert wing.geometry.parameters["pipe_contact_angle_deg"] == 120
    assert wing.geometry.parameters["upper_angle_deg"] == 45
    assert wing.geometry.fabrication_ready is False
    assert result.meta["fabrication"]["not_furnished"] == []
    assert not result.meta["fabrication"]["bom_ready"]
