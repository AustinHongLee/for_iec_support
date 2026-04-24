"""
材料合計表 — 將多筆分析結果聚合為採購清單

聚合邏輯:
  1. 展開所有 AnalysisResult 的 entries
  2. 按 (name, spec, material) 聚合
  3. 線性材料 (Pipe/Angle/H/C): 加總長度，算採購根數
  4. 面材料 (Plate): 加總數量/面積
  5. 計件材料 (Bolt/Nut/Washer): 加總數量
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Sequence
from collections import defaultdict
import math

from core.models import AnalysisResult, AnalysisEntry
from data.stock_lengths import (
    STOCK_LENGTH_PIPE, STOCK_LENGTH_STEEL,
    get_effective_stock_length,
)


# ── 品名分類判斷 ──
_LINEAR_NAMES = {"Pipe", "Angle"}                # 可能有長度需下料的
_PLATE_NAMES = {"Plate"}                          # 鋼板 (算片數)
# 其餘 (EXP.BOLT, MACH.BOLT, Nut, Washer 等) → 計件

def _classify_entry(entry: AnalysisEntry) -> str:
    """判斷 entry 屬於哪種聚合方式"""
    base = entry.name.split("_")[0].strip()
    if base in _LINEAR_NAMES:
        return "linear"
    if base.startswith("Plate"):
        return "plate"
    # 鋼材 section (H, C, L) 也是線性
    if any(base.startswith(p) for p in ("H", "C", "L")) and entry.unit == "M":
        return "linear"
    return "piece"


@dataclass
class SummaryLine:
    """合計表中的一行"""
    name: str = ""                  # 品名
    spec: str = ""                  # 規格
    material: str = ""              # 材質
    category: str = ""              # 屬性 (管路類/鋼板類/螺栓類)
    aggregate_type: str = ""        # linear / plate / piece

    # 線性材料
    total_length_mm: float = 0.0    # 需求總長 (mm)
    piece_count: int = 0            # 需求件數 (多少段)
    piece_lengths: List[Tuple[float, str]] = field(default_factory=list)
    # (長度mm, 來源編碼) 明細

    # 鋼板
    total_qty: int = 0              # 需求總數量
    plate_dims: List[Tuple[float, float, float]] = field(default_factory=list)
    # (length, width, thickness) 明細

    # 通用
    weight_per_unit: float = 0.0    # kg/m 或 kg/pc
    total_weight: float = 0.0       # 總重 (kg)

    # 採購建議
    stock_length: float = 0.0       # 標準原料長度 (mm)
    purchase_qty: int = 0           # 建議採購數量 (根/片/組)
    purchase_unit: str = ""         # 根 / 片 / 組

    # 來源追蹤
    source_fullstrings: List[str] = field(default_factory=list)


@dataclass
class MaterialSummary:
    """完整材料合計表"""
    lines: List[SummaryLine] = field(default_factory=list)

    @property
    def total_weight(self) -> float:
        return sum(ln.total_weight for ln in self.lines)

    def get_linear_lines(self) -> List[SummaryLine]:
        return [ln for ln in self.lines if ln.aggregate_type == "linear"]

    def get_plate_lines(self) -> List[SummaryLine]:
        return [ln for ln in self.lines if ln.aggregate_type == "plate"]

    def get_piece_lines(self) -> List[SummaryLine]:
        return [ln for ln in self.lines if ln.aggregate_type == "piece"]


def _project_source_label(designation: str, quantity: int) -> str:
    """Human-readable project source label for material summary/cutting."""
    return f"{designation} × {quantity}" if quantity != 1 else designation


def aggregate_project(project) -> MaterialSummary:
    """
    Aggregate a ProjectAnalysisResult for procurement/cutting.

    Numeric totals come from scaled_result, while source labels preserve the
    project row quantity so cutting plans remain traceable to the input list.
    """
    results = [row.scaled_result for row in project.rows]
    labels = [
        _project_source_label(row.input_row.designation, row.input_row.quantity)
        for row in project.rows
    ]
    return aggregate(results, source_labels=labels)


def aggregate(
    results: List[AnalysisResult],
    source_labels: Sequence[str] | None = None,
) -> MaterialSummary:
    """
    將多筆 AnalysisResult 聚合為 MaterialSummary

    Parameters
    ----------
    results : list of AnalysisResult
        來自 analyze_batch 的所有分析結果
    source_labels : sequence of str, optional
        與 results 平行的來源標籤；project aggregation 會用它保留「型號 × 組數」。

    Returns
    -------
    MaterialSummary
        按 (name, spec, material) 聚合的採購清單
    """
    if source_labels is not None and len(source_labels) != len(results):
        raise ValueError("source_labels must have the same length as results")

    # key = (name, spec, material) — 鋼板額外按尺寸分
    groups: Dict[tuple, List[Tuple[AnalysisEntry, str]]] = defaultdict(list)

    for index, r in enumerate(results):
        if r.error:
            continue
        source_label = source_labels[index] if source_labels is not None else r.fullstring
        for entry in r.entries:
            if _classify_entry(entry) == "plate":
                # 鋼板按 (name, material, length, width, thickness) 分組
                key = (entry.name, entry.material,
                       round(entry.length, 1), round(entry.width, 1), entry.spec)
            else:
                key = (entry.name, entry.spec, entry.material)
            groups[key].append((entry, source_label))

    summary = MaterialSummary()

    for key, items in groups.items():
        entries = [e for e, _ in items]
        fullstrings = list(dict.fromkeys(fs for _, fs in items))  # 去重保序

        first = entries[0]
        agg_type = _classify_entry(first)

        if agg_type == "plate":
            # key = (name, material, length, width, thickness_str)
            name, material = key[0], key[1]
            pl_l, pl_w, pl_t_str = key[2], key[3], key[4]
            spec = f"{pl_l:.0f}×{pl_w:.0f}×{pl_t_str}t"
        else:
            name, spec, material = key[0], key[1], key[2]

        ln = SummaryLine(
            name=name,
            spec=spec,
            material=material,
            category=first.category,
            aggregate_type=agg_type,
            weight_per_unit=first.weight_per_unit,
            source_fullstrings=fullstrings,
        )

        if agg_type == "linear":
            _aggregate_linear(ln, items)
        elif agg_type == "plate":
            _aggregate_plate(ln, entries)
        else:
            _aggregate_piece(ln, entries)

        # 過濾無效行 (例如計算出負值長度的)
        if agg_type == "linear" and ln.total_length_mm <= 0:
            continue
        if agg_type in ("plate", "piece") and ln.total_qty <= 0:
            continue

        summary.lines.append(ln)

    # 排序: 管路類 → 鋼板類 → 螺栓類，同類內按 spec 排
    _CATEGORY_ORDER = {"管路類": 0, "鋼板類": 1, "鋼材類": 2, "螺栓類": 3, "": 9}
    summary.lines.sort(key=lambda x: (
        _CATEGORY_ORDER.get(x.category, 9), x.name, x.spec, x.material
    ))

    return summary


def _aggregate_linear(ln: SummaryLine, items: List[Tuple[AnalysisEntry, str]]):
    """聚合線性材料 (管 / 角鋼 / 型鋼)"""
    for e, fullstring in items:
        if e.length <= 0:
            continue  # 跳過計算異常的負值/零長度
        for _ in range(e.quantity):
            ln.piece_lengths.append((e.length, fullstring))
            ln.total_length_mm += e.length
            ln.piece_count += 1
    ln.total_weight = sum(e.weight_output for e, _ in items if e.length > 0)

    # 採購建議: 總長度 / 標準長度 → 無條件進位
    if "Pipe" in ln.name:
        ln.stock_length = STOCK_LENGTH_PIPE
        ln.purchase_unit = "根"
    else:
        ln.stock_length = STOCK_LENGTH_STEEL
        ln.purchase_unit = "根"

    effective = get_effective_stock_length(
        "pipe" if "Pipe" in ln.name else "steel"
    )
    if effective > 0:
        ln.purchase_qty = math.ceil(ln.total_length_mm / effective)
    else:
        ln.purchase_qty = ln.piece_count


def _aggregate_plate(ln: SummaryLine, entries: List[AnalysisEntry]):
    """聚合鋼板 (同尺寸已在上層按 key 分組)"""
    for e in entries:
        ln.total_qty += e.quantity
        if e.length and e.width:
            try:
                t = float(e.spec)
            except (ValueError, TypeError):
                t = 0
            for _ in range(e.quantity):
                ln.plate_dims.append((e.length, e.width, t))
    ln.total_weight = sum(e.weight_output for e in entries)
    ln.purchase_qty = ln.total_qty
    ln.purchase_unit = "片"


def _aggregate_piece(ln: SummaryLine, entries: List[AnalysisEntry]):
    """聚合計件材料 (螺栓等)"""
    for e in entries:
        ln.total_qty += e.quantity
    ln.total_weight = sum(e.weight_output for e in entries)
    ln.purchase_qty = ln.total_qty
    ln.purchase_unit = "組"
