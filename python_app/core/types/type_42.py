"""
Type 42 計算器 — Trunnion 曲面設備斜撐支撐 (D-50)
格式: 42-{line_size}B-{MEMBER}-{H} {A|B}

H = F - √(R² - E²)  (圓弧反算)
G = g_coeff × H + g_offset (斜撐長)

BOM (5 筆): ① 主梁(H) ② 斜撐(G) ③ Trunnion ④ C/S Shim ⑤ M.B.
"""
import math
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.steel_sections import get_section_details
from data.type42_table import get_type42_member, get_type42_pipe


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")
_ANCHOR_BOLT_MATERIAL = _material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑 (如 8B)
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 42: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)
    pipe_data = get_type42_pipe(line_size)
    if not pipe_data:
        result.error = f"Type 42: 管徑 {part2} ({line_size}\") 不在查表範圍 (2\"~24\")"
        return result

    # 第三段: 型鋼代碼 (如 C125)
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 42: 缺少型鋼代碼"
        return result
    member_code = part3.strip()
    member_data = get_type42_member(member_code)
    if not member_data:
        result.error = f"Type 42: 未知型鋼 {member_code} (支援 L75~C200)"
        return result
    details = get_section_details(member_code)
    if not details:
        result.error = f"Type 42: steel_sections 無 {member_code}"
        return result

    # 第四段: "H FIG" (如 "500 A" 或 "500 B")
    part4 = get_part(fullstring, 4)
    if not part4:
        result.error = "Type 42: 缺少 H 值與 FIG 類型"
        return result
    parts4 = part4.strip().split()
    h_mm = int(parts4[0])
    fig_type = parts4[1].upper() if len(parts4) > 1 else "A"

    # 超限檢查
    h_max = member_data["H_MAX"]
    if h_mm > h_max:
        result.warnings.append(f"H={h_mm}mm 超出 {member_code} 上限 ({h_max}mm)")

    # 計算斜撐長度 G
    fig_formula = member_data.get(fig_type)
    if not fig_formula:
        result.error = f"Type 42: FIG-{fig_type} 無效 (A=30°, B=45°)"
        return result
    g_val = round(fig_formula["g_coeff"] * h_mm + fig_formula["g_offset"])

    section_type = details["type"]
    section_dim = details["size"][1:]
    theta = 30 if fig_type == "A" else 45
    E = pipe_data["E"]
    trunnion = pipe_data["trunnion"]

    # ① 主梁 — length = H
    add_steel_section_entry(
        result, section_type, section_dim, h_mm, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"主梁 (立柱), H={h_mm}mm"

    # ② 斜撐 — length = G
    add_steel_section_entry(
        result, section_type, section_dim, g_val, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"斜撐 FIG-{fig_type}(θ={theta}°), G={g_val}mm"

    # ③ Trunnion (管件, 以 custom entry 處理)
    add_custom_entry(result, name="TRUNNION", spec=trunnion,
                     material=_SUPPORT_PIPE_MATERIAL, quantity=1,
                     unit_weight=2.0, unit="SET")
    result.entries[-1].remark = f"Trunnion {trunnion}, E={E}mm, 需 D-72/73/74 校核"

    # ④ C/S Shim
    add_plate_entry(result, plate_a=member_data["C"], plate_b=member_data["D"],
                    plate_thickness=6, plate_name="C/S SHIM",
                        plate_role="shim_plate",
                    material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
    result.entries[-1].remark = "現場微調用"

    # ⑤ M.B. (3/4"×50)
    add_custom_entry(result, name="M.BOLT", spec='3/4"x50',
                     material=_ANCHOR_BOLT_MATERIAL, quantity=2,
                     unit_weight=0.8, unit="SET")
    result.entries[-1].remark = "Ø22 孔固定"

    return result
