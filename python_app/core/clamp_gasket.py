"""Shared M-4 pipe-clamp and M-47 gasket BOM builders."""

from __future__ import annotations

from .component_roles import ComponentRole
from .component_rules import component_or_estimated_clamp_weight
from .material_specs import (
    CLAMP_BODY_A36_SS400,
    COLD_SHOE_INSULATION_CLAMP_M47,
)
from .models import AnalysisEntry, AnalysisResult, set_remark
from data.m4_table import build_m4_item
from data.m47_table import build_m47_item


def add_m4_pipe_clamp_entry(
    result: AnalysisResult,
    line_size: float,
) -> None:
    clamp_item = build_m4_item(line_size)
    unit_weight = component_or_estimated_clamp_weight(
        clamp_item,
        line_size,
        component_id="M-4",
    )
    spec = (
        clamp_item["designation"]
        if clamp_item
        else f'TYPE-A {line_size:g}"'
    )

    entry = AnalysisEntry(
        name="PIPE CLAMP",
        spec=spec,
        material=CLAMP_BODY_A36_SS400.name,
        quantity=1,
        unit_weight=unit_weight,
        total_weight=unit_weight,
        unit="SET",
        factor=1,
        qty_subtotal=1,
        weight_output=unit_weight,
        weight_per_unit=unit_weight,
        category="管夾類",
        role=ComponentRole.CLAMP.value,
    )
    entry.material_canonical_id = CLAMP_BODY_A36_SS400.canonical_id
    if clamp_item:
        set_remark(
            entry,
            f'參見 M-4，螺桿徑={clamp_item["rod_size_a"]}；重量為估算值',
            f'SEE M-4, rod {clamp_item["rod_size_a"]}; weight estimated',
        )
        if not clamp_item.get("weight_ready"):
            result.warnings.append(
                "M-4 clamp 無 source unit-weight 欄，PIPE CLAMP 重量使用集中估算規則"
            )
    else:
        set_remark(
            entry,
            "M-4 查表失敗；重量依集中規則估算",
            "M-4 lookup failed; weight estimated by core.component_rules",
        )
        result.warnings.append(
            "M-4 table lookup failed，PIPE CLAMP 重量使用集中估算規則"
        )
    result.add_entry(entry)


def add_m47_gasket_entry(
    result: AnalysisResult,
    line_size: float,
) -> None:
    gasket_item = build_m47_item(line_size)
    if gasket_item is None:
        raise ValueError(f'M-47 不支援 {line_size:g}" gasket')

    width = gasket_item["width_mm"]
    length = gasket_item["length_mm"]
    thickness = gasket_item["thickness_mm"]
    weight = gasket_item["unit_weight_kg"]
    entry = AnalysisEntry(
        name="NON-ASBESTOS",
        spec=f"{width}×{length}×{thickness:g}t",
        material=COLD_SHOE_INSULATION_CLAMP_M47.name,
        quantity=1,
        unit_weight=weight,
        total_weight=weight,
        unit="PC",
        factor=1,
        length=length,
        width=width,
        qty_subtotal=1,
        weight_output=weight,
        weight_per_unit=weight,
        category="墊片類",
        role=ComponentRole.GASKET.value,
        remark=gasket_item["thickness_source"],
    )
    entry.material_canonical_id = (
        COLD_SHOE_INSULATION_CLAMP_M47.canonical_id
    )
    result.add_entry(entry)
    if gasket_item.get("thickness_inferred"):
        result.warnings.append(
            "M-47 gasket 長寬已查表，但厚度仍為既有集中推論值，發包前需核原始 M-47"
        )
