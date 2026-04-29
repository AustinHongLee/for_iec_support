"""
Pipe Clamp shared builders.

Component table rule:
- Raw PDF/source values must live in each component file (`m4_table.py`,
  `m5_table.py`, `m6_table.py`, `m7_table.py`).
- This common module only normalizes rows and provides lookup/build helpers.
"""
from __future__ import annotations

from copy import deepcopy

from .component_size_utils import normalize_fractional_size, size_to_float
from .pipe_table import get_pipe_od


EXTRA_PIPE_OD = {
    '1 1/4"': 42.2,
    '3 1/2"': 101.6,
}


def _pipe_od_for_line_size(line_size: str) -> float:
    pipe_od_mm = EXTRA_PIPE_OD.get(line_size)
    if pipe_od_mm is not None:
        return pipe_od_mm
    return get_pipe_od(size_to_float(line_size))


def build_clamp_table(raw_rows: list[dict], *, type_label: str, source_component: str) -> dict:
    """Normalize a component-owned raw clamp table into lookup rows."""
    table = {}
    for row in raw_rows:
        line_size = normalize_fractional_size(row["line_size"])
        item = deepcopy(row)
        item.setdefault("type", item.get("designation", ""))
        item.setdefault("designation", item["type"])
        item["type_label"] = type_label
        item["source_component"] = source_component
        item["line_size"] = line_size
        item.setdefault("pipe_od_mm", _pipe_od_for_line_size(line_size))
        item.setdefault("load_650f_kg", 0)
        item.setdefault("load_750f_kg", 0)
        item.setdefault("source_transcribed", False)
        item.setdefault("weight_ready", False)
        item.setdefault("weight_status", "estimated_no_source_weight_column")
        item.setdefault("set_weight_kg", item.get("estimated_set_weight_kg"))
        item.setdefault("set_weight_is_estimated", not item.get("weight_ready", False))
        if item.get("set_weight_kg") is None:
            item.setdefault("half_weight_kg", None)
        else:
            item.setdefault("half_weight_kg", round(item["set_weight_kg"] / 2, 2))
        table[line_size] = item
    return table


def get_clamp_by_line_size(table: dict, line_size) -> dict | None:
    row = table.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None


def get_clamp_by_type(table: dict, clamp_type: str) -> dict | None:
    for row in table.values():
        if row["type"] == clamp_type or row["designation"] == clamp_type:
            return deepcopy(row)
    return None


def build_clamp_item(table: dict, line_size) -> dict | None:
    row = get_clamp_by_line_size(table, line_size)
    if not row:
        return None
    return row
