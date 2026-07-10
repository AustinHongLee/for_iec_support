"""PENETRATION HOLE: project-scoped opening reinforcement MTO calculator."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from ..models import AnalysisEntry, AnalysisResult, GeometryHints
from ..component_roles import ComponentRole, item_class_for, manufacturing_type_for
from ..penetration_hole import build_item_code, parse_insulation
from ..parser import get_lookup_value
from ..truth import apply_truth_contract, make_evidence
from data.pipe_table import get_pipe_od

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "configs" / "type_penetration_hole.json"


@lru_cache(maxsize=1)
def _rules() -> dict:
    with _CONFIG_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def _round_up(value: float, increment_mm: float) -> float:
    return float(int((value + increment_mm - 0.000001) // increment_mm) * increment_mm)


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    overrides = overrides or {}
    result = AnalysisResult(fullstring=fullstring)
    rules = _rules()
    flat_bar = rules["flat_bar"]
    nominal_size = overrides.get("nominal_size") or overrides.get("pipe_size")
    if not nominal_size:
        result.error = "PENETRATION HOLE 缺少 nominal_size（管徑），無法計算開孔"
        return result

    try:
        line_size = get_lookup_value(str(nominal_size))
        od_mm = get_pipe_od(line_size)
        insulation_mm, insulation_label = parse_insulation(overrides.get("insulation"))
    except ValueError as exc:
        result.error = f"PENETRATION HOLE 輸入無效: {exc}"
        return result

    hole_size_mm = _round_up(od_mm + 2 * insulation_mm, float(rules["rounding_mm"])) + float(rules["opening_clearance_mm"])
    flat_bar_length_mm = hole_size_mm * 4
    weight_per_m = (
        float(flat_bar["width_mm"])
        * float(flat_bar["thickness_mm"])
        * float(flat_bar["density_kg_per_mm3"])
        * 1000
    )
    item_code = build_item_code(nominal_size, insulation_label)

    entry = AnalysisEntry(
        name="FB50×6 開孔補強",
        spec="FB50×6",
        length=flat_bar_length_mm,
        material=str(flat_bar["material"]),
        quantity=1,
        weight_per_unit=round(weight_per_m, 3),
        unit_weight=round(flat_bar_length_mm / 1000 * weight_per_m, 3),
        total_weight=round(flat_bar_length_mm / 1000 * weight_per_m, 3),
        unit="M",
        factor=1,
        length_subtotal=round(flat_bar_length_mm / 1000, 3),
        qty_subtotal=1,
        weight_output=round(flat_bar_length_mm / 1000 * weight_per_m, 3),
        category="型鋼類",
        role=ComponentRole.OPENING_REINFORCEMENT.value,
        geometry=GeometryHints(
            formula="ROUNDUP(OD + 2×保溫厚度, -1) + 50；FB50×6 = 開孔大小×4",
            notes_zh=(
                f"{item_code}；OD={od_mm:g}mm，保溫={insulation_mm:g}mm，"
                f"開孔={hole_size_mm:g}mm"
            ),
        ),
        part_key=f"penetration_hole_{item_code.replace(chr(34), '').replace('/', '_')}",
    )
    entry.item_class = item_class_for(entry.role, category=entry.category)
    entry.manufacturing_type = manufacturing_type_for(entry.role, category=entry.category)
    result.add_entry(entry)

    result.evidence = [
        make_evidence("nominal_size", nominal_size, "rule", source="rule", confidence=1.0),
        make_evidence("pipe_od_mm", od_mm, "standard_table", source="standard_table", confidence=1.0),
        make_evidence("insulation_mm", insulation_mm, "rule", source="rule", confidence=1.0),
        make_evidence("opening_size_mm", hole_size_mm, "formula", source="formula", confidence=1.0),
        make_evidence("fb50x6_length_mm", flat_bar_length_mm, "formula", source="formula", confidence=1.0),
    ]
    return apply_truth_contract(result, type_id="PENETRATION HOLE")
