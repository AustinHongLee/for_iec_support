"""
Type 58 計算器 — U-Bolt Plate Saddle on Steel Plate / Shape Steel
圖號: D-69
格式: 58-{size}B-{FIG}
例: 58-4B-A, 58-8B-B
"""
from ..models import AnalysisResult
from ..type_spec_engine import calculate_table_plate_spec


def calculate(fullstring: str) -> AnalysisResult:
    return calculate_table_plate_spec(fullstring, "58")
