"""
Type 03 計算器
格式: 03-{pipe_size}-{H}{M42_letter}
  例: 03-1B-05N
- 第二段: 管徑 (1B = 1", 2B = 2")  ≤ 2" 小管徑
- 第三段: 高度(數字×100mm) + M42代碼(字母)

構件:
  1. 角鐵 L-75×75×9 (固定規格, 兩支: 垂直H + 水平130mm)
  2. U-bolt (依管徑, SUS304, 1 SET)
  3. M42 底板 (依字母, 用角鐵尺寸 L75*75*9 查表)
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..m42 import perform_action_by_letter

# PDF 規範: Supported Line Size ≤ 2"
_MAX_LINE_SIZE = 2.0


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    pipe_size = get_part(fullstring, 2)

    # 管徑超限檢查
    size_val = get_lookup_value(pipe_size)
    if size_val > _MAX_LINE_SIZE:
        result.warnings.append(
            f"管徑 {pipe_size} ({size_val}\") 超出 Type 03 適用範圍 (≤ 2\")"
        )

    # 第三段: H高度 + M42字母
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h = int(part3[:-1]) * 100  # 05 -> 500mm

    # 1. 角鐵 L-75×75×9, 垂直段 (H)
    add_steel_section_entry(result, "Angle", "75*75*9", h)

    # 2. 角鐵 L-75×75×9, 水平段 (固定 130mm)
    add_steel_section_entry(result, "Angle", "75*75*9", 130)

    # 2. U-bolt
    _add_ubolt_entry(result, pipe_size)

    # 3. M42 底板 (用角鐵尺寸查表)
    perform_action_by_letter(result, letter, "L75*75*9")

    return result


def _add_ubolt_entry(result: AnalysisResult, pipe_size: str):
    """U-bolt: 1 SET, 1kg, SUS304"""
    entry = AnalysisEntry()
    entry.name = "U.bolt"
    entry.spec = f"UB-{pipe_size}"
    entry.material = "SUS304"
    entry.quantity = 1
    entry.unit_weight = 1
    entry.total_weight = 1
    entry.unit = "SET"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 1
    entry.weight_output = 1
    entry.weight_per_unit = 1
    entry.category = "管路類"
    result.add_entry(entry)
