"""
Type 49 計算器 — 立管固定支撐 (D-60)
格式: 49-{line_size}{fig}{mat_sym}
  例: 49-8A, 49-2B, 49-10A(A)

FIG-A: ≥3", Riser Clamp TYPE-A (M-11) + Lug Plate TYPE-P (M-41)
FIG-B: <3", Riser Clamp TYPE-B (M-12) 直接壓於 Base

BOM:
  FIG-A: ① RISER CLAMP TYPE-A ② LUG PLATE TYPE-P
  FIG-B: ① RISER CLAMP TYPE-B
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts
from ..bolt import add_custom_entry


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: {line_size}{fig}{mat_sym}
    # 例: "8A", "2B", "10A(A)"
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 49: 缺少管徑與 FIG 類型"
        return result

    # 拆分材質括號
    main_str, mat_paren = extract_parts(part2)

    # 最後一個字母是 FIG (A 或 B)
    if main_str and main_str[-1].upper() in ("A", "B"):
        fig = main_str[-1].upper()
        size_str = main_str[:-1]
    else:
        result.error = f"Type 49: 無法解析 FIG 類型 (需以 A 或 B 結尾): {part2}"
        return result

    line_size = get_lookup_value(size_str)
    if line_size <= 0:
        result.error = f"Type 49: 無效管徑 '{size_str}'"
        return result

    # 材質
    mat_map = {"": "A36/SS400", "(A)": "AS", "(B)": "SUS304"}
    material = mat_map.get(mat_paren, "A36/SS400")

    if fig == "A":
        # FIG-A: ≥3", M-11 Riser Clamp TYPE-A + M-41 Lug Plate TYPE-P
        if line_size < 3:
            result.warnings.append(f"FIG-A 通常用於 ≥3\", 目前管徑={line_size}\"")

        # ① RISER CLAMP TYPE-A (M-11)
        add_custom_entry(result, name="RISER CLAMP TYPE-A",
                         spec=f'{size_str}"',
                         material=material, quantity=1,
                         unit_weight=max(1.0, line_size * 0.5), unit="SET")
        result.entries[-1].remark = "SEE M-11"

        # ② LUG PLATE TYPE-P (M-41)
        add_custom_entry(result, name="LUG PLATE TYPE-P",
                         spec=f'{size_str}"',
                         material=material, quantity=1,
                         unit_weight=max(0.5, line_size * 0.3), unit="PC")
        result.entries[-1].remark = "SEE M-41"
    else:
        # FIG-B: <3", M-12 Riser Clamp TYPE-B
        if line_size >= 3:
            result.warnings.append(f"FIG-B 通常用於 <3\", 目前管徑={line_size}\"")

        # ① RISER CLAMP TYPE-B (M-12)
        add_custom_entry(result, name="RISER CLAMP TYPE-B",
                         spec=f'{size_str}"',
                         material=material, quantity=1,
                         unit_weight=max(0.5, line_size * 0.3), unit="SET")
        result.entries[-1].remark = "SEE M-12, 直接壓於 Base"

    return result
