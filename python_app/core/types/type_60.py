"""
Type 60 計算器 — Large Bore Shoe Side Support
圖號: D-71
格式: 60-{size}B-{FIG}
例: 60-20B-A, 60-36B-B
FIG-A: insulated pipe
FIG-B: bare pipe (多 F 尺寸, 45°/120° 幾何)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..plate import add_plate_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type60_table import get_type60_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析 ──
    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)

    if not part2:
        result.error = "缺少管徑欄位"
        return result

    size_str = part2.replace("B", "").strip()
    pipe_size = get_lookup_value(size_str)

    fig = "A"
    if part3 and part3.strip().upper() in ("A", "B"):
        fig = part3.strip().upper()

    if pipe_size < 16 or pipe_size > 42:
        result.error = f"管徑 {size_str}\" 超出 Type 60 範圍 (16\"~42\")"
        return result

    # ── 查表 (完整 support no.) ──
    support_no = f"60-{part2.strip()}-{fig}"
    data = get_type60_data(support_no)
    if not data:
        result.error = f"找不到 {support_no} 的尺寸資料"
        return result

    t = data["T"]

    # ① Side Plate ×2 (A×B×T) — 主側板
    add_plate_entry(
        result, data["A"], data["B"], t,
        "SIDE PLATE", _SUPPORT_PLATE_MATERIAL, 2
    )

    # ② 若 FIG-B 有 F 值，額外計入底部連接板
    if data["F"] is not None:
        add_plate_entry(
            result, data["C"], data["F"], t,
            "BOTTOM PLATE", _SUPPORT_PLATE_MATERIAL, 1
        )

    # ③ Shoe reference (D-80/80B, NOT FURNISHED)
    result.warnings.append(
        f"FIG-{fig}: Pipe Shoe (D-80/80B) NOT FURNISHED, 需另行計算 TYPE-66"
    )

    return result
