"""Source locks for the first N-series cold-component fabrication wave."""

import math

import pytest

from core.calculator import analyze_single
from data.component_table_registry import get_component_table_coverage
from data.n9_table import get_n9_lower_component
from data.n10_table import get_n10_by_supporting_pipe
from data.n12_table import get_n12_clip
from data.n12a_table import (
    get_n12a_clip_type3,
    get_n12a_insulation_row,
)
from data.n27_pu_block_table import get_n27_pu_block
from data.n28_table import get_n28_by_number


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def _entries(result, component_id):
    return [
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    ]


def test_n27_regular_and_u_rows_preserve_exact_geometry_and_density():
    block_1 = get_n27_pu_block(1)
    block_4 = get_n27_pu_block("PUBK-4")
    block_2u = get_n27_pu_block("2U")

    expected_1_volume = (
        125 * 70 * 50
        - 2 * math.pi * 8**2 * 50
    )
    assert block_1["net_volume_mm3"] == pytest.approx(expected_1_volume)
    assert block_1["unit_weight_kg"] == pytest.approx(
        expected_1_volume / 1_000_000_000 * 320
    )
    assert block_1["hole_centers_mm"] == [
        {"x_mm": 20, "y_mm": 35},
        {"x_mm": 105, "y_mm": 35},
    ]
    assert block_4["hole_diameter_mm"] == 19
    assert block_4["hole_count"] == 4
    assert block_2u["hole_count"] == 0
    assert block_2u["unit_weight_kg"] == pytest.approx(
        130 * 130 * 100 / 1_000_000_000 * 320
    )


def test_n28_preserves_holes_and_does_not_invent_white_oak_density():
    wood_1 = get_n28_by_number(1)
    wood_3 = get_n28_by_number("WOOD-3")

    assert wood_1["weight_ready"] is False
    assert wood_1["hole_centers_mm"][0] == {"x_mm": 50, "y_mm": 40}
    assert not wood_1["fabrication_ready"]
    assert any(
        "chamfer" in blocker for blocker in wood_1["fabrication_blockers"]
    )
    assert wood_3["hole_centers_mm"] == [
        {"x_mm": 40, "y_mm": 110},
        {"x_mm": 190, "y_mm": 110},
    ]
    assert wood_3["fabrication_ready"]


def test_n9_n10_resolve_plate_rows_and_apply_host_deletion_note():
    row = get_n10_by_supporting_pipe("8in SCH.40")
    normal = get_n9_lower_component(
        "B",
        "2in SCH.40",
        host_type="06C",
    )
    adjustable = get_n9_lower_component(
        "B",
        "2in SCH.40",
        host_type="09C",
    )

    assert row["B_mm"] == 330
    assert row["E_mm"] == 490
    assert row["plate_K_mm"] == 16
    assert [plate["plate"] for plate in normal["plates"]] == ["a", "d"]
    assert [plate["plate"] for plate in adjustable["plates"]] == ["d"]
    assert adjustable["plate_a_deleted_by_n9_note_1"]
    assert adjustable["plates"][0]["holes"]["pitch_x_mm"] == 220


@pytest.mark.parametrize(
    ("insulation", "plate_t", "dim_a"),
    [
        (140, 9, 100),
        (141, 9, 180),
        (215, 9, 180),
        (216, 12, 260),
        (300, 12, 260),
    ],
)
def test_n12a_note2_boundaries_select_plate_and_a(
    insulation, plate_t, dim_a
):
    row = get_n12a_insulation_row(insulation)

    assert row["plate_thickness_mm"] == plate_t
    assert row["A_mm"] == dim_a


def test_n12_clip_types_keep_distinct_layouts_and_hole_geometry():
    clip_1 = get_n12_clip(1, 100)
    clip_2 = get_n12_clip(2, 200)
    clip_3 = get_n12a_clip_type3(220)

    assert clip_1["plan_layout"] == "single radial clip"
    assert clip_1["horizontal_hole_pitch_mm"] == 100
    assert clip_1["vertical_hole_pitch_mm"] == 200
    assert clip_2["plan_layout"] == "opposed pair about working point"
    assert clip_2["A_mm"] == 180
    assert clip_3["A_mm"] == 260
    assert clip_3["outer_width_mm"] == 240
    assert clip_3["horizontal_hole_pitch_mm"] == 150


@pytest.mark.parametrize(
    ("designation", "block_no", "weight"),
    [
        ("06C-12B", "PUBK-1", 0.13),
        ("07C-2B-12G", "PUBK-2U", 0.54),
        ("08C-2B-12J", "PUBK-2", 0.52),
        ("09C-2B-08B", "PUBK-2", 0.52),
        ("10C-6B-08B", "PUBK-3", 1.13),
    ],
)
def test_type06c_to_10c_emit_exact_n27_weight(
    designation, block_no, weight
):
    result = analyze_single(designation)
    block = _entry(result, "N27-PU BLOCK")

    assert not result.error
    assert block.geometry.parameters["block_no"] == block_no
    assert block.geometry.fabrication_ready
    assert result.total_weight == pytest.approx(weight)
    assert _entry(result, "N-9").unit_weight == 0


def test_type07c_to_10c_enforce_source_lower_component_sets():
    assert analyze_single("07C-2B-12B").error
    assert analyze_single("08C-2B-12A").error
    assert analyze_single("09C-2B-08J").error
    assert analyze_single("10C-6B-08R").error


def test_type09c_exposes_n9_note1_plate_a_deletion():
    result = analyze_single("09C-2B-08B")
    lower = _entry(result, "N-9").geometry.parameters

    assert lower["plate_a_deleted_by_n9_note_1"]
    assert [plate["plate"] for plate in lower["plates"]] == ["d"]


def test_type109c_and_110c_derive_insulation_and_resolve_clip_a():
    type109 = analyze_single("109C-6B-300-500")
    type110 = analyze_single("110C-4B-200-500")
    clip109 = _entry(type109, "N-12A").geometry.parameters
    clip110 = _entry(type110, "N-12").geometry.parameters

    assert not type109.error and not type110.error
    assert clip109["A_mm"] == 180
    assert clip109["plate_thickness_mm"] == 9
    assert clip110["A_mm"] == 100
    assert clip110["plate_thickness_mm"] == 9
    assert len(_entries(type109, "N-28")) == 3
    assert len(_entries(type110, "N-28")) == 1


@pytest.mark.parametrize(
    ("designation", "component_id"),
    [
        ("112C-200-500", "N-12A"),
        ("113C-L75-500", "N-12"),
        ("117C-L75-200-500", "N-12"),
    ],
)
def test_types_without_derivable_insulation_accept_explicit_override(
    designation, component_id
):
    unresolved = analyze_single(designation)
    resolved = analyze_single(
        designation,
        overrides={"insulation_thickness_mm": 220},
    )

    assert not _entry(
        unresolved, component_id
    ).geometry.parameters["lookup_ready"]
    clip = _entry(resolved, component_id).geometry.parameters
    assert clip["A_mm"] == 260
    assert clip["plate_thickness_mm"] == 12


def test_component_registry_promotes_six_n_series_tables():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["metadata_only"] == 8
