"""
Type 56 計算器 — 結構式管線檔止 (D-67, D-67A)
格式: 56-{line_size}B
  例: 56-2B, 56-10B, 56-36B

自成一體的結構鋼檔止, 不引用 D-80/D-81
四種結構:
  ≤2-1/2": PL 100×100×6
  3"~4": FAB FROM 6t PLATE
  5"~14": H型鋼切割
  16"~24": FAB FROM 12t PLATE
  26"~42": 大型結構 + 120° 鞍座 + D-91

BOM:
  小管 (≤2-1/2"): ① PLATE 100×100×6
  中管 (3"~14"): ① MEMBER C (H型鋼 or 鋼板)
  大管 (16"~24"): ① MEMBER C (12t 板) + 側板
  超大管 (26"~42"): ① MEMBER C + 鞍座 + D-91
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
from data.type56_table import get_type56_data
from data.pipe_table import get_pipe_od


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 56: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)

    data = get_type56_data(line_size)
    if not data:
        result.error = f"Type 56: 管徑 {part2} ({line_size}\") 不在範圍 (3/4\"~42\")"
        return result

    R = data["R"]

    if line_size <= 2.5:
        # 小管: PL 100×100×6
        add_plate_entry(result, plate_a=100, plate_b=100,
                        plate_thickness=6, plate_name="PLATE",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"管線檔止, PL 100×100×6, R={R}mm"

    elif line_size <= 4:
        # 3"~4": FAB FROM 6t PLATE
        A = data["A"]
        B = data["B"]
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=6, plate_name="MEMBER C",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"FAB FROM 6t PLATE, {A}x{B}x6, R={R}mm"

    elif line_size <= 14:
        # 5"~14": CUT FROM H型鋼
        A = data["A"]
        B = data["B"]
        C_desc = data["C"]  # "CUT FROM H200*100*5.5*8" etc.
        D = data["D"]
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=12, plate_name="MEMBER C",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"{C_desc}, A={A}, B={B}, D={D}, R={R}mm"

    elif line_size <= 24:
        # 16"~24": FAB FROM 12t PLATE
        A = data["A"]
        B = data["B"]
        E = data["E"]
        D = data["D"]
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=E, plate_name="MEMBER C",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"FAB FROM {E}t PLATE, A={A}, D={D}, R={R}mm"

        # 側板 ×2
        add_plate_entry(result, plate_a=D, plate_b=B,
                        plate_thickness=E, plate_name="SIDE PLATE",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"側板, {D}x{B}x{E}t, ×2"

    else:
        # 26"~42": 大型結構 + 120° 鞍座
        A = data["A"]
        B = data["B"]
        C = data["C"]
        D = data["D"]
        E = data["E"]
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=E, plate_name="MEMBER C",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"主承載框, A={A}, B={B}, C={C}, R={R}mm"

        add_plate_entry(result, plate_a=D, plate_b=B,
                        plate_thickness=E, plate_name="SIDE PLATE",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"側板, {D}x{B}x{E}t, ×2"

        # 120° 鞍座
        add_plate_entry(result, plate_a=C, plate_b=C,
                        plate_thickness=E, plate_name="SADDLE (120°)",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"120° 鞍座, 含 D-91 REIN. PAD"

        result.warnings.append(
            f"大管 ({line_size}\") 需 D-91 Reinforcing Pad, 尺寸另查"
        )

    return result
