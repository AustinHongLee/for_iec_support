"""
受控詞彙：ComponentRole
=======================
所有 AnalysisEntry 的 role 欄位都應使用這裡的 enum。
好處：
  - 聚合 key 改用 (role, spec, material)，不再被命名大小寫/空格影響
  - CAD 端拿到 role 可直接對應圖庫零件
  - i18n: 顯示名稱從 ROLE_DISPLAY_NAME 推導

遷移策略：
  Phase 0 — 新 type 開始用 ComponentRole；舊 type remark 字串仍保留
  Phase 3 — 舊字串統一映射到 enum（見 LEGACY_NAME_MAP）
"""

from enum import Enum


class ComponentRole(str, Enum):
    # ── 鋼板類 ──────────────────────────────────────────────
    BASE_PLATE          = "base_plate"
    LUG_PLATE           = "lug_plate"
    SHIM_PLATE          = "shim_plate"
    COVER_PLATE         = "cover_plate"
    WING_PLATE          = "wing_plate"
    STOPPER_PLATE       = "stopper_plate"
    SIDE_PLATE          = "side_plate"
    TOP_PLATE           = "top_plate"
    SADDLE_PLATE        = "saddle_plate"
    REINFORCEMENT_PAD   = "reinforcement_pad"
    FLAT_BAR            = "flat_bar"
    GENERIC_PLATE       = "generic_plate"       # 尚未細分

    # ── 管路/型鋼 ────────────────────────────────────────────
    PIPE                = "pipe"
    COLUMN              = "column"
    TOP_BEAM            = "top_beam"
    DIAGONAL_BRACE      = "diagonal_brace"
    TRUNNION            = "trunnion"
    ANGLE               = "angle"
    CHANNEL             = "channel"
    H_SECTION           = "h_section"
    OPENING_REINFORCEMENT = "opening_reinforcement"

    # ── 螺栓/五金 ────────────────────────────────────────────
    EXPANSION_BOLT      = "expansion_bolt"
    MACHINE_BOLT        = "machine_bolt"
    K_BOLT              = "k_bolt"
    NUT                 = "nut"
    WASHER              = "washer"
    U_BOLT              = "u_bolt"

    # ── 其他 ─────────────────────────────────────────────────
    GASKET              = "gasket"
    PU_BLOCK            = "pu_block"
    CLAMP               = "clamp"
    UNKNOWN             = "unknown"             # 尚未分類


class ItemClass(str, Enum):
    """採購/製造語意層，不取代 category 或 role。"""

    PRIMARY_STRUCTURE = "primary_structure"     # 管線、型鋼主體、trunnion 等承載骨架
    FABRICATED_PART = "fabricated_part"         # 需切割、鑽孔、放樣、焊接的加工件
    ACCESSORY = "accessory"                     # 外購標準件、五金、彈簧、墊片等
    REFERENCE_ONLY = "reference_only"           # 圖面參照但不供貨/不列 BOM
    UNKNOWN = "unknown"


class ManufacturingType(str, Enum):
    """製造/取得方式。"""

    RAW_CUT = "raw_cut"                         # 管材/型鋼原料裁切
    PLATE_CUT = "plate_cut"                     # 矩形/一般板件切割
    SHAPED_PLATE = "shaped_plate"               # 異形板、需放樣輪廓
    MACHINED = "machined"                       # 孔加工、局部機加工
    PURCHASED = "purchased"                     # 外購標準件
    NOT_FURNISHED = "not_furnished"
    UNKNOWN = "unknown"


# ── 聚合類型映射 ─────────────────────────────────────────────
#   供 material_summary._classify_entry 使用
#   取代原本的字串前綴比對

