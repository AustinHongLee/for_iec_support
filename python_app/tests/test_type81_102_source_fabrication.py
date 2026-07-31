"""Drawing-truth locks for the Type 81~102 implementation wave."""

import math

import pytest

from core.calculator import analyze_single
from core.source_profiles import (
    CTCI_20E4588,
    CTCI_22A_5123A,
    CW_E25_24_HP6,
)


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


@pytest.mark.parametrize("type_id,detail", [("81", "97"), ("86", "107")])
def test_type81_family_reuses_d81_but_retires_unproven_supplier_weights(
    type_id, detail
):
    result = analyze_single(
        f"{type_id}-6B-A-150-250",
        source_profile=CW_E25_24_HP6,
    )

    assert not result.error
    assert result.meta["fabrication"]["branch"] == f"D-{detail}"
    clamp = _entry(result, f"D{detail}-D81-M4-PIPE-CLAMP")
    gasket = _entry(result, f"D{detail}-D81-M47-GASKET")
    member = _entry(result, f"D{detail}-MEMBER-C")
    assert clamp.unit_weight == gasket.unit_weight == 0
    assert gasket.geometry.parameters["thickness_mm"] == 1.5
    assert member.unit_weight > 0
    assert member.geometry.parameters["field_fit"] is True
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_type81_large_and_fabricated_small_ranges_stay_as_zero_references():
    fabricated = analyze_single("81-16B-A-150-250")
    large = analyze_single("81-26B-A-150-250")

    assert _entry(fabricated, "D97-D81-ASSEMBLY-REFERENCE").unit_weight == 0
    assert _entry(large, "D98-D81A-ASSEMBLY-REFERENCE").unit_weight == 0
    assert all(
        entry.geometry.fabrication_blockers
        for result in (fabricated, large)
        for entry in result.entries
    )


def test_type84_adds_guide_reference_without_inventing_lops_cut_length():
    result = analyze_single("84-6B-A-150-250")

    guide = _entry(result, "D103-GUIDE-ANGLE-SET")
    assert guide.spec == "L40*40*5; CUT LENGTH/PIECE COUNT TBD"
    assert guide.unit_weight == 0
    assert guide.geometry.fabrication_blockers
    assert "LOPS" in guide.remark


def test_type82_and_82a_share_table_but_keep_guide_and_fixed_geometry_separate():
    guide = analyze_single("82-6B")
    fixed = analyze_single("82A-6B")

    guide_angle = _entry(guide, "D99-MEMBER-M-GUIDE-ANGLES")
    fixed_angle = _entry(fixed, "D100A-1-MEMBER-M-GUIDE-ANGLES")
    assert (guide_angle.spec, guide_angle.length, guide_angle.quantity) == (
        "65*65*6",
        150,
        2,
    )
    assert guide_angle.geometry.parameters["pipe_clearance_mm"] == 3
    assert not guide_angle.geometry.parameters["fixed_to_pipe"]
    assert fixed_angle.geometry.parameters["pipe_clearance_mm"] == 0
    assert fixed_angle.geometry.parameters["fixed_to_pipe"]
    assert guide.meta["fabrication"]["source_drawing"] == "TYPE-82_D-99.pdf"
    assert fixed.meta["fabrication"]["source_drawing"] == (
        "TYPE-82A_D-100A-1.pdf"
    )


def test_type82_large_saddle_preserves_dimensions_but_not_bounding_weight():
    result = analyze_single("82-36B")

    assembly = _entry(result, "D100-MEMBER-C-ASSEMBLY-REFERENCE")
    assert result.total_weight == 0
    assert assembly.geometry.parameters["A_mm"] == 450
    assert assembly.geometry.parameters["B_mm"] == 300
    assert assembly.geometry.parameters["D_mm"] == 400
    assert assembly.geometry.parameters["pipe_contact_angle_deg"] == 80
    assert assembly.geometry.parameters["reinforcing_pad_reference"] == "D-91"
    assert assembly.geometry.fabrication_blockers


@pytest.mark.parametrize(
    ("profile", "expected_b", "material_symbol"),
    [
        (CW_E25_24_HP6, 100, "(A)"),
        (CTCI_22A_5123A, 100, "(A)"),
        (CTCI_20E4588, 100, "(R)"),
    ],
)
def test_type83_uses_same_source_type80_shoe_and_adds_axial_stop(
    profile, expected_b, material_symbol
):
    result = analyze_single(
        f"83-6B(P)-A{material_symbol}-130-500",
        source_profile=profile,
    )

    assert not result.error
    assert result.meta["fabrication"]["branch"] == "D-101"
    assert (
        result.meta["fabrication"]["base_pipe_shoe"]["assembly_dimensions"]["B"]
        == expected_b
    )
    stop = _entry(result, "D101-AXIAL-STOP-ASSEMBLY")
    assert stop.unit_weight == 0
    assert stop.geometry.fabrication_blockers
    assert all(
        entry.geometry.parameters.get("parent_type") == "83"
        for entry in result.entries
        if entry is not stop
    )


def test_type83_large_branch_retains_each_multi_piece_blocker():
    result = analyze_single("83-26B(P)-A(A)-130-500")

    assert not result.error
    assert result.total_weight == 0
    assert result.meta["fabrication"]["branch"] == "D-102"
    assert {
        entry.geometry.component_id for entry in result.entries
    } == {
        "D96-D80B-LARGE-SHOE-ASSEMBLY",
        "D96-BEAM-INTERFACE-PARTS",
        "D102-AXIAL-STOP-ASSEMBLY",
    }
    assert all(entry.geometry.fabrication_blockers for entry in result.entries)


