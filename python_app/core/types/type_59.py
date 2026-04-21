"""
Type 59 計算器 — Lug Plate Support for Shoe / Bare Pipe
圖號: D-70
格式: 59-{size}B-{FIG}{material_symbol?}
例: 59-6B-A, 59-14B-B(S)
FIG-A: insulated pipe, 配 D-63 shoe (NOT FURNISHED)
FIG-B: bare pipe, 配 D-68 U-bolt
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from data.type59_table import get_type59_dims, get_type59_material


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析 ──
    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)

    if not part2:
        result.error = "缺少管徑欄位"
        return result

    size_str = part2.replace("B", "").strip()
    pipe_size = get_lookup_value(size_str)

    # part3 = "A" or "B(S)" or "A(A)" etc.
    fig = "A"
    mat_symbol = ""
    if part3:
        p3 = part3.strip()
        if "(" in p3:
            fig_part, paren = extract_parts(p3)
            fig = fig_part.upper() if fig_part else "A"
            mat_symbol = paren  # e.g. "(S)"
        else:
            fig = p3.upper()

    if fig not in ("A", "B"):
        fig = "A"

    # ── 查表 ──
    dims = get_type59_dims(size_str)
    if not dims:
        result.error = f"管徑 {size_str}\" 不在 Type 59 範圍內 (2-1/2\" & smaller, 3\"~8\", 10\"~14\")"
        return result

    # 材料
    mat_info = get_type59_material(mat_symbol)
    material = mat_info["material"] if mat_info else "A283 Gr.C"

    # 板厚：不鏽鋼使用 S_T（圖紙 D-70 "FOR STAINLESS STEEL ONLY" 欄）
    # large (10"~14") 該欄為 "–"（無定義），發警告並沿用 T=12
    thickness = dims["T"]
    s_t = dims.get("S_T")
    if mat_symbol == "(S)":
        if s_t is not None:
            thickness = s_t
        else:
            result.warnings.append(
                f"Type 59 大管徑 (10\"~14\") 無不鏽鋼板厚定義 (D-70 TABLE A SS欄為 \"—\")，沿用 T={dims['T']}mm"
            )

    # 板片數量：D=None → 1片（小/中管徑）；D≠None → 2片（大管徑）
    plate_qty = dims["plate_qty"]

    # ① Lug Plate ×plate_qty (A×B×thickness)
    add_plate_entry(
        result,
        dims["A"],
        dims["B"],
        thickness,
        "LUG PLATE",
        material,
        plate_qty,
    )

    # ② 中間件 (依 FIG)
    if fig == "A":
        # D-63 shoe — NOT FURNISHED, 只記 remark
        result.warnings.append("FIG-A: Pipe Shoe (D-63) NOT FURNISHED, 需另行計算")
    else:
        # FIG-B: U-bolt (D-68 = TYPE-57)
        # U-bolt 估算：依管徑粗估
        ubolt_wt = 0.3 if pipe_size <= 2.5 else (0.8 if pipe_size <= 8 else 1.5)
        add_custom_entry(result, "U-BOLT", f"D-68, {size_str}\"", "A36/SS400", 1, ubolt_wt, "SET")

    return result
