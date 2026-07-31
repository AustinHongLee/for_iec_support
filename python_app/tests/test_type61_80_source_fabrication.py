"""Source-truth and fabrication-readiness locks for rebuilt Type 61~80 rules."""

import pytest

from core.calculator import analyze_single
from core.source_profiles import (
    CTCI_20E4588,
    CTCI_22A_5123A,
    CW_E25_24_HP6,
)
from data.m54_table import get_m54_by_line_size
from data.m55_table import get_m55_by_line_size
from data.type77_table import get_type77_data
from data.type79_table import get_type79_data


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


@pytest.mark.parametrize(
    ("profile", "revision"),
    [
        (CW_E25_24_HP6, "1"),
        (CTCI_22A_5123A, "1"),
        (CTCI_20E4588, "1A"),
    ],
)
def test_type61_uses_source_profile_and_d73_trunnion_minimums(profile, revision):
    sch80 = analyze_single("61-2B-T1-05", source_profile=profile)
    wall_3_8 = analyze_single("61-12B-T2-10", source_profile=profile)

    assert not sch80.error and not wall_3_8.error
    assert sch80.entries[0].spec == '2" SCH.80'
    assert sch80.entries[0].length == 500
    assert wall_3_8.entries[0].geometry.parameters["wall_thickness_mm"] == 9.525
    assert wall_3_8.entries[0].quantity == 2
    assert wall_3_8.meta["fabrication"]["source_revision"] == revision
    assert not wall_3_8.meta["fabrication"]["capacity_verified"]


def test_type61_pad_is_reference_until_developed_dimensions_are_explicit():
    blocked = analyze_single("61-4B-T1-05(P)")
    exact = analyze_single(
        "61-4B-T1-05(P)",
        {
            "pad_developed_length_mm": 300,
            "pad_width_mm": 180,
            "pad_thickness_mm": 12,
        },
    )

    reference = _entry(blocked, "D72-REINFORCING-PAD-REFERENCE")
    assert reference.unit_weight == 0
    assert reference.length == 0
    assert reference.geometry.fabrication_blockers
    assert "OD+50" in reference.remark

    pad = _entry(exact, "D72-REINFORCING-PAD")
    assert (pad.length, pad.width, pad.spec) == (300, 180, "12.0")
    assert pad.unit_weight > 0
    assert pad.geometry.fabrication_ready


def test_type64_d78_table_and_figure_restrictions_are_exact():
    starred_bad = analyze_single("64-1/2-8-05A")
    starred_ok = analyze_single("64-3.1/2-8-05B")
    removed_size = analyze_single("64-1.1/4-8-05B")
    four_inch = analyze_single("64-4-8-05A")

    assert starred_bad.error and "FIG-B/C" in starred_bad.error
    assert not starred_ok.error
    assert starred_ok.meta["fabrication"]["assembly_dimensions"]["rod_size"] == '1/2"'
    assert removed_size.error and "不在 D-78 表列" in removed_size.error
    assert four_inch.meta["fabrication"]["assembly_dimensions"]["rod_size"] == '5/8"'


def test_type64_centerline_h_never_becomes_rod_cut_length():
    blocked = analyze_single("64-2-8-05A")
    explicit = analyze_single("64-2-8-05A", {"rod_cut_length_mm": 800})

    blocked_rod = _entry(blocked, "D78-M22-RODS")
    explicit_rod = _entry(explicit, "D78-M22-RODS")
    assert blocked_rod.length == 0
    assert blocked_rod.geometry.parameters["assembly_centerline_H_mm"] == 500
    assert blocked_rod.geometry.fabrication_blockers
    assert explicit_rod.length == 800 and explicit_rod.unit_weight > 0
    # Other purchased-source weights are still unresolved.
    assert not explicit.meta["fabrication"]["bom_ready"]


def test_type65_d79_rows_and_field_fit_rules_do_not_invent_parts():
    result = analyze_single("65-6B-1505")
    missing_size = analyze_single("65-2.1/2B-1505")

    assert not result.error
    member = _entry(result, "D79-MEMBER-M")
    rod = _entry(result, "D79-M23-WELDED-EYE-RODS")
    assert (member.spec, member.length) == ("100*50*5", 1500)
    assert member.geometry.parameters["selection_bucket_mm"] == 1500
    assert member.geometry.fabrication_blockers
    assert rod.length == 0
    assert rod.geometry.parameters["assembly_H_mm"] == 500
    assert missing_size.error and "未表列 2.5" in missing_size.error


