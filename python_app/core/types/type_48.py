"""
Type 48 計算器 — Drain Hub 偏移底座支撐 (D-59)
格式: 48-{line_size}{mat_sym}
  例: 48-2, 48-4(A), 48-6(B)

mat_sym: (空)=CS, (A)=AS, (B)=SS

BOM (1 筆): ① PLATE (150×100×6 or 9)
"""
from ..models import AnalysisResult
from ..type_spec_engine import calculate_table_plate_spec


def calculate(fullstring: str) -> AnalysisResult:
    return calculate_table_plate_spec(fullstring, "48")
