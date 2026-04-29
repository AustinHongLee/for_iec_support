"""
Project-level BOM aggregation wrapper.

This module is deliberately outside Type calculators. Quantity belongs to the
project layer: each row is calculated as one support, scaled on a deep copy, and
then aggregated for project-level material statistics.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable

from .calculator import analyze_single
from .models import AnalysisEntry, AnalysisResult


@dataclass(frozen=True)
class ProjectInputRow:
    """One project row: a support designation plus project quantity."""

    designation: str
    quantity: int = 1
    enabled: bool = True
    overrides: dict | None = None


@dataclass
class ProjectRowResult:
    """Single project row result, preserving both original and scaled outputs."""

    input_row: ProjectInputRow
    single_result: AnalysisResult
    scaled_result: AnalysisResult
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ProjectAnalysisResult:
    """Project-level analysis suitable for material summary and procurement."""

    rows: list[ProjectRowResult] = field(default_factory=list)
    aggregated_entries: list[AnalysisEntry] = field(default_factory=list)
    total_weight: float = 0.0
    total_support_count: int = 0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _validate_quantity(quantity: int) -> None:
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError(f"Project quantity must be a positive integer: {quantity!r}")


def scale_analysis_result(result: AnalysisResult, quantity: int) -> AnalysisResult:
    """
    Return a scaled deep copy of a single-support AnalysisResult.

    The original result is never modified. Descriptive fields such as material,
    designation, remarks, meta, and evidence are preserved as-is.
    """
    _validate_quantity(quantity)

    scaled = deepcopy(result)
    if result.error:
        return scaled

    for entry in scaled.entries:
        entry.quantity *= quantity
        entry.qty_subtotal *= quantity
        entry.length_subtotal *= quantity
        entry.weight_output *= quantity

        # Excel export still reads total_weight, so keep the scaled copy internally
        # consistent without changing unit_weight / weight_per_unit semantics.
        entry.total_weight *= quantity

    return scaled


def _entry_key(entry: AnalysisEntry) -> tuple:
    """
    Project aggregation key.

    It intentionally excludes support designation. Dimensions are included so
    different plate sizes do not collapse into one procurement row.
    """
    return (
        entry.name,
        entry.spec,
        round(entry.length or 0.0, 4),
        round(entry.width or 0.0, 4),
        entry.material,
        getattr(entry, "material_canonical_id", ""),
        entry.unit,
        entry.category,
        entry.remark,
    )


def _copy_entry_for_aggregation(entry: AnalysisEntry) -> AnalysisEntry:
    aggregate = deepcopy(entry)
    aggregate.item_no = 0
    return aggregate


def aggregate_scaled_results(results: list[AnalysisResult]) -> list[AnalysisEntry]:
    """Merge scaled AnalysisResult entries into project-level BOM entries."""
    merged: dict[tuple, AnalysisEntry] = {}

    for result in results:
        if result.error:
            continue

        for entry in result.entries:
            key = _entry_key(entry)
            aggregate = merged.get(key)
            if aggregate is None:
                merged[key] = _copy_entry_for_aggregation(entry)
                continue

            aggregate.quantity += entry.quantity
            aggregate.qty_subtotal += entry.qty_subtotal
            aggregate.length_subtotal += entry.length_subtotal
            aggregate.total_weight += entry.total_weight
            aggregate.weight_output += entry.weight_output

    entries = sorted(
        merged.values(),
        key=lambda entry: (
            entry.category,
            entry.name,
            entry.spec,
            round(entry.length or 0.0, 4),
            round(entry.width or 0.0, 4),
            entry.material,
            getattr(entry, "material_canonical_id", ""),
            entry.unit,
            entry.remark,
        ),
    )
    for index, entry in enumerate(entries, start=1):
        entry.item_no = index
    return entries


def analyze_project_rows(
    rows: list[ProjectInputRow],
    *,
    calculate_type: Callable[[str, dict | None], AnalysisResult] = analyze_single,
) -> ProjectAnalysisResult:
    """
    Analyze quantity-aware project rows without modifying Type calculators.

    Disabled rows are skipped. Enabled rows are counted toward total support
    count even if the underlying single calculation returns an error.
    """
    project = ProjectAnalysisResult()
    scaled_results: list[AnalysisResult] = []

    for row in rows:
        if not row.enabled:
            continue

        _validate_quantity(row.quantity)
        project.total_support_count += row.quantity

        single_result = calculate_type(row.designation, row.overrides or None)
        scaled_result = scale_analysis_result(single_result, row.quantity)

        row_errors = []
        if single_result.error:
            row_errors.append(f"{row.designation}: {single_result.error}")

        row_warnings = [f"{row.designation}: {warning}" for warning in single_result.warnings]

        project.rows.append(
            ProjectRowResult(
                input_row=row,
                single_result=single_result,
                scaled_result=scaled_result,
                errors=row_errors,
                warnings=row_warnings,
            )
        )
        project.errors.extend(row_errors)
        project.warnings.extend(row_warnings)
        scaled_results.append(scaled_result)

    project.aggregated_entries = aggregate_scaled_results(scaled_results)
    project.total_weight = sum(entry.weight_output for entry in project.aggregated_entries)
    return project
