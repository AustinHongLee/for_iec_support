"""
鋼材處理模組 - 對應 VBA: C_鋼材處理
"""
from .models import AnalysisEntry, AnalysisResult
from .hardware_material import MaterialSpec
from .material_identity import canonical_material_id
from data.steel_sections import get_section_weight


_DEFAULT_STEEL_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.steel.default_material",
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


def add_steel_section_entry(result: AnalysisResult, section_type: str,
                            section_dim: str, total_length: float,
                            steel_qty: int = 1, material: str | MaterialSpec = ""):
    """
    新增鋼材項目到結果
    對應 VBA: AddSteelSectionEntry
    """
    material_name, canonical_id = _material_name_and_identity(
        material,
        default=_DEFAULT_STEEL_MATERIAL,
    )

    weight_per_m = get_section_weight(section_type, section_dim)

    entry = AnalysisEntry()
    entry.name = section_type
    entry.spec = section_dim
    entry.length = total_length
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = steel_qty
    entry.weight_per_unit = weight_per_m
    entry.unit_weight = round(total_length / 1000 * weight_per_m, 2)
    entry.total_weight = round(entry.unit_weight * entry.quantity, 2)
    entry.unit = "M"
    entry.factor = 1
    entry.length_subtotal = round(entry.factor * total_length / 1000 * entry.quantity, 3)
    entry.qty_subtotal = entry.factor * entry.quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = "管路類"

    result.add_entry(entry)
