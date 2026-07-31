import math

import pytest

from core.calculator import analyze_single
from data.component_table_registry import get_component_table_coverage
from data.m3_table import M3_TABLE, get_m3_by_line_size
from data.m31_table import M31_TABLE, get_m31_by_rod_size
from data.m33_table import M33_TABLE, get_m33_by_line_size
from data.m8_table import M8_TABLE, get_m8_by_line_size
from data.m9_table import M9_TABLE, get_m9_by_line_size
from data.m10_table import M10_TABLE, get_m10_by_line_size


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def test_m3_transcribes_all_adjustable_clevis_rows():
    four = get_m3_by_line_size("4B")
    thirty = get_m3_by_line_size(30)

    assert len(M3_TABLE) == 21
    assert four["designation"] == "ADC-4B"
    assert four["maximum_recommended_load_kg"] == 650
    assert (
        four["upper_steel_thickness_mm"],
        four["upper_steel_width_mm"],
        four["lower_steel_thickness_mm"],
        four["lower_steel_width_mm"],
    ) == (6, 32, 5, 32)
    assert (
        four["A_rod_size_in"],
        four["B_inside_width_mm"],
        four["C_overall_height_mm"],
        four["D_top_to_pipe_center_mm"],
        four["E_cross_bolt_to_pipe_center_mm"],
        four["F_adjustment_mm"],
        four["G_cross_bolt_diameter_in"],
    ) == ('5/8"', 141, 198, 89, 114, 49, '3/8"')
    assert thirty["designation"] == "ADC-30B"
    assert thirty["maximum_recommended_load_kg"] == 2725
    assert thirty["C_overall_height_mm"] == 994
    assert not thirty["weight_ready"]
    assert not thirty["fabrication_ready"]
    assert get_m3_by_line_size(7) is None


def test_m31_uses_square_blank_minus_center_hole_weight():
    row = get_m31_by_rod_size("5/8")
    expected_area = 76**2 - math.pi * 19**2 / 4

    assert len(M31_TABLE) == 17
    assert row["designation"] == "SWP-5/8"
    assert row["net_area_mm2"] == pytest.approx(expected_area)
    assert row["calculated_net_weight_kg"] == pytest.approx(
        expected_area * 9 * 7.85e-6
    )
    assert row["blank_weight_ready"]
    assert row["weight_ready"]
    assert not row["fabrication_ready"]


def test_m31_preserves_the_source_3_1_2_inch_d75_anomaly():
    row = get_m31_by_rod_size('3 1/2"')

    assert row["C_square_side_mm"] == 178
    assert row["D_hole_diameter_mm"] == 75
    assert any(
        "non-monotonic" in note
        for note in row["source_anomalies"]
    )
    assert get_m31_by_rod_size('1 1/8"') is None


def test_m33_transcribes_exact_lug_rows_without_fake_weight():
    twelve = get_m33_by_line_size(12)
    twenty = get_m33_by_line_size(20)

    assert len(M33_TABLE) == 12
    assert (
        twelve["designation"],
        twelve["B_hanger_rod_size_in"],
        twelve["C_mm"],
        twelve["D_mm"],
        twelve["E_mm"],
        twelve["K_mm"],
        twelve["R_mm"],
        twelve["T_thickness_mm"],
        twelve["S_weld_size_mm"],
        twelve["maximum_recommended_load_kg"],
    ) == ("LGP-B-12B", '7/8"', 180, 90, 305, 28, 40, 12, 6, 1700)
    assert (
        twenty["B_hanger_rod_size_in"],
        twenty["T_thickness_mm"],
        twenty["S_weld_size_mm"],
        twenty["maximum_recommended_load_kg"],
    ) == ('1 1/8"', 16, 9, 4500)
    assert not twenty["weight_ready"]
    assert not twenty["fabrication_ready"]
    assert get_m33_by_line_size(5) is None


