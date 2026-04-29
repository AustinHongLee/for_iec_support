"""
Type 64 計算器 — Pipe-to-Pipe Rod Hanger
圖號: D-78
格式: 64-{E}-{F}-{HH}{FIG}
例: 64-2-8-05A, 64-6-12-15C
E = supported line size, F = supporting line size
H = HH × 100 mm (500~3000)
FIG = A/B/C/D (決定 upper/lower clamp 類型)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..bolt import add_custom_entry
from ..component_rules import (
    component_or_estimated_clamp_weight,
    estimate_eye_nut_weight,
    estimate_rod_weight,
)
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.type64_table import get_type64_rod, get_type64_figure
from data.m22_table import build_m22_item
from data.m25_table import build_m25_item
from data.m4_table import build_m4_item
from data.m6_table import build_m6_item


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def _add_custom_entry(
    result: AnalysisResult,
    name: str,
    spec: str,
    material: MaterialSpec,
    quantity: int,
    unit_weight: float,
    unit: str = "SET",
    remark: str = "",
    category: str = "螺栓類",
):
    add_custom_entry(
        result,
        name,
        spec,
        material.name,
        quantity,
        unit_weight,
        unit,
        remark=remark,
        category=category,
    )
    if result.entries:
        result.entries[-1].material_canonical_id = material.canonical_id


def _build_clamp_remark(source: str, clamp_item: dict | None) -> str:
    if not clamp_item:
        return ""
    rod = clamp_item.get("rod_size_a")
    if clamp_item.get("designation_inferred"):
        base = f"推論 designation, ref {source}"
    else:
        base = f"SEE {source}"
    return f"{base}, rod {rod}" if rod else base


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material_context = parse_hardware_material_context(
        overrides,
        all_hardware_keys=("hardware_material", "material", "upper_material"),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides
    rod_material = _material(HardwareKind.THREADED_ROD, service=service, overrides=material_overrides)
    eye_nut_material = _material(HardwareKind.WELDLESS_EYE_NUT, service=service, overrides=material_overrides)
    clamp_material = _material(HardwareKind.CLAMP_BODY, service=service, overrides=material_overrides)

    # ── 解析: 64-{E}-{F}-{HH}{FIG} ──
    part2 = get_part(fullstring, 2)  # E (supported)
    part3 = get_part(fullstring, 3)  # F (supporting)
    part4 = get_part(fullstring, 4)  # {HH}{FIG}

    if not part2 or not part3 or not part4:
        result.error = "格式錯誤，應為 64-{E}-{F}-{HH}{FIG}"
        return result

    e_str = part2.replace("B", "").strip()
    f_str = part3.replace("B", "").strip()
    e_size = get_lookup_value(e_str)
    f_size = get_lookup_value(f_str)

    # 拆 HH 和 FIG
    p4 = part4.strip()
    fig = ""
    hh_str = ""
    if p4 and p4[-1].isalpha():
        fig = p4[-1].upper()
        hh_str = p4[:-1]
    else:
        result.error = f"無法辨識 FIG，part4='{p4}'"
        return result

    if not hh_str.isdigit():
        result.error = f"無法解析 H 值，HH='{hh_str}'"
        return result

    h_mm = int(hh_str) * 100

    # ── 驗證 ──
    if h_mm < 500 or h_mm > 3000:
        result.error = f"H={h_mm}mm 超出範圍 (500~3000)"
        return result

    if f_size <= e_size:
        result.warnings.append(
            f"⚠ Supporting line ({f_str}\") 不應小於 Supported line ({e_str}\")"
        )

    # ── 查表 ──
    rod_info = get_type64_rod(e_str)
    if not rod_info:
        result.error = f"Supported size {e_str}\" 不在 Type 64 查詢表中"
        return result

    fig_info = get_type64_figure(fig)
    if not fig_info:
        result.error = f"FIG-{fig} 無效 (應為 A/B/C/D)"
        return result

    # 檢查 fig_bc_only
    if rod_info["fig_bc_only"] and fig not in ("B", "C"):
        result.warnings.append(
            f"管徑 {e_str}\" 圖面標記僅適用 FIG-B/C, 目前選用 FIG-{fig}"
        )

    rod_size = rod_info["g"]

    # ① Threaded Rod ×2 (M-22), 長度 ≈ H
    rod_item = build_m22_item(rod_size, h_mm)
    rod_unit_wt = rod_item["unit_weight_kg"] if rod_item else estimate_rod_weight(rod_size, h_mm)
    _add_custom_entry(
        result, "THREADED ROD",
        rod_item["designation"] if rod_item else f"M-22, {rod_size}, L={h_mm}mm",
        rod_material, 2, rod_unit_wt, "PC"
    )
    if not rod_item:
        result.warnings.append(f"M-22 table 尚無 rod size {rod_size}，暫以 rod 鋼材重量估算")

    # ② Weldless Eye Nut ×2 (M-25)
    eye_nut_item = build_m25_item(rod_size)
    _add_custom_entry(
        result, "WELDLESS EYE NUT",
        eye_nut_item["designation"] if eye_nut_item else f"M-25, {rod_size}",
        eye_nut_material, 2, eye_nut_item["unit_weight_kg"] if eye_nut_item else estimate_eye_nut_weight(rod_size), "PC"
    )
    if not eye_nut_item:
        result.warnings.append(f"M-25 table 尚無 rod size {rod_size}，weldless eye nut 重量暫用估算值")

    # ③ Upper Clamp ×1 set
    upper_builder = build_m6_item if "M-6" in fig_info["upper_clamp"] else build_m4_item
    upper_clamp = upper_builder(f_str)
    _add_custom_entry(
        result, "UPPER CLAMP",
        upper_clamp["designation"] if upper_clamp else f"{fig_info['upper_clamp']}, {f_str}\"",
        clamp_material, 1, component_or_estimated_clamp_weight(
            upper_clamp,
            f_str,
            component_id="M-6" if upper_builder is build_m6_item else "M-4",
        ), "SET",
        remark=_build_clamp_remark("M-6" if upper_builder is build_m6_item else "M-4", upper_clamp),
    )
    if not upper_clamp or not upper_clamp.get("weight_ready"):
        result.warnings.append("UPPER CLAMP 重量使用 core.component_rules 集中估算")

    # ④ Lower Clamp ×1 set
    lower_builder = build_m6_item if "M-6" in fig_info["lower_clamp"] else build_m4_item
    lower_clamp = lower_builder(e_str)
    _add_custom_entry(
        result, "LOWER CLAMP",
        lower_clamp["designation"] if lower_clamp else f"{fig_info['lower_clamp']}, {e_str}\"",
        clamp_material, 1, component_or_estimated_clamp_weight(
            lower_clamp,
            e_str,
            component_id="M-6" if lower_builder is build_m6_item else "M-4",
        ), "SET",
        remark=_build_clamp_remark("M-6" if lower_builder is build_m6_item else "M-4", lower_clamp),
    )
    if not lower_clamp or not lower_clamp.get("weight_ready"):
        result.warnings.append("LOWER CLAMP 重量使用 core.component_rules 集中估算")

    return result
