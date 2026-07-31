"""Type 19 drawing-backed relief-valve lateral brace (Chung Wei D-21)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("19", strict=True)
    if not config:
        raise FileNotFoundError("Type 19 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 19 尚未建立來源 profile: {profile_id}") from exc
    table = {
        float(key): value
        for key, value in config[profile["table_source"]].items()
    }
    return profile_id, profile, table, config


def _cut_length(overrides):
    raw = overrides.get("member_cut_length_mm")
    if raw in (None, ""):
        return None
    value = float(raw)
    if value <= 0:
        raise ValueError("member_cut_length_mm 必須大於0")
    return value


def _decorate(entry, profile, kind, spec, params, blockers):
    entry.geometry.component_id = "D21-MEMBER-M"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = kind
    entry.geometry.shape_spec = spec
    entry.geometry.parameters = params
    entry.geometry.fabrication_ready = not blockers
    entry.geometry.fabrication_blockers = list(blockers)


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, table, config = _load(source_profile)
        if get_part(fullstring, 3) not in (None, ""):
            raise ValueError("D-21 designation 只有 Type 與 supported line size 兩段")
        line_size = float(get_lookup_value(get_part(fullstring, 2)))
        cut_length = _cut_length(overrides)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 19: {exc}"
        return result

    row = table.get(line_size)
    if row is None:
        result.error = f'Type 19 / {profile_id}: D-21 未表列 {line_size:g}"'
        return result

    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=material_context.service,
        overrides=material_context.material_overrides,
    )
    fab = config["fabrication_contract"]
    length = cut_length or 0
    common_params = {
        "supported_line_size_in": line_size,
        "drawing_L_mm": row["drawing_L_mm"],
        "cut_length_mm": cut_length,
        "field_cut": True,
        "slope_ratio": "1:1",
        "slope_degrees": fab["slope_degrees"],
        "weld_mm": fab["fillet_weld_mm"],
        "weld_sides": fab["weld_sides"],
    }
    blockers = []
    if cut_length is None:
        blockers.append("D-21 NOTE 1: 缺 member_cut_length_mm 現場切長")
    blockers.append("上下端貼管 cope/端切輪廓未尺寸化")

    if row["section_family"] == "angle":
        add_steel_section_entry(
            result, "Angle", row["lookup_dim"], length, material=material
        )
        entry = result.entries[-1]
        params = {
            **common_params,
            "section": row["member"],
            "lower_end_pocket_drain_cut_mm": fab["angle_pocket_drain_cut_mm"],
            "lower_end_detail": "DETAIL Z / L-ANGLE ONLY",
        }
        angle_blockers = [
            *blockers,
            "DETAIL Z 的 20C pocket-drain cut 未定義完整 arc/切線幾何",
        ]
        _decorate(
            entry,
            profile,
            "diagonal_angle_with_pocket_drain_cut",
            f'{row["member"]}; CUT L={length:g}; LOWER END 20C',
            params,
            angle_blockers,
        )
    else:
        add_steel_section_entry(
            result, "H Beam", row["lookup_dim"], length, material=material
        )
        entry = result.entries[-1]
        parent_weight = float(fab["parent_h_section_weight_per_m_kg"])
        split_count = int(fab["t_section_split_count"])
        entry.name = "T型鋼（H型鋼剖分）"
        entry.weight_per_unit = parent_weight / split_count
        entry.unit_weight = round(length / 1000 * entry.weight_per_unit, 2)
        entry.total_weight = round(entry.unit_weight * entry.quantity, 2)
        entry.weight_output = round(entry.factor * entry.total_weight, 2)
        params = {
            **common_params,
            "parent_section": row["parent_section"],
            "split_count": split_count,
            "weight_basis": "one half of parent H-section kg/m",
            "parent_weight_per_m_kg": parent_weight,
            "t_section_weight_per_m_kg": entry.weight_per_unit,
            "nominal_T_overall_depth_mm": 97,
            "flange_width_mm": 150,
            "flange_thickness_mm": 9,
            "web_thickness_mm": 6,
        }
        t_blockers = [
            *blockers,
            "H194 縱向剖分的 kerf/圓角/實際 T 截面尺寸未標示",
        ]
        _decorate(
            entry,
            profile,
            "t_section_split_from_h_beam",
            f'T CUT FROM {row["parent_section"]}; CUT L={length:g}',
            params,
            t_blockers,
        )

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": row["section_family"],
        "bom_ready": cut_length is not None,
        "fabrication_ready": False,
        "blockers": list(entry.geometry.fabrication_blockers),
        "dimensions": {
            "supported_line_size_in": line_size,
            "drawing_L_mm": row["drawing_L_mm"],
            "member_cut_length_mm": cut_length,
            "member_M": row["member"],
        },
    }
    if cut_length is None:
        result.warnings.append(
            f'D-21 NOTE 1 指定 L 現場切割；表列 {row["drawing_L_mm"]}mm '
            "不再當成實際下料，缺 member_cut_length_mm 時重量為0"
        )
    result.warnings.append("D-21 上下端貼管切口尚未尺寸化，暫不能直接出完整加工圖")
    result.evidence.extend([
        make_evidence(
            "type19_source_row", row, "visual_transcription",
            source=profile["drawing"], confidence=0.99,
            note="D-21 M/L table and A-A view",
        ),
        make_evidence(
            "member_cut_length_mm", cut_length, "field_measurement",
            source=profile["drawing"], confidence=1.0 if cut_length else 0.0,
            note=fab["field_cut_basis"],
        ),
        make_evidence(
            "member_slope", "1:1", "visual_transcription",
            source=profile["drawing"], confidence=0.99,
        ),
    ])
    return result
