"""
Type 59 計算器 — Detail Z wing lug plate
圖號: D-70
格式: 59-{size}B-{FIG}{material_symbol?}
例: 59-6B-A, 59-14B-B(S)

Type 59 BOM 永遠只產生 TYPE 59 翼形角板。FIG 仍保留在輸入格式中，
但不會追加 U-bolt、finished hex nut 或 shoe reference。
"""
from math import sqrt
from hashlib import sha1

from ..models import AnalysisResult
from ..parser import get_part, extract_parts, parse_pipe_size
from ..plate import add_plate_entry
from data.type59_table import get_type59_dims, get_type59_material


_LUG_DISPLAY_NAME = "TYPE 59 翼形角板"
_LUG_SHAPE_KIND = "wing"


def _fmt_dim(value) -> str:
    return f"{float(value):g}"


def _dim_token(value) -> str:
    return _fmt_dim(value).replace(".", "p")


def _lug_part_key(dims: dict, thickness: float) -> str:
    return (
        "59_lug_plate_wing"
        f"_a{_dim_token(dims['A'])}"
        f"_b{_dim_token(dims['B'])}"
        "_p25"
        f"_c{_dim_token(dims['C'])}"
        f"_t{_dim_token(thickness)}"
    )


def _lug_stock_id(part_key: str, material: str) -> str:
    seed = f"{part_key}|material={material}"
    digest = sha1(seed.encode("utf-8")).hexdigest()[:8].upper()
    return f"PL-{digest}"


def _lug_net_geometry(dims: dict) -> dict[str, float]:
    a = float(dims["A"])
    b = float(dims["B"])
    c = float(dims["C"])
    cut_base = b - c
    cut_height = a - 25
    cut_hypotenuse = sqrt(cut_base**2 + cut_height**2)
    gross_area = a * b
    cutout_area = cut_base * cut_height / 2
    net_area = gross_area - cutout_area
    return {
        "gross_area": gross_area,
        "cut_base": cut_base,
        "cut_height": cut_height,
        "cut_hypotenuse": cut_hypotenuse,
        "cutout_area": cutout_area,
        "net_area": net_area,
    }


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析 ──
    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)

    if not part2:
        result.error = "缺少管徑欄位"
        return result

    size_str = parse_pipe_size(part2)

    # part3 = "A" or "B(S)" or "A(A)" etc.
    # FIG is kept only for legacy designation compatibility; BOM is always lug plate only.
    mat_symbol = ""
    if part3:
        p3 = part3.strip()
        if "(" in p3:
            _, paren = extract_parts(p3)
            mat_symbol = paren  # e.g. "(S)"

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

    # Detail Z is an irregular lug plate: A high, B base, 25 toe, C top flat, t thick.
    # Net weight is the A x B gross rectangle minus the missing right triangle.
    lug_shape_spec = (
        f"A{_fmt_dim(dims['A'])} x B{_fmt_dim(dims['B'])}"
        f" x P25 x C{_fmt_dim(dims['C'])} x t{_fmt_dim(thickness)}"
    )
    geom = _lug_net_geometry(dims)
    area_formula = (
        f"{_fmt_dim(dims['A'])}×{_fmt_dim(dims['B'])}"
        f" - ({_fmt_dim(dims['B'])}-{_fmt_dim(dims['C'])})"
        f"×({_fmt_dim(dims['A'])}-25)/2"
    )
    part_key = _lug_part_key(dims, thickness)
    stock_id = _lug_stock_id(part_key, material)

    # ① Lug Plate ×plate_qty (net area from gross rectangle minus missing triangle)
    add_plate_entry(
        result,
        dims["A"],
        dims["B"],
        thickness,
        _LUG_DISPLAY_NAME,
        material,
        plate_qty,
        plate_role="lug_plate",
        formula=area_formula,
        notes_zh=(
            f"淨面積 {area_formula} = {_fmt_dim(geom['net_area'])} mm2; "
            f"缺角三角形 底{_fmt_dim(geom['cut_base'])} 高{_fmt_dim(geom['cut_height'])} "
            f"斜邊{geom['cut_hypotenuse']:.1f} mm"
        ),
        shape_spec=lug_shape_spec,
        shape_kind=_LUG_SHAPE_KIND,
        gross_area_mm2=geom["gross_area"],
        cutout_area_mm2=geom["cutout_area"],
        net_area_mm2=geom["net_area"],
    )
    result.entries[-1].part_key = part_key
    result.entries[-1].stock_id = stock_id
    result.entries[-1].remark = lug_shape_spec

    return result
