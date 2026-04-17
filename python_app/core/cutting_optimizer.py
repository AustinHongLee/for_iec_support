"""
下料計算 — 1D Cutting Stock (FFD 演算法)

實務考量:
  - 每刀損耗 = kerf(鋸口) + tolerance(量測容差)
  - 原料兩端各切除 end_trim (毛邊/壓痕)
  - 材質不同絕對不能混用 → 已在 material_summary 分組
  - 最小餘料 < min_usable_remnant 者報廢
  - 不追蹤跨批次餘料

演算法: First Fit Decreasing (FFD)
  1. 所有需求段按長度降序排列
  2. 依序嘗試放入已開的原料
  3. 放不下就開新一根

  FFD 簡單且結果接近最優，適合現場可讀性。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import math

from data.stock_lengths import (
    STOCK_LENGTH_PIPE, STOCK_LENGTH_STEEL,
    STOCK_END_TRIM, KERF_WIDTH, LENGTH_TOLERANCE,
    MIN_USABLE_REMNANT, get_effective_stock_length,
)


@dataclass
class CutPiece:
    """一段需求料"""
    demand_length: float        # 原始需求長度 (mm)
    source: str = ""            # 來源編碼 (fullstring)
    label: str = ""             # 標記 (如 "上管", "下管")

    @property
    def cut_length(self) -> float:
        """實際佔用長度 (含 kerf + tolerance)"""
        return self.demand_length + KERF_WIDTH + LENGTH_TOLERANCE


@dataclass
class StockBar:
    """一根原料的切割排列"""
    stock_length: float         # 原料標稱長度 (mm)
    effective_length: float     # 有效長度 (扣除頭尾)
    pieces: List[CutPiece] = field(default_factory=list)

    @property
    def used_length(self) -> float:
        """已使用長度 (含 kerf)"""
        return sum(p.cut_length for p in self.pieces)

    @property
    def remaining(self) -> float:
        """剩餘可用長度"""
        return self.effective_length - self.used_length

    @property
    def remnant(self) -> float:
        """切完後的實際餘料

        每一刀 (含最後一刀) 都消耗 kerf，因為需要鋸切來分離工件與餘料。
        """
        if not self.pieces:
            return self.effective_length
        return self.remaining

    @property
    def waste(self) -> float:
        """廢料 = 餘料中不可再利用的部分"""
        r = self.remnant
        return r if r < MIN_USABLE_REMNANT else 0.0

    @property
    def utilization(self) -> float:
        """使用率 (%)"""
        if self.effective_length <= 0:
            return 0.0
        actual_used = sum(p.demand_length for p in self.pieces)
        return (actual_used / self.effective_length) * 100

    def can_fit(self, piece: CutPiece) -> bool:
        """這根料還放不放得下這段"""
        return piece.cut_length <= self.remaining


@dataclass
class CuttingPlan:
    """一種規格材料的完整下料方案"""
    name: str = ""              # 品名
    spec: str = ""              # 規格
    material: str = ""          # 材質
    stock_length: float = 0.0   # 原料標稱長度

    bars: List[StockBar] = field(default_factory=list)

    @property
    def total_bars(self) -> int:
        return len(self.bars)

    @property
    def total_pieces(self) -> int:
        return sum(len(b.pieces) for b in self.bars)

    @property
    def total_demand_length(self) -> float:
        return sum(p.demand_length for b in self.bars for p in b.pieces)

    @property
    def total_waste(self) -> float:
        return sum(b.waste for b in self.bars)

    @property
    def total_remnant(self) -> float:
        return sum(b.remnant for b in self.bars)

    @property
    def avg_utilization(self) -> float:
        if not self.bars:
            return 0.0
        return sum(b.utilization for b in self.bars) / len(self.bars)


def optimize_cutting(
    pieces: List[CutPiece],
    stock_type: str = "pipe",
    stock_length: Optional[float] = None,
) -> CuttingPlan:
    """
    FFD 下料排列

    Parameters
    ----------
    pieces : list of CutPiece
        所有需求段 (同一 name+spec+material)
    stock_type : 'pipe' | 'steel'
        決定預設原料長度
    stock_length : float, optional
        自定原料長度 (覆蓋預設值)

    Returns
    -------
    CuttingPlan
        排列結果
    """
    if stock_length is None:
        stock_length = STOCK_LENGTH_PIPE if stock_type == "pipe" else STOCK_LENGTH_STEEL

    effective = stock_length - 2 * STOCK_END_TRIM

    plan = CuttingPlan(stock_length=stock_length)

    # 過濾無效段 (負值或零長度)
    valid_pieces = [p for p in pieces if p.demand_length > 0]

    # FFD: 按需求長度降序排列
    sorted_pieces = sorted(valid_pieces, key=lambda p: p.demand_length, reverse=True)

    for piece in sorted_pieces:
        if piece.cut_length > effective:
            # 單段超過原料有效長度 → 需要特殊處理
            # 開一根專用料，標記為超長
            bar = StockBar(
                stock_length=piece.demand_length + 2 * STOCK_END_TRIM + KERF_WIDTH,
                effective_length=piece.demand_length + KERF_WIDTH,
            )
            bar.pieces.append(piece)
            plan.bars.append(bar)
            continue

        # 找第一根放得下的原料
        placed = False
        for bar in plan.bars:
            if bar.can_fit(piece):
                bar.pieces.append(piece)
                placed = True
                break

        if not placed:
            # 開新一根
            bar = StockBar(
                stock_length=stock_length,
                effective_length=effective,
            )
            bar.pieces.append(piece)
            plan.bars.append(bar)

    return plan


def optimize_from_summary(summary_line) -> Optional[CuttingPlan]:
    """
    從 SummaryLine 直接產生下料方案

    Parameters
    ----------
    summary_line : material_summary.SummaryLine
        聚合後的一行 (必須是 linear 類型)

    Returns
    -------
    CuttingPlan or None
    """
    if summary_line.aggregate_type != "linear":
        return None

    pieces = []
    for i, (length, source) in enumerate(summary_line.piece_lengths):
        pieces.append(CutPiece(
            demand_length=length,
            source=source,
            label=f"#{i+1}",
        ))

    stock_type = "pipe" if "Pipe" in summary_line.name else "steel"

    plan = optimize_cutting(pieces, stock_type=stock_type)
    plan.name = summary_line.name
    plan.spec = summary_line.spec
    plan.material = summary_line.material

    return plan
