"""
Type 58 計算器 — U-Bolt Plate Saddle on Steel Plate / Shape Steel
圖號: D-69
格式: 58-{size}B-{FIG}
例: 58-4B-A, 58-8B-B
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type58_table import get_type58_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")
_U_BOLT_MATERIAL = _material_spec(HardwareKind.U_BOLT, "A36/SS400")


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 解析 ──
    # part1 = "58", part2 = "{size}B", part3 = "{FIG}" (optional)
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

    # ── 查表 ──
    data = get_type58_data(size_str)
    if not data:
        result.error = f"管徑 {size_str}\" 不在 Type 58 查詢表中"
        return result

    # ① Steel Plate (L×B×T)
    add_plate_entry(
        result,
        data["plate_l"],
        data["plate_b"],
        data["plate_t"],
        "STEEL PLATE",
        _SUPPORT_PLATE_MATERIAL,
        1,
    )

    # ② U-bolt set (M-26)
    # M-26 table 目前由 Codex 施工中，先以 custom_entry 估算
    rod_size = data["rod_size"]
    # U-bolt 估算重量：根據 rod size 粗估
    ubolt_weight_est = {
        '1/4"': 0.1, '3/8"': 0.2, '1/2"': 0.4, '5/8"': 0.6,
        '3/4"': 0.9, '7/8"': 1.3, '1"': 1.8, '1-1/8"': 2.3,
        '1-1/4"': 2.9, '1-3/8"': 3.5, '1-1/2"': 4.2, '1-5/8"': 5.0,
    }
    uw = ubolt_weight_est.get(rod_size, 1.0)
    add_custom_entry(
        result, "U-BOLT", f"M-26, {rod_size}",
        _U_BOLT_MATERIAL, 1, uw, "SET",
    )

    # ── remark for FIG ──
    if fig == "B":
        result.warnings.append(f"FIG-B: 鋼板安裝於型鋼上, X={data['x']}mm")

    return result
