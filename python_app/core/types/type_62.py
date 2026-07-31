"""
Type 62 calculator — Pipe hanger combination (D-75/D-76).

Designation:
    62-{line_size}B-{rod_size}-{HH}[~{HH2}]{upper_fig}-{lower_fig}[(T)]

Example from drawing:
    62-4B-5/8-05~30D-J(T)

This calculator is intentionally conservative.  D-75/D-76 define a hanger
assembly height and component selection, not a released threaded-rod cut length.
Only source-backed component rows and weights are emitted; unresolved purchased
weights and fabrication contours remain zero-weight references with blockers.
"""
from __future__ import annotations

import re
from copy import deepcopy

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..models import AnalysisResult, HolePattern
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.component_size_utils import (
    normalize_fractional_size,
)
from data.m10_table import get_m10_by_line_size
from data.m21_table import get_m21_by_dia
from data.m22_table import build_m22_item
from data.m24_table import get_m24_by_dia
from data.m25_table import build_m25_item
from data.m28_table import get_m28_by_rod_size
from data.m3_table import get_m3_by_line_size
from data.m31_table import get_m31_by_rod_size
from data.m33_table import get_m33_by_line_size
from data.m4_table import build_m4_item
from data.m5_table import build_m5_item
from data.m6_table import build_m6_item
from data.m7_table import build_m7_item
from data.m8_table import get_m8_by_line_size
from data.m9_table import get_m9_by_line_size
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

_HIGH_TEMP_CLAMP_LOOKUPS = {
    "L": ("M-8", get_m8_by_line_size),
    "M": ("M-9", get_m9_by_line_size),
    "N": ("M-10", get_m10_by_line_size),
}

_HIGH_TEMP_CLAMP_MATERIAL_IDS = {
    "M-8": "ASTM_A387_GR22",
    "M-9": "COMPOSITE_CHROME_MOLY_STAINLESS_UBOLT",
    "M-10": "COMPOSITE_CHROME_MOLY_STAINLESS_UBOLT",
}


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

def _source_clamp_material(
    result: AnalysisResult,
    *,
    row: dict,
    requested_material: MaterialSpec,
) -> MaterialSpec:
    if requested_material.source.startswith("override."):
        result.warnings.append(
            f"{row['component_id']}原圖指定 {row['material']}；"
            f"本次 explicit hardware override 使用 {requested_material.name}，"
            "須由專案核准後才能出加工/採購資料"
        )
        return requested_material

    return MaterialSpec(
        name=row["material"],
        canonical_id=_HIGH_TEMP_CLAMP_MATERIAL_IDS[row["component_id"]],
        source=f"{row['component_id']} Rev.{row['revision']} material note",
        requires_review=row["component_id"] in {"M-9", "M-10"},
        notes=(
            ("M-9/M-10 do not release the chrome-moly or stainless grade.",)
            if row["component_id"] in {"M-9", "M-10"}
            else ()
        ),
    )


def _add_high_temp_clamp(
    result: AnalysisResult,
    *,
    lower_fig: str,
    row: dict,
    requested_material: MaterialSpec,
) -> None:
    component_id = row["component_id"]
    material = _source_clamp_material(
        result,
        row=row,
        requested_material=requested_material,
    )
    dimension_tokens = [
        f"{letter}={row[key]}"
        for key, letter in (
            ("B_mm", "B"),
            ("C_mm", "C"),
            ("D_mm", "D"),
            ("E_mm", "E"),
            ("H_mm", "H"),
            ("K_overall_width_mm", "K"),
            ("M_upper_side_width_mm", "M"),
        )
        if key in row
    ]
    _add_custom_entry(
        result,
        "LOWER PIPE CLAMP",
        f"{row['designation']}; {' '.join(dimension_tokens)}",
        material,
        1,
        0,
        "SET",
        remark=(
            f"Lower FIG-{lower_fig}, SEE {component_id}; "
            "source dimensions/load selected, finished weight unavailable"
        ),
        category="組件類",
    )
    entry = result.entries[-1]
    entry.role = ComponentRole.CLAMP.value
    entry.item_class = "accessory"
    entry.manufacturing_type = "purchased"
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = (
        f"purchased_pipe_clamp_type_{row['designation'].split('-')[1].lower()}"
    )
    entry.geometry.shape_spec = (
        f"{row['designation']}; "
        + " ".join(dimension_tokens)
    )
    entry.geometry.parameters = {
        key: deepcopy(value)
        for key, value in row.items()
        if key != "fabrication_blockers"
    }
    entry.geometry.parameters["type62_lower_figure"] = lower_fig
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )
    result.warnings.append(
        f"{row['designation']}已依{component_id}原表完成尺寸/負載選型；"
        "原圖未給成品重量，本筆clamp重量未計"
    )


