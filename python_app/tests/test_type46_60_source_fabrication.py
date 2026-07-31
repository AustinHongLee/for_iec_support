import pytest

from core.calculator import analyze_single


def _entry(result, component_id):
    return next(entry for entry in result.entries if entry.geometry.component_id == component_id)


def test_type46_uses_d56_frame_dimensions_and_keeps_cw_d80_in_bom_scope():
    result = analyze_single("46-8B-C100-1300 A", source_profile="cw_e25_24_hp6")

    assert not result.error
    assert (_entry(result, "D56-LONGITUDINAL").length,
            _entry(result, "D56-LONGITUDINAL").quantity) == (1563, 2)
    assert (_entry(result, "D56-TRANSVERSE").length,
            _entry(result, "D56-TRANSVERSE").quantity) == (426, 2)
    assert (_entry(result, "D56-L50-BRACE").length,
            _entry(result, "D56-L50-BRACE").quantity) == (1016, 2)
    assert _entry(result, "D56-CLIP-PLATE").quantity == 2
    assert _entry(result, "D56-D80-REFERENCE").unit_weight == 0
    assert result.meta["fabrication"]["not_furnished"] == []
    assert not result.meta["fabrication"]["bom_ready"]


def test_type47_source_changes_member_fasteners_and_d80_ownership():
    cw = analyze_single("47-8B-C100-1300 A", source_profile="cw_e25_24_hp6")
    ctci = analyze_single("47-24B-C200-1300 B", source_profile="ctci_20e4588")

    assert not cw.error and not ctci.error
    assert (_entry(cw, "D57-LONGITUDINAL").length,
            _entry(cw, "D57-TRANSVERSE").length) == (1563, 426)
    assert _entry(cw, "D57-L50-BRACE").quantity == 2
    assert _entry(cw, "D57-D80-REFERENCE").unit_weight == 0
    assert not cw.meta["fabrication"]["bom_ready"]

    assert (_entry(ctci, "D57-LONGITUDINAL").length,
            _entry(ctci, "D57-TRANSVERSE").length) == (1758, 816)
    assert _entry(ctci, "D57-LONGITUDINAL").spec == "200*90*8"
    assert (_entry(ctci, "D57-DETAIL-Z-K-BOLT").spec,
            _entry(ctci, "D57-DETAIL-Z-K-BOLT").quantity) == ("M20x50", 12)
    assert (_entry(ctci, "D57-DETAIL-Y-K-BOLT").spec,
            _entry(ctci, "D57-DETAIL-Y-K-BOLT").quantity) == ("M16x40", 12)
    assert all(entry.geometry.component_id != "D57-D80-REFERENCE" for entry in ctci.entries)
    assert ctci.meta["fabrication"]["not_furnished"] == ["D-80 pipe-interface assembly"]
    assert ctci.meta["fabrication"]["bom_ready"]


def test_type48_is_blank_ready_but_not_bend_ready():
    result = analyze_single("48-2B", source_profile="cw_e25_24_hp6")

    assert not result.error
    entry = _entry(result, "D59-OFFSET-PLATE")
    assert (entry.length, entry.width, entry.spec, entry.material) == (
        150, 100, "6", "Carbon Steel",
    )
    assert entry.geometry.shape_kind == "bent_offset_plate_blank"
    assert entry.geometry.parameters["blank_length_mm"] == 150
    assert entry.geometry.parameters["lower_offset_mm"] == 20
    assert result.meta["fabrication"]["blank_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_type49_allows_both_d60_branches_for_the_full_drawing_range():
    a_small = analyze_single("49-2B-A", source_profile="cw_e25_24_hp6")
    a_large = analyze_single("49-4B-A", source_profile="cw_e25_24_hp6")
    b_large = analyze_single("49-4B-B", source_profile="cw_e25_24_hp6")

    assert not a_small.error and not a_large.error and not b_large.error
    assert [entry.geometry.component_id for entry in a_small.entries] == [
        "M-11",
        "M-11-FASTENERS",
    ]
    assert [entry.geometry.component_id for entry in a_large.entries] == [
        "M-11",
        "M-11-FASTENERS",
        "M-41",
    ]
    assert [entry.geometry.component_id for entry in b_large.entries] == [
        "M-12",
        "M-12-FASTENERS",
        "D-60-FIG-B-LUG-AMBIGUITY",
    ]
    assert all(result.total_weight > 0 for result in (a_small, a_large, b_large))
    assert all(not result.meta["fabrication"]["bom_ready"]
               for result in (a_small, a_large, b_large))


def test_type51_source_member_difference_and_large_cut_override():
    cw = analyze_single("51-10B", source_profile="cw_e25_24_hp6")
    ctci = analyze_single("51-10B", source_profile="ctci_22a_5123a")
    ctci_24 = analyze_single("51-24B", source_profile="ctci_22a_5123a")
    blocked = analyze_single("51-36B", source_profile="cw_e25_24_hp6")
    complete = analyze_single(
        "51-36B",
        overrides={"member_cut_length_mm": 420},
        source_profile="cw_e25_24_hp6",
    )

    assert cw.entries[0].spec == "65*65*6"
    assert ctci.entries[0].spec == "75*75*9"
    assert ctci_24.entries[0].length == 350
    assert not blocked.meta["fabrication"]["bom_ready"]
    assert blocked.entries[0].unit_weight == 0
    assert _entry(complete, "D62A-MEMBER-M").length == 420
    assert _entry(complete, "D91-REINFORCING-PAD-REFERENCE").unit_weight == 0
    assert not complete.meta["fabrication"]["bom_ready"]


def test_type51_half_inch_is_cw_high_risk_only_and_22a_excludes_d91_pad():
    half = analyze_single("51-1/2B", source_profile="cw_e25_24_hp6")
    half_22a = analyze_single("51-1/2B", source_profile="ctci_22a_5123a")
    result = analyze_single(
        "51-36B",
        overrides={"member_cut_length_mm": 420},
        source_profile="ctci_22a_5123a",
    )

    assert not half.error
    assert half.meta["issue_summary"]["highest_severity"] == "high"
    assert not half.meta["fabrication"]["bom_ready"]
    assert half_22a.error
    assert half_22a.entries == []
    assert not result.error
    assert "D-91 reinforcing pad" in result.meta["fabrication"]["not_furnished"]
    assert all(entry.geometry.component_id != "D91-REINFORCING-PAD-REFERENCE"
               for entry in result.entries)
    assert result.entries[0].geometry.parameters["saddle_contact_angle_deg"] == 120
    assert result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]


