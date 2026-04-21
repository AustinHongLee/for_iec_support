"""
Type 62 calculator — Pipe hanger combination (D-75/D-76).

Designation:
    62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]

Example from drawing:
    62-4B-5/8-05~30D-J(T)

This calculator is intentionally conservative.  The Type 62 drawing is a hanger
combination selector; exact weights depend on M-series component tables.  Missing
component tables are emitted as estimated placeholders with warnings.
"""
from __future__ import annotations

import re

from ..bolt import add_custom_entry
from ..component_rules import (
    DEFAULT_STRUCTURAL_MATERIAL,
    component_or_estimated_clamp_weight,
    estimate_eye_nut_weight,
    estimate_heavy_hex_nut_weight,
    estimate_m28_weight,
    estimate_missing_component_weight,
    estimate_rod_weight,
    resolve_material,
)
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from data.component_size_utils import (
    normalize_fractional_size,
)
from data.m21_table import get_m21_by_dia
from data.m22_table import build_m22_item
from data.m24_table import get_m24_by_dia
from data.m25_table import build_m25_item
from data.m28_table import get_m28_by_rod_size
from data.m4_table import build_m4_item
from data.m5_table import build_m5_item
from data.m6_table import build_m6_item
from data.m7_table import build_m7_item
from data.type62_table import (
    TYPE62_LOWER_FIGS,
    TYPE62_UPPER_FIGS,
    get_type62_lower_part,
    get_type62_upper_part,
    validate_type62_lower_pipe_size,
)


_CLAMP_BUILDERS = {
    "G": ("M-4", build_m4_item),
    "H": ("M-5", build_m5_item),
    "J": ("M-6", build_m6_item),
    "K": ("M-7", build_m7_item),
}


def _parse_height_and_upper_fig(part4: str):
    token = str(part4).strip().replace(" ", "").upper()
    match = re.fullmatch(r"(?P<h1>\d{2})(?:~(?P<h2>\d{2}))?(?P<fig>[A-Z])", token)
    if not match:
        match = re.fullmatch(r"(?P<h1>\d{2})(?P<h2>\d{2})(?P<fig>[A-Z])", token)
    if not match:
        return None

    h1 = int(match.group("h1")) * 100
    h2 = int(match.group("h2")) * 100 if match.group("h2") else None
    return {
        "height_min_mm": h1,
        "height_max_mm": h2 or h1,
        "is_range": h2 is not None,
        "upper_fig": match.group("fig"),
    }

def _add_estimated_component(
    result: AnalysisResult,
    *,
    name: str,
    component_id: str,
    fig: str,
    line_size: float | None,
    rod_size: str,
    category: str = "螺栓類",
    material: str = DEFAULT_STRUCTURAL_MATERIAL,
):
    unit_weight = estimate_missing_component_weight(component_id, line_size=line_size, rod_size=rod_size)
    add_custom_entry(
        result,
        name,
        f"{component_id}, FIG-{fig}",
        material,
        1,
        unit_weight,
        "SET",
        remark="component table missing; estimated placeholder",
        category=category,
    )
    result.warnings.append(
        f"Type 62 FIG-{fig} uses {component_id}; component table 尚未建立，重量為估算值"
    )


def _add_threaded_rod(
    result: AnalysisResult,
    rod_size: str,
    height_mm: int,
    *,
    height_is_range: bool,
    left_hand: bool,
    material: str,
):
    rod_item = build_m22_item(rod_size, height_mm, left_hand=left_hand)
    unit_weight = (
        rod_item["unit_weight_kg"]
        if rod_item
        else estimate_rod_weight(rod_size, height_mm)
    )
    add_custom_entry(
        result,
        "MACH. THREADED ROD",
        rod_item["designation"] if rod_item else f"M-22, {rod_size}, L={height_mm}mm",
        material,
        1,
        unit_weight,
        "PC",
        remark=f"L takeoff uses H={height_mm}mm" + (", left-hand end for turnbuckle" if left_hand else ""),
    )
    if not rod_item:
        result.warnings.append(f"M-22 table 尚無 rod size {rod_size}，rod 重量暫以圓鋼估算")
    if height_is_range:
        result.warnings.append(
            f"H is a range in designation; rod takeoff uses max H={height_mm}mm conservatively"
        )