@pytest.mark.parametrize(
    ("profile", "designation"),
    [
        (CW_E25_24_HP6, "85-6B(P)-A(A)-150-250"),
        (CTCI_22A_5123A, "85-4B(P)-A(A)-150-250"),
        (CTCI_20E4588, "85-6B(P)-A(R)-150-250"),
    ],
)
def test_type85_is_the_same_source_d80_not_an_insulation_saddle(
    profile, designation
):
    result = analyze_single(designation, source_profile=profile)

    assert not result.error
    assert result.meta["fabrication"]["branch"] == "D-80"
    assert all(
        entry.geometry.parameters["parent_type"] == "85"
        for entry in result.entries
    )
    assert not any("INSULATION SADDLE" in entry.name for entry in result.entries)


def test_type85_large_range_and_20e_maximum_follow_each_source_drawing():
    cw = analyze_single(
        "85-30B(P)-A(A)-150-250",
        source_profile=CW_E25_24_HP6,
    )
    ctci20 = analyze_single(
        "85-30B(P)-A(R)-150-250",
        source_profile=CTCI_20E4588,
    )

    assert not cw.error
    assert _entry(cw, "D106-D80B-ASSEMBLY-REFERENCE").unit_weight == 0
    assert ctci20.error and "未表列 30" in ctci20.error


def test_type86_22a_has_small_d107_only():
    small = analyze_single(
        "86-6B-A-150-250",
        source_profile=CTCI_22A_5123A,
    )
    large = analyze_single(
        "86-26B-A-150-250",
        source_profile=CTCI_22A_5123A,
    )

    assert not small.error
    assert small.meta["fabrication"]["branch"] == "D-107"
    assert large.error and "未表列 26" in large.error


def test_type87_h_is_assembly_height_and_cw_round_plate_is_exact():
    result = analyze_single("87-M27-10G")

    support_pipe = _entry(result, "D109-SUPPORT-PIPE")
    disc = _entry(result, "D109-ROUND-PLATE-D")
    assert support_pipe.length == 0
    assert support_pipe.geometry.parameters["assembly_H_mm"] == 1000
    assert support_pipe.geometry.parameters["pipe_cut_length_mm"] is None
    assert disc.geometry.parameters["diameter_mm"] == 72
    assert disc.geometry.parameters["thickness_mm"] == 9
    assert disc.unit_weight == pytest.approx(
        math.pi * 72**2 / 4 * 9 * 7.85e-6,
        abs=0.01,
    )
    assert disc.geometry.fabrication_ready


def test_type87_source_profiles_have_different_e_and_lower_component_sets():
    cw_bad = analyze_single("87-M27-10T")
    ctci = analyze_single(
        "87-1-10T",
        source_profile=CTCI_22A_5123A,
    )

    assert cw_bad.error and "G/J/R" in cw_bad.error
    assert not ctci.error
    assert ctci.meta["fabrication"]["assembly_dimensions"]["thread_E_mm"] == 190
    assert not any(
        entry.geometry.component_id == "D108-ROUND-PLATE-D"
        for entry in ctci.entries
    )


def test_type101_keeps_source_rib_count_but_blocks_fake_finished_length():
    cw = analyze_single("101-1.1/2B(S)-A")
    ctci = analyze_single(
        "101-1.1/2B(S)-A",
        source_profile=CTCI_20E4588,
    )

    cw_ribs = _entry(cw, "D110-SMALL-BORE-RIB-SET")
    ctci_ribs = _entry(ctci, "D110-SMALL-BORE-RIB-SET")
    assert cw_ribs.geometry.parameters["rib_count"] == 3
    assert cw_ribs.geometry.parameters["plan_spacing_deg"] == 120
    assert ctci_ribs.geometry.parameters["rib_count"] == 1
    assert ctci_ribs.geometry.parameters["plan_spacing_deg"] is None
    assert cw.total_weight == ctci.total_weight == 0
    assert "190/sin60" in cw_ribs.remark


def test_type101_retains_20e_material_symbol_conflict_for_confirmation():
    result = analyze_single(
        "101-1B(R)-A",
        source_profile=CTCI_20E4588,
    )

    assert not result.error
    assert result.entries[0].material == "LTCS"
    assert any("A/R source notation conflict" in warning for warning in result.warnings)


def test_type102_e_and_w_boundary_differs_between_cw_and_22a():
    cw = analyze_single("102-6B-A")
    ctci = analyze_single(
        "102-6B-B",
        source_profile=CTCI_22A_5123A,
    )

    cw_plate = _entry(cw, "D111-E-PLATE-INTERFACE-SET")
    ctci_plate = _entry(ctci, "D111-E-PLATE-INTERFACE-SET")
    assert (
        cw_plate.geometry.parameters["plate_thickness_E_mm"],
        cw_plate.geometry.parameters["fillet_weld_W_mm"],
    ) == (9, 6)
    assert (
        ctci_plate.geometry.parameters["plate_thickness_E_mm"],
        ctci_plate.geometry.parameters["fillet_weld_W_mm"],
    ) == (12, 10)
    assert cw_plate.geometry.parameters["pipe_side_offset_mm"] == 40
    assert ctci_plate.geometry.parameters["pipe_side_offset_mm"] == 75
    assert ctci_plate.geometry.parameters["G_mm"] == 50
    assert cw.total_weight == ctci.total_weight == 0
    assert cw.meta["fabrication"]["not_furnished"] == [
        "D-80 pipe shoe",
        "existing member",
    ]
