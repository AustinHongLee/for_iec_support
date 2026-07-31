"""Material-BOM inclusion helpers for unresolved drawing references."""

from __future__ import annotations

from copy import deepcopy

from .models import AnalysisEntry, AnalysisResult


def exclude_unresolved_entry(
    result: AnalysisResult,
    entry: AnalysisEntry,
    *,
    reason: str,
) -> dict:
    """Remove an unresolved zero-value placeholder from the material BOM.

    The source callout is retained in structured result metadata, so the
    missing item remains auditable without appearing as a real 0 mm / 0 kg
    procurement row.
    """

    record = {
        "component_id": entry.geometry.component_id,
        "name": entry.name,
        "spec": entry.spec,
        "material": entry.material,
        "quantity": entry.quantity,
        "unit": entry.unit,
        "category": entry.category,
        "role": entry.role,
        "source_drawing": entry.geometry.source_drawing,
        "source_revision": entry.geometry.source_revision,
        "shape_kind": entry.geometry.shape_kind,
        "shape_spec": entry.geometry.shape_spec,
        "parameters": deepcopy(entry.geometry.parameters),
        "reason": reason,
        "excluded_from_material_bom": True,
    }
    result.meta.setdefault("excluded_bom_components", []).append(record)
    result.entries.remove(entry)
    for index, remaining in enumerate(result.entries, start=1):
        remaining.item_no = index
    return record


def scale_entry_quantity(entry: AnalysisEntry, multiplier: int) -> None:
    """Scale one physical BOM item while preserving its unit semantics."""

    if multiplier <= 0:
        raise ValueError("BOM quantity multiplier must be positive")
    entry.quantity *= multiplier
    entry.qty_subtotal *= multiplier
    entry.length_subtotal *= multiplier
    entry.total_weight *= multiplier
    entry.weight_output *= multiplier