ROLE_AGGREGATE_TYPE: dict[ComponentRole, str] = {
    # linear
    ComponentRole.PIPE:             "linear",
    ComponentRole.COLUMN:           "linear",
    ComponentRole.TOP_BEAM:         "linear",
    ComponentRole.DIAGONAL_BRACE:   "linear",
    ComponentRole.TRUNNION:         "linear",
    ComponentRole.ANGLE:            "linear",
    ComponentRole.CHANNEL:          "linear",
    ComponentRole.H_SECTION:        "linear",
    ComponentRole.OPENING_REINFORCEMENT: "linear",
    ComponentRole.FLAT_BAR:         "plate",   # flat bar in shoe context = discrete piece (add_plate_entry)

    # plate
    ComponentRole.BASE_PLATE:       "plate",
    ComponentRole.LUG_PLATE:        "plate",
    ComponentRole.SHIM_PLATE:       "plate",
    ComponentRole.COVER_PLATE:      "plate",
    ComponentRole.WING_PLATE:       "plate",
    ComponentRole.STOPPER_PLATE:    "plate",
    ComponentRole.SIDE_PLATE:       "plate",
    ComponentRole.TOP_PLATE:        "plate",
    ComponentRole.SADDLE_PLATE:     "plate",
    ComponentRole.REINFORCEMENT_PAD:"plate",
    ComponentRole.GENERIC_PLATE:    "plate",

    # piece
    ComponentRole.EXPANSION_BOLT:   "piece",
    ComponentRole.MACHINE_BOLT:     "piece",
    ComponentRole.K_BOLT:           "piece",
    ComponentRole.NUT:              "piece",
    ComponentRole.WASHER:           "piece",
    ComponentRole.U_BOLT:           "piece",
    ComponentRole.GASKET:           "piece",
    ComponentRole.PU_BLOCK:         "piece",
    ComponentRole.CLAMP:            "piece",
    ComponentRole.UNKNOWN:          "piece",
}


# ── 採購/製造語意映射 ───────────────────────────────────────

ROLE_ITEM_CLASS: dict[ComponentRole, ItemClass] = {
    ComponentRole.PIPE:             ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.COLUMN:           ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.TOP_BEAM:         ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.DIAGONAL_BRACE:   ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.TRUNNION:         ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.ANGLE:            ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.CHANNEL:          ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.H_SECTION:        ItemClass.PRIMARY_STRUCTURE,
    ComponentRole.OPENING_REINFORCEMENT: ItemClass.FABRICATED_PART,

    ComponentRole.FLAT_BAR:         ItemClass.FABRICATED_PART,
    ComponentRole.BASE_PLATE:       ItemClass.FABRICATED_PART,
    ComponentRole.LUG_PLATE:        ItemClass.FABRICATED_PART,
    ComponentRole.SHIM_PLATE:       ItemClass.FABRICATED_PART,
    ComponentRole.COVER_PLATE:      ItemClass.FABRICATED_PART,
    ComponentRole.WING_PLATE:       ItemClass.FABRICATED_PART,
    ComponentRole.STOPPER_PLATE:    ItemClass.FABRICATED_PART,
    ComponentRole.SIDE_PLATE:       ItemClass.FABRICATED_PART,
    ComponentRole.TOP_PLATE:        ItemClass.FABRICATED_PART,
    ComponentRole.SADDLE_PLATE:     ItemClass.FABRICATED_PART,
    ComponentRole.REINFORCEMENT_PAD:ItemClass.FABRICATED_PART,
    ComponentRole.GENERIC_PLATE:    ItemClass.FABRICATED_PART,

    ComponentRole.EXPANSION_BOLT:   ItemClass.ACCESSORY,
    ComponentRole.MACHINE_BOLT:     ItemClass.ACCESSORY,
    ComponentRole.K_BOLT:           ItemClass.ACCESSORY,
    ComponentRole.NUT:              ItemClass.ACCESSORY,
    ComponentRole.WASHER:           ItemClass.ACCESSORY,
    ComponentRole.U_BOLT:           ItemClass.ACCESSORY,
    ComponentRole.GASKET:           ItemClass.ACCESSORY,
    ComponentRole.PU_BLOCK:         ItemClass.ACCESSORY,
    ComponentRole.CLAMP:            ItemClass.ACCESSORY,
    ComponentRole.UNKNOWN:          ItemClass.UNKNOWN,
}


