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
  中管 (4"~24"): ① Member M ×2
  大管 (26"~42"): ① Member M ×2  (+ D-91 Rein. Pad 由圖面另計)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.steel_sections import get_section_details
from data.type51_table import get_type51_data


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
                # 中管 (4"~24"): Member ×2, length = member 標準切割
                # 長度由梁寬決定, 此處以 200mm 估算
                add_steel_section_entry(result, section_type, section_dim,
                                        200, steel_qty=2,
                                        material=_STRUCTURAL_MATERIAL)
                result.entries[-1].remark = (
                    f"Member M, ×2, H={h_val}mm, 長度≤梁寬(NOTE 2)"
                )
            else:
                # 大管 (26"~42"): Member + 80° 鞍座
                add_steel_section_entry(result, section_type, section_dim,
                                        300, steel_qty=2,
                                        material=_STRUCTURAL_MATERIAL)
                result.entries[-1].remark = (
                    f"Member M, ×2, 含80°鞍座, 長度≤梁寬"
                )
                result.warnings.append(
                    f"大管 ({line_size}\") 需 D-91 Reinforcing Pad, 另行計算"
                )
        else:
            result.warnings.append(f"Member {member} 無法自動查表")

    return result
