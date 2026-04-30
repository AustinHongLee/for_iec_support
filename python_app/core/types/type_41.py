"""
Type 41 計算器 — 牆面錨定支撐 (D-49)
格式: 41-{n}  (n = 1~9)

BOM:
  FIG-A (41-1~4): ① Member 1 ② Base Plate ③ EXP. BOLT (M-45)
  FIG-B (41-5~9): ① Member 1 ② Member 2 (斜撐) ③ Base Plate ④ EXP. BOLT (M-45)
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from ..material_specs import (
    EXPANSION_BOLT_SUS304,
    STRUCTURAL_A36_SS400,
    SUPPORT_PLATE_A36_SS400,
)
from data.type41_table import get_type41_data
from data.m45_table import get_m45_by_dia


_STRUCTURAL_MATERIAL = STRUCTURAL_A36_SS400
_SUPPORT_PLATE_MATERIAL = SUPPORT_PLATE_A36_SS400
_EXPANSION_BOLT_MATERIAL = EXPANSION_BOLT_SUS304


def _parse_member(spec_str: str):
    """解析 'L75*75*9' → (type='Angle', dim='75*75*9')"""
    if spec_str.startswith("H"):
        return "H Beam", spec_str[1:]
    elif spec_str.startswith("L"):
        return "Angle", spec_str[1:]
    elif spec_str.startswith("C"):
        return "Channel", spec_str[1:]
    return "Angle", spec_str


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 支撐型號 (1~9)
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 41: 缺少支撐型號 (1~9)"
        return result

    data = get_type41_data(part2)
    if not data:
        result.error = f"Type 41: 未知支撐型號 41-{part2}"
        return result

    fig = data["fig"]
    L = data["L"]

    # ① Member 1 (懸臂)
    m1_type, m1_dim = _parse_member(data["member1"])
    add_steel_section_entry(
        result, m1_type, m1_dim, L, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"FIG-{fig} 懸臂, L={L}mm"

    # ② Member 2 (斜撐, 僅 FIG-B)
    if data["member2"]:
        m2_type, m2_dim = _parse_member(data["member2"])
        # 斜撐長度 ≈ L×√2 (45° 對角), 簡化取 L
        brace_len = round(L * 1.414)
        add_steel_section_entry(
            result, m2_type, m2_dim, brace_len,
            material=_STRUCTURAL_MATERIAL,
        )
        result.entries[-1].remark = f"FIG-B 斜撐, ~{brace_len}mm"

    # ③ Base Plate — A283 Gr.C
    bp_t = data["base_plate_t"]
    bd = data["bolt_dist"]
    # Base Plate 大小取 bolt_dist + 2*b 的正方形
    bp_size = bd + 2 * data["b"]
    add_plate_entry(result, plate_a=bp_size, plate_b=bp_size,
                    plate_thickness=bp_t, plate_name="BASE PLATE",
                        plate_role="base_plate",
                    material=_SUPPORT_PLATE_MATERIAL)
    result.entries[-1].remark = f"{bp_size}x{bp_size}x{bp_t}t, A283 Gr.C"

    # ④ EXP. BOLT (M-45)
    eb_dia = data["exp_bolt_dia"]
    m45 = get_m45_by_dia(eb_dia)
    eb_qty = 4  # 4 EA standard
    if m45:
        add_custom_entry(result, name="EXP.BOLT", spec=f"EB-{eb_dia}",
                         material=_EXPANSION_BOLT_MATERIAL, quantity=eb_qty,
                         unit_weight=m45["L"] / 1000 * 0.5, unit="SET")
        result.entries[-1].remark = (
            f"M-45, Ø{eb_dia}, L={m45['L']}mm, "
            f"容許拉力={m45['tensile_kg']}kg, 剪力={m45['shear_kg']}kg"
        )
    else:
        add_custom_entry(result, name="EXP.BOLT", spec=eb_dia,
                         material=_EXPANSION_BOLT_MATERIAL, quantity=eb_qty,
                         unit_weight=0.5, unit="SET")

    return result
