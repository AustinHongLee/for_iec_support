"""Type 07 source-aware sliding elbow support (Chung Wei D-7)."""
from __future__ import annotations

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
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m42_table import resolve_m42_data


def _load(source_profile):
    config = load_config("07", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 07 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) != 3:
        raise ValueError("格式應為 07-{line size}-{HH}{M42}")
    line_size = float(get_lookup_value(parts[1]))
    token = parts[2].upper()
    if len(token) < 2 or not token[:-1].isdigit() or not token[-1].isalpha():
        raise ValueError("第三段應為高度(100mm)加 M-42 字母，例如 20J")
    return parts[1], line_size, int(token[:-1]) * 100, token[-1]


def _positive_override(overrides, key, default):
    raw = overrides.get(key)
    if raw in (None, ""):
        return float(default), False
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{key} 必須大於0")
    return value, True


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


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, config = _load(source_profile)
        pipe_token, line_size, h_mm, letter = _parse(fullstring)
    except (TypeError, ValueError) as exc:
        result.error = f"Type 07: {exc}"
        return result

    table = config[profile["table"]]
    row = table.get(str(int(line_size))) if line_size.is_integer() else None
    if not row:
        result.error = (
            f'Type 07 / {profile_id}: D-7未表列 supported line {line_size:g}"'
        )
        return result
    limits = config["constraints"]
    if h_mm <= limits["H_min_exclusive_mm"]:
        result.error = (
            f"Type 07 / {profile_id}: D-7要求 "
            f"{limits['H_min_exclusive_mm']}<H<{limits['H_max_exclusive_mm']}mm，"
            f"收到 H={h_mm}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 07 / {profile_id}",
        source_ref=f"D-7 H<{limits['H_max_exclusive_mm']}mm",
        checks=(
            (
                "H",
                h_mm,
                limits["H_max_exclusive_mm"],
                False,
            ),
        ),
    ):
        return result
    if letter not in limits["allowed_m42"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 07 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 07 / {profile_id}",
            source_ref="D-7",
            letter=letter,
            host_allowed=limits["allowed_m42"],
        )

    pipe_b_size, pipe_b_sch = row["pipe_b"]
    pipe_c_size, pipe_c_sch = row["pipe_c"]
    plate_e = row["plate_e"]
    plate_f = row["plate_f"]
    fab = config["fabrication_contract"]
    pipe_c_value = float(get_lookup_value(pipe_c_size))
    m42_row, m42_warning = resolve_m42_data(pipe_c_value)
    if m42_warning:
        result.warnings.append(m42_warning)
    m42_t = m42_row["plate_thickness"]
    pipe_b_formula_cut = row["L"] + fab["supported_line_to_sliding_surface_mm"]
    pipe_c_formula_cut = (
        h_mm
        - fab["supported_line_to_sliding_surface_mm"]
        - plate_f[2]
        - m42_t
    )
    try:
        pipe_b_cut, pipe_b_explicit = _positive_override(
            overrides, "support_pipe_b_cut_length_mm", pipe_b_formula_cut
        )
        pipe_c_cut, pipe_c_explicit = _positive_override(
            overrides, "support_pipe_c_cut_length_mm", pipe_c_formula_cut
        )
        weep_raw = overrides.get("weep_hole_center_offset_mm")
        weep_offset = (
            float(weep_raw)
            if weep_raw not in (None, "")
            else fab["weep_hole_center_offset_mm"]
        )
        if weep_offset is not None and weep_offset < 0:
            raise ValueError("weep_hole_center_offset_mm 不得小於0")
    except (TypeError, ValueError) as exc:
        result.error = f"Type 07: {exc}"
        return result

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = ctx.service
    material_overrides = ctx.material_overrides
    support_pipe_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PIPE,
        service=service,
        overrides=material_overrides,
    )
    plate_material = resolve_hardware_material(
        HardwareKind.SUPPORT_PLATE,
        service=service,
        overrides=material_overrides,
    )
    bolt_material = resolve_hardware_material(
        HardwareKind.EXPANSION_BOLT,
        service=service,
        overrides=material_overrides,
    )
    m42_steel_material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=service,
        overrides=material_overrides,
    )

    add_pipe_entry(
        result,
        pipe_b_size,
        pipe_b_sch,
        pipe_b_cut,
        support_pipe_material,
    )
    pipe_b = result.entries[-1]
    pipe_b.geometry.component_id = "D7-SUPPORTING-PIPE-B"
    pipe_b.geometry.source_drawing = profile["drawing"]
    pipe_b.geometry.source_revision = profile["revision"]
    pipe_b.geometry.shape_kind = "dummy_pipe_welded_to_lr_elbow"
    pipe_b.geometry.shape_spec = (
        f'{pipe_b_size}" {pipe_b_sch}; CUT={pipe_b_cut:g}; '
        "TOP END FIT TO LR ELBOW"
    )
    pipe_b.geometry.formula = (
        "support_pipe_b_cut_length_mm override"
        if pipe_b_explicit
        else "L + 200"
    )
    pipe_b.geometry.parameters = {
        "pipe_size_B": pipe_b_size,
        "schedule": pipe_b_sch,
        "L_lr_elbow_mm": row["L"],
        "supported_line_to_sliding_surface_mm": fab[
            "supported_line_to_sliding_surface_mm"
        ],
        "cut_length_mm": pipe_b_cut,
        "cut_length_explicit": pipe_b_explicit,
        "weld_mm": fab["weld_mm"],
    }
    pipe_b.geometry.fabrication_ready = False
    pipe_b.geometry.fabrication_blockers = [
        "D-7未完整尺寸化 Pipe B 與長半徑彎頭的貼合端輪廓"
    ]
    set_remark(pipe_b, f"L={row['L']}+200；上端與LR elbow貼合")

    add_pipe_entry(
        result,
        pipe_c_size,
        pipe_c_sch,
        pipe_c_cut,
        support_pipe_material,
    )
    pipe_c = result.entries[-1]
    pipe_c.geometry.component_id = "D7-SUPPORTING-PIPE-C"
    pipe_c.geometry.source_drawing = profile["drawing"]
    pipe_c.geometry.source_revision = profile["revision"]
    pipe_c.geometry.shape_kind = "square_cut_pipe_with_weep_hole"
    pipe_c.geometry.shape_spec = (
        f'{pipe_c_size}" {pipe_c_sch}; CUT={pipe_c_cut:g}; '
        f'DIA{fab["weep_hole_diameter_mm"]} WEEP HOLE'
    )
    pipe_c.geometry.formula = (
        "support_pipe_c_cut_length_mm override"
        if pipe_c_explicit
        else "H - 200 - Plate_F_t - M42_t"
    )
    pipe_c.geometry.parameters = {
        "H_mm": h_mm,
        "offset_mm": fab["supported_line_to_sliding_surface_mm"],
        "plate_F_thickness_mm": plate_f[2],
        "m42_plate_thickness_mm": m42_t,
        "cut_length_mm": pipe_c_cut,
        "cut_length_explicit": pipe_c_explicit,
        "weep_hole_diameter_mm": fab["weep_hole_diameter_mm"],
        "weep_hole_center_offset_mm": weep_offset,
        "weld_mm": fab["weld_mm"],
    }
    pipe_c_blockers = []
    if not pipe_c_explicit:
        pipe_c_blockers.append("D-7 H需現場調整")
    if weep_offset is None:
        pipe_c_blockers.append("D-7未標Ø6 weep hole中心離底板尺寸")
    pipe_c.geometry.fabrication_ready = not pipe_c_blockers
    pipe_c.geometry.fabrication_blockers = pipe_c_blockers
    set_remark(pipe_c, f"H-200-Ft-M42t={pipe_c_cut:g}；H現場調整")

    add_plate_entry(
        result,
        plate_e[0],
        plate_e[1],
        plate_e[2],
        "Plate_E",
        material=plate_material,
        plate_role="base_plate",
        shape_spec=f'{plate_e[0]}x{plate_e[1]}x{plate_e[2]}t',
        shape_kind="square_base_plate",
    )
    base_e = result.entries[-1]
    base_e.geometry.component_id = "D7-BASE-PLATE-E"
    base_e.geometry.source_drawing = profile["drawing"]
    base_e.geometry.source_revision = profile["revision"]
    base_e.geometry.parameters.update(
        {
            "side_mm": plate_e[0],
            "thickness_mm": plate_e[2],
            "weld_mm": fab["weld_mm"],
        }
    )
    base_e.geometry.fabrication_ready = True

    add_plate_entry(
        result,
        plate_f[0],
        plate_f[1],
        plate_f[2],
        "Plate_F",
        material=plate_material,
        plate_role="generic_plate",
        shape_spec=f'{plate_f[0]}x{plate_f[1]}x{plate_f[2]}t',
        shape_kind="square_sliding_plate",
    )
    sliding_f = result.entries[-1]
    sliding_f.geometry.component_id = "D7-SLIDING-PLATE-F"
    sliding_f.geometry.source_drawing = profile["drawing"]
    sliding_f.geometry.source_revision = profile["revision"]
    sliding_f.geometry.parameters.update(
        {
            "side_mm": plate_f[0],
            "thickness_mm": plate_f[2],
            "sliding_surface": True,
        }
    )
    sliding_f.geometry.fabrication_ready = True

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        pipe_c_value,
        plate_material=plate_material,
        bolt_material=bolt_material,
        steel_material=m42_steel_material,
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    _decorate_m42(result.entries[m42_start:], profile)

    blockers = [
        *pipe_b.geometry.fabrication_blockers,
        *pipe_c.geometry.fabrication_blockers,
    ]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f'{pipe_token}/M42-{letter}',
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "line_size_A": line_size,
            "H_mm": h_mm,
            "pipe_B_cut_length_mm": pipe_b_cut,
            "pipe_C_cut_length_mm": pipe_c_cut,
            "plate_E": plate_e,
            "plate_F": plate_f,
            "L_mm": row["L"],
            "m42_plate_thickness_mm": m42_t,
        },
    }
    result.warnings.append(
        "D-7 H需現場調整；Pipe B elbow貼合端與Ø6 weep-hole定位仍是加工圖 blocker"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type07_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type07_pipe_B_cut_length_mm",
                pipe_b_cut,
                "formula",
                source=profile["drawing"],
                confidence=0.99,
                note="D-7 NOTE 4; L + 200",
            ),
            make_evidence(
                "type07_pipe_C_cut_length_mm",
                pipe_c_cut,
                "formula",
                source=profile["drawing"],
                confidence=0.94,
                note="H - 200 - Plate F thickness - M42 plate thickness",
            ),
        ]
    )
    return result
