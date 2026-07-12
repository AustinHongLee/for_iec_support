"""
Type 20 計算器 - 長孔滑動底座支撐 (Slotted Clamp Base Support)
U-bolt 所在的固定點，透過長孔(slot hole)產生滑移自由度

格式: 20-{M}-{HH}{Fig}
  例: 20-L50-05A → Member=L50X50X6, H=500mm, Fig.A
- 第二段: 型鋼代碼 (L50/L65/L75/C100)
- 第三段: H(數字, *100mm) + Fig字母(A/B)

Note 1: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
Note 2: STANDARD U-BOLT (NOT FURNISHED)

構件 (1 項):
  1. MEMBER "M": Angle 或 Channel，長度 H，A36/SS400
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details
from data.type20_table import MEMBER_H_MAX


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 20: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # ── 第三段: H + Fig ──
    part3 = get_part(fullstring, 3)
    fig_choice = part3[-1]

    # 檢查 Fig 不應為數字
    if fig_choice.isdigit():
        result.error = f"Type 20: Fig 代碼不應為數字 ({fullstring})"
        return result

    section_length_h = int(part3[:-1]) * 100

    # ── H_MAX 驗證 ──
    h_max = MEMBER_H_MAX.get(part2)
    if h_max and section_length_h > h_max:
        result.warnings.append(
            f"H={section_length_h}mm 超過 {part2} 的上限 {h_max}mm"
        )

    # ── 1. Member M ──
    section_dim = full_size[1:]
    add_steel_section_entry(result, section_type, section_dim, section_length_h)

    return result
