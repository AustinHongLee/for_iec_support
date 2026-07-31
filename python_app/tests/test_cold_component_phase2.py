import pytest

from core.calculator import analyze_single
from data.cold_support_core_tables import (
    get_cradle_candidates,
    get_cradle_selection,
    get_n1_dimensions,
    get_n2_layer_system,
    get_n3_construction,
    get_n4_shield,
    get_n5_material_properties,
    resolve_cradle_designation,
)
from data.component_table_registry import get_component_table_coverage


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def _core(result):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.shape_kind == "cold_support_core_lookup"
    ).geometry.parameters["resolved_components"]


def test_n1_keeps_small_and_large_overlap_t1_separate():
    small = get_n1_dimensions("CR41", 24)
    large = get_n1_dimensions("CR41", 30)

    assert small["R_mm"] == 520
    assert small["T1_mm"] == 12
    assert "A_mm" not in small
    assert large["T1_mm"] == 10
    assert large["A_mm"] == 706
    assert large["B_mm"] == 12
    assert get_n1_dimensions("CR32", 26) is None


def test_n2_n3_resolve_layer_and_axial_rules_without_weight_guess():
    layer = get_n2_layer_system(150)
    construction = get_n3_construction(150, 300)

    assert (
        layer["inner_layer_mm"],
        layer["middle_layer_mm"],
        layer["outer_layer_mm"],
    ) == (50, 50, 50)
    assert construction["construction_type"] == (
        "three_layer_requires_project_detail"
    )
    assert construction["jacket_length_mm"] == 400
    assert construction["foam_and_vapor_barrier_length_mm"] == 450
    assert construction["inner_layer_foam_length_mm"] == 500
    assert not construction["weight_ready"]


def test_n4_and_n5_source_values_are_exact_lookups():
    shield = get_n4_shield("CR40", 300)
    material = get_n5_material_properties(320)

    assert shield["R_mm"] == 509
    assert shield["T2_mm"] == 5.0
    assert shield["axial_length_mm"] == 300
    assert material["load_at_yield_lb"] == 14600
    assert material["engineering_strength_sf5_kg_cm2"] == 18.59
    assert material["sustainable_load_formula"] == "C * (pi * D * L) / 6"


def test_n20_n23_small_pipe_selection_rows_and_source_blank():
    n20 = get_cradle_selection(0.5, 25)
    n23 = get_cradle_selection(20, 265)

    assert n20["component_id"] == "N-20"
    assert n20["cradle_no"] == "CR2.5"
    assert (n20["F_mm"], n20["H_mm"]) == (39, 79)
    assert n20["max_allowable_load_kg"] == 125
    assert n23["component_id"] == "N-23"
    assert n23["cradle_no"] == "CR41"
    assert (n23["F_mm"], n23["H_mm"]) == (532, 572)
    assert get_cradle_selection(24, 265) is None


def test_n24_n26_large_pipe_selection_rows():
    n24 = get_cradle_selection(30, 25)
    n26 = get_cradle_selection(60, 200)

    assert n24["component_id"] == "N-24"
    assert n24["cradle_no"] == "CR32"
    assert (n24["F_mm"], n24["H_mm"]) == (417, 509)
    assert n24["max_allowable_load"] == 49050
    assert n24["max_allowable_load_unit"] == "source_conflict"
    assert n24["max_allowable_load_source_sheet_unit_label"] == "kg"
    assert n24["max_allowable_load_kg"] is None
    assert n24["max_allowable_load_lb"] is None
    assert "N-24 labels" in n24["source_conflict"]
    assert n26["component_id"] == "N-26"
    assert n26["cradle_no"] == "CR76"
    assert (n26["F_mm"], n26["H_mm"]) == (977, 1067)
    assert n26["polyurethane_density_kg_m3"] == 320
    assert n26["max_allowable_load_source_sheet_unit_label"] == "lb"


def test_n24_n26_all_90_source_cradle_cells_are_locked():
    expected = {
        25: (32, 38, 44, 50, 56, 62),
        40: (33, 39, 45, 51, 57, 63),
        50: (34, 40, 46, 52, 58, 64),
        65: (35, 41, 47, 53, 59, 65),
        75: (36, 42, 48, 54, 60, 66),
        90: (37, 43, 49, 55, 61, 67),
        100: (38, 44, 50, 56, 62, 68),
        115: (39, 45, 51, 57, 63, 69),
        125: (40, 46, 52, 58, 64, 70),
        140: (41, 47, 53, 59, 65, 71),
        150: (42, 48, 54, 60, 66, 72),
        165: (43, 49, 55, 61, 67, 73),
        175: (44, 50, 56, 62, 68, 74),
        190: (45, 51, 57, 63, 69, 75),
        200: (46, 52, 58, 64, 70, 76),
    }
    sizes = (30, 36, 42, 48, 54, 60)

    actual = {
        thickness: tuple(
            int(get_cradle_selection(size, thickness)["cradle_no"][2:])
            for size in sizes
        )
        for thickness in expected
    }

    assert actual == expected


