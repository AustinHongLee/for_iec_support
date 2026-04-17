"""
分析結果的資料模型
每筆計算結果以 AnalysisEntry 表示，最終匯出用 AnalysisResult
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AnalysisEntry:
    """一筆材料明細"""
    item_no: int = 0                    # 項次 (B欄)
    name: str = ""                      # 品名 (C欄): Pipe, Angle, Plate, EXP.BOLT...
    spec: str = ""                      # 尺寸/規格 (D欄)
    length: float = 0.0                 # 長度 (E欄, mm)
    width: float = 0.0                  # 寬度 (F欄, mm) - 鋼板用
    material: str = ""                  # 材質 (G欄)
    quantity: int = 1                   # 數量 (H欄)
    weight_per_unit: float = 0.0        # 每米重 (I欄, kg/m)
    unit_weight: float = 0.0            # 單重 (J欄, kg)
    total_weight: float = 0.0           # 總重小計 (K欄, kg)
    unit: str = "M"                     # 單位 (L欄): M, PC, SET
    factor: float = 1.0                 # 係數 (M欄)
    length_subtotal: float = 0.0        # 長度小計 (N欄)
    qty_subtotal: float = 0.0           # 數量小計 (O欄)
    weight_output: float = 0.0          # 總重合計 (P欄)
    category: str = ""                  # 屬性 (Q欄): 管路類, 鋼板類
    remark: str = ""                    # 備註 (R欄)


@dataclass
class AnalysisResult:
    """一筆支撐編碼的完整分析結果"""
    fullstring: str = ""                # 原始輸入字串
    entries: List[AnalysisEntry] = field(default_factory=list)
    error: str = ""                     # 錯誤訊息 (若有)
    warnings: List[str] = field(default_factory=list)  # 警告 (仍計算但需注意)

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
