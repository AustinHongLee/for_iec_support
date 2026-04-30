"""
Type 47 計算器 — 曲面設備直接夾持支撐含 D-80 接口 (D-57/D-58)
格式: 47-{line_size}B-{MEMBER}-{H} {A|B}

H = P - √(R² - Q²) - 60 - t
有 Lug Plate, 管線端連接 D-80, 2"~14"
Detail Y=Vessel端 M-35/36, Detail Z=管線端 M-34 (同 Type 45)

BOM: ① Channel(H+A) ② L50斜撐(條件: H>1140) ③ LUG PLATE TYPE-C (M-34)
     ④ LUG PLATE TYPE-D/E (M-35/36) ⑤ K BOLT ×2
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from ..material_specs import (
    ANCHOR_BOLT_SUS304,
    PLATE_LUG_A36_SS400,
    STRUCTURAL_A36_SS400,
)
from data.steel_sections import get_section_details
from data.type46_table import (get_type46_47_q, TYPE47_BRACE, TYPE47_BRACE_H_MIN,
                                TYPE47_MEMBER)
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member


_STRUCTURAL_MATERIAL = STRUCTURAL_A36_SS400
_PLATE_LUG_MATERIAL = PLATE_LUG_A36_SS400
_ANCHOR_BOLT_MATERIAL = ANCHOR_BOLT_SUS304


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 47: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)
    q_val = get_type46_47_q(line_size)
    if q_val is None:
        result.error = f"Type 47: 管徑 {part2} ({line_size}\") 不在範圍 (2\"~14\")"
        return result

    # 第三段: 型鋼代碼
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 47: 缺少型鋼代碼"
        return result
    member_code = part3.strip()
    t47_member = TYPE47_MEMBER.get(member_code)
    if not t47_member:
        result.error = f"Type 47: 未知型鋼 {member_code} (支援 C100/C125/C150)"
        return result
    details = get_section_details(member_code)
    if not details:
        result.error = f"Type 47: steel_sections 無 {member_code}"
        return result

    # 第四段: "H FIG"
    part4 = get_part(fullstring, 4)
    if not part4:
        result.error = "Type 47: 缺少 H 值與 FIG 類型"
        return result
    parts4 = part4.strip().split()
    h_mm = int(parts4[0])
    fig_type = parts4[1].upper() if len(parts4) > 1 else "A"

    section_type = details["type"]
    section_dim = details["size"][1:]
    theta = 30 if fig_type == "A" else 45

    # ① Channel 主柱 — length = H + A
    main_len = h_mm + t47_member["A"]
    add_steel_section_entry(
        result, section_type, section_dim, main_len, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"主柱, H={h_mm}+A={t47_member['A']}={main_len}mm"

    # ② L50 斜撐 (條件: H > 1140)
    if h_mm > TYPE47_BRACE_H_MIN:
        brace = TYPE47_BRACE.get(fig_type)
        if brace:
            add_steel_section_entry(
                result, "Angle", "50*50*6", brace["length"],
                material=_STRUCTURAL_MATERIAL,
            )
            result.entries[-1].remark = (
                f"斜撐 FIG-{fig_type}(θ={theta}°), "
                f"L={brace['length']}mm, H>{TYPE47_BRACE_H_MIN}"
            )

    # ③ LUG PLATE TYPE-C (M-34, Detail Z — 管線端)
    m34 = get_m34_by_member(member_code)
    if m34:
        add_plate_entry(result, plate_a=m34["A"], plate_b=m34["B"],
                        plate_thickness=m34["T"], plate_name="LUG PLATE TYPE-C",
                            plate_role="lug_plate",
                        material=_PLATE_LUG_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"Detail Z(管線端), {m34['type']}"

    # ④ LUG PLATE TYPE-D/E (M-35/36, Detail Y — Vessel端)
    if fig_type == "B":
        m_dy = get_m35_by_member(member_code)
        dy_label = "TYPE-D"
    else:
        m_dy = get_m36_by_member(member_code)
        dy_label = "TYPE-E"
    if m_dy:
        add_plate_entry(result, plate_a=m_dy["A"], plate_b=m_dy["B"],
                        plate_thickness=m_dy["T"],
                        plate_name=f"LUG PLATE {dy_label}",
                            plate_role="lug_plate",
                        material=_PLATE_LUG_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"Detail Y(Vessel端), {dy_label}"

    # ⑤ K BOLT ×2
    add_custom_entry(result, name="K BOLT", spec='3/4"x50',
                     material=_ANCHOR_BOLT_MATERIAL, quantity=1,
                     unit_weight=0.8, unit="SET")
    result.entries[-1].remark = "Detail Z(管線端), Ø22"

    add_custom_entry(result, name="K BOLT", spec='5/8"x40',
                     material=_ANCHOR_BOLT_MATERIAL, quantity=1,
                     unit_weight=0.5, unit="SET")
    result.entries[-1].remark = "Detail Y(Vessel端), Ø19"

    # NOTE: D-80 Shoe 由 Type 66 獨立計算
    result.warnings.append("管線端 D-80 Shoe 需另行計算 (Type 66)")

    return result