def _add_turnbuckle(result: AnalysisResult, rod_size: str, *, material: str):
    row = get_m21_by_dia(rod_size)
    add_custom_entry(
        result,
        "TURNBUCKLE",
        row["designation"] if row else f"M-21, {rod_size}",
        material,
        1,
        row["unit_weight_kg"] if row else estimate_rod_weight(rod_size, 300, min_weight=0.5),
        "PC",
        remark="SEE M-21",
    )
    if not row:
        result.warnings.append(f"M-21 table 尚無 rod size {rod_size}，turnbuckle 重量暫估")


def _add_eye_nut(result: AnalysisResult, rod_size: str, *, left_hand: bool, remark: str, material: str):
    item = build_m25_item(rod_size, left_hand=left_hand)
    add_custom_entry(
        result,
        "WELDLESS EYE NUT",
        item["designation"] if item else f"M-25, {rod_size}",
        material,
        1,
        item["unit_weight_kg"] if item else estimate_eye_nut_weight(rod_size),
        "PC",
        remark=remark,
    )
    if not item:
        result.warnings.append(f"M-25 table 尚無 rod size {rod_size}，eye nut 重量暫估")


def _add_heavy_hex_nuts(result: AnalysisResult, rod_size: str, *, material: str):
    unit_weight = estimate_heavy_hex_nut_weight(rod_size)
    add_custom_entry(
        result,
        "HEAVY HEX. NUT",
        f"{rod_size}",
        material,
        2,
        unit_weight,
        "PC",
        remark="drawing callout; weight estimated",
    )
    result.warnings.append("HEAVY HEX. NUT 重量為 rod-size 估算值，尚未接正式 nut table")


def _add_upper_part(
    result: AnalysisResult,
    upper_fig: str,
    rod_size: str,
    has_turnbuckle: bool,
    *,
    material: str,
):
    row = get_type62_upper_part(upper_fig)
    component_id = row["component_id"]
    if component_id == "M-28":
        item = get_m28_by_rod_size(rod_size)
        add_custom_entry(
            result,
            "UPPER ATTACHMENT",
            item["type"] if item else f"M-28, FIG-{upper_fig}, {rod_size}",
            material,
            1,
            item["unit_weight_kg"] if item else estimate_m28_weight(rod_size),
            "SET",
            remark=f"Upper FIG-{upper_fig}, SEE M-28",
        )
        if not item:
            result.warnings.append(f"M-28 table 尚無 rod size {rod_size}，upper attachment 重量暫估")
    else:
        _add_estimated_component(
            result,
            name="UPPER ATTACHMENT",
            component_id=component_id,
            fig=upper_fig,
            line_size=None,
            rod_size=rod_size,
            material=material,
        )

    if upper_fig == "D" and not has_turnbuckle:
        _add_eye_nut(
            result,
            rod_size,
            left_hand=True,
            remark="NOTE 4: FIG-D without turnbuckle requires left-hand thread",
            material=material,
        )
        result.warnings.append(
            "NOTE 4 applied: FIG-D without turnbuckle uses left-hand threaded weldless eye nut"
        )


