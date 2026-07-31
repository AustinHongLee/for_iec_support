"""Type 03 source-aware elbow support (Chung Wei D-3)."""
from __future__ import annotations

from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import (
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..models import AnalysisEntry, AnalysisResult, GeometryHints, set_remark
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.pipe_table import get_pipe_od


def _load(source_profile):
    config = load_config("03", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 03 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) != 3:
        raise ValueError("格式應為 03-{line size}-{HH}{M42}")
    line_size = float(get_lookup_value(parts[1]))
    token = parts[2].upper()
    if len(token) < 2 or not token[:-1].isdigit() or not token[-1].isalpha():
        raise ValueError("第三段應為高度(100mm)加 M-42 字母，例如 05N")
    return parts[1], line_size, int(token[:-1]) * 100, token[-1]


def _decorate_m42(entries, profile):
    for index, entry in enumerate(entries, start=1):
        entry.geometry.source_drawing = profile["m42_drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.component_id = f"M42-{entry.name.upper()}-{index}"
        if entry.category == "鋼板類":
            entry.geometry.shape_kind = entry.geometry.shape_kind or "m42_plate"
            entry.geometry.fabrication_ready = True
        elif entry.category == "螺栓類":
            entry.geometry.shape_kind = "purchased_fastener"
            entry.geometry.fabrication_ready = False
            entry.geometry.fabrication_blockers = ["M-43只給扣件公稱直徑，未給完整長度/單重"]


def _add_ubolt(result, pipe_token, overrides, profile):
    spec_override = str(overrides.get("ubolt_spec") or "").strip()
    material_override = str(overrides.get("ubolt_material") or "").strip()
    weight_raw = overrides.get("ubolt_unit_weight_kg")
    try:
        unit_weight = float(weight_raw) if weight_raw not in (None, "") else 0.0
    except (TypeError, ValueError):
        raise ValueError("ubolt_unit_weight_kg 必須為數值")
    if unit_weight < 0:
        raise ValueError("ubolt_unit_weight_kg 不得小於0")

    spec = spec_override or f"U-BOLT FOR {pipe_token}"
    material = material_override or "NOT SPECIFIED IN D-3"
    blockers = []
    if not spec_override:
        blockers.append("D-3未指定U-bolt標準、桿徑、腿長與孔距")
    if not material_override:
        blockers.append("D-3未指定U-bolt材質")
    entry = AnalysisEntry(
        name="U.bolt",
        spec=spec,
        material=material,
        quantity=1,
        unit_weight=unit_weight,
        total_weight=unit_weight,
        unit="SET",
        factor=1,
        qty_subtotal=1,
        weight_output=unit_weight,
        category="螺栓類",
        role=ComponentRole.U_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
        geometry=GeometryHints(
            role=ComponentRole.U_BOLT.value,
            component_id="D3-U-BOLT",
            source_drawing=profile["drawing"],
            source_revision=profile["revision"],
            shape_kind="purchased_ubolt",
            shape_spec=spec,
            fabrication_ready=not blockers,
            fabrication_blockers=blockers,
            parameters={
                "supported_line_size": pipe_token,
                "spec_explicit": bool(spec_override),
                "material_explicit": bool(material_override),
                "unit_weight_kg": unit_weight,
            },
        ),
    )
    result.add_entry(entry)
    return blockers


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, config = _load(source_profile)
        pipe_token, line_size, h_mm, letter = _parse(fullstring)
    except (TypeError, ValueError) as exc:
        result.error = f"Type 03: {exc}"
        return result

    limits = config["constraints"]
    if line_size <= 0 or line_size > limits["line_size_max_in"]:
        result.error = (
            f'Type 03 / {profile_id}: supported line {line_size:g}" '
            f'超出 D-3 範圍 (≤{limits["line_size_max_in"]}")'
        )
        return result
    if h_mm <= 0:
        result.error = (
            f"Type 03 / {profile_id}: H={h_mm}mm 超出 D-3 "
            f"0<H≤{limits['H_max_mm']}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 03 / {profile_id}",
        source_ref="D-3 H上限",
        checks=(("H", h_mm, limits["H_max_mm"], True),),
    ):
        return result
    if letter not in limits["allowed_m42"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 03 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 03 / {profile_id}",
            source_ref="D-3",
            letter=letter,
            host_allowed=limits["allowed_m42"],
        )

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    steel_material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    fab = config["fabrication_contract"]
    explicit_radius = overrides.get("elbow_center_radius_mm")
    explicit_cut = overrides.get("vertical_cut_length_mm")
    try:
        radius_mm = (
            float(explicit_radius)
            if explicit_radius not in (None, "")
            else line_size * 25.4 * fab["elbow_center_radius_factor_assumption"]
        )
        vertical_cut = (
            float(explicit_cut)
            if explicit_cut not in (None, "")
            else h_mm + radius_mm + get_pipe_od(line_size) / 2
            + fab["elbow_top_clearance_mm"]
        )
    except (TypeError, ValueError) as exc:
        result.error = f"Type 03: 切長覆寫無法解析 ({exc})"
        return result
    if radius_mm <= 0 or vertical_cut <= 0:
        result.error = "Type 03: elbow_center_radius_mm / vertical_cut_length_mm 必須大於0"
        return result

    add_steel_section_entry(
        result, "Angle", "75*75*9", round(vertical_cut, 1),
        material=steel_material,
    )
    vertical = result.entries[-1]
    vertical.geometry.component_id = "D3-VERTICAL-L75"
    vertical.geometry.source_drawing = profile["drawing"]
    vertical.geometry.source_revision = profile["revision"]
    vertical.geometry.shape_kind = "stock_section_cut"
    vertical.geometry.formula = (
        "vertical_cut_length_mm override"
        if explicit_cut not in (None, "")
        else fab["vertical_formula"]
    )
    vertical.geometry.shape_spec = f"L75X75X9; CUT={vertical_cut:g}"
    vertical.geometry.parameters = {
        "H_mm": h_mm,
        "elbow_center_radius_mm": radius_mm,
        "elbow_radius_explicit": explicit_radius not in (None, ""),
        "supported_pipe_od_mm": get_pipe_od(line_size),
        "clearance_mm": fab["elbow_top_clearance_mm"],
        "cut_length_mm": vertical_cut,
        "cut_length_explicit": explicit_cut not in (None, ""),
        "weld_mm": fab["weld_mm"],
    }
    vertical.geometry.fabrication_ready = explicit_cut not in (None, "")
    vertical.geometry.fabrication_blockers = (
        []
        if vertical.geometry.fabrication_ready
        else [
            "D-3 H為現場調整尺寸",
            "D-3未文字指定彎頭半徑；目前依長半徑1.5D推導",
        ]
    )
    set_remark(
        vertical,
        (
            f"H={h_mm}+彎頭中心半徑={radius_mm:g}+OD/2="
            f"{get_pipe_od(line_size) / 2:g}+20；D-3 H現場調整"
        ),
    )

    add_steel_section_entry(
        result, "Angle", "75*75*9", fab["horizontal_cut_length_mm"],
        material=steel_material,
    )
    horizontal = result.entries[-1]
    horizontal.geometry.component_id = "D3-HORIZONTAL-L75"
    horizontal.geometry.source_drawing = profile["drawing"]
    horizontal.geometry.source_revision = profile["revision"]
    horizontal.geometry.shape_kind = "stock_section_with_ubolt_holes"
    horizontal.geometry.shape_spec = "L75X75X9; CUT=130; U-BOLT HOLES TBD"
    horizontal.geometry.parameters = {
        "cut_length_mm": fab["horizontal_cut_length_mm"],
        "u_bolt_hole_diameter_mm": None,
        "u_bolt_hole_pitch_mm": None,
        "weld_mm": fab["weld_mm"],
    }
    horizontal.geometry.fabrication_ready = False
    horizontal.geometry.fabrication_blockers = ["D-3未標U-bolt孔徑與孔距"]

    try:
        ubolt_blockers = _add_ubolt(result, pipe_token, overrides, profile)
    except ValueError as exc:
        result.error = f"Type 03: {exc}"
        result.entries.clear()
        return result

    m42_start = len(result.entries)
    perform_action_by_letter(
        result, letter, "L75*75*9", source_profile=profile_id
    )
    if result.error:
        result.entries.clear()
        return result
    _decorate_m42(result.entries[m42_start:], profile)

    blockers = [
        *vertical.geometry.fabrication_blockers,
        *horizontal.geometry.fabrication_blockers,
        *ubolt_blockers,
    ]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f'{pipe_token}/M42-{letter}',
        "bom_ready": not ubolt_blockers,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "H_mm": h_mm,
            "vertical_cut_length_mm": round(vertical_cut, 1),
            "horizontal_cut_length_mm": fab["horizontal_cut_length_mm"],
            "elbow_center_radius_mm": radius_mm,
        },
    }
    if explicit_radius in (None, "") and explicit_cut in (None, ""):
        result.warnings.append(
            "D-3未明文指定彎頭半徑；垂直角鋼暫按長半徑1.5D推導，"
            "最終加工需 elbow_center_radius_mm 或 vertical_cut_length_mm"
        )
    result.warnings.append(
        "D-3 U-bolt 無標準號/桿徑/腿長/材質/單重；已移除舊 SUS304 1kg 假值"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type03_constraints",
                limits,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type03_horizontal_cut_length_mm",
                fab["horizontal_cut_length_mm"],
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type03_vertical_cut_length_mm",
                round(vertical_cut, 1),
                "rule" if explicit_cut not in (None, "") else "assumption",
                source=profile["drawing"],
                confidence=0.99 if explicit_cut not in (None, "") else 0.65,
                note=vertical.geometry.formula,
            ),
        ]
    )
    return result
