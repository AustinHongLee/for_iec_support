import pytest

from core.bolt import add_bolt_entry
from core.calculator import analyze_single
from core.fastener_weight import (
    estimate_fastener,
    estimate_u_bolt_assembly,
    estimate_metric_fastener,
    fastener_density_for_material,
    parse_fastener_diameter_length,
    parse_imperial_diameter_length,
    parse_metric_diameter_length,
    theoretical_hex_nut_weight,
)
from core.models import AnalysisResult
from core.source_profiles import EKO


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("M12x50L", (12.0, 50.0)),
        ("M16 X 60", (16.0, 60.0)),
        ("EB2-M20-130L", (20.0, 130.0)),
        ("EB2-M16x125L", (16.0, 125.0)),
    ],
)
def test_metric_fastener_parser_accepts_project_spellings(spec, expected):
    assert parse_metric_diameter_length(spec) == expected


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ('5/8"X40', (15.875, 40.0)),
        ('EB-1/2"; L=114', (12.7, 114.0)),
        ('DIA3/4"x120; A193 Gr.B8', (19.05, 120.0)),
        ('1/2"x145L', (12.7, 145.0)),
        ("1/4in x 4in EXPANSION BOLT", (6.35, 101.6)),
        ("1 3/8in x 130", (34.925, 130.0)),
    ],
)
def test_imperial_fastener_parser_converts_only_explicit_inch_lengths(
    spec,
    expected,
):
    assert parse_imperial_diameter_length(spec) == pytest.approx(expected)
    assert parse_fastener_diameter_length(spec) == pytest.approx(expected)


def test_metric_fastener_estimate_exposes_replaceable_geometry_basis():
    machine = estimate_metric_fastener(
        "M12x50L W./WASHER",
        kind="machine_bolt_with_nut",
    )
    expansion = estimate_metric_fastener(
        "EB2-M16-100L",
        kind="expansion_bolt",
    )

    assert machine["unit_weight_kg"] == pytest.approx(0.080)
    assert machine["washer_count"] == 1
    assert machine["components_kg"]["proportional_hex_nut"] > 0
    assert machine["requires_supplier_confirmation"]
    assert expansion["unit_weight_kg"] == pytest.approx(0.278)
    assert expansion["components_kg"]["proportional_expansion_sleeve"] > 0
    assert estimate_metric_fastener('5/8"', kind="expansion_bolt") is None


def test_imperial_fastener_estimate_uses_same_traceable_weight_model():
    machine = estimate_fastener(
        '5/8"x40',
        kind="machine_bolt_with_nut",
    )
    expansion = estimate_fastener(
        'EB-1/2"; L=114',
        kind="expansion_bolt",
    )

    assert machine["nominal_diameter_mm"] == pytest.approx(15.875)
    assert machine["nominal_length_mm"] == 40
    assert machine["unit_weight_kg"] > 0
    assert expansion["unit_weight_kg"] > 0


def test_hex_nut_estimate_scales_with_rod_diameter():
    half_inch = theoretical_hex_nut_weight(12.7)
    seven_eighth = theoretical_hex_nut_weight(22.225)

    assert half_inch == pytest.approx(0.0177663, rel=1e-4)
    assert seven_eighth > half_inch * 5


def test_u_bolt_estimator_requires_source_derived_developed_length():
    estimate = estimate_u_bolt_assembly(
        12.7,
        700,
        nut_count=2,
    )

    assert estimate["unit_weight_kg"] > 0
    assert estimate["components_kg"]["u_bolt_rod"] > 0
    assert estimate["components_kg"]["proportional_hex_nuts"] > 0
    assert estimate["nut_count"] == 2
    assert estimate_u_bolt_assembly(12.7, 0, nut_count=2) is None


def test_fastener_density_distinguishes_stainless_304_from_carbon_steel():
    carbon = fastener_density_for_material("A307-B 鍍鋅")
    stainless = fastener_density_for_material("SUS304")

    assert carbon == pytest.approx(7.85e-6)
    assert stainless == pytest.approx(7.93e-6)
    assert stainless > carbon


def test_legacy_m42_bolt_path_no_longer_invents_one_kg_per_set():
    result = AnalysisResult(fullstring="M42 legacy bolt")

    add_bolt_entry(result, 2, 4)

    entry = result.entries[0]
    assert entry.spec == '5/8"'
    assert entry.unit_weight == 0
    assert entry.weight_output == 0
    assert "不再套用舊有1 kg/組假預設" in entry.remark


def test_custom_dimensioned_bolt_gets_weight_but_ubolt_does_not_fake_it():
    result = AnalysisResult(fullstring="imperial hardware")

    from core.bolt import add_custom_entry

    add_custom_entry(
        result,
        "K BOLT",
        '5/8"x40',
        "A307-B",
        2,
        0,
        unit="PC",
    )
    add_custom_entry(
        result,
        "U-BOLT",
        '5/8"x40',
        "A307-B",
        1,
        0,
        unit="PC",
    )

    assert result.entries[0].unit_weight > 0
    assert result.entries[0].density_requires_review
    assert result.entries[1].unit_weight == 0


def test_eko_common_engines_include_dimensioned_fastener_estimates():
    machine = analyze_single("FS2B-2\"-600H-200H1", source_profile=EKO)
    expansion = analyze_single("FS2E-6\"-600H-200H1", source_profile=EKO)

    machine_bolt = next(
        entry for entry in machine.entries if entry.name == "螺栓連帽"
    )
    expansion_bolt = next(
        entry for entry in expansion.entries if entry.name == "擴展螺栓"
    )
    assert machine_bolt.spec == "M16x50L"
    assert machine_bolt.unit_weight == pytest.approx(0.154)
    assert machine_bolt.geometry.parameters["weight_estimate"][
        "kind"
    ] == "machine_bolt_with_nut"
    assert expansion_bolt.spec == "EB2-M16x125L"
    assert expansion_bolt.unit_weight > machine_bolt.unit_weight
    assert expansion_bolt.density_requires_review
