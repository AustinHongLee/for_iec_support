"""
Type 57 計算器 — U-Bolt on Existing Steel (D-68)
格式: 57-{line_size}-{mode}
  例: 57-2B-A
- 第二段: 管徑 (2B = 2", 10 = 10")
- 第三段: 模式 A=SLIDE / B=FIXED

構件:
  1. U-BOLT (ref M-26, 依管徑查表, SUS304, 1 SET)
  2. ROD (threaded rod, 依管徑查表, SUS304, 1 SET)

備註:
  - 無底板（直接固定於既有鋼構）
  - 不適用於保溫管、高溫管、關鍵管線
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from data.type57_table import get_type57_data

_VALID_MODES = {"A", "B"}
_MODE_LABELS = {"A": "SLIDE", "B": "FIXED"}


def calculate(fullstring: str, **kwargs) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # --- 解析 ---
    line_size_raw = get_part(fullstring, 2)
    mode = get_part(fullstring, 3).upper()

    # 模式檢查
    if mode not in _VALID_MODES:
        result.warnings.append(
            f"模式 '{mode}' 無效，Type 57 僅支援 A(SLIDE) / B(FIXED)"
        )

    # 管徑轉換
    size_val = get_lookup_value(line_size_raw)

    # 查表
    row = get_type57_data(size_val)
    if row is None:
        result.error = f"Type 57 查表失敗: 管徑 {line_size_raw} ({size_val}\") 不在查表範圍"
        return result

    # --- 構件 1: U-BOLT ---
    ub = AnalysisEntry()
    ub.name = "U-BOLT"
    ub.spec = row["u_bolt"]
    ub.material = "SUS304"
    ub.quantity = 1
    ub.unit_weight = 1
    ub.total_weight = 1
    ub.unit = "SET"
    ub.factor = 1
    ub.qty_subtotal = 1
    ub.weight_output = 1
    ub.category = "螺栓類"
    ub.remark = f"ref M-26, {_MODE_LABELS.get(mode, mode)}"
    result.add_entry(ub)

    # --- 構件 2: ROD ---
    rod = AnalysisEntry()
    rod.name = "ROD"
    rod.spec = row["rod"]
    rod.material = "SUS304"
    rod.quantity = 1
    rod.unit_weight = 1
    rod.total_weight = 1
    rod.unit = "SET"
    rod.factor = 1
    rod.qty_subtotal = 1
    rod.weight_output = 1
    rod.category = "螺栓類"
    result.add_entry(rod)

    return result