def _add_threaded_rod(
    result: AnalysisResult,
    rod_size: str,
    height_min_mm: int,
    height_max_mm: int,
    *,
    rod_cut_length_mm: float | None,
    left_hand: bool,
    material: MaterialSpec,
):
    rod_item = (
        build_m22_item(
            rod_size,
            rod_cut_length_mm,
            left_hand=left_hand,
        )
        if rod_cut_length_mm is not None
        else None
    )
    _add_custom_entry(
        result,
        "MACH. THREADED ROD",
        (
            rod_item["designation"]
            if rod_item
            else f"M-22, {rod_size}, CUT LENGTH TO BE CONFIRMED"
        ),
        material,
        1,
        rod_item["unit_weight_kg"] if rod_item else 0,
        "PC",
        remark=(
            f"Type 62 H={height_min_mm}~{height_max_mm} mm is an "
            "assembly dimension, not a rod cut"
            if rod_item is None
            else (
                f"rod_cut_length_mm override={rod_cut_length_mm:g} mm"
                + (
                    ", left-hand end for turnbuckle"
                    if left_hand
                    else ""
                )
            )
        ),
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "M-22"
    entry.geometry.shape_kind = "machine_threaded_rod"
    entry.geometry.parameters = {
        "rod_size_in": rod_size,
        "assembly_height_min_mm": height_min_mm,
        "assembly_height_max_mm": height_max_mm,
        "rod_cut_length_mm": rod_cut_length_mm,
        "left_hand_end": left_hand,
    }
    entry.geometry.fabrication_ready = rod_item is not None
    if not rod_item:
        blocker = (
            "D-75/D-76 define assembly H but do not release the finished "
            "M-22 rod cut/thread-engagement deduction; provide "
            "rod_cut_length_mm"
        )
        entry.geometry.fabrication_blockers = [blocker]
        result.warnings.append(
            "Type 62不再把H直接當M-22切長；未提供"
            " rod_cut_length_mm，本筆rod重量未計"
        )


def _add_turnbuckle(result: AnalysisResult, rod_size: str, *, material: MaterialSpec):
    row = get_m21_by_dia(rod_size)
    _add_custom_entry(
        result,
        "TURNBUCKLE",
        row["designation"] if row else f"M-21, {rod_size}",
        material,
        1,
        row["unit_weight_kg"] if row else 0,
        "PC",
        remark="SEE M-21",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "M-21"
    entry.geometry.fabrication_ready = False
    if not row:
        entry.geometry.fabrication_blockers = [
            f"M-21 has no exact row for rod size {rod_size}"
        ]
        result.warnings.append(
            f"M-21 table 尚無 rod size {rod_size}，turnbuckle 重量未計"
        )


def _add_eye_nut(result: AnalysisResult, rod_size: str, *, left_hand: bool, remark: str, material: MaterialSpec):
    item = build_m25_item(rod_size, left_hand=left_hand)
    _add_custom_entry(
        result,
        "WELDLESS EYE NUT",
        item["designation"] if item else f"M-25, {rod_size}",
        material,
        1,
        item["unit_weight_kg"] if item else 0,
        "PC",
        remark=remark,
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "M-25"
    entry.geometry.fabrication_ready = False
    if not item:
        entry.geometry.fabrication_blockers = [
            f"M-25 has no exact row for rod size {rod_size}"
        ]
        result.warnings.append(
            f"M-25 table 尚無 rod size {rod_size}，eye nut 重量未計"
        )


def _add_heavy_hex_nuts(result: AnalysisResult, rod_size: str, *, material: MaterialSpec):
    _add_custom_entry(
        result,
        "HEAVY HEX. NUT",
        f"{rod_size}",
        material,
        2,
        0,
        "PC",
        remark="drawing callout; finished nut table/weight not connected",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D75-HEAVY-HEX-NUT"
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [
        "heavy-hex nut finished product table/weight is not connected"
    ]
    result.warnings.append(
        "HEAVY HEX. NUT 尚未接正式成品表，重量未計"
    )


def _add_m31_washer_plate(
    result: AnalysisResult,
    row: dict,
    *,
    material: MaterialSpec,
) -> None:
    material_upper = material.name.upper()
    uses_source_carbon_density = any(
        token in material_upper
        for token in ("A36", "SS400", "CARBON STEEL")
    )
    _add_custom_entry(
        result,
        "STEEL WASHER PLATE",
        (
            f"{row['designation']}; "
            f"{row['C_square_side_mm']}x"
            f"{row['C_square_side_mm']}x"
            f"{row['T_thickness_mm']}t; "
            f"1-DIA{row['D_hole_diameter_mm']}"
        ),
        material,
        1,
        (
            row["calculated_net_weight_kg"]
            if uses_source_carbon_density
            else 0
        ),
        "PC",
        remark=(
            (
                "M-31方板扣中心圓孔淨重；"
                "碳鋼牌號/塗裝與現場焊接位置待確認"
            )
            if uses_source_carbon_density
            else (
                "M-31原圖只釋出carbon-steel材質；"
                "目前選材非碳鋼，未套用7.85e-6密度"
            )
        ),
        category="鋼板類",
    )
    entry = result.entries[-1]
    entry.role = ComponentRole.GENERIC_PLATE.value
    entry.item_class = "fabricated_part"
    entry.manufacturing_type = "plate_cut"
    entry.length = row["C_square_side_mm"]
    entry.width = row["C_square_side_mm"]
    entry.geometry.component_id = "M-31"
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = "square_washer_plate_with_center_hole"
    entry.geometry.shape_spec = (
        f"{row['designation']}: "
        f"C{row['C_square_side_mm']} square x "
        f"T{row['T_thickness_mm']}; "
        f"center hole DIA{row['D_hole_diameter_mm']}"
    )
    entry.geometry.gross_area_mm2 = row["gross_area_mm2"]
    entry.geometry.cutout_area_mm2 = row["hole_area_mm2"]
    entry.geometry.net_area_mm2 = row["net_area_mm2"]
    entry.geometry.holes = HolePattern(
        pattern="single",
        pitch_x=row["hole_center_x_mm"],
        pitch_y=row["hole_center_y_mm"],
        diameter=row["D_hole_diameter_mm"],
        count=1,
    )
    entry.geometry.parameters = {
        key: deepcopy(row[key])
        for key in (
            "designation",
            "rod_size_in",
            "C_square_side_mm",
            "D_hole_diameter_mm",
            "T_thickness_mm",
            "hole_center_x_mm",
            "hole_center_y_mm",
            "gross_area_mm2",
            "hole_area_mm2",
            "net_area_mm2",
            "calculated_net_weight_kg",
            "source_anomalies",
        )
    }
    entry.geometry.parameters[
        "weight_uses_source_carbon_density"
    ] = uses_source_carbon_density
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )
    if not uses_source_carbon_density:
        entry.geometry.fabrication_blockers.append(
            "M-31 non-carbon material/density requires an approved "
            "project component rule before weight can be released"
        )
        result.warnings.append(
            f"M-31原圖材質為carbon steel；目前選材 {material.name} "
            "未有核定密度/構件規則，washer plate重量未計"
        )


def _add_m3_adjustable_clevis(
    result: AnalysisResult,
    row: dict,
    *,
    material: MaterialSpec,
) -> None:
    _add_custom_entry(
        result,
        "ADJUSTABLE CLEVIS",
        (
            f"{row['designation']}; "
            f"A={row['A_rod_size_in']}; "
            f"GRINNELL FIG. 260 OR EQ."
        ),
        material,
        1,
        0,
        "SET",
        remark=(
            "M-3尺寸/負載已查原表；原圖無成品重量，故重量未計"
        ),
        category="組件類",
    )
    entry = result.entries[-1]
    entry.role = ComponentRole.CLAMP.value
    entry.item_class = "accessory"
    entry.manufacturing_type = "purchased"
    entry.geometry.component_id = "M-3"
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = "purchased_adjustable_clevis"
    entry.geometry.shape_spec = (
        f"{row['designation']}; "
        f"UPPER FB{row['upper_steel_thickness_mm']}x"
        f"{row['upper_steel_width_mm']}; "
        f"LOWER FB{row['lower_steel_thickness_mm']}x"
        f"{row['lower_steel_width_mm']}; "
        f"B{row['B_inside_width_mm']} "
        f"C{row['C_overall_height_mm']} "
        f"D{row['D_top_to_pipe_center_mm']} "
        f"E{row['E_cross_bolt_to_pipe_center_mm']} "
        f"F{row['F_adjustment_mm']}"
    )
    excluded = {
        "fabrication_blockers",
        "source_anomalies",
    }
    entry.geometry.parameters = {
        key: deepcopy(value)
        for key, value in row.items()
        if key not in excluded
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )
    result.warnings.append(
        f"{row['designation']}已完成尺寸/負載選型；原圖未給成品重量，本筆M-3重量未計"
    )


def _add_m33_lug_plate(
    result: AnalysisResult,
    row: dict,
    *,
    material: MaterialSpec,
) -> None:
    _add_custom_entry(
        result,
        "LUG PLATE TYPE-B",
        (
            f"{row['designation']}; "
            f"C{row['C_mm']} D{row['D_mm']} "
            f"E{row['E_mm']} K{row['K_mm']} "
            f"R{row['R_mm']} T{row['T_thickness_mm']}"
        ),
        material,
        1,
        0,
        "PC",
        remark=(
            "M-33選型尺寸已查原表；管面貼合輪廓/坡口不足以唯一算淨重"
        ),
        category="鋼板類",
    )
    entry = result.entries[-1]
    entry.role = ComponentRole.LUG_PLATE.value
    entry.item_class = "fabricated_part"
    entry.manufacturing_type = "shaped_plate"
    entry.length = row["E_mm"]
    entry.width = row["D_mm"]
    entry.geometry.component_id = "M-33"
    entry.geometry.source_drawing = row["source_drawing"]
    entry.geometry.source_revision = row["revision"]
    entry.geometry.shape_kind = (
        "lug_plate_type_b_with_unresolved_pipe_contact_profile"
    )
    entry.geometry.shape_spec = (
        f"{row['designation']}: "
        f"A{row['A_line_size_in']:g}in "
        f"B{row['B_hanger_rod_size_in']} "
        f"C{row['C_mm']} D{row['D_mm']} "
        f"E{row['E_mm']} K{row['K_mm']} "
        f"R{row['R_mm']} T{row['T_thickness_mm']} "
        f"S{row['S_weld_size_mm'] or '-'}"
    )
    entry.geometry.parameters = {
        key: deepcopy(value)
        for key, value in row.items()
        if key != "fabrication_blockers"
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = list(
        row["fabrication_blockers"]
    )
    result.warnings.append(
        f"{row['designation']}已完成尺寸/負載選型；"
        "未釋出可唯一算重的管面貼合輪廓，本筆M-33重量未計"
    )


def _add_upper_part(
    result: AnalysisResult,
    upper_fig: str,
    rod_size: str,
    has_turnbuckle: bool,
    *,
    m31_row: dict | None,
    material: MaterialSpec,
    eye_nut_material: MaterialSpec,
):
    row = get_type62_upper_part(upper_fig)
    component_id = row["component_id"]
    if component_id == "M-28":
        item = get_m28_by_rod_size(rod_size)
        _add_custom_entry(
            result,
            "UPPER ATTACHMENT",
            item["type"] if item else f"M-28, FIG-{upper_fig}, {rod_size}",
            material,
            1,
            item["unit_weight_kg"] if item else 0,
            "SET",
            remark=f"Upper FIG-{upper_fig}, SEE M-28",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "M-28"
        entry.geometry.fabrication_ready = False
        if not item:
            entry.geometry.fabrication_blockers = [
                f"M-28 has no exact row for rod size {rod_size}"
            ]
            result.warnings.append(
                f"M-28 table 尚無 rod size {rod_size}，upper attachment 重量未計"
            )
    else:
        if m31_row is None:
            raise ValueError(
                f"M-31 has no exact row for rod size {rod_size}"
            )
        _add_m31_washer_plate(
            result,
            m31_row,
            material=material,
        )

    if upper_fig == "D" and not has_turnbuckle:
        _add_eye_nut(
            result,
            rod_size,
            left_hand=True,
            remark="NOTE 4: FIG-D without turnbuckle requires left-hand thread",
            material=eye_nut_material,
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
    m3_row: dict | None,
    m33_row: dict | None,
    high_temp_clamp_row: dict | None,
    clamp_material: MaterialSpec,
    eye_nut_material: MaterialSpec,
    hex_nut_material: MaterialSpec,
    clevis_material: MaterialSpec,
    lug_material: MaterialSpec,
):
    row = get_type62_lower_part(lower_fig)
    component_id = row["component_id"]

    if lower_fig in _CLAMP_BUILDERS:
        _, builder = _CLAMP_BUILDERS[lower_fig]
        item = builder(line_size)
        source_weight_ready = bool(
            item and item.get("weight_ready")
        )
        _add_custom_entry(
            result,
            "LOWER PIPE CLAMP",
            item["designation"] if item else f"{component_id}, FIG-{lower_fig}, {line_size:g}\"",
            clamp_material,
            1,
            (
                item["unit_weight_kg"]
                if source_weight_ready
                else 0
            ),
            "SET",
            remark=f"Lower FIG-{lower_fig}, SEE {component_id}",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = component_id
        entry.geometry.fabrication_ready = False
        if not source_weight_ready:
            entry.geometry.fabrication_blockers = [
                f"{component_id} source finished weight is unavailable"
            ]
            result.warnings.append(
                f"{component_id} lower clamp 原圖無可證實成品重量，本筆重量未計"
            )
        _add_eye_nut(result, rod_size, left_hand=False, remark="lower clamp connector, SEE M-25", material=eye_nut_material)
        _add_heavy_hex_nuts(result, rod_size, material=hex_nut_material)
        return

    if lower_fig in ("L", "M", "N"):
        if high_temp_clamp_row is None:
            raise ValueError(
                f"{component_id} has no exact row for line size "
                f'{line_size:g}"'
            )
        _add_high_temp_clamp(
            result,
            lower_fig=lower_fig,
            row=high_temp_clamp_row,
            requested_material=clamp_material,
        )
        _add_eye_nut(result, rod_size, left_hand=False, remark="lower clamp connector, SEE M-25", material=eye_nut_material)
        _add_heavy_hex_nuts(result, rod_size, material=hex_nut_material)
        return

    if lower_fig == "Q":
        clevis = get_m24_by_dia(rod_size)
        _add_custom_entry(
            result,
            "FORGED STEEL CLEVIS",
            clevis["designation"] if clevis else f"M-24, {rod_size}",
            clevis_material,
            1,
            clevis["unit_weight_kg"] if clevis else 0,
            "PC",
            remark="Lower FIG-Q, SEE M-24",
        )
        entry = result.entries[-1]
        entry.geometry.component_id = "M-24"
        entry.geometry.fabrication_ready = False
        if not clevis:
            entry.geometry.fabrication_blockers = [
                f"M-24 has no exact row for rod size {rod_size}"
            ]
            result.warnings.append(
                f"M-24 table 尚無 rod size {rod_size}，clevis 重量未計"
            )
        if m33_row is None:
            raise ValueError(
                f"M-33 has no exact row for line size {line_size:g}"
            )
        _add_m33_lug_plate(
            result,
            m33_row,
            material=lug_material,
        )
        result.warnings.append("FIG-Q welding size: see M-28 per Type 62 NOTE 2")
        return

    if lower_fig == "E":
        # D-75 FIG-E shows the M-3 adjustable clevis only.  Unlike clamp figures
        # G/H/J/K/L/M/N, there is no separate M-25 or heavy-hex-nut callout.
        if m3_row is None:
            raise ValueError(
                f"M-3 has no exact row for line size {line_size:g}"
            )
        _add_m3_adjustable_clevis(
            result,
            m3_row,
            material=clevis_material,
        )
        return

    raise ValueError(f"unhandled lower_fig {lower_fig}")


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("62", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = (
            f"Type 62: 尚未建立來源 profile {profile_id}；"
            "中鼎20E4588的P/Q、M16編碼與Detail Z不可套用中威規則"
        )
        return result

    material_context = parse_hardware_material_context(
        overrides,
        all_hardware_keys=("hardware_material", "material", "upper_material"),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides
    rod_material = _material(HardwareKind.THREADED_ROD, service=service, overrides=material_overrides)
    upper_material = _material(HardwareKind.BEAM_ATTACHMENT, service=service, overrides=material_overrides)
    turnbuckle_material = _material(HardwareKind.TURNBUCKLE, service=service, overrides=material_overrides)
    clamp_material = _material(HardwareKind.CLAMP_BODY, service=service, overrides=material_overrides)
    eye_nut_material = _material(HardwareKind.WELDLESS_EYE_NUT, service=service, overrides=material_overrides)
    hex_nut_material = _material(HardwareKind.HEAVY_HEX_NUT, service=service, overrides=material_overrides)
    clevis_material = _material(HardwareKind.CLEVIS, service=service, overrides=material_overrides)
    lug_material = _material(HardwareKind.PLATE_LUG, service=service, overrides=material_overrides)

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

    m31_row = (
        get_m31_by_rod_size(rod_size)
        if upper_fig == "A"
        else None
    )
    if upper_fig == "A" and m31_row is None:
        result.error = (
            f"Type 62 FIG-A: M-31未表列 rod size {rod_size}，"
            "不允許區間內插"
        )
        return result

    m3_row = (
        get_m3_by_line_size(line_size)
        if lower_fig == "E"
        else None
    )
    if lower_fig == "E":
        if m3_row is None:
            result.error = (
                f'Type 62 FIG-E: M-3未表列 line size {line_size:g}"，'
                "不允許區間內插"
            )
            return result
        if normalize_fractional_size(
            m3_row["A_rod_size_in"]
        ) != rod_size:
            result.error = (
                f"Type 62 FIG-E: {m3_row['designation']}原表要求"
                f" rod {m3_row['A_rod_size_in']}，"
                f"designation卻為 {rod_size}"
            )
            return result

    m33_row = (
        get_m33_by_line_size(line_size)
        if lower_fig == "Q"
        else None
    )
    if lower_fig == "Q":
        if m33_row is None:
            result.error = (
                f'Type 62 FIG-Q: M-33未表列 line size {line_size:g}"，'
                "不允許區間內插"
            )
            return result
        if normalize_fractional_size(
            m33_row["B_hanger_rod_size_in"]
        ) != rod_size:
            result.error = (
                f"Type 62 FIG-Q: {m33_row['designation']}原表要求"
                f" rod {m33_row['B_hanger_rod_size_in']}，"
                f"designation卻為 {rod_size}"
            )
            return result

    high_temp_clamp_row = None
    if lower_fig in _HIGH_TEMP_CLAMP_LOOKUPS:
        component_id, lookup = _HIGH_TEMP_CLAMP_LOOKUPS[lower_fig]
        high_temp_clamp_row = lookup(line_size)
        if high_temp_clamp_row is None:
            result.error = (
                f'Type 62 FIG-{lower_fig}: {component_id}未表列 '
                f'line size {line_size:g}"，不允許區間內插'
            )
            return result

    rod_cut_length = overrides.get("rod_cut_length_mm")
    if rod_cut_length not in (None, ""):
        try:
            rod_cut_length = float(rod_cut_length)
        except (TypeError, ValueError):
            result.error = "rod_cut_length_mm 必須為正數"
            return result
        if rod_cut_length <= 0:
            result.error = "rod_cut_length_mm 必須為正數"
            return result
        if rod_cut_length.is_integer():
            rod_cut_length = int(rod_cut_length)
    else:
        rod_cut_length = None

    _add_threaded_rod(
        result,
        rod_size,
        height_min,
        height_max,
        rod_cut_length_mm=rod_cut_length,
        left_hand=has_turnbuckle,
        material=rod_material,
    )
    _add_upper_part(
        result,
        upper_fig,
        rod_size,
        has_turnbuckle,
        m31_row=m31_row,
        material=upper_material,
        eye_nut_material=eye_nut_material,
    )

    if has_turnbuckle:
        _add_turnbuckle(result, rod_size, material=turnbuckle_material)

    _add_lower_part(
        result,
        lower_fig,
        line_size,
        rod_size,
        m3_row=m3_row,
        m33_row=m33_row,
        high_temp_clamp_row=high_temp_clamp_row,
        clamp_material=clamp_material,
        eye_nut_material=eye_nut_material,
        hex_nut_material=hex_nut_material,
        clevis_material=clevis_material,
        lug_material=lug_material,
    )

    if height_max > 2000 and not has_turnbuckle:
        result.warnings.append('NOTE 3: DIM "H" larger than 2000mm should use turnbuckle; designation lacks (T)')
    if upper_fig == "D" and not has_turnbuckle:
        result.warnings.append("NOTE 3: Upper FIG-D is normally used with turnbuckle; review designation")

    lower_info = get_type62_lower_part(lower_fig)
    if lower_info and lower_info.get("remarks"):
        result.warnings.append(f"FIG-{lower_fig}: {lower_info['remarks']}")

    component_rows = {
        entry.geometry.component_id: entry.spec
        for entry in result.entries
        if entry.geometry.component_id
    }
    blockers = [
        blocker
        for entry in result.entries
        for blocker in entry.geometry.fabrication_blockers
    ]
    blockers.extend(
        [
            "D-75 is an assembly arrangement; final hanger component "
            "orientation/field interface must be confirmed in the project layout",
            "D-75 NOTE 2 delegates FIG-Q welding size/detail review to M-28",
        ]
        if lower_fig == "Q"
        else [
            "D-75 is an assembly arrangement; final hanger component "
            "orientation/field interface must be confirmed in the project layout"
        ]
    )
    blockers = list(dict.fromkeys(blockers))
    excluded_weight_scope = [
        entry.name
        for entry in result.entries
        if entry.unit_weight == 0
    ]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawings": list(profile["drawings"]),
        "source_revision": profile["revision"],
        "branch": f"UPPER-{upper_fig}/LOWER-{lower_fig}",
        "bom_ready": not excluded_weight_scope,
        "known_material_weight_ready": any(
            entry.unit_weight > 0
            for entry in result.entries
        ),
        "fabrication_ready": False,
        "blockers": blockers,
        "referenced_components": list(component_rows),
        "component_rows": component_rows,
        "excluded_weight_scope": excluded_weight_scope,
        "assembly_dimensions": {
            "line_size_in": line_size,
            "rod_size_in": rod_size,
            "H_min_mm": height_min,
            "H_max_mm": height_max,
            "H_is_range": parsed_h["is_range"],
            "rod_cut_length_mm": rod_cut_length,
            "turnbuckle": has_turnbuckle,
        },
    }
    result.evidence.extend(
        [
            make_evidence(
                "type62_component_selection",
                {
                    "upper_figure": upper_fig,
                    "lower_figure": lower_fig,
                    "component_rows": component_rows,
                },
                "visual_transcription",
                source=profile["drawings"][1],
                page=1,
                confidence=0.99,
            ),
            make_evidence(
                "type62_assembly_geometry",
                result.meta["fabrication"]["assembly_dimensions"],
                "visual_transcription",
                source=profile["drawings"][0],
                page=1,
                confidence=0.98,
                note=(
                    "H is preserved as assembly height; it is not "
                    "silently converted to M-22 cut length."
                ),
            ),
        ]
    )

    return result