def test_type56_keeps_only_the_small_plate_as_exact_and_blocks_invented_breakdowns():
    small = analyze_single("56-2B", source_profile="cw_e25_24_hp6")
    plate_assembly = analyze_single("56-3B", source_profile="cw_e25_24_hp6")
    h_cut = analyze_single("56-5B", source_profile="cw_e25_24_hp6")
    large = analyze_single("56-26B", source_profile="cw_e25_24_hp6")

    assert small.meta["fabrication"]["fabrication_ready"]
    assert (_entry(small, "D67-PL100-PIPE-STOPS").length,
            _entry(small, "D67-PL100-PIPE-STOPS").quantity) == (100, 2)
    assert all(not result.meta["fabrication"]["bom_ready"]
               for result in (plate_assembly, h_cut, large))
    assert _entry(plate_assembly, "D67-3-MEMBER-C-ASSEMBLY").unit_weight == 0
    assert _entry(h_cut, "D67-5-MEMBER-C-ASSEMBLY").unit_weight == 0
    assert _entry(large, "D67-26-MEMBER-C-ASSEMBLY").unit_weight == 0
    assert _entry(large, "D67A-D91-REINFORCING-PAD").unit_weight == 0


def test_type57_20e_stainless_uses_one_m26_set_and_bwg21_shim():
    result = analyze_single("57-2B-A(S)", source_profile="ctci_20e4588")

    assert not result.error
    assembly = _entry(result, "D68-U-BOLT-ASSEMBLY")
    shim = _entry(result, "D68-SS-SHIM-PLATE")
    assert (assembly.name, assembly.quantity, assembly.material) == (
        "U-BOLT ASSEMBLY", 1, "Stainless Steel",
    )
    assert (shim.length, shim.width, shim.spec) == (101, 30, "0.8128")
    assert shim.geometry.parameters["gauge"] == "BWG #21"
    assert (shim.geometry.holes.count, shim.geometry.holes.pitch_x,
            shim.geometry.holes.diameter) == (2, 71, 12)
    assert all(entry.name != "FINISHED HEX NUT" for entry in result.entries)


def test_type57_20e_quarter_inch_keeps_table_row_but_blocks_source_conflict():
    result = analyze_single("57-1/4B-A", source_profile="ctci_20e4588")

    assert not result.error
    assert [entry.geometry.component_id for entry in result.entries] == [
        "D68-U-BOLT-ASSEMBLY",
    ]
    assert not result.meta["fabrication"]["bom_ready"]
    assert any("1/4" in blocker for blocker in result.meta["fabrication"]["blockers"])


def test_type58_requires_figure_and_uses_d69_m26_material_truth():
    missing_fig = analyze_single("58-4B", source_profile="cw_e25_24_hp6")
    result = analyze_single("58-4B-B", source_profile="cw_e25_24_hp6")

    assert missing_fig.error
    assert not result.error
    plate = _entry(result, "D69-U-BOLT-PLATE")
    rod = _entry(result, "D69-M26-U-BOLT-ROD")
    nuts = _entry(result, "D69-M26-FINISHED-HEX-NUTS")
    assert plate.material == "Carbon Steel (grade not specified in D-69)"
    assert rod.material == "CARBON STEEL (GRADE NOT SPECIFIED IN M-26)"
    assert rod.length == pytest.approx(3.141592653589793 * 116 / 2 + 2 * 108)
    assert rod.unit_weight > 0
    assert nuts.quantity == 4
    assert nuts.unit_weight > 0
    assert not result.meta["fabrication"]["bom_ready"]
    assert result.meta["fabrication"]["installation"]["fig_b_fillet_weld_mm"] == 5


