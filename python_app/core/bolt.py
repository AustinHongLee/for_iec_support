"""
螺栓處理模組 - 對應 VBA: D_螺栓處理 + X_M42底板程序 的 AddBoltEntry
"""
from .models import AnalysisEntry, AnalysisResult
from .component_roles import (
    ComponentRole,
    item_class_for,
    manufacturing_type_for,
    role_from_legacy_name,
)
from .hardware_material import MaterialSpec
from .fastener_weight import (
    estimate_fastener,
    fastener_density_for_material,
)
from .material_identity import canonical_material_id
from data.m42_table import resolve_m42_data
from .parser import get_lookup_value


_DEFAULT_EXP_BOLT_MATERIAL = MaterialSpec(
    name="SUS304",
    canonical_id=canonical_material_id("SUS304") or "UNRESOLVED_SUS304",
    source="core.bolt.default_exp_bolt_material",
    requires_review=True,
)


def _material_name_and_identity(
    material: str | MaterialSpec | None,
    *,
    default: MaterialSpec | None = None,
) -> tuple[str, str | None]:
    if isinstance(material, MaterialSpec):
        return material.name, material.canonical_id
    if material is None or material == "":
        if default is not None:
            return default.name, default.canonical_id
        return "", None
    return str(material), None


def add_bolt_entry(
    result: AnalysisResult,
    pipe_size,
    quantity: int,
    material: str | MaterialSpec | None = None,
):
    """
    新增螺栓項目到結果
    對應 VBA: AddBoltEntry
    pipe_size 可以是數字(管徑)或含"*"的型鋼字串
    """
    material_name, canonical_id = _material_name_and_identity(
        material,
        default=_DEFAULT_EXP_BOLT_MATERIAL,
    )
    s = str(pipe_size)
    if "*" in s or "x" in s:
        m42, warning = resolve_m42_data(s)
    else:
        size_val = get_lookup_value(pipe_size)
        m42, warning = resolve_m42_data(size_val)
    if warning and warning not in result.warnings:
        result.warnings.append(warning)
    bolt_size = m42["exp_bolt_spec"]
    estimate = estimate_fastener(
        bolt_size,
        kind="expansion_bolt",
        density_kg_per_mm3=fastener_density_for_material(material_name),
    )
    unit_weight = float(estimate["unit_weight_kg"]) if estimate else 0.0

    entry = AnalysisEntry()
    entry.name = "EXP.BOLT"
    entry.spec = bolt_size
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = quantity
    entry.unit_weight = unit_weight
    entry.total_weight = entry.unit_weight * quantity
    entry.unit = "SET"
    entry.factor = 1
    entry.qty_subtotal = entry.factor * quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = "螺栓類"
    entry.role = ComponentRole.EXPANSION_BOLT.value
    entry.item_class = item_class_for(entry.role, category=entry.category)
    entry.manufacturing_type = manufacturing_type_for(entry.role, category=entry.category)
    entry.remark = (
        "依名義直徑／長度理論估重，供應商成品重量待確認"
        if estimate
        else "圖面只有扣件直徑、未給長度；不再套用舊有1 kg/組假預設"
    )
    entry.geometry.shape_kind = "purchased_expansion_bolt"
    entry.geometry.shape_spec = bolt_size
    entry.geometry.parameters = {
        "spec": bolt_size,
        "quantity": quantity,
        "weight_estimate": estimate,
    }
    entry.geometry.fabrication_ready = True
    if estimate:
        entry.length = float(estimate["nominal_length_mm"])
        entry.density_g_cm3 = float(estimate["density_kg_per_mm3"]) * 1e6
        entry.density_source = "core.fastener_weight.nominal_geometry_estimate"
        entry.density_requires_review = True

    result.add_entry(entry)