ROLE_MANUFACTURING_TYPE: dict[ComponentRole, ManufacturingType] = {
    ComponentRole.PIPE:             ManufacturingType.RAW_CUT,
    ComponentRole.COLUMN:           ManufacturingType.RAW_CUT,
    ComponentRole.TOP_BEAM:         ManufacturingType.RAW_CUT,
    ComponentRole.DIAGONAL_BRACE:   ManufacturingType.RAW_CUT,
    ComponentRole.TRUNNION:         ManufacturingType.RAW_CUT,
    ComponentRole.ANGLE:            ManufacturingType.RAW_CUT,
    ComponentRole.CHANNEL:          ManufacturingType.RAW_CUT,
    ComponentRole.H_SECTION:        ManufacturingType.RAW_CUT,
    ComponentRole.OPENING_REINFORCEMENT: ManufacturingType.RAW_CUT,
    ComponentRole.FLAT_BAR:         ManufacturingType.RAW_CUT,

    ComponentRole.BASE_PLATE:       ManufacturingType.PLATE_CUT,
    ComponentRole.LUG_PLATE:        ManufacturingType.PLATE_CUT,
    ComponentRole.SHIM_PLATE:       ManufacturingType.PLATE_CUT,
    ComponentRole.COVER_PLATE:      ManufacturingType.PLATE_CUT,
    ComponentRole.WING_PLATE:       ManufacturingType.PLATE_CUT,
    ComponentRole.STOPPER_PLATE:    ManufacturingType.PLATE_CUT,
    ComponentRole.SIDE_PLATE:       ManufacturingType.PLATE_CUT,
    ComponentRole.TOP_PLATE:        ManufacturingType.PLATE_CUT,
    ComponentRole.SADDLE_PLATE:     ManufacturingType.PLATE_CUT,
    ComponentRole.REINFORCEMENT_PAD:ManufacturingType.PLATE_CUT,
    ComponentRole.GENERIC_PLATE:    ManufacturingType.PLATE_CUT,

    ComponentRole.EXPANSION_BOLT:   ManufacturingType.PURCHASED,
    ComponentRole.MACHINE_BOLT:     ManufacturingType.PURCHASED,
    ComponentRole.K_BOLT:           ManufacturingType.PURCHASED,
    ComponentRole.NUT:              ManufacturingType.PURCHASED,
    ComponentRole.WASHER:           ManufacturingType.PURCHASED,
    ComponentRole.U_BOLT:           ManufacturingType.PURCHASED,
    ComponentRole.GASKET:           ManufacturingType.PURCHASED,
    ComponentRole.PU_BLOCK:         ManufacturingType.PURCHASED,
    ComponentRole.CLAMP:            ManufacturingType.PURCHASED,
    ComponentRole.UNKNOWN:          ManufacturingType.UNKNOWN,
}


CATEGORY_ITEM_CLASS: dict[str, ItemClass] = {
    "管路類": ItemClass.PRIMARY_STRUCTURE,
    "型鋼類": ItemClass.PRIMARY_STRUCTURE,
    "鋼板類": ItemClass.FABRICATED_PART,
    "螺栓類": ItemClass.ACCESSORY,
    "管夾類": ItemClass.ACCESSORY,
    "墊片類": ItemClass.ACCESSORY,
    "彈簧類": ItemClass.ACCESSORY,
}


CATEGORY_MANUFACTURING_TYPE: dict[str, ManufacturingType] = {
    "管路類": ManufacturingType.RAW_CUT,
    "型鋼類": ManufacturingType.RAW_CUT,
    "鋼板類": ManufacturingType.PLATE_CUT,
    "螺栓類": ManufacturingType.PURCHASED,
    "管夾類": ManufacturingType.PURCHASED,
    "墊片類": ManufacturingType.PURCHASED,
    "彈簧類": ManufacturingType.PURCHASED,
}


def _role_or_none(role: str | ComponentRole | None) -> ComponentRole | None:
    if isinstance(role, ComponentRole):
        return role
    if not role:
        return None
    try:
        return ComponentRole(str(role))
    except ValueError:
        return None


