import math

import pytest

from core.calculator import analyze_single
from data.cold_restraint_tables import (
    get_n6_component,
    get_n7_by_cradle,
    get_n7a_by_cradle,
    get_n8_by_cradle,
    get_n8a_by_line_size,
)
from data.component_table_registry import get_component_table_coverage


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def _has_component(result, prefix):
    return any(
        entry.geometry.component_id.startswith(prefix)
        for entry in result.entries
        if entry.geometry.component_id
    )


def test_n6_preserves_single_component_geometry_without_fake_pipe_cut():
    row = get_n6_component()

    assert row["overall_height_mm"] == 200
    assert row["base_plate"]["outside_diameter_mm"] == 150
    assert row["base_plate"]["thickness_mm"] == 12
    assert row["base_plate"]["half_hole_diameter_mm"] == 10
    assert row["pipe_stub"]["material"] == "A53 Gr.B"
    assert row["pipe_stub"]["cross_hole_diameter_mm"] == 15
    assert row["coupling"]["outside_diameter_mm"] == 108
    assert row["coupling"]["axial_length_mm"] == 54
    assert row["pipe_to_plate_weld_mm"] == 6
    assert "cut_length_mm" not in row["pipe_stub"]
    assert not row["weight_ready"]
    assert not row["fabrication_ready"]


def test_n7_and_n7a_are_distinct_source_rows_not_aliases():
    n7 = get_n7_by_cradle("CR3")
    n7a = get_n7a_by_cradle("CR3")

    assert (n7["R_mm"], n7["B_centerline_mm"]) == (50, 100)
    assert n7["C_overall_mm"] == 105
    assert n7a["C_overall_mm"] == 106
    assert (n7["D_thread_length_mm"], n7["E_leg_to_bend_center_mm"]) == (
        84,
        134,
    )
    assert (
        n7a["D_thread_length_mm"],
        n7a["E_leg_to_bend_center_mm"],
    ) == (52, 94)
    assert n7["rod_developed_length_mm"] != pytest.approx(
        n7a["rod_developed_length_mm"]
    )


def test_n7_rod_length_and_weight_follow_centerline_geometry():
    row = get_n7_by_cradle("CR8")
    developed = math.pi * 234 / 2 + 2 * 222
    weight = (
        math.pi
        * (0.375 * 25.4) ** 2
        / 4
        * developed
        * 7.85e-6
    )

    assert row["rod_developed_length_mm"] == pytest.approx(developed)
    assert row["rod_calculated_weight_kg"] == pytest.approx(weight)
    assert row["rod_weight_ready"]
    assert not row["weight_ready"]


def test_n8_cradle_rows_keep_thickness_steps_and_block_flat_weight():
    cr17 = get_n8_by_cradle("CR17")
    cr22 = get_n8_by_cradle("CR22")

    assert (cr17["A_mm"], cr17["B_hole_pitch_mm"]) == (600, 536)
    assert cr17["thickness_mm"] == 12
    assert cr22["thickness_mm"] == 16
    assert cr22["A_mm"] == cr22["B_hole_pitch_mm"] + 64
    assert cr22["hole_center_end_offset_mm"] == 32
    assert cr22["hole_count"] == 2
    assert cr22["hole_diameter_mm"] == 22
    assert get_n8_by_cradle("CR4") is None
    assert get_n8_by_cradle("CR26") is None
    assert not cr22["weight_ready"]


def test_n8a_uses_line_size_not_cradle_number():
    row = get_n8a_by_line_size(8)

    assert row["designation"] == "STR1-8B"
    assert (row["R_mm"], row["A_mm"], row["B_hole_pitch_mm"]) == (
        113,
        380,
        316,
    )
    assert row["thickness_mm"] == 10
    assert get_n8a_by_line_size(4) is None
    assert get_n8a_by_line_size(12) is None


def test_type04c_adds_exact_n6_reference_without_claiming_weight():
    result = analyze_single("04C-6B-12B")
    base = _entry(result, "N-6")

    assert not result.error
    assert base.geometry.parameters["overall_height_mm"] == 200
    assert base.geometry.parameters["base_plate"]["outside_diameter_mm"] == 150
    assert base.unit_weight == 0
    assert not base.geometry.fabrication_ready


def test_type18c_adds_n7_rod_weight_and_zero_weight_nuts():
    result = analyze_single("18C-B-CR8-4B")
    rod = _entry(result, "N-7-U-BOLT-ROD")
    nuts = _entry(result, "N-7-FINISHED-HEX-NUTS")

    assert not result.error
    assert rod.geometry.parameters["designation"] == "SUB-CR8"
    assert rod.geometry.parameters["D_thread_length_mm"] == 105
    assert rod.unit_weight == pytest.approx(0.454)
    assert nuts.quantity == 4
    assert nuts.unit_weight == 0


def test_type20c_selects_n8a_only_for_6_8_10_branch():
    selected = analyze_single("20C-8B-500")
    small = analyze_single("20C-3B-500")
    large = analyze_single("20C-14B-500")

    assert not selected.error
    assert _entry(selected, "N-8A").geometry.parameters[
        "designation"
    ] == "STR1-8B"
    assert not _has_component(small, "N-8A")
    assert not _has_component(large, "N-8A")


def test_type22c_selects_n7a_and_n8_on_separate_branches():
    small = analyze_single("22C-A-CR9-2B-500")
    three_four = analyze_single("22C-A-CR9-4B-500")
    large = analyze_single("22C-A-CR10-8B-500")

    assert not small.error
    assert not three_four.error
    assert not large.error
    assert _entry(
        small,
        "N-7A-U-BOLT-ROD",
    ).geometry.parameters["designation"] == "SUB1-CR9"
    assert _entry(
        three_four,
        "N-8",
    ).geometry.parameters["designation"] == "STR-CR9"
    assert not _has_component(large, "N-7A")
    assert not _has_component(large, "N-8")


@pytest.mark.parametrize(
    ("designation", "expected_component"),
    (
        ("114C-A-CR9-4B-500", "N-8"),
        ("115C-ACR9-2B-800", "N-7A-U-BOLT-ROD"),
        ("115C-ACR9-4B-800", "N-8"),
        ("116C-A-CR8-1B-500A", "N-7-U-BOLT-ROD"),
    ),
)
def test_custom_cold_hosts_resolve_their_selected_restraint(
    designation,
    expected_component,
):
    result = analyze_single(designation)

    assert not result.error
    assert _has_component(result, expected_component)


def test_component_registry_promotes_five_restraint_sheets():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["partial_lookup"] == 3
    assert coverage["metadata_only"] == 8
