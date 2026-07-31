import pytest

from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows


def _pipe_entry(result):
    return next(entry for entry in result.entries if entry.category == "管路類")


def test_pipe_quantity_subtotal_matches_single_support_quantity():
    result = analyze_single(
        "01-2B-05A",
        source_profile="cw_e25_24_hp6",
    )

    assert not result.error
    pipe = _pipe_entry(result)
    assert pipe.qty_subtotal == pipe.quantity * pipe.factor == 1
    assert pipe.weight_output == pytest.approx(pipe.factor * pipe.total_weight)


def test_pipe_quantity_subtotal_scales_once_at_project_layer():
    project = analyze_project_rows(
        [ProjectInputRow("01-2B-05A", quantity=3)],
        source_profile="cw_e25_24_hp6",
    )

    assert not project.errors
    row = project.rows[0]
    single_pipe = _pipe_entry(row.single_result)
    scaled_pipe = _pipe_entry(row.scaled_result)
    aggregate_pipe = next(
        entry
        for entry in project.aggregated_entries
        if entry.category == "管路類"
    )

    assert single_pipe.qty_subtotal == 1
    assert scaled_pipe.quantity == 3
    assert scaled_pipe.qty_subtotal == 3
    assert aggregate_pipe.quantity == 3
    assert aggregate_pipe.qty_subtotal == 3
    assert scaled_pipe.weight_output == pytest.approx(
        single_pipe.weight_output * 3
    )


def test_plate_density_evidence_distinguishes_table_value_from_legacy_fallback():
    exact = analyze_single(
        "60-20B-A",
        source_profile="cw_e25_24_hp6",
    )
    unresolved = analyze_single(
        "48-2B(B)",
        source_profile="cw_e25_24_hp6",
    )

    assert not exact.error
    assert not unresolved.error
    exact_plate = next(
        entry for entry in exact.entries if entry.category == "鋼板類"
    )
    unresolved_plate = next(
        entry for entry in unresolved.entries if entry.category == "鋼板類"
    )

    assert exact_plate.material == "A283 Gr.C"
    assert exact_plate.density_g_cm3 == pytest.approx(7.85)
    assert not exact_plate.density_requires_review
    assert "MATERIAL_DENSITY" in exact_plate.density_source

    assert unresolved_plate.material == "Stainless Steel"
    assert unresolved_plate.density_g_cm3 == pytest.approx(7.85)
    assert unresolved_plate.density_requires_review
    assert "unverified" in unresolved_plate.density_source
