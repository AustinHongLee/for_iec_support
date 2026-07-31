"""
分析結果的資料模型
每筆計算結果以 AnalysisEntry 表示，最終匯出用 AnalysisResult

Phase 0 變更 (2026-04-29):
  - 新增 HolePattern dataclass：結構化儲存螺孔資訊（取代 remark 拼字）
  - 新增 GeometryHints dataclass：結構化儲存角色、公式、孔位、中文備註
  - AnalysisEntry 新增 role (str) 及 geometry (GeometryHints) 欄位
  - 舊欄位 remark 保留，不破壞現有邏輯

Phase 2 變更 (2026-04-30):
  - AnalysisEntry 新增 display_remark property：
    優先顯示結構化 geometry.holes，fallback 到 remark 字串
  - 供 UI / export 使用，取代直接讀 entry.remark

遷移策略：
  新 type 直接填 role + geometry；舊 type 的 remark 字串短期繼續有效。
  Phase 3 統一把 remark 搬進 geometry.notes_zh，role 改用 ComponentRole enum。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from .component_roles import item_class_for, manufacturing_type_for
from .truth import default_unknown_meta


# ── 子結構 ───────────────────────────────────────────────────

@dataclass
class HolePattern:
    """
    螺孔分布資訊（供 CAD 串接、UI 獨立欄位顯示）

    pattern 可選值：
      "rect"     — 矩形排列 (pitch_x x pitch_y)
      "circular" — 環狀排列 (pitch_x = 節圓半徑)
      "single"   — 單孔
      "none"     — 無孔
    """
    pattern: str = "none"
    pitch_x: float = 0.0
    pitch_y: float = 0.0
    diameter: float = 0.0
    fastener_spec: str = ""
    count: int = 0


@dataclass
class GeometryHints:
    """
    結構化幾何資訊，讓 UI / CAD / export 直接讀，不需 parse remark。

    role     : ComponentRole 的值字串，例如 "lug_plate"
    formula  : 長度計算公式追溯，例如 "H - 15" / "H + A"
    holes    : 螺孔分布（None 表示無孔）
    notes_zh : 工程師看的中文說明（Phase 3 取代 remark）
    shape_spec : 放樣/裁切用的完整輪廓規格；空白時使用 length x width x thickness
    shape_kind : 輪廓分類，例如 "wing"；供 part key / CAD / procurement 管控使用
    gross_area_mm2 : 外接矩形/毛坯面積
    cutout_area_mm2: 扣除面積，例如缺角三角形
    net_area_mm2   : 實際算重淨面積；0 表示使用 length x width
    component_id   : 圖面件號／穩定零件識別，供加工圖與 CAD 對應
    source_drawing : 幾何直接依據的圖號
    source_revision: 幾何直接依據的版次
    fabrication_ready : 是否已具備足以出加工圖的幾何
    fabrication_blockers : 尚缺的加工尺寸／輪廓／製程資料
    parameters     : CAD/加工圖可直接消費的具名尺寸與製程參數
    """
    role: str = ""
    formula: str = ""
    holes: Optional[HolePattern] = None
    notes_zh: str = ""
    shape_spec: str = ""
    shape_kind: str = ""
    gross_area_mm2: float = 0.0
    cutout_area_mm2: float = 0.0
    net_area_mm2: float = 0.0
    component_id: str = ""
    source_drawing: str = ""
    source_revision: str = ""
    fabrication_ready: bool = False
    fabrication_blockers: List[str] = field(default_factory=list)
    parameters: dict = field(default_factory=dict)


# ── 主要 dataclass ───────────────────────────────────────────

@dataclass
class AnalysisEntry:
    """一筆材料明細"""
    item_no: int = 0
    name: str = ""
    spec: str = ""
    length: float = 0.0
    width: float = 0.0
    material: str = ""
    quantity: int = 1
    weight_per_unit: float = 0.0
    unit_weight: float = 0.0
    total_weight: float = 0.0
    unit: str = "M"
    factor: float = 1.0
    length_subtotal: float = 0.0
    qty_subtotal: float = 0.0
    weight_output: float = 0.0
    category: str = ""
    remark: str = ""                    # 備註 (R欄) — Phase 3 前仍保留
    part_key: str = ""                  # 人/程式可讀的零件識別，例如 59_lug_plate_wing_a150...
    stock_id: str = ""                  # 採購/庫存用短碼，依材料與幾何生成
    item_class: str = ""                # primary_structure / fabricated_part / accessory / reference_only
    manufacturing_type: str = ""        # raw_cut / plate_cut / shaped_plate / purchased / not_furnished
    density_g_cm3: float = 0.0           # 算重採用密度；0 表示不以體積密度算重
    density_source: str = ""             # 密度查表／來源識別，供加工與採購稽核
    density_requires_review: bool = False  # True 表示密度是未由來源釋出的 fallback

    # ── Phase 0 新增欄位（optional，向後相容）────────────────
    role: str = ""                      # ComponentRole 的值，例如 "lug_plate"
    geometry: GeometryHints = field(default_factory=GeometryHints)

    # ── Phase 2 新增 property ────────────────────────────────
    @property
    def display_spec(self) -> str:
        """UI / export 顯示用規格；內部 spec 仍保留計算用原始值。"""
        shape_spec = getattr(self.geometry, "shape_spec", "") if self.geometry else ""
        shape_spec = str(shape_spec).strip()
        return shape_spec or self.spec

    @property
    def display_remark(self) -> str:
        """
        優先顯示結構化幾何資訊，fallback 到 remark 字串。
        供 UI / export 使用，取代直接讀 entry.remark。

        輸出範例：
          "螺孔: rect Φ18 [70×100] 5/8\" ×4"
          "螺孔: circular Φ22 [R=60] M20 ×6"
          "中文備註文字"
          ""  (若皆無資訊)
        """
        h = self.geometry.holes
        if h and h.pattern != "none" and h.diameter > 0:
            if h.pattern == "circular":
                pitch = f"R={h.pitch_x:.0f}"
            elif h.pitch_y:
                pitch = f"{h.pitch_x:.0f}×{h.pitch_y:.0f}"
            else:
                pitch = f"{h.pitch_x:.0f}"
            spec = f" {h.fastener_spec}" if h.fastener_spec else ""
            count = f" ×{h.count}" if h.count else ""
            hole_str = f"螺孔: {h.pattern} Φ{h.diameter:.0f} [{pitch}]{spec}{count}"
            if self.geometry.notes_zh:
                return f"{hole_str} | {self.geometry.notes_zh}"
            return hole_str
        if self.geometry.notes_zh:
            return self.geometry.notes_zh
        return self.remark


def set_remark(entry: "AnalysisEntry", zh: str, en: str = "") -> None:
    """設定備註：zh 為中文顯示用，en 為英文版（保留於 remark 欄位供後續用）。
    若未提供 en，則 remark 也存中文。
    display_remark 會優先顯示 geometry.notes_zh（中文）。
    """
    entry.geometry.notes_zh = zh
    entry.remark = en if en else zh


@dataclass
class AnalysisResult:
    """一筆支撐編碼的完整分析結果"""
    fullstring: str = ""
    entries: List[AnalysisEntry] = field(default_factory=list)
    error: str = ""
    warnings: List[str] = field(default_factory=list)
    meta: dict = field(default_factory=default_unknown_meta)
    evidence: List[dict] = field(default_factory=list)

    def add_entry(self, entry: AnalysisEntry):
        """新增一筆明細，自動編號"""
        if self.entries:
            entry.item_no = self.entries[-1].item_no + 1
        else:
            entry.item_no = 1
        if not entry.item_class:
            entry.item_class = item_class_for(entry.role, category=entry.category)
        if not entry.manufacturing_type:
            shape_kind = getattr(entry.geometry, "shape_kind", "") if entry.geometry else ""
            entry.manufacturing_type = manufacturing_type_for(
                entry.role,
                category=entry.category,
                shape_kind=shape_kind,
            )
        self.entries.append(entry)

    @property
    def total_weight(self) -> float:
        return sum(e.weight_output for e in self.entries)