def test_type62_fig_a_e_uses_real_m31_and_m3_rows():
    result = analyze_single(
        "62-4B-5/8-05A-E",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert [
        entry.geometry.component_id
        for entry in result.entries
    ] == ["M-22", "M-31", "M-3"]
    washer = _entry(result, "M-31")
    clevis = _entry(result, "M-3")
    assert washer.unit_weight == pytest.approx(
        get_m31_by_rod_size("5/8")["calculated_net_weight_kg"]
    )
    assert washer.geometry.parameters["D_hole_diameter_mm"] == 19
    assert clevis.spec.startswith("ADC-4B")
    assert clevis.geometry.parameters["maximum_recommended_load_kg"] == 650
    assert clevis.unit_weight == 0
    assert not result.meta["fabrication"]["bom_ready"]
    assert {
        "MACH. THREADED ROD",
        "ADJUSTABLE CLEVIS",
    }.issubset(
        result.meta["fabrication"]["excluded_weight_scope"]
    )


def test_type62_m31_does_not_reuse_carbon_density_for_noncarbon_override():
    result = analyze_single(
        "62-4B-5/8-05A-E",
        source_profile="cw_e25_24_hp6",
        overrides={"hardware_material": "INCONEL"},
    )
    washer = _entry(result, "M-31")

    assert not result.error
    assert washer.material == "INCONEL"
    assert washer.unit_weight == 0
    assert not washer.geometry.parameters[
        "weight_uses_source_carbon_density"
    ]
    assert any(
        "non-carbon material/density" in blocker
        for blocker in washer.geometry.fabrication_blockers
    )


def test_type62_m3_and_m33_enforce_source_rod_selection():
    wrong_m3 = analyze_single(
        "62-4B-3/4-05A-E",
        source_profile="cw_e25_24_hp6",
    )
    wrong_m33 = analyze_single(
        "62-12B-1-05A-Q",
        source_profile="cw_e25_24_hp6",
    )

    assert wrong_m3.error
    assert 'ADC-4B原表要求 rod 5/8"' in wrong_m3.error
    assert wrong_m33.error
    assert 'LGP-B-12B原表要求 rod 7/8"' in wrong_m33.error
    assert not wrong_m3.entries
    assert not wrong_m33.entries


def test_type62_fig_q_uses_real_m33_dimensions_but_excludes_its_weight():
    result = analyze_single(
        "62-12B-7/8-05A-Q",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    assert [
        entry.geometry.component_id
        for entry in result.entries
    ] == ["M-22", "M-31", "M-24", "M-33"]
    lug = _entry(result, "M-33")
    assert lug.spec.startswith("LGP-B-12B")
    assert lug.geometry.parameters["E_mm"] == 305
    assert lug.geometry.parameters["S_weld_size_mm"] == 6
    assert lug.unit_weight == 0
    assert lug.geometry.fabrication_blockers
    assert not result.meta["fabrication"]["bom_ready"]


def test_type62_never_converts_assembly_h_to_rod_cut_implicitly():
    unresolved = analyze_single(
        "62-4B-5/8-05~30A-E",
        source_profile="cw_e25_24_hp6",
    )
    released = analyze_single(
        "62-4B-5/8-05~30A-E",
        source_profile="cw_e25_24_hp6",
        overrides={"rod_cut_length_mm": 850},
    )

    unresolved_rod = _entry(unresolved, "M-22")
    released_rod = _entry(released, "M-22")
    assert unresolved_rod.unit_weight == 0
    assert "CUT LENGTH TO BE CONFIRMED" in unresolved_rod.spec
    assert unresolved_rod.geometry.parameters["rod_cut_length_mm"] is None
    assert released_rod.spec == "MTR-5/8-850"
    assert released_rod.unit_weight > 0
    assert released_rod.geometry.fabrication_ready
    assert released.meta["fabrication"]["assembly_dimensions"][
        "rod_cut_length_mm"
    ] == 850


def test_type62_keeps_ctci_20e4588_behind_the_source_gate():
    result = analyze_single(
        "62-4B-M16-05~30D-P(T)",
        source_profile="ctci_20e4588",
    )

    assert result.error
    assert "尚未完成" in result.error
    assert "避免誤套中威基準" in result.error
    assert not result.entries


def test_m8_transcribes_all_type_e_dimensions_and_hot_loads():
    one_and_half = get_m8_by_line_size('1 1/2"')
    ten = get_m8_by_line_size(10)

    assert len(M8_TABLE) == 9
    assert one_and_half["designation"] == "PCL-E-1 1/2B"
    assert one_and_half[
        "maximum_recommended_load_kg_by_temperature_f"
    ] == {650: 700, 750: 635, 1000: 450, 1050: 335}
    assert (
        one_and_half["B_mm"],
        one_and_half["C_mm"],
        one_and_half["D_mm"],
        one_and_half["E_mm"],
        one_and_half["F_cross_bolt_diameter_in"],
        one_and_half["G_formed_steel_size_mm"],
        one_and_half["H_mm"],
    ) == (46, 27, 124, 105, '5/8"', "6 x 32", 60)
    assert (
        ten["designation"],
        ten["B_mm"],
        ten["F_cross_bolt_diameter_in"],
        ten["G_formed_steel_size_mm"],
        ten["H_mm"],
    ) == ("PCL-E-10B", 179, '1"', "12 x 64", 210)
    assert not ten["weight_ready"]
    assert not ten["fabrication_ready"]
    assert get_m8_by_line_size(7) is None


def test_m9_transcribes_all_type_f_dimensions_and_hot_loads():
    four = get_m9_by_line_size(4)
    sixteen = get_m9_by_line_size(16)

    assert len(M9_TABLE) == 7
    assert four["designation"] == "PCL-F-4B"
    assert four[
        "maximum_recommended_load_kg_by_temperature_f"
    ] == {750: 1710, 950: 1495, 1000: 1255, 1050: 855}
    assert (
        four["C_mm"],
        four["D_mm"],
        four["E_mm"],
        four["F_upper_cross_pin_diameter_in"],
        four["H_u_bolt_diameter_in"],
        four["K_overall_width_mm"],
    ) == (27, 98, 171, '7/8"', '1/2"', 165)
    assert (
        sixteen["designation"],
        sixteen["D_mm"],
        sixteen["E_mm"],
        sixteen["F_upper_cross_pin_diameter_in"],
        sixteen["H_u_bolt_diameter_in"],
        sixteen["K_overall_width_mm"],
    ) == ("PCL-F-16B", 311, 381, '1 1/2"', '7/8"', 499)
    assert not sixteen["weight_ready"]
    assert get_m9_by_line_size(5) is None


def test_m10_transcribes_all_type_g_dimensions_od_ranges_and_hot_loads():
    ten = get_m10_by_line_size(10)
    twenty_four = get_m10_by_line_size(24)

    assert len(M10_TABLE) == 7
    assert ten["designation"] == "PCL-G-10B"
    assert ten["used_on_od_pipe_size_in"] == {"min": 8, "max": 10}
    assert ten[
        "maximum_recommended_load_kg_by_temperature_f"
    ] == {950: 6120, 1000: 5340, 1050: 3560, 1075: 2775}
    assert (
        ten["C_mm"],
        ten["D_mm"],
        ten["E_mm"],
        ten["F_upper_cross_pin_diameter_in"],
        ten["H_u_bolt_diameter_in"],
        ten["K_overall_width_mm"],
        ten["M_upper_side_width_mm"],
    ) == (51, 232, 305, '1 1/2"', '1"', 391, 83)
    assert (
        twenty_four["used_on_od_pipe_size_in"],
        twenty_four["D_mm"],
        twenty_four["E_mm"],
        twenty_four["F_upper_cross_pin_diameter_in"],
        twenty_four["H_u_bolt_diameter_in"],
        twenty_four["K_overall_width_mm"],
        twenty_four["M_upper_side_width_mm"],
    ) == (
        {"min": 20, "max": 24},
        464,
        559,
        '2 1/4"',
        '1 3/8"',
        781,
        152,
    )
    assert not twenty_four["weight_ready"]
    assert get_m10_by_line_size(22) is None


def test_type62_fig_l_m_n_use_exact_source_rows_without_fake_weight():
    cases = (
        ("62-4B-5/8-05A-L", "M-8", "PCL-E-4B", "B_mm", 86),
        ("62-4B-5/8-05A-M", "M-9", "PCL-F-4B", "D_mm", 98),
        ("62-10B-7/8-05A-N", "M-10", "PCL-G-10B", "M_upper_side_width_mm", 83),
    )

    for designation, component_id, clamp_type, field, expected in cases:
        result = analyze_single(
            designation,
            source_profile="cw_e25_24_hp6",
        )
        clamp = _entry(result, component_id)

        assert not result.error
        assert clamp.spec.startswith(clamp_type)
        assert clamp.geometry.parameters[field] == expected
        assert clamp.unit_weight == 0
        assert clamp.geometry.fabrication_blockers
        assert not result.meta["fabrication"]["bom_ready"]
        assert component_id in result.meta["fabrication"][
            "referenced_components"
        ]


def test_type62_clamp_pin_and_u_bolt_dimensions_are_not_hanger_rod_rules():
    result_l = analyze_single(
        "62-4B-5/8-05A-L",
        source_profile="cw_e25_24_hp6",
    )
    result_m = analyze_single(
        "62-4B-5/8-05A-M",
        source_profile="cw_e25_24_hp6",
    )

    assert not result_l.error
    assert not result_m.error
    assert _entry(result_l, "M-8").geometry.parameters[
        "F_cross_bolt_diameter_in"
    ] == '3/4"'
    assert _entry(result_m, "M-9").geometry.parameters[
        "F_upper_cross_pin_diameter_in"
    ] == '7/8"'
    assert _entry(result_m, "M-9").geometry.parameters[
        "H_u_bolt_diameter_in"
    ] == '1/2"'


def test_type62_fig_l_m_n_reject_missing_rows_inside_nominal_ranges():
    results = (
        analyze_single(
            "62-7B-5/8-05A-L",
            source_profile="cw_e25_24_hp6",
        ),
        analyze_single(
            "62-5B-5/8-05A-M",
            source_profile="cw_e25_24_hp6",
        ),
        analyze_single(
            "62-22B-1-05A-N",
            source_profile="cw_e25_24_hp6",
        ),
    )

    assert all(result.error for result in results)
    assert ["M-8未表列", "M-9未表列", "M-10未表列"] == [
        next(
            token
            for token in ("M-8未表列", "M-9未表列", "M-10未表列")
            if token in result.error
        )
        for result in results
    ]
    assert all(not result.entries for result in results)


def test_type62_high_temp_clamps_use_source_material_notes():
    m8 = analyze_single(
        "62-4B-5/8-05A-L",
        source_profile="cw_e25_24_hp6",
    )
    m9 = analyze_single(
        "62-4B-5/8-05A-M",
        source_profile="cw_e25_24_hp6",
    )

    assert _entry(m8, "M-8").material == (
        "CHROME MOLYBDENUM STEEL (ASTM A387-GR.22)"
    )
    assert _entry(m8, "M-8").material_canonical_id == "ASTM_A387_GR22"
    assert _entry(m9, "M-9").material == (
        "CHROME MOLYBDENUM STEEL, EXCEPT U-BOLT WHICH IS STAINLESS STEEL"
    )
    assert _entry(m9, "M-9").material_canonical_id == (
        "COMPOSITE_CHROME_MOLY_STAINLESS_UBOLT"
    )


def test_component_registry_promotes_all_six_type62_components():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["partial_lookup"] == 3
    assert coverage["metadata_only"] == 8