def _add_lower_part(
    result: AnalysisResult,
    lower_fig: str,
    line_size: float,
    rod_size: str,
    *,
    material: str,
):
    row = get_type62_lower_part(lower_fig)
    component_id = row["component_id"]

    if lower_fig in _CLAMP_BUILDERS:
        _, builder = _CLAMP_BUILDERS[lower_fig]
        item = builder(line_size)
        add_custom_entry(
            result,
            "LOWER PIPE CLAMP",
            item["designation"] if item else f"{component_id}, FIG-{lower_fig}, {line_size:g}\"",
            material,
            1,
            component_or_estimated_clamp_weight(item, line_size, component_id=component_id),
            "SET",
            remark=f"Lower FIG-{lower_fig}, SEE {component_id}",
        )
        if not item or not item.get("weight_ready"):
            result.warnings.append(f"{component_id} lower clamp 重量使用 core.component_rules 集中估算")
        _add_eye_nut(result, rod_size, left_hand=False, remark="lower clamp connector, SEE M-25", material=material)
        _add_heavy_hex_nuts(result, rod_size, material=material)
        return

    if lower_fig in ("L", "M", "N"):
        _add_estimated_component(
            result,
            name="LOWER PIPE CLAMP",
            component_id=component_id,
            fig=lower_fig,
            line_size=line_size,
            rod_size=rod_size,
            material=material,
        )
        _add_eye_nut(result, rod_size, left_hand=False, remark="lower clamp connector, SEE M-25", material=material)
        _add_heavy_hex_nuts(result, rod_size, material=material)
        return

    if lower_fig == "Q":
        clevis = get_m24_by_dia(rod_size)
        add_custom_entry(
            result,
            "FORGED STEEL CLEVIS",
            clevis["designation"] if clevis else f"M-24, {rod_size}",
            material,
            1,
            clevis["unit_weight_kg"] if clevis else estimate_rod_weight(rod_size, 150, min_weight=0.25),
            "PC",
            remark="Lower FIG-Q, SEE M-24",
        )
        if not clevis:
            result.warnings.append(f"M-24 table 尚無 rod size {rod_size}，clevis 重量暫估")
        _add_estimated_component(
            result,
            name="LUG PLATE TYPE-B",
            component_id="M-33",
            fig=lower_fig,
            line_size=line_size,
            rod_size=rod_size,
            category="鋼板類",
            material=material,
        )
        result.warnings.append("FIG-Q welding size: see M-28 per Type 62 NOTE 2")
        return

    if lower_fig == "E":
        # D-75 FIG-E shows the M-3 adjustable clevis only.  Unlike clamp figures
        # G/H/J/K/L/M/N, there is no separate M-25 or heavy-hex-nut callout.
        _add_estimated_component(
            result,
            name="ADJUSTABLE CLEVIS",
            component_id=component_id,
            fig=lower_fig,
            line_size=line_size,
            rod_size=rod_size,
            material=material,
        )
        return

    raise ValueError(f"unhandled lower_fig {lower_fig}")


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material = resolve_material(overrides=overrides, default=DEFAULT_STRUCTURAL_MATERIAL)

    part2 = get_part(fullstring, 2)
    part3 = get_part(fullstring, 3)
    part4 = get_part(fullstring, 4)
    part5 = get_part(fullstring, 5)

    if not part2 or not part3 or not part4 or not part5:
        result.error = "格式錯誤，應為 62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]"
        return result

    line_size = get_lookup_value(part2)
    rod_size = normalize_fractional_size(part3)

    parsed_h = _parse_height_and_upper_fig(part4)
    if not parsed_h:
        result.error = f"無法解析 H/upper fig 欄位 '{part4}'，例: 05C 或 05~30D"
        return result

    upper_fig = parsed_h["upper_fig"]
    if upper_fig not in TYPE62_UPPER_FIGS or not get_type62_upper_part(upper_fig):
        result.error = f"Upper FIG-{upper_fig} 無效，應為 A/C/D"
        return result

    lower_token, paren = extract_parts(part5.strip().upper())
    lower_fig = lower_token.strip().upper()
    has_turnbuckle = "(T)" in paren.upper()

    if lower_fig not in TYPE62_LOWER_FIGS or not get_type62_lower_part(lower_fig):
        result.error = f"Lower FIG-{lower_fig} 無效，應為 E/G/H/J/K/L/M/N/Q"
        return result

    ok, message = validate_type62_lower_pipe_size(lower_fig, line_size)
    if not ok:
        result.error = f"Type 62: line size {line_size:g}\" 不適用 Lower FIG-{lower_fig} ({message})"
        return result

    height_min = parsed_h["height_min_mm"]
    height_max = parsed_h["height_max_mm"]
    if height_min < 500 or height_max > 3000 or height_min > height_max:
        result.error = f"H={height_min}~{height_max}mm 超出 Type 62 圖面範圍 500~3000mm"
        return result

    _add_threaded_rod(
        result,
        rod_size,
        height_max,
        height_is_range=parsed_h["is_range"],
        left_hand=has_turnbuckle,
        material=material,
    )
    _add_upper_part(
        result,
        upper_fig,
        rod_size,
        has_turnbuckle,
        material=material,
    )

    if has_turnbuckle:
        _add_turnbuckle(result, rod_size, material=material)

    _add_lower_part(
        result,
        lower_fig,
        line_size,
        rod_size,
        material=material,
    )

    if height_max > 2000 and not has_turnbuckle:
        result.warnings.append('NOTE 3: DIM "H" larger than 2000mm should use turnbuckle; designation lacks (T)')
    if upper_fig == "D" and not has_turnbuckle:
        result.warnings.append("NOTE 3: Upper FIG-D is normally used with turnbuckle; review designation")

    lower_info = get_type62_lower_part(lower_fig)
    if lower_info and lower_info.get("remarks"):
        result.warnings.append(f"FIG-{lower_fig}: {lower_info['remarks']}")

    return result