def add_custom_entry(result: AnalysisResult, name: str, spec: str,
                     material: str | MaterialSpec, quantity: int, unit_weight: float,
                     unit: str = "SET", remark: str = "", category: str = "螺栓類",
                     role: str = "", item_class: str = "", manufacturing_type: str = ""):
    """新增自訂項目 (Machine Bolt, Washer, Spring 等).

    Dimensioned straight fasteners that still arrive with ``unit_weight=0``
    are given the shared theoretical MTO estimate.  U-bolts are deliberately
    excluded because their mass must use the developed U geometry, not the
    straight-bolt nominal length.
    """
    material_name, canonical_id = _material_name_and_identity(material)
    inferred_role = role or role_from_legacy_name(name).value
    estimate = None
    if float(unit_weight or 0) == 0 and inferred_role in {
        ComponentRole.EXPANSION_BOLT.value,
        ComponentRole.MACHINE_BOLT.value,
        ComponentRole.K_BOLT.value,
    }:
        weight_kind = (
            "expansion_bolt"
            if inferred_role == ComponentRole.EXPANSION_BOLT.value
            else "machine_bolt_with_nut"
        )
        estimate = estimate_fastener(
            spec,
            kind=weight_kind,
            density_kg_per_mm3=fastener_density_for_material(material_name),
        )
        if estimate:
            unit_weight = float(estimate["unit_weight_kg"])
            estimate_note = (
                f"理論估重 {unit_weight:.3f} kg/{unit}；"
                "依名義直徑×長度與比例化扣件幾何，供應商成品重量待確認"
            )
            remark = "；".join(
                value
                for value in (str(remark or "").strip(), estimate_note)
                if value
            )
    entry = AnalysisEntry()
    entry.name = name
    entry.spec = spec
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = quantity
    entry.unit_weight = unit_weight
    entry.total_weight = round(unit_weight * quantity, 2)
    entry.unit = unit
    entry.factor = 1
    entry.qty_subtotal = entry.factor * quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = category
    entry.remark = remark
    if inferred_role != ComponentRole.UNKNOWN.value:
        entry.role = inferred_role
    entry.item_class = item_class or item_class_for(entry.role, category=entry.category)
    entry.manufacturing_type = (
        manufacturing_type
        or manufacturing_type_for(entry.role, category=entry.category)
    )
    if estimate:
        entry.length = float(estimate["nominal_length_mm"])
        entry.density_g_cm3 = float(estimate["density_kg_per_mm3"]) * 1e6
        entry.density_source = (
            "core.fastener_weight.nominal_geometry_estimate"
        )
        entry.density_requires_review = True
        entry.geometry.parameters["weight_estimate"] = estimate

    result.add_entry(entry)


def add_estimated_fastener_entry(
    result: AnalysisResult,
    *,
    name: str,
    spec: str,
    material: str | MaterialSpec,
    quantity: int,
    kind: str | None = None,
    unit: str = "SET",
    remark: str = "",
    role: str = "",
):
    """Add a dimensioned fastener with a traceable theoretical MTO weight."""

    normalized_name = str(name or "").upper()
    normalized_spec = str(spec or "").upper()
    inferred_role = role or role_from_legacy_name(name).value
    if kind:
        weight_kind = kind
    elif (
        inferred_role == ComponentRole.EXPANSION_BOLT.value
        or "擴展" in name
        or "EXPANSION" in normalized_name
        or normalized_spec.startswith("EB")
    ):
        weight_kind = "expansion_bolt"
    elif "基礎" in name or "ANCHOR" in normalized_name:
        weight_kind = "foundation_bolt"
    else:
        weight_kind = "machine_bolt_with_nut"

    estimate = estimate_fastener(
        spec,
        kind=weight_kind,
        density_kg_per_mm3=fastener_density_for_material(material),
    )
    unit_weight = float(estimate["unit_weight_kg"]) if estimate else 0.0
    estimate_note = (
        f"理論估重 {unit_weight:.3f} kg/{unit}；"
        "依名義直徑×長度與比例化扣件幾何，供應商成品重量確認後應覆蓋"
        if estimate
        else "規格沒有完整直徑×長度，無法建立可追溯扣件估重"
    )
    combined_remark = "；".join(
        value for value in (str(remark or "").strip(), estimate_note) if value
    )
    add_custom_entry(
        result,
        name,
        spec,
        material,
        quantity,
        unit_weight,
        unit=unit,
        remark=combined_remark,
        category="螺栓類",
        role=inferred_role,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    entry = result.entries[-1]
    entry.geometry.shape_kind = (
        "purchased_expansion_bolt"
        if weight_kind == "expansion_bolt"
        else "purchased_foundation_bolt"
        if weight_kind == "foundation_bolt"
        else "purchased_machine_bolt_with_nut"
    )
    entry.geometry.shape_spec = str(spec)
    entry.geometry.parameters = {
        "spec": spec,
        "quantity": quantity,
        "weight_estimate": estimate,
    }
    entry.geometry.fabrication_ready = True
    if estimate:
        entry.length = float(estimate["nominal_length_mm"])
        entry.density_g_cm3 = float(estimate["density_kg_per_mm3"]) * 1e6
        entry.density_source = "core.fastener_weight.nominal_geometry_estimate"
        entry.density_requires_review = True
    return entry
