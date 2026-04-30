"""
Type 60 計算器 — Large Bore Shoe Side Support
圖號: D-71
格式: 60-{size}B-{FIG}
例: 60-20B-A, 60-36B-B
FIG-A: insulated pipe
FIG-B: bare pipe (多 F 尺寸, 45°/120° 幾何)
"""
from ..models import AnalysisResult
from ..type_spec_engine import calculate_table_plate_spec


def calculate(fullstring: str) -> AnalysisResult:
    return calculate_table_plate_spec(fullstring, "60")
