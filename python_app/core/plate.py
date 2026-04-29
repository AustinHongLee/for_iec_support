"""
鋼板處理模組 - 對應 VBA: C_鋼板處理

Phase 1 變更 (2026-04-29):
  - add_plate_entry 現在填 entry.role + entry.geometry.holes
  - bolt 螺孔資訊改寫進 HolePattern，不再拼 remark 字串
  - remark 仍保留（向後相容），但螺孔資訊雙寫進 geometry.holes
  - 呼叫方可透過 plate_role 參數指定 ComponentRole，預設 GENERIC_PLATE
"""
from .models import AnalysisEntry, AnalysisResult, HolePattern, GeometryHints
from .component_roles import ComponentRole
from .hardware_material import MaterialSpec
from .material_identity import canonical_material_id


_DEFAULT_PLATE_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.plate.default_material",
    requires_review=True,
)

MATERIAL_DENSITY = {
    "A36/SS400": 7.85,
    "SUS304": 7.93,
    "AS": 7.82,
}


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


def add_plate_entry(
    result: AnalysisResult,
    plate_a: float,
    plate_b: float,
    plate_thickness: float,
    plate_name: str,
    material: str | MaterialSpec = "",
    plate_qty: int = 1,
    bolt_switch: bool = False,
    bolt_x: float = 0,
    bolt_y: float = 0,
    bolt_hole: float = 0,
    bolt_size: str = "",
    plate_role: str = "",          # Phase 1: ComponentRole 值，例如 "lug_plate"
    formula: str = "",             # Phase 1: 長度計算公式追溯
    notes_zh: str = "",            # Phase 1: 中文備註
):
    """
    新增鋼板項目到結果
    對應 VBA: MainAddPlate

    新參數（Phase 1）:
      plate_role  — ComponentRole 的值字串，預設從 plate_name legacy 推導
      formula     — 長度公式追溯（例如 "H - 15"）
      notes_zh    — 中文備註（取代 remark 字串拼裝）
    """
    material_name, canonical_id = _material_name_and_identity(
        material,
        default=_DEFAULT_PLATE_MATERIAL,
    )

    density = MATERIAL_DENSITY.get(material_name, 7.85)
    weight = plate_a / 1000 * plate_b / 1000 * plate_thickness * density

    # ── Phase 1: 結構化螺孔資訊 ───────────────────────────────
    hole_pattern = None
    remark = ""
    if bolt_switch:
        hole_pattern = HolePattern(
            pattern="rect",
            pitch_x=bolt_x,
            pitch_y=bolt_y,
            diameter=bolt_hole,
            fastener_spec=bolt_size,
            count=4,  # 預設 4 孔；呼叫方可之後補充
        )
        # 保留舊 remark 字串（向後相容，Phase 3 後可移除）
        remark = f"{plate_a}x{plate_b}x{plate_thickness}[{bolt_x}x{bolt_y}]_{bolt_hole}%{bolt_size}"

    # ── role 推導：優先用傳入的 plate_role，否則從 name legacy map ─
    from .component_roles import role_from_legacy_name
    resolved_role = plate_role or role_from_legacy_name(plate_name).value

    geometry = GeometryHints(
        role=resolved_role,
        formula=formula,
        holes=hole_pattern,
        notes_zh=notes_zh,
    )

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
    entry.remark = remark           # 向後相容保留
    entry.role = resolved_role      # Phase 1 新增
    entry.geometry = geometry       # Phase 1 新增

    result.add_entry(entry)