def item_class_for(
    role: str | ComponentRole | None = "",
    *,
    category: str = "",
) -> str:
    cr = _role_or_none(role)
    if cr is not None:
        return ROLE_ITEM_CLASS.get(cr, ItemClass.UNKNOWN).value
    return CATEGORY_ITEM_CLASS.get(category, ItemClass.UNKNOWN).value


def manufacturing_type_for(
    role: str | ComponentRole | None = "",
    *,
    category: str = "",
    shape_kind: str = "",
) -> str:
    cr = _role_or_none(role)
    if cr is not None:
        if shape_kind and ROLE_AGGREGATE_TYPE.get(cr) == "plate":
            return ManufacturingType.SHAPED_PLATE.value
        return ROLE_MANUFACTURING_TYPE.get(cr, ManufacturingType.UNKNOWN).value
    if shape_kind and category == "鋼板類":
        return ManufacturingType.SHAPED_PLATE.value
    return CATEGORY_MANUFACTURING_TYPE.get(category, ManufacturingType.UNKNOWN).value


# ── 顯示名稱 (供 UI 與 export 使用) ──────────────────────────
ROLE_DISPLAY_NAME: dict[ComponentRole, dict[str, str]] = {
    ComponentRole.BASE_PLATE:       {"zh": "底板",     "en": "Base Plate"},
    ComponentRole.LUG_PLATE:        {"zh": "角板",     "en": "Lug Plate"},
    ComponentRole.SHIM_PLATE:       {"zh": "墊板",     "en": "Shim Plate"},
    ComponentRole.COVER_PLATE:      {"zh": "蓋板",     "en": "Cover Plate"},
    ComponentRole.WING_PLATE:       {"zh": "翼板",     "en": "Wing Plate"},
    ComponentRole.STOPPER_PLATE:    {"zh": "止擋板",   "en": "Stopper Plate"},
    ComponentRole.SIDE_PLATE:       {"zh": "側板",     "en": "Side Plate"},
    ComponentRole.TOP_PLATE:        {"zh": "頂板",     "en": "Top Plate"},
    ComponentRole.SADDLE_PLATE:     {"zh": "鞍板",     "en": "Saddle Plate"},
    ComponentRole.REINFORCEMENT_PAD:{"zh": "補強墊板", "en": "Reinforcement Pad"},
    ComponentRole.FLAT_BAR:         {"zh": "扁鋼",     "en": "Flat Bar"},
    ComponentRole.GENERIC_PLATE:    {"zh": "鋼板",     "en": "Plate"},
    ComponentRole.PIPE:             {"zh": "管路",     "en": "Pipe"},
    ComponentRole.COLUMN:           {"zh": "立柱",     "en": "Column"},
    ComponentRole.TOP_BEAM:         {"zh": "主梁",     "en": "Top Beam"},
    ComponentRole.DIAGONAL_BRACE:   {"zh": "斜撐",     "en": "Diagonal Brace"},
    ComponentRole.TRUNNION:         {"zh": "管托",     "en": "Trunnion"},
    ComponentRole.ANGLE:            {"zh": "角鋼",     "en": "Angle"},
    ComponentRole.CHANNEL:          {"zh": "槽鋼",     "en": "Channel"},
    ComponentRole.H_SECTION:        {"zh": "H型鋼",    "en": "H Section"},
    ComponentRole.OPENING_REINFORCEMENT: {"zh": "開孔補強扁鋼", "en": "Opening Reinforcement Flat Bar"},
    ComponentRole.EXPANSION_BOLT:   {"zh": "膨脹螺栓", "en": "Expansion Bolt"},
    ComponentRole.MACHINE_BOLT:     {"zh": "機械螺栓", "en": "Machine Bolt"},
    ComponentRole.K_BOLT:           {"zh": "K型螺栓",  "en": "K-Bolt"},
    ComponentRole.NUT:              {"zh": "螺帽",     "en": "Nut"},
    ComponentRole.WASHER:           {"zh": "墊圈",     "en": "Washer"},
    ComponentRole.U_BOLT:           {"zh": "U型螺栓",  "en": "U-Bolt"},
    ComponentRole.GASKET:           {"zh": "墊片",     "en": "Gasket"},
    ComponentRole.PU_BLOCK:         {"zh": "PU塊",    "en": "PU Block"},
    ComponentRole.CLAMP:            {"zh": "管夾",     "en": "Clamp"},
    ComponentRole.UNKNOWN:          {"zh": "未分類",   "en": "Unknown"},
}