def test_type59_includes_d68_and_20e_profile_specific_interfaces():
    cw_b = analyze_single("59-6B-B", source_profile="cw_e25_24_hp6")
    ctci_too_large = analyze_single("59-14B-B", source_profile="ctci_20e4588")
    ctci_pending = analyze_single("59-6B-B(S)", source_profile="ctci_20e4588")
    ctci_no_pad = analyze_single(
        "59-6B-B(S)",
        overrides={"reinforcing_pad_required": False},
        source_profile="ctci_20e4588",
    )
    ctci_a = analyze_single("59-6B-A", source_profile="ctci_20e4588")
    ctci_a_large = analyze_single("59-14B-A", source_profile="ctci_20e4588")

    assert not cw_b.error
    assert [entry.geometry.component_id for entry in cw_b.entries] == [
        "D70-DETAIL-Z-LUG",
        "D70-D68-M26-U-BOLT-ROD",
        "D70-D68-M26-FINISHED-HEX-NUTS",
    ]
    assert not cw_b.meta["fabrication"]["bom_ready"]
    assert _entry(cw_b, "D70-D68-M26-U-BOLT-ROD").unit_weight > 0
    assert ctci_too_large.error
    assert not ctci_pending.meta["fabrication"]["bom_ready"]
    assert not ctci_no_pad.meta["fabrication"]["fabrication_ready"]
    assert _entry(ctci_a, "D70-20E-L40-INTERFACE").quantity == 2
    assert ctci_a.meta["fabrication"]["not_furnished"] == ["D-80 pipe shoe"]
    assert _entry(ctci_a_large, "D70-20E-6T-INTERFACE-PLATES").unit_weight == 0
    assert not ctci_a_large.meta["fabrication"]["bom_ready"]


def test_type59_cw_large_stainless_borrows_12t_as_high_risk():
    result = analyze_single("59-14B-B(S)", source_profile="cw_e25_24_hp6")

    assert not result.error
    lug = _entry(result, "D70-DETAIL-Z-LUG")
    assert (lug.material, lug.spec, lug.quantity) == ("A240-304", "12", 2)
    assert result.meta["issue_summary"]["highest_severity"] == "high"
    assert not result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert any("暫借碳鋼T=12mm" in warning for warning in result.warnings)


def test_type60_fig_a_has_two_base_and_four_wing_plates():
    result = analyze_single("60-20B-A", source_profile="cw_e25_24_hp6")

    assert not result.error
    base = _entry(result, "D71-SIDE-BASE-PLATES")
    wings = _entry(result, "D71-FIG-A-WING-PLATES")
    assert (base.length, base.width, base.spec, base.quantity) == (120, 340, "12", 2)
    assert (wings.length, wings.width, wings.spec, wings.quantity) == (200, 120, "12", 4)
    assert base.material == wings.material == "A283 Gr.C"
    assert result.meta["fabrication"]["bom_ready"]
    assert not result.meta["fabrication"]["fabrication_ready"]
    assert result.meta["fabrication"]["not_furnished"] == ["D-80 / D-80B pipe shoe"]


def test_type60_fig_b_keeps_exact_base_but_blocks_undimensioned_wing_contact():
    result = analyze_single("60-20B-B", source_profile="cw_e25_24_hp6")

    assert not result.error
    base = _entry(result, "D71-SIDE-BASE-PLATES")
    wings = _entry(result, "D71-FIG-B-WING-PLATES")
    assert (base.length, base.width, base.quantity) == (150, 260, 2)
    assert wings.quantity == 4
    assert wings.unit_weight == 0
    assert wings.geometry.parameters["pipe_contact_angle_deg"] == 120
    assert wings.geometry.parameters["upper_angle_deg"] == 45
    assert not result.meta["fabrication"]["bom_ready"]
    assert result.meta["fabrication"]["not_furnished"] == []


@pytest.mark.parametrize(
    ("designation", "profile"),
    [
        ("46-8B-C100-1000 A", "ctci_22a_5123a"),
        ("48-2B", "ctci_20e4588"),
        ("49-4A", "ctci_22a_5123a"),
        ("56-2B", "ctci_20e4588"),
        ("58-4B-A", "ctci_22a_5123a"),
        ("60-20B-A", "ctci_20e4588"),
    ],
)
def test_types_without_source_drawings_are_gated(designation, profile):
    result = analyze_single(designation, source_profile=profile)

    assert result.error
    assert "尚未完成" in result.error
    assert result.entries == []