def test_reverse_lookup_preserves_the_only_cr_pipe_ambiguity():
    candidates = get_cradle_candidates("CR12", 1.5)
    unresolved = resolve_cradle_designation("CR12", 1.5)
    resolved = resolve_cradle_designation(
        "CR12",
        1.5,
        insulation_thickness_mm=140,
    )

    assert [row["insulation_thickness_mm"] for row in candidates] == [
        125,
        140,
    ]
    assert not unresolved["selection_resolved"]
    assert unresolved["insulation_thickness_mm"] is None
    assert resolved["selection_resolved"]
    assert resolved["insulation_thickness_mm"] == 140


def test_type11_unique_selection_resolves_full_cold_core():
    result = analyze_single("11C-A-CR12-8B")
    core = _core(result)

    assert not result.error
    assert core["selection"]["insulation_thickness_mm"] == 50
    assert core["selection"]["F_mm"] == 168
    assert core["N-1"]["T1_mm"] == 5
    assert core["N-2"]["inner_layer_mm"] == 50
    assert core["N-3"]["cradle_length_L_mm"] == 300
    assert core["N-3"]["jacket_length_mm"] == 400
    assert core["N-4"]["T2_mm"] == 1.6
    assert core["N-5"]["density_kg_m3"] == 224


def test_type11_ambiguous_selection_requires_override_for_layers():
    unresolved = analyze_single("11C-A-CR12-1.1/2B")
    resolved = analyze_single(
        "11C-A-CR12-1.1/2B",
        overrides={"insulation_thickness_mm": 140},
    )
    invalid = analyze_single(
        "11C-A-CR12-1.1/2B",
        overrides={"insulation_thickness_mm": 1250},
    )

    unresolved_core = _core(unresolved)
    resolved_core = _core(resolved)
    assert not unresolved.error
    assert not unresolved_core["selection"]["selection_resolved"]
    assert unresolved_core["N-2"] is None
    assert resolved_core["selection"]["insulation_thickness_mm"] == 140
    assert resolved_core["N-2"]["inner_layer_mm"] == 65
    assert resolved_core["N-2"]["middle_layer_mm"] == 75
    assert invalid.error
    assert "原圖候選為 [125, 140]" in invalid.error


def test_type13_and_type121_cross_validate_large_cradle_rows():
    type13 = analyze_single("13C-B-CR32-30B")
    type121 = analyze_single("121C-A-CR32-30B-G")

    assert not type13.error
    assert not type121.error
    assert _core(type13)["selection"]["insulation_thickness_mm"] == 25
    selection = _core(type121)["selection"]
    assert selection["max_allowable_load"] == 49050
    assert selection["max_allowable_load_unit"] == "source_conflict"
    assert _entry(
        type121,
        "C70-MEMBER-Q-GUIDES",
    ).geometry.parameters["H_mm"] == 509


def test_type22_rejects_cr_pipe_pair_not_listed_in_n20_to_n23():
    invalid = analyze_single("22C-A-CR9-8B-500")
    valid = analyze_single("22C-A-CR10-8B-500")

    assert invalid.error
    assert not valid.error
    assert _core(valid)["selection"]["insulation_thickness_mm"] == 25


def test_type119_keeps_host_range_but_marks_unlisted_n20_size_unresolved():
    result = analyze_single("119C-CR12-2.1/2B")
    assembly = _entry(result, "C67-TYPE119C-ASSEMBLY")

    assert not result.error
    selection = assembly.geometry.parameters["resolved_components"][
        "selection"
    ]
    assert not selection["lookup_ready"]
    assert "N-20~N-23 exact cradle row unresolved" in " ".join(
        result.warnings
    )


def test_unlisted_host_pipe_does_not_bypass_n1_cradle_family():
    result = analyze_single("116C-A-CR80-2.1/2B-500A")

    assert result.error
    assert "N-20~N-26 無 CR80/2.5in 原圖組合" in result.error


@pytest.mark.parametrize(
    (
        "designation",
        "assembly_id",
        "source_sheet",
        "insulation",
        "f_mm",
        "expected_b_mm",
    ),
    (
        (
            "114C-A-CR9-2B-500",
            "C57-C59-TYPE114C-ASSEMBLY",
            "N-21",
            90,
            127,
            None,
        ),
        (
            "115C-ACR9-6B-800",
            "C60-C61-TYPE115C-ASSEMBLY",
            "N-20",
            40,
            127,
            140,
        ),
        (
            "116C-A-CR8-1B-500A",
            "C62-C63-TYPE116C-FIG-A",
            "N-21",
            90,
            114,
            None,
        ),
        (
            "120C-A-CR4-2B-1/2-2000-A",
            "C68-TYPE120C-FIG-A",
            "N-20",
            25,
            60,
            None,
        ),
    ),
)
def test_type114_to_120_custom_hosts_resolve_the_same_cold_core_truth(
    designation,
    assembly_id,
    source_sheet,
    insulation,
    f_mm,
    expected_b_mm,
):
    result = analyze_single(designation)
    assembly = _entry(result, assembly_id)
    selection = assembly.geometry.parameters["resolved_components"][
        "selection"
    ]

    assert not result.error
    assert selection["component_id"] == source_sheet
    assert selection["insulation_thickness_mm"] == insulation
    assert selection["F_mm"] == f_mm
    assert _core(result)["selection"] == selection
    if expected_b_mm is not None:
        assert assembly.geometry.parameters["dimension_B_mm"] == expected_b_mm


def test_component_registry_promotes_twelve_cold_core_sheets():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["partial_lookup"] == 3
    assert coverage["metadata_only"] == 8
