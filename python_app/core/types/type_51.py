"""
Type 51 計算器 — 管線鞍座承托支撐 (D-62, D-62A)
格式: 51-{line_size}B
  例: 51-2B, 51-12B, 51-36B

三種結構:
  ≤3": Flat Bar (H×50×9), 無 Member
  4"~24": 角鐵 Member "M" 兩側
  26"~42": 槽鋼 + 鞍座

BOM:
  小管 (≤3"): ① FLAT BAR (H×50×9)
  中管 (4"~24"): ① Member M ×2, 每支長度 = 表內 H
  大管 (26"~42"): ① Member M ×2  (+ D-91 Rein. Pad / saddle 由圖面另計)
"""
from ..models import AnalysisResult
import math

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
from data.type51_table import get_type51_data
from data.type76_table import get_type76_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑 (如 2B, 12B)
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 51: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)

    data = get_type51_data(line_size)
    if not data:
        result.error = f"Type 51: 管徑 {part2} ({line_size}\") 不在範圍 (3/4\"~42\")"
        return result

    member = data["member"]
    h_val = data["H"]

    if member is None and h_val is not None:
        # ≤3": Flat Bar
        add_plate_entry(result, plate_a=h_val, plate_b=50,
                        plate_thickness=9, plate_name="FLAT BAR",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"鞍座, {h_val}x50x9, 全焊接(6V), ×2"
    elif member is not None:
        # 4"+: 角鐵或槽鋼
        details = get_section_details(member.split("*")[0])
        if details:
            section_type = details["type"]
            section_dim = details["size"][1:]
            if h_val:
                # 中管 (4"~24"): table H is the member cut length.
                add_steel_section_entry(result, section_type, section_dim,
                                        h_val, steel_qty=2,
                                        material=_STRUCTURAL_MATERIAL)
                result.entries[-1].remark = (
                    f"Member M, ×2, H={h_val}mm, 兩側3mm gap, 長度≤梁寬(NOTE 2)"
                )
            else:
                # 大管 (26"~42"): D-62A gives channel member family; D-91 is
                # Type 76 and provides the reinforcing pad geometry.
                add_steel_section_entry(result, section_type, section_dim,
                                        300, steel_qty=2,
                                        material=_STRUCTURAL_MATERIAL)
                result.entries[-1].remark = (
                    f"Member M, ×2, D-62A大管承托, 80° saddle, provisional length=300"
                )
                pad = get_type76_data(line_size)
                if pad:
                    pad_arc_width = round(
                        math.pi * pad["od_mm"] * (pad["pad_angle_deg"] / 360),
                        1,
                    )
                    add_custom_entry(
                        result,
                        "PIPE PAD",
                        str(pad["thickness_mm"]),
                        "Same as pipe / Carbon Steel",
                        1,
                        pad["unit_weight_kg"],
                        "PC",
                        remark=(
                            f'D-91 reinforcing pad, {pad["pad_angle_deg"]}deg x '
                            f'{pad["pad_length_mm"]}L x {pad["thickness_mm"]}t, '
                            f'OD={pad["od_mm"]}, arc_width={pad_arc_width}; '
                            "cut from main pipe or fabricated from C/S plate"
                        ),
                        category="鋼板類",
                    )
                    result.entries[-1].length = pad["pad_length_mm"]
                    result.entries[-1].width = pad_arc_width
                else:
                    result.warnings.append(
                        f"大管 ({line_size}\") 需 D-91 Reinforcing Pad, 但 Type 76 pad data 查無資料"
                    )
        else:
            result.warnings.append(f"Member {member} 無法自動查表")

    return result
