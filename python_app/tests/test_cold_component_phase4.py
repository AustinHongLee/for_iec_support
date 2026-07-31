import math

import pytest

from core.calculator import analyze_single
from data.cold_interface_tables import (
    get_n11_by_size,
    get_n13_component,
    get_n14_component,
    get_n15_by_cradle,
    get_n16_by_cradle,
    resolve_n19_designation,
)
from data.component_table_registry import get_component_table_coverage


def _entry(result, component_id):
    return next(
        entry
        for entry in result.entries
        if entry.geometry.component_id == component_id
    )


def _has_component(result, component_id):
    return any(
        entry.geometry.component_id == component_id
        for entry in result.entries
    )


def _type_parameters(result):
    return next(
        entry.geometry.parameters
        for entry in result.entries
        if entry.geometry.shape_kind == "cold_support_assembly_reference"
    )


def test_n11_transcribes_dimensions_loads_and_sf5_values():
    small = get_n11_by_size("EB-1/4")
    large = get_n11_by_size('7/8"')
    decimal = get_n11_by_size(0.625)

    assert (
        small["overall_length_mm"],
        small["thread_length_mm"],
        small["r_c_hole_depth_mm"],
    ) == (76, 19, 32)
    assert (
        large["source_tensile_loading_kg"],
        large["source_shear_loading_kg"],
    ) == (5629, 8400)
    assert large["design_shear_at_sf5_kg"] == 1680
    assert decimal["designation"] == "EB-5/8"
    assert get_n11_by_size("1in") is None


def test_n11_keeps_the_n9_revision_conflict_visible():
    row = get_n11_by_size("5/8")

    assert row["n9_grout_lower_types"] == ["B", "E", "G", "L", "M"]
    assert "no L/M" in row["source_conflict"]
    assert "A/B/E/G" in row["source_conflict"]
    assert "Type A is an N-9-only" in row["source_conflict"]


def test_n13_and_n14_preserve_distinct_clip_type_geometry():
    n13 = get_n13_component()
    n14 = get_n14_component()

    assert n13["designation"] == "CLIP TYPE 5"
    assert n13["plate_thickness_mm"] == 10
    assert n13["elevation"]["hole_count_per_plate"] == 2
    assert n13["elevation"]["support_variants"]["L75x75x9"] == {
        "free_end_depth_mm": 75,
        "top_to_hole_center_mm": 40,
        "hole_center_to_lower_edge_mm": 35,
    }
    assert n14["designation"] == "CLIP TYPE 6"
    assert n14["plate_thickness_mm"] == 12
    assert n14["elevation"]["hole_count_per_plate"] == 4
    assert n14["elevation"]["hole_pitch_vertical_mm"] == 55
    assert n14["elevation"]["support_angle_spec"] == "L130x130x12"
    assert n14["elevation"]["support_leg_depth_mm"] == 130
    assert n14["elevation"]["free_end_plate_depth_mm"] == 160
    assert n14["elevation"]["weld_mm"] == 9
    assert n14["plan"]["weld_mm"] == 8
    assert n13["plan"]["weld_mm"] == 6
    assert n13["plan"]["bolt_nominal_diameter_in"] == 0.75
    assert not n13["weight_ready"]
    assert not n14["fabrication_ready"]


def test_n15_releases_flat_development_and_weight():
    row = get_n15_by_cradle("CR8")
    expected_length = math.pi * (117 + 10 / 2) + 2 * 154
    expected_weight = expected_length * 75 * 10 * 7.85e-6

    assert row["W_outside_span_mm"] == 2 * (
        row["RG_inside_radius_mm"] + row["T_thickness_mm"]
    )
    assert row["developed_length_mm"] == pytest.approx(expected_length)
    assert row["calculated_weight_kg"] == pytest.approx(expected_weight)
    assert row["weight_ready"]
    assert row["flat_pattern_ready"]
    assert not row["fabrication_ready"]
    assert get_n15_by_cradle("CR14") is None


def test_n16_keeps_component_dimensions_separate_and_calculates_known_steel():
    cr14 = get_n16_by_cradle("CR14")
    cr40 = get_n16_by_cradle("CR40")

    assert (
        cr14["RG_inside_radius_mm"],
        cr14["H_to_attachment_reference_mm"],
        cr14["straight_leg_length_mm"],
        cr14["W_outside_span_mm"],
    ) == (187, 214, 224, 398)
    assert cr14["member_M"]["spec"] == "L65x65x6"
    assert cr14["member_M"]["length_each_mm"] == 130
    assert cr40["member_M"]["spec"] == "C180x75x7x10.5"
    assert cr40["member_M"]["length_each_mm"] == 290
    assert cr40["developed_length_mm"] == pytest.approx(
        math.pi * (524 + 25 / 2) + 2 * (551 + 10)
    )
    assert cr40["known_steel_weight_kg"] > 80
    assert cr40["band_weight_ready"]
    assert not cr40["weight_ready"]
    assert not cr40["fabrication_ready"]