def test_m54_formed_straps_are_dimensional_lookups_not_flat_blank_weights():
    row = get_m54_by_line_size('2"', fig_no=2)
    type72 = analyze_single("72-2B")
    type78 = analyze_single("78-2B(A)")

    assert row["dimensions_mm"]["B"] == 150
    assert row["unit_weight_kg"] == 0
    for result in (type72, type78):
        assert not result.error
        assert result.total_weight == 0
        assert not result.meta["fabrication"]["bom_ready"]
        assert result.entries[0].geometry.fabrication_blockers


def test_type73_uses_m53_developed_blank_but_blocks_unproven_accessory_weights():
    result = analyze_single("73-6B-G")
    strap = _entry(result, "D88-M53-STRAP")

    assert not result.error
    assert (strap.length, strap.width, strap.spec) == (396, 125, "9.0")
    assert strap.geometry.gross_area_mm2 == 396 * 125
    assert strap.geometry.cutout_area_mm2 > 0
    assert strap.unit_weight == 3.44
    assert strap.geometry.fabrication_ready
    assert all(entry.unit_weight == 0 for entry in result.entries[1:])
    assert not result.meta["fabrication"]["bom_ready"]


def test_type76_d91_weight_requires_actual_development_and_thickness():
    blocked = analyze_single("76-30B")
    exact = analyze_single(
        "76-30B",
        {
            "pad_developed_width_mm": 800,
            "pad_thickness_mm": 12,
        },
    )

    assert blocked.total_weight == 0
    assert blocked.entries[0].geometry.fabrication_blockers
    assert exact.total_weight == 30.14
    assert (exact.entries[0].length, exact.entries[0].width) == (400, 800)
    assert exact.meta["fabrication"]["bom_ready"]


def test_type77_and_type79_retire_assembly_bounding_rectangle_weights():
    row77 = get_type77_data('40"')
    row79 = get_type79_data('8"')
    result77 = analyze_single("77-40B-(A)")
    result79 = analyze_single("79-8B(A)")

    assert row77["unit_weight_kg"] == 0
    assert row77["retired_bounding_weight_kg"] > 0
    assert row79["unit_weight_kg"] == 0
    assert row79["retired_B_E_T_estimate_kg"] > 0
    for result in (result77, result79):
        assert result.total_weight == 0
        assert not result.meta["fabrication"]["bom_ready"]
        assert result.entries[0].geometry.fabrication_blockers


def test_type80_d95_rows_are_selected_by_project_source():
    cw = analyze_single(
        "80-6B(P)-A(A)-130-500",
        source_profile=CW_E25_24_HP6,
    )
    ctci22 = analyze_single(
        "80-6B(P)-A(A)-130-500",
        source_profile=CTCI_22A_5123A,
    )
    ctci20 = analyze_single(
        "80-10B(P)-A(R)-130-500",
        source_profile=CTCI_20E4588,
    )

    assert cw.meta["fabrication"]["assembly_dimensions"]["A"] == 100
    assert ctci22.meta["fabrication"]["assembly_dimensions"]["A"] == 200
    assert ctci20.meta["fabrication"]["assembly_dimensions"]["B"] == 100
    assert _entry(cw, "D95-BEAM-INTERFACE-MEMBER-C").length == 500
    assert _entry(ctci22, "D95-D80-SHOE-REFERENCE").unit_weight == 0


def test_type80_d96_stays_blocked_and_20e_size_range_is_enforced():
    supported = analyze_single(
        "80-28B-A(R)-130-500",
        source_profile=CTCI_20E4588,
    )
    unsupported = analyze_single(
        "80-30B-A(R)-130-500",
        source_profile=CTCI_20E4588,
    )

    assert not supported.error
    assert supported.total_weight == 0
    assert [
        entry.geometry.component_id for entry in supported.entries
    ] == [
        "D96-D80B-LARGE-SHOE-ASSEMBLY",
        "D96-BEAM-INTERFACE-PARTS",
    ]
    assert all(entry.geometry.fabrication_blockers for entry in supported.entries)
    assert unsupported.error and "未表列 30" in unsupported.error
