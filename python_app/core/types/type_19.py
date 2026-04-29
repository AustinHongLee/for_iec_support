"""
Type 19 計算器 - 斜撐式 (Lateral Bracing) 支撐
Diagonal brace using angle steel or H-beam cut piece

格式: 19-{A}B
  例: 19-2B → Line size A = 2"
- 第二段: Line size "A"
- 無第三段 (L 為現場裁切，查表固定值)

Note 1: DIMENSION "L" SHALL BE CUT TO SUIT IN FIELD.
Note 2: 合金鋼/不鏽鋼/stress relief 材質同主管

構件 (1 項):
  1. MEMBER "M": Angle 或 H Beam，長度 L，A36/SS400
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from data.type19_table import get_type19_data


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: pipe size A ──
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 19: 缺少第二段 (Line size)"
        return result

    pipe_size = get_lookup_value(part2)

    # 查表
    data = get_type19_data(pipe_size)
    if not data:
        result.error = (
            f"Type 19: Pipe size {part2} ({pipe_size}\") 不在查表範圍 "
            f"(1\"/1.5\"/2\"/3\"/4\"/6\"/8\"/10\"/12\")"
        )
        return result

    section_type = data["section_type"]
    dim = data["dim"]
    length = data["L"]

    # ── 1. Member M ──
    add_steel_section_entry(
        result,
        section_type=section_type,
        section_dim=dim,
        total_length=length,
        material="A36/SS400",
    )

    return result
