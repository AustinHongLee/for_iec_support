"""
Type 06 計算器
格式: 06-{member}-{HL}-{AB}  (第4段可省略)
  例: 06-L50-0510-0401
- 第二段: 型鋼代碼 Member C (L50, L65, L75)
- 第三段: H(前2碼×100mm) + L(後2碼×100mm)
- 第四段: A(前2碼×100mm) + B(後2碼×100mm), 選填, 預設 A=B=L/2

PDF 限制: H≤1500mm, L≤1000mm
構件: 角鐵兩支(垂直H + 水平L), M-37 Lug Plate 不含在材料內
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

_MAX_H = 1500
_MAX_L = 1000


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 型鋼代碼
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 06: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]
    full_size = details["size"]
    section_dim = full_size[1:]  # L50*50*6 -> 50*50*6

    # 第三段: H + L
    part3 = get_part(fullstring, 3)
    h = int(part3[:2]) * 100
    l = int(part3[2:]) * 100

    # H 超限檢查
    if h > _MAX_H:
        result.warnings.append(
            f"H={h}mm 超出 Type 06 適用範圍 (≤ {_MAX_H}mm)"
        )

    # L 超限檢查
    if l > _MAX_L:
        result.warnings.append(
            f"L={l}mm 超出 Type 06 適用範圍 (≤ {_MAX_L}mm)"
        )

    # 1. 角鐵 垂直段 (H)
    add_steel_section_entry(result, section_type, section_dim, h)

    # 2. 角鐵 水平段 (L)
    add_steel_section_entry(result, section_type, section_dim, l)

    return result
