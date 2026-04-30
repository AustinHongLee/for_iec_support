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
from ..models import AnalysisResult
from ..type_spec_engine import calculate_table_plate_spec


def calculate(fullstring: str, **kwargs) -> AnalysisResult:
    return calculate_table_plate_spec(fullstring, "57")
