"""
鋼板處理模組 - 對應 VBA: C_鋼板處理

Phase 1 變更 (2026-04-29):
  - add_plate_entry 現在填 entry.role + entry.geometry.holes
  - bolt 螺孔資訊改寫進 HolePattern，不再拼 remark 字串
  - remark 仍保留（向後相容），但螺孔資訊雙寫進 geometry.holes
  - 呼叫方可透過 plate_role 參數指定 ComponentRole，預設 GENERIC_PLATE
"""
from .models import AnalysisEntry, AnalysisResult, HolePattern, GeometryHints
from .component_roles import ComponentRole, item_class_for, manufacturing_type_for
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
    "A283 Gr.C": 7.85,
    "A516-60": 7.85,
    "A387-22": 7.85,
    "SUS304": 7.93,
    "A240-304": 7.93,
    "AS": 7.82,
}


def resolve_plate_density(material_name: str) -> tuple[float, str, bool]:
    """
    Return the legacy plate density together with its evidence state.

    Unknown labels retain 7.85 g/cm³ so existing BOM totals do not change
    silently, but the result is marked review-required rather than drawing truth.
    """
    if material_name in MATERIAL_DENSITY:
        return (
            MATERIAL_DENSITY[material_name],
            f"core.plate.MATERIAL_DENSITY[{material_name}]",
            False,
        )
    return 7.85, "core.plate.legacy_unverified_default_7_85", True


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
    shape_spec: str = "",           # 放樣/裁切用完整規格，例如 "150x100x25x50x12t"
    shape_kind: str = "",           # 輪廓分類，例如 "wing"
    gross_area_mm2: float = 0,       # 毛坯/外接矩形面積
    cutout_area_mm2: float = 0,      # 扣除面積
    net_area_mm2: float = 0,         # 實際算重淨面積；0 時採 plate_a × plate_b
    item_class: str = "",            # 主結構 / 加工品 / 配件語意；空白時依板件類別推導
    manufacturing_type: str = "",    # 製造方式；空白時依板件類別/shape_kind 推導
):
    """
    新增鋼板項目到結果
    對應 VBA: MainAddPlate

    新參數（Phase 1）:
      plate_role  — ComponentRole 的值字串，預設從 plate_name legacy 推導
      formula     — 長度公式追溯（例如 "H - 15"）
      notes_zh    — 中文備註（取代 remark 字串拼裝）
      shape_spec  — 放樣/裁切用完整規格；空白時採 length × width × thickness
      shape_kind  — 輪廓分類；供 part key / CAD / procurement 管控
      net_area_mm2 — 非矩形板實際算重面積；空白時採 plate_a × plate_b
      item_class / manufacturing_type — 採購/製造語意層；空白時依板件類別推導
    """
    material_name, canonical_id = _material_name_and_identity(
        material,
        default=_DEFAULT_PLATE_MATERIAL,
    )

    density, density_source, density_requires_review = resolve_plate_density(
        material_name
    )
    gross_area = gross_area_mm2 or plate_a * plate_b
    weight_area = net_area_mm2 or gross_area
    weight = weight_area * plate_thickness * density / 1_000_000

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
        shape_spec=shape_spec,
        shape_kind=shape_kind,
        gross_area_mm2=gross_area,
        cutout_area_mm2=cutout_area_mm2,
        net_area_mm2=weight_area,
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
    entry.item_class = item_class or item_class_for("", category=entry.category)
    entry.manufacturing_type = (
        manufacturing_type
        or manufacturing_type_for(
            "",
            category=entry.category,
            shape_kind=shape_kind,
        )
    )
    entry.density_g_cm3 = density
    entry.density_source = density_source
    entry.density_requires_review = density_requires_review
    entry.remark = remark           # 向後相容保留
    entry.role = resolved_role      # Phase 1 新增
    entry.geometry = geometry       # Phase 1 新增

    result.add_entry(entry)
