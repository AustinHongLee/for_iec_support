"""
Type 22 計算器 - 落地式懸臂 U-bolt 支撐 (Ground Cantilever Support)
Type 21 的落地版: 有 base plate + M42 下部構件

格式: 22-{M}-{HH}({Fig}){M42}
      22-{M}-{HH}(C){M42}-{LL}      (Fig = C only, LL=L/100)
- 第二段: 型鋼代碼 (L50/L65/L75)
- 第三段: H(數字) + (Fig字母 A/B/C) + M42字母
- 第四段(Fig.C only): L dimension (*100mm)

Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
現場 designation 的 M42 字母保留在括號後，例如 12(A)X => Fig=A, M42=X。

構件 (2 + M42):
  1. MEMBER "M" (H段): 垂直, 長度 H, A36/SS400
  2. MEMBER "M" (L段): 水平, 長度 L, A36/SS400
  3. M42 下部構件 (PerformActionByLetter)
"""
import re

from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..m42 import perform_action_by_letter
from data.steel_sections import get_section_details
from data.type22_table import MEMBER_H_MAX, FIG_L_MAP, ALLOWED_M42_LETTERS


_FORMAT_HELP = "22-{M}-{HH}({Fig}){M42} 或 22-{M}-{HH}(C){M42}-{LL}"


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 22: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]
    section_dim = full_size[1:]  # strip leading letter

    parts = fullstring.split("-")
    if len(parts) not in (3, 4):
        result.error = f"Type 22: Designation 格式錯誤，應為 {_FORMAT_HELP}"
        return result

    # ── 第三段: H + (Fig) + M42 letter ──
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = f"Type 22: 第三段格式錯誤，應為 HH(Fig)M42，例如 12(A)X"
        return result

    match = re.fullmatch(r"(\d+)\(([ABCabc])\)([A-Za-z])", part3)
    if not match:
        result.error = f"Type 22: 第三段格式錯誤，應為 HH(Fig)M42，例如 12(A)X"
        return result

    h_digits = match.group(1)
    fig_choice = match.group(2).upper()
    m42_letter = match.group(3).upper()

    if not h_digits.isdigit():
        result.error = f"Type 22: H 值無法解析 ({fullstring})"
        return result

    if fig_choice not in FIG_L_MAP:
        result.error = f"Type 22: 不支援的 Fig 代碼 '{fig_choice}' (僅 A/B/C)"
        return result

    if m42_letter not in ALLOWED_M42_LETTERS:
        allowed = "/".join(sorted(ALLOWED_M42_LETTERS))
        result.error = (
            f"Type 22: 不支援的 M42 字母 '{m42_letter}' "
            f"(允許: {allowed})"
        )
        return result

    section_length_h = int(h_digits) * 100

    # ── L 值 ──
    fixed_l = FIG_L_MAP[fig_choice]
    if fixed_l is not None:
        if len(parts) == 4:
            result.error = f"Type 22: 只有 Fig.C 可指定第四段 L 值，應為 {_FORMAT_HELP}"
            return result
        section_length_l = fixed_l
    else:
        # Fig.C: 從第四段取得
        part4 = get_part(fullstring, 4)
        if not part4:
            result.error = f"Type 22: Fig.C 需要第四段指定 L 值 ({fullstring})"
            return result
        if not part4.isdigit():
            result.error = f"Type 22: Fig.C 的 L 值須為數字 ({fullstring})"
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

    # ── 3. M42 下部構件 ──
    perform_action_by_letter(result, m42_letter, full_size)

    return result
