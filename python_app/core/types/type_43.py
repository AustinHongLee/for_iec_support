"""
Type 43 計算器 — Trunnion 曲面設備全約束支撐 (D-51, D-52)
格式: 43-{line_size}B-{MEMBER}-{H} {A|B}

H = K - √(R² - Q²) - t - E - 30
S/N 依公式表計算

BOM (7 筆): ① 主梁(H+A) ② 斜撐(N) ③ Trunnion ④ LUG PLATE TYPE-C (M-34)
            ⑤ LUG PLATE TYPE-D/E (M-35/36) ⑥ K BOLT ⑦ C/S Shim
"""
from ..models import AnalysisResult
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
from data.type43_table import (get_type43_data, get_type43_formula,
                                get_type43_pipe, get_type43_h_max)
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")
_PLATE_LUG_MATERIAL = _material_spec(HardwareKind.PLATE_LUG, "A36/SS400")
_ANCHOR_BOLT_MATERIAL = _material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 43: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)
    pipe_data = get_type43_pipe(line_size)
    if not pipe_data:
        result.error = f"Type 43: 管徑 {part2} ({line_size}\") 不在查表範圍 (2\"~24\")"
        return result

    # 第三段: 型鋼代碼
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 43: 缺少型鋼代碼"
        return result
    member_code = part3.strip()
    t43_data = get_type43_data(member_code)
    if not t43_data:
        result.error = f"Type 43: 未知型鋼 {member_code} (支援 L75~C200)"
        return result
    details = get_section_details(member_code)
    if not details:
        result.error = f"Type 43: steel_sections 無 {member_code}"
        return result

    # 第四段: "H FIG"
    part4 = get_part(fullstring, 4)
    if not part4:
        result.error = "Type 43: 缺少 H 值與 FIG 類型"
        return result
    parts4 = part4.strip().split()
    h_mm = int(parts4[0])
    fig_type = parts4[1].upper() if len(parts4) > 1 else "A"

    # 超限檢查
    h_max = get_type43_h_max(member_code)
    if h_max and h_mm > h_max:
        result.warnings.append(f"H={h_mm}mm 超出 {member_code} 上限 ({h_max}mm)")

    # 計算 S/N
    formula = get_type43_formula(member_code, fig_type)
    if not formula:
        result.error = f"Type 43: 無 {member_code} FIG-{fig_type} 公式"
        return result
    s_val = round(formula["s_coeff"] * h_mm + formula["s_offset"])
    n_val = round(formula["n_coeff"] * h_mm + formula["n_offset"])
    b_val = formula["B"]

    section_type = details["type"]
    section_dim = details["size"][1:]
    theta = 30 if fig_type == "A" else 45
    Q = pipe_data["Q"]
    trunnion = pipe_data["trunnion"]

    # ① 主梁 — length = H + A
    main_len = h_mm + t43_data["A"]
    add_steel_section_entry(
        result, section_type, section_dim, main_len, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"主梁, H={h_mm}+A={t43_data['A']}={main_len}mm"

    # ② 斜撐 — length = N
    add_steel_section_entry(
        result, section_type, section_dim, n_val, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"斜撐 FIG-{fig_type}(θ={theta}°), S={s_val}, N={n_val}"

    # ③ Trunnion
    add_custom_entry(result, name="TRUNNION", spec=trunnion,
                     material=_SUPPORT_PIPE_MATERIAL, quantity=1,
                     unit_weight=2.0, unit="SET")
    result.entries[-1].remark = f"Trunnion {trunnion}, Q={Q}mm, 需 D-72/73/74 校核"

    # ④ LUG PLATE TYPE-C (M-34, DETAIL Y — 管線端)
    m34 = get_m34_by_member(member_code)
    if m34:
        add_plate_entry(result, plate_a=m34["A"], plate_b=m34["B"],
                        plate_thickness=m34["T"], plate_name="LUG PLATE TYPE-C",
                            plate_role="lug_plate",
                        material=_PLATE_LUG_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"DETAIL Y(管線端), {m34['type']}"
    else:
        result.warnings.append(f"M-34 無 {member_code} 對應的 LUG PLATE")

    # ⑤ LUG PLATE TYPE-D/E (M-35 or M-36, DETAIL Z — Vessel端)
    if fig_type == "B":
        m_dz = get_m35_by_member(member_code)
        dz_label = "TYPE-D"
    else:
        m_dz = get_m36_by_member(member_code)
        dz_label = "TYPE-E"
    if m_dz:
        add_plate_entry(result, plate_a=m_dz["A"], plate_b=m_dz["B"],
                        plate_thickness=m_dz["T"],
                        plate_name=f"LUG PLATE {dz_label}",
                            plate_role="lug_plate",
                        material=_PLATE_LUG_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"DETAIL Z(Vessel端), {dz_label}"

    # ⑥ K BOLT — 3/4"x50, ×2 SET
    add_custom_entry(result, name="K BOLT", spec='3/4"x50',
                     material=_ANCHOR_BOLT_MATERIAL, quantity=2,
                     unit_weight=0.8, unit="SET")

    # ⑦ C/S Shim
    add_plate_entry(result, plate_a=t43_data["C"], plate_b=b_val,
                    plate_thickness=6, plate_name="C/S SHIM",
                        plate_role="shim_plate",
                    material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
    result.entries[-1].remark = "現場微調用"

    return result