def test_n19_decodes_all_four_dimension_pairs_without_inventing_ptfe():
    row = resolve_n19_designation("SLP-A-5347-4715")

    assert (
        row["upper_plate"]["A_length_mm"],
        row["upper_plate"]["B_width_mm"],
    ) == (530, 470)
    assert (
        row["ptfe_slide_element"]["L_length_mm"],
        row["ptfe_slide_element"]["W_width_mm"],
    ) == (470, 150)
    assert (
        row["lower_backing_plate"]["outside_length_mm"],
        row["lower_backing_plate"]["outside_width_mm"],
    ) == (494, 174)
    assert row["ptfe_slide_element"]["thickness_mm"] is None
    assert row["ptfe_slide_element"]["derivable_thickness_mm"] == 2.8
    assert "N-19 Note calls L/W" in row["source_conflict"]
    assert row["known_metal_weight_kg"] > 0
    assert not row["weight_ready"]
    assert resolve_n19_designation("SLP-A-534-4715") is None


def test_type17_keeps_host_c24_row_and_n16_row_both_true():
    result = analyze_single("17C-A-CR14-8B-G")
    host = _type_parameters(result)["source_rows"]["cradle"]
    component = _entry(result, "N-16-U-BAND").geometry.parameters
    cr26_result = analyze_single("17C-B-CR26-20B-G")
    cr26_host = _type_parameters(cr26_result)["source_rows"]["cradle"]
    cr26_component = _entry(
        cr26_result,
        "N-16-U-BAND",
    ).geometry.parameters

    assert not result.error
    assert not cr26_result.error
    assert host["H_mm"] == 224
    assert component["H_to_attachment_reference_mm"] == 214
    assert component["straight_leg_length_mm"] == 224
    assert host["RG_mm"] == component["RG_inside_radius_mm"] == 187
    assert cr26_host["H_mm"] == 360
    assert cr26_component["H_to_attachment_reference_mm"] == 370
    assert cr26_component["straight_leg_length_mm"] == 380
    assert result.total_weight == pytest.approx(8.99)


@pytest.mark.parametrize(
    ("designation", "band_id", "bolt_quantity"),
    (
        ("17C-A-CR8-4B-G", "N-15-U-BAND", None),
        ("17C-A-CR25-18B-G", "N-16-U-BAND", 2),
        ("17C-B-CR40-24B-G", "N-16-U-BAND", 4),
    ),
)
def test_type17_selects_n15_n16_and_host_bolt_quantity(
    designation,
    band_id,
    bolt_quantity,
):
    result = analyze_single(designation)

    assert not result.error
    assert _has_component(result, band_id)
    assert result.total_weight > 0
    if bolt_quantity is None:
        assert not _has_component(result, "N-16-MACHINE-BOLTS")
    else:
        fastener = _entry(
            result,
            "N-16-MACHINE-BOLTS",
        )
        assert fastener.quantity == bolt_quantity
        assert fastener.geometry.parameters[
            "quantity_status"
        ] == "provisional_host_callout"
        assert "Section V-V" in fastener.geometry.parameters[
            "source_conflict"
        ]


def test_n9_b_e_g_receive_n11_but_j_is_not_silently_mapped():
    lower_b = analyze_single("09C-2B-12B")
    lower_e = analyze_single("08C-14B-12E")
    lower_g = analyze_single("07C-2B-12G")
    lower_j = analyze_single("08C-14B-12J")

    assert _entry(lower_b, "N-11").geometry.parameters[
        "designation"
    ] == "EB-5/8"
    assert _entry(lower_e, "N-11").geometry.parameters[
        "designation"
    ] == "EB-3/4"
    assert _entry(lower_g, "N-11").quantity == 4
    assert not _has_component(lower_j, "N-11")
    assert any("omits J" in warning for warning in lower_j.warnings)


def test_type114_selects_n13_or_n14_from_the_host_branch():
    small = analyze_single("114C-A-CR9-4B-500")
    large = analyze_single("114C-A-CR20-14B-700")
    n13 = _entry(small, "N-13")
    n14 = _entry(large, "N-14")

    assert not small.error
    assert not large.error
    assert n13.geometry.parameters["plate_thickness_mm"] == 10
    assert n13.geometry.parameters["host_parameters"]["B_mm"] == 140
    assert n14.geometry.parameters["plate_thickness_mm"] == 12
    assert n14.geometry.parameters["elevation"][
        "hole_count_per_plate"
    ] == 4


def test_type116_fig_a_gets_n13_but_other_figures_do_not():
    figure_a = analyze_single("116C-A-CR8-1B-500A")
    figure_b = analyze_single("116C-A-CR8-1B-500B")
    figure_c = analyze_single("116C-A-CR8-1B-500C")

    assert not figure_a.error
    assert not figure_b.error
    assert not figure_c.error
    assert _has_component(figure_a, "N-13")
    assert _has_component(figure_b, "N-12")
    assert _has_component(figure_b, "N-28")
    assert _entry(figure_b, "C-63-STUD-BOLTS").quantity == 4
    assert _entry(figure_b, "C-63-STUD-BOLT-NUTS").quantity == 8
    assert _entry(figure_b, "C-63-STUD-BOLTS").material == (
        "ASTM A193 Gr.B8"
    )
    params = _type_parameters(figure_b)
    assert params["resolved_components"]["selection"][
        "polyurethane_density_kg_m3"
    ] == 320
    assert not _has_component(figure_c, "N-13")
    assert not _has_component(figure_c, "N-12")


def test_component_registry_promotes_final_six_cold_sheets():
    coverage = get_component_table_coverage()

    assert coverage["lookup_ready"] == 60
    assert coverage["partial_lookup"] == 3
    assert coverage["metadata_only"] == 8
