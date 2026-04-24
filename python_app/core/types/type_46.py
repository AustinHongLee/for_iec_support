"""
Type 46 計算器 — 曲面設備直接支撐含 D-80 接口 (D-56)
格式: 46-{line_size}B-{MEMBER}-{H} {A|B}

H = P - √(R² - Q²)
無 Trunnion, 無 Lug Plate, 管線端連接 D-80, 2"~14"

BOM: ① Channel(H) ② L50斜撐(條件: H>1200) ③ Plate 90×45×6 ④ M.B.
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
from data.type46_table import (get_type46_47_q, TYPE46_BRACE, TYPE46_BRACE_H_MIN)


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")
_ANCHOR_BOLT_MATERIAL = _material_spec(HardwareKind.ANCHOR_BOLT, "SUS304")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 46: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)
    q_val = get_type46_47_q(line_size)
    if q_val is None:
        result.error = f"Type 46: 管徑 {part2} ({line_size}\") 不在範圍 (2\"~14\")"
        return result

    # 第三段: 型鋼代碼
    part3 = get_part(fullstring, 3)
    if not part3:
        result.error = "Type 46: 缺少型鋼代碼"
        return result
    member_code = part3.strip()
    details = get_section_details(member_code)
    if not details:
        result.error = f"Type 46: 未知型鋼 {member_code} (支援 C100/C125/C150)"
        return result

    # 第四段: "H FIG"
    part4 = get_part(fullstring, 4)
    if not part4:
        result.error = "Type 46: 缺少 H 值與 FIG 類型"
        return result
    parts4 = part4.strip().split()
    h_mm = int(parts4[0])
    fig_type = parts4[1].upper() if len(parts4) > 1 else "A"

    section_type = details["type"]
    section_dim = details["size"][1:]
    theta = 30 if fig_type == "A" else 45

    # ① Channel 主柱 — length = H
    add_steel_section_entry(
        result, section_type, section_dim, h_mm, material=_STRUCTURAL_MATERIAL
    )
    result.entries[-1].remark = f"主柱, H={h_mm}mm, Q={q_val}mm (含D-80偏移)"

    # ② L50 斜撐 (條件: H > 1200)
    if h_mm > TYPE46_BRACE_H_MIN:
        brace = TYPE46_BRACE.get(fig_type)
        if brace:
            add_steel_section_entry(
                result, "Angle", "50*50*6", brace["length"],
                material=_STRUCTURAL_MATERIAL,
            )
            result.entries[-1].remark = (
                f"斜撐 FIG-{fig_type}(θ={theta}°), "
                f"L={brace['length']}mm, H>{TYPE46_BRACE_H_MIN}"
            )

    # ③ Plate 90×45×6 (承托板)
    add_plate_entry(result, plate_a=90, plate_b=45,
                    plate_thickness=6, plate_name="PLATE",
                    material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
    result.entries[-1].remark = "承托板"

    # ④ M.B. 1/2"×30
    add_custom_entry(result, name="M.BOLT", spec='1/2"x30',
                     material=_ANCHOR_BOLT_MATERIAL, quantity=2,
                     unit_weight=0.3, unit="SET")

    # NOTE: D-80 Shoe 由 Type 66 獨立計算, 此處不重複列入
    result.warnings.append("管線端 D-80 Shoe 需另行計算 (Type 66)")

    return result
