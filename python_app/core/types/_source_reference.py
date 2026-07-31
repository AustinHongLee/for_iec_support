"""Small helpers for source-backed partial fabrication calculators."""

from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult, set_remark


def add_reference(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: str,
    quantity: int,
    category: str,
    component_id: str,
    drawing: str,
    revision: str,
    shape_kind: str,
    parameters: dict,
    blocker: str,
    manufacturing_type: str = "not_furnished",
):
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        0,
        "SET" if quantity == 1 else "PC",
        remark=blocker,
        category=category,
        item_class="reference_only",
        manufacturing_type=manufacturing_type,
    )
    entry = result.entries[-1]
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = shape_kind
    entry.geometry.shape_spec = spec
    entry.geometry.parameters = parameters
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)
    return entry


def retire_entry_weight(entry, *, blocker: str) -> None:
    """Keep source dimensions but retire an unproven finished-part weight."""
    entry.weight_per_unit = 0
    entry.unit_weight = 0
    entry.total_weight = 0
    entry.weight_output = 0
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, blocker)
