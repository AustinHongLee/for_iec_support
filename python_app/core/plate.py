"""
鋼板處理模組 - 對應 VBA: C_鋼板處理
"""
from .models import AnalysisEntry, AnalysisResult
from .hardware_material import MaterialSpec


# 材質密度 (g/cm³ -> t/m³)
MATERIAL_DENSITY = {
    "A36/SS400": 7.85,
    "SUS304": 7.93,
    "AS": 7.82,
}


def _material_name_and_identity(material: str | MaterialSpec) -> tuple[str, str | None]:
    if isinstance(material, MaterialSpec):
        return material.name, material.canonical_id
    return str(material), None


def add_plate_entry(result: AnalysisResult, plate_a: float, plate_b: float,
                    plate_thickness: float, plate_name: str,
                    material: str | MaterialSpec = "", plate_qty: int = 1,
                    bolt_switch: bool = False,
                    bolt_x: float = 0, bolt_y: float = 0,
                    bolt_hole: float = 0, bolt_size: str = ""):
    """
    新增鋼板項目到結果
    對應 VBA: MainAddPlate
    """
    material_name, canonical_id = _material_name_and_identity(material)
    if not material_name:
        material_name = "A36/SS400"

    density = MATERIAL_DENSITY.get(material_name, 7.85)
    weight = plate_a / 1000 * plate_b / 1000 * plate_thickness * density

    remark = ""
    if bolt_switch:
        remark = f"{plate_a}x{plate_b}x{plate_thickness}[{bolt_x}x{bolt_y}]_{bolt_hole}%{bolt_size}"

    entry = AnalysisEntry()
    entry.name = plate_name
    entry.spec = str(plate_thickness)
    entry.length = plate_a
    entry.width = plate_b
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = plate_qty
    entry.unit_weight = round(weight, 2)
    entry.total_weight = round(weight * plate_qty, 2)
    entry.unit = "PC"
    entry.factor = 1
    entry.qty_subtotal = entry.factor * plate_qty
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = "鋼板類"
    entry.remark = remark

    result.add_entry(entry)
