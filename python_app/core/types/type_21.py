"""
Type 21 計算器 - 側掛式懸臂 U-bolt 支撐 (Cantilever Clamp Support)
固定在 existing steel 上的側掛式支架，無滑動功能

格式: 21-{M}-{HH}{Fig}        (Fig = A/B)
      21-{M}-{HH}{Fig}-{LL}   (Fig = C, LL=L/100)
- 第二段: 型鋼代碼 (L50/L65/L75)
- 第三段: H(數字, *100mm) + Fig字母(A/B/C)
- 第四段: L(數字, *100mm) — 僅 Fig.C 才有

Note 1: U-BOLT (D-68) NOT FURNISHED
Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.

構件 (2 項):
  1. MEMBER "M" (H段): 垂直, 長度 H, A36/SS400
  2. MEMBER "M" (L段): 水平, 長度 L, A36/SS400
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details
from data.type21_table import MEMBER_H_MAX, FIG_L_MAP


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 21: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]
    section_dim = full_size[1:]  # strip leading letter

    # ── 第三段: H + Fig ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 3:
        result.error = f"Type 21: 第三段格式錯誤 ({fullstring})"
        return result

    fig_choice = part3[-1].upper()

    if fig_choice.isdigit():
        result.error = f"Type 21: Fig 代碼不應為數字 ({fullstring})"
        return result

    if fig_choice not in FIG_L_MAP:
        result.error = f"Type 21: 不支援的 Fig 代碼 '{fig_choice}' (僅 A/B/C)"
        return result

    section_length_h = int(part3[:-1]) * 100

    # ── L 值 ──
    fixed_l = FIG_L_MAP[fig_choice]
    if fixed_l is not None:
        section_length_l = fixed_l
    else:
        # Fig.C: 從第四段取得
        part4 = get_part(fullstring, 4)
        if not part4:
            result.error = f"Type 21: Fig.C 需要第四段指定 L 值 ({fullstring})"
            return result
        section_length_l = int(part4) * 100

    # ── H_MAX 驗證 ──
    h_max = MEMBER_H_MAX.get(part2)
    if h_max and section_length_h > h_max:
        result.warnings.append(
            f"H={section_length_h}mm 超過 {part2} 的上限 {h_max}mm"
        )

    # ── 1. Member M (H段 - 垂直) ──
    add_steel_section_entry(result, section_type, section_dim, section_length_h)

    # ── 2. Member M (L段 - 水平) ──
    add_steel_section_entry(result, section_type, section_dim, section_length_l)

    return result