# ── 舊字串 → ComponentRole 映射（Phase 3 遷移用）─────────────
#   key: 舊 entry.name 的可能寫法（全小寫比對）
LEGACY_NAME_MAP: dict[str, ComponentRole] = {
    # lug plate 的各種寫法
    "lug_plate_c":          ComponentRole.LUG_PLATE,
    "lug plate type-c":     ComponentRole.LUG_PLATE,
    "lug plate type-a":     ComponentRole.LUG_PLATE,
    "lug plate type-b":     ComponentRole.LUG_PLATE,

    # base plate
    "base plate":           ComponentRole.BASE_PLATE,
    "plate_base":           ComponentRole.BASE_PLATE,
    "baseplate":            ComponentRole.BASE_PLATE,

    # shim
    "c/s shim":             ComponentRole.SHIM_PLATE,
    "shim":                 ComponentRole.SHIM_PLATE,

    # cover
    "cover_pl":             ComponentRole.COVER_PLATE,
    "cover plate":          ComponentRole.COVER_PLATE,

    # wing
    "plate_wing":           ComponentRole.WING_PLATE,
    "plate_9t_wing":        ComponentRole.WING_PLATE,

    # stopper
    "plate_stopper":        ComponentRole.STOPPER_PLATE,

    # side
    "plate_6t_side":        ComponentRole.SIDE_PLATE,
    "plate_a_有鑽孔":        ComponentRole.SIDE_PLATE,
    "plate_a_無鑽孔":        ComponentRole.SIDE_PLATE,

    # top
    "plate_top":            ComponentRole.TOP_PLATE,

    # reinforcement
    "rein. pad":            ComponentRole.REINFORCEMENT_PAD,
    "rein.pad":             ComponentRole.REINFORCEMENT_PAD,

    # flat bar
    "flat bar":             ComponentRole.FLAT_BAR,
    "flatbar":              ComponentRole.FLAT_BAR,

    # structural
    "member c":             ComponentRole.CHANNEL,
    "saddle (120°)":        ComponentRole.SADDLE_PLATE,

    # bolts
    "exp.bolt":             ComponentRole.EXPANSION_BOLT,
    "expansion bolt":       ComponentRole.EXPANSION_BOLT,
    "adj.bolt":             ComponentRole.MACHINE_BOLT,
    "anchor bolt":          ComponentRole.EXPANSION_BOLT,
    "m.bolt":               ComponentRole.MACHINE_BOLT,
    "m.b.":                 ComponentRole.MACHINE_BOLT,
    "m.b.(full threaded)":  ComponentRole.MACHINE_BOLT,
    "mach.bolt":            ComponentRole.MACHINE_BOLT,
    "machine bolt":         ComponentRole.MACHINE_BOLT,
    "k-bolt":               ComponentRole.K_BOLT,
    "k bolt":               ComponentRole.K_BOLT,
    "hex nut":              ComponentRole.NUT,
    "nut":                  ComponentRole.NUT,
    "washer":               ComponentRole.WASHER,
    "u.bolt":               ComponentRole.U_BOLT,
    "u-bolt":               ComponentRole.U_BOLT,
    "u bolt":               ComponentRole.U_BOLT,
    "pipe clamp":           ComponentRole.CLAMP,
    "riser clamp type-a":   ComponentRole.CLAMP,
    "riser clamp type-b":   ComponentRole.CLAMP,
    "non-asbestos":         ComponentRole.GASKET,
    "gasket":               ComponentRole.GASKET,
}


def role_from_legacy_name(name: str) -> ComponentRole:
    """
    從舊式字串名稱推斷 ComponentRole。
    Phase 3 遷移工具；新程式不應使用此函式。
    """
    return LEGACY_NAME_MAP.get(name.strip().lower(), ComponentRole.UNKNOWN)
