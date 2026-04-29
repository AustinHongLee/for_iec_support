"""
Type 48 計算器 — Drain Hub 偏移底座支撐 (D-59)
格式: 48-{line_size}{mat_sym}
  例: 48-2, 48-4(A), 48-6(B)

mat_sym: (空)=CS, (A)=AS, (B)=SS

BOM (1 筆): ① PLATE (150×100×6 or 9)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts
from ..plate import add_plate_entry
from data.type48_table import get_type48_data, TYPE48_MATERIAL_SYMBOL


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑 + 材質符號 (如 "2", "4(A)", "6(B)")
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 48: 缺少管徑"
        return result

    # 拆分材質符號
    size_str, mat_paren = extract_parts(part2)
    line_size = get_lookup_value(size_str)

    data = get_type48_data(line_size)
    if not data:
        result.error = f"Type 48: 管徑 {size_str} ({line_size}\") 不在範圍 (1/2\"~6\")"
        return result

    # 材質判定
    mat_map = {"": "A36/SS400", "(A)": "AS", "(B)": "SUS304"}
    material = mat_map.get(mat_paren, "A36/SS400")

    # ① PLATE — 150×100×(6 or 9)
    add_plate_entry(result, plate_a=data["plate_a"], plate_b=data["plate_b"],
                    plate_thickness=data["plate_t"],
                    plate_name="PLATE",
                    material=material, plate_qty=1)
    result.entries[-1].remark = (
        f"Drain Hub 偏移底座, {data['plate_size']}, "
        f"offset=100mm, 全焊接(6V)"
    )

    return result
