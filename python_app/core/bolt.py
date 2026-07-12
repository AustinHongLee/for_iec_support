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

    entry = AnalysisEntry()
    entry.name = "EXP.BOLT"
    entry.spec = bolt_size
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = quantity
    entry.unit_weight = 1  # 預設每組重量 1 kg
    entry.total_weight = entry.unit_weight * quantity
    entry.unit = "SET"
    entry.factor = 1
    entry.qty_subtotal = entry.factor * quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = "螺栓類"
    entry.role = ComponentRole.EXPANSION_BOLT.value
    entry.item_class = item_class_for(entry.role, category=entry.category)
    entry.manufacturing_type = manufacturing_type_for(entry.role, category=entry.category)

    result.add_entry(entry)


def add_custom_entry(result: AnalysisResult, name: str, spec: str,
                     material: str | MaterialSpec, quantity: int, unit_weight: float,
                     unit: str = "SET", remark: str = "", category: str = "螺栓類",
                     role: str = "", item_class: str = "", manufacturing_type: str = ""):
    """新增自訂項目 (Machine Bolt, Washer, Spring 等)"""
    material_name, canonical_id = _material_name_and_identity(material)
    inferred_role = role or role_from_legacy_name(name).value
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

    result.add_entry(entry)
