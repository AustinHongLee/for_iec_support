"""
Type 05 計算器
格式: 05-L50-05L
- 第二段: 型鋼代碼 (L50, L65, L75)
- 第三段: 長度(數字×100mm) + M42代碼(字母)
PDF 限制: 管徑≤2", H≤1500mm, M42僅允許 D/L/P/R
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..m42 import perform_action_by_letter
from data.steel_sections import get_section_details

_ALLOWED_M42_LETTERS = {"D", "L", "P", "R"}
_MAX_H = 1500


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 解析第二段: 型鋼代碼
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 05: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]

    # 解析第三段
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h = int(part3[:-1]) * 100

    # H 超限檢查
    if h > _MAX_H:
        result.warnings.append(
            f"H={h}mm 超出 Type 05 適用範圍 (≤ {_MAX_H}mm)"
        )

    # M42 字母限制檢查
    if letter.upper() not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 05 允許範圍 (僅 D/L/P/R)"
        )

    # 去掉型鋼前綴字母得到純尺寸 (L50*50*6 -> 50*50*6)
    section_dim = full_size[1:]  # 去掉第一個字元

    # 1. 角鐵 垂直段 (H)
    add_steel_section_entry(result, section_type, section_dim, h)

    # 2. 角鐵 水平段 (固定 130mm)
    add_steel_section_entry(result, section_type, section_dim, 130)

    # 3. M42 底板
    perform_action_by_letter(result, letter, full_size)

    return result
