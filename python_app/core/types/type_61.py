"""
Type 61 計算器 — Trunnion 支座設計 (D-72/D-73/D-74)
格式: 61-{trunnion_size}B-T{1|2}-{L/100}[(P)]
  例: 61-4B-T1-05, 61-8B-T2-10(P)

T1=單管, T2=雙管(容量×2)
(P)=附 Reinforcing Pad

此型不產出結構 BOM, 主要是 Trunnion 零件本身
BOM: ① TRUNNION PIPE ② PAD (若有)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts
from ..bolt import add_custom_entry
from ..plate import add_plate_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.pipe_table import get_pipe_details


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: Trunnion 管徑 (如 4B, 8B)
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 61: 缺少 Trunnion 管徑"
        return result
    trunn_size = get_lookup_value(part2)

    # 第三段: T1 or T2
    part3 = get_part(fullstring, 3)
    if not part3 or part3.upper() not in ("T1", "T2"):
        result.error = f"Type 61: 第三段須為 T1 或 T2, 得到 '{part3}'"
        return result
    t_type = part3.upper()
    t_mult = 1 if t_type == "T1" else 2

    # 第四段: L/100 [(P)]
    part4 = get_part(fullstring, 4)
    if not part4:
        result.error = "Type 61: 缺少 Trunnion 長度"
        return result
    l_str, pad_paren = extract_parts(part4)
    has_pad = pad_paren.upper() == "(P)"
    try:
        trunn_length = int(l_str) * 100
    except ValueError:
        result.error = f"Type 61: 無法解析長度 '{part4}'"
        return result

    # 查管道資料取重量
    pipe_details = get_pipe_details(trunn_size, "STD.WT")
    if not pipe_details:
        pipe_details = get_pipe_details(trunn_size, "40S")

    weight_per_m = pipe_details["weight_per_m"] if pipe_details else trunn_size * 2.0

    # ① TRUNNION PIPE
    pipe_qty = t_mult
    add_custom_entry(result, name="TRUNNION PIPE",
                     spec=f'{int(trunn_size)}"*STD.WT',
                     material=_SUPPORT_PIPE_MATERIAL, quantity=pipe_qty,
                     unit_weight=round(trunn_length / 1000 * weight_per_m, 2),
                     unit="PC")
    result.entries[-1].remark = (
        f"{t_type}, L={trunn_length}mm, ×{pipe_qty}"
    )

    # ② PAD (若有)
    if has_pad:
        # Pad 大小估算: OD + 2" × OD + 2" × 12t
        od = pipe_details["od_mm"] if pipe_details else trunn_size * 25.4
        pad_size = round(od + 50)
        add_plate_entry(result, plate_a=pad_size, plate_b=pad_size,
                        plate_thickness=12, plate_name="REIN. PAD",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=pipe_qty)
        result.entries[-1].remark = f"Reinforcing Pad, ~{pad_size}×{pad_size}×12t"

    result.warnings.append(
        "力矩容量需查 D-73(CS) 或 D-74(SS) 校核, 溫度修正另計"
    )

    return result
