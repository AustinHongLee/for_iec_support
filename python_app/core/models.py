"""
分析結果的資料模型
每筆計算結果以 AnalysisEntry 表示，最終匯出用 AnalysisResult

Phase 0 變更 (2026-04-29):
  - 新增 HolePattern dataclass：結構化儲存螺孔資訊（取代 remark 拼字）
  - 新增 GeometryHints dataclass：結構化儲存角色、公式、孔位、中文備註
  - AnalysisEntry 新增 role (str) 及 geometry (GeometryHints) 欄位
  - 舊欄位 remark 保留，不破壞現有邏輯

遷移策略：
  新 type 直接填 role + geometry；舊 type 的 remark 字串短期繼續有效。
  Phase 3 統一把 remark 搬進 geometry.notes_zh，role 改用 ComponentRole enum。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

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
    """
    role: str = ""
    formula: str = ""
    holes: Optional[HolePattern] = None
    notes_zh: str = ""


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

    # ── Phase 0 新增欄位（optional，向後相容）────────────────
    role: str = ""                      # ComponentRole 的值，例如 "lug_plate"
    geometry: GeometryHints = field(default_factory=GeometryHints)


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
        self.entries.append(entry)

    @property
    def total_weight(self) -> float:
        return sum(e.weight_output for e in self.entries)
