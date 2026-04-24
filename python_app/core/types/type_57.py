"""
Type 57 計算器 — U-Bolt on Existing Steel (D-68)
格式: 57-{line_size}-{mode}
  例: 57-2B-A
- 第二段: 管徑 (2B = 2", 10 = 10")
- 第三段: 模式 A=SLIDE / B=FIXED

構件:
  1. U-BOLT (ref M-26, 依管徑查表, Carbon Steel, 1 SET)
  2. FINISHED HEX NUTS (M-26, 4 PCS)

備註:
  - 無底板（直接固定於既有鋼構）
  - 不適用於保溫管、高溫管、關鍵管線
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from data.m26_table import get_m26_by_line_size

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

    # 查 M-26 table
    row = get_m26_by_line_size(size_val)
    if row is None:
        result.error = f"Type 57 / M-26 查表失敗: 管徑 {line_size_raw} ({size_val}\") 不在查表範圍"
        return result

    # --- 構件 1: U-BOLT ---
    ub = AnalysisEntry()
    ub.name = "U-BOLT"
    ub.spec = row["type"]
    ub.material = "Carbon Steel"
    ub.quantity = 1
    ub.unit_weight = 1
    ub.total_weight = 1
    ub.unit = "SET"
    ub.factor = 1
    ub.qty_subtotal = 1
    ub.weight_output = 1
    ub.category = "螺栓類"
    ub.remark = (
        f'M-26, {_MODE_LABELS.get(mode, mode)}, rod={row["rod_size_a"]}, '
        f'B/C/D/E={row["B"]}/{row["C"]}/{row["D"]}/{row["E"]}, '
        f'load650/750={row["load_650f_kg"]}/{row["load_750f_kg"]}kg, '
        "unit weight placeholder"
    )
    result.add_entry(ub)

    # --- 構件 2: Finished hex nuts ---
    nuts = AnalysisEntry()
    nuts.name = "FINISHED HEX NUT"
    nuts.spec = row["rod_size_a"]
    nuts.material = "Carbon Steel"
    nuts.quantity = 4
    nuts.unit_weight = 0
    nuts.total_weight = 0
    nuts.unit = "PC"
    nuts.factor = 1
    nuts.qty_subtotal = 4
    nuts.weight_output = 0
    nuts.category = "螺栓類"
    nuts.remark = "M-26 note 1: four finished hex nuts, nut weight included in U-bolt set placeholder"
    result.add_entry(nuts)

    return result
