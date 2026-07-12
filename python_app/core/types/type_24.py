"""
Type 24 計算器
格式: 24-L50-05
- 第二段: 型鋼代碼 (L50, L75)
- 第三段: H 高度 (數字×100mm)

結構: 單一角鋼貼附在結構面上，U-bolt 固定管線
- Member "M": L50×50×6 或 L75×75×9
- 偏距固定 100mm (pipe center 到牆面)
- H 為唯一可變尺寸
- U-bolt (D-68) NOT FURNISHED — 不計入
- 無 M42 底板

H MAX 限制:
  L50×50×6 → 1000mm
  L75×75×9 → 1500mm
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

_FIXED_OFFSET = 100  # mm, pipe center 到結構面

_H_MAX = {
    "L50": 1000,
    "L75": 1500,
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 24: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle"
    full_size = details["size"]      # "L50*50*6"

    # ── 第三段: H 高度 ──
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 24: 缺少第三段 (H 高度)"
        return result

    try:
        h = int(part3) * 100
    except ValueError:
        result.error = f"Type 24: 無法解析 H 值 '{part3}'"
        return result

    # H 超限檢查
    h_max = _H_MAX.get(part2, 1500)
    if h > h_max:
        result.warnings.append(
            f"H={h}mm 超出 {part2} 適用範圍 (≤ {h_max}mm)"
        )

    # 去掉型鋼前綴字母 (L50*50*6 -> 50*50*6)
    section_dim = full_size[1:]

    # ── 角鋼長度 = H (VBA 原始邏輯: Total_Length = H) ──
    # 100mm 偏距是角鐵 L 型 leg 的自然偏移，不額外加長
    angle_length = h

    # 1. 角鐵 (一支)
    add_steel_section_entry(result, section_type, section_dim, angle_length)

    return result
