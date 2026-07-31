"""Type 20 source-aware slotted member calculator (D-22)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import register_source_envelope
from ..models import AnalysisResult
from ..parser import get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("20", strict=True)
    if not config:
        raise FileNotFoundError("Type 20 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 20 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config[profile["member_table"]], config


def _optional_positive(overrides, key):
    raw = overrides.get(key)
    if raw in (None, ""):
        return None
    value = float(raw)
    if value <= 0:
        raise ValueError(f"{key} 必須大於0")
    return value


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, members, config = _load(source_profile)
        member_code = str(get_part(fullstring, 2) or "").upper()
        token = str(get_part(fullstring, 3) or "")
        if len(token) < 2 or token[-1].upper() not in ("A", "B") or not token[:-1].isdigit():
            raise ValueError("第三段需為 H(100mm單位)+Fig A/B")
        fig = token[-1].upper()
        h_mm = int(token[:-1]) * 100
        line_size = _optional_positive(overrides, "supported_line_size_in")
        rod_diameter = _optional_positive(overrides, "u_bolt_rod_diameter_mm")
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 20: {exc}"
        return result

    row = members.get(member_code)
    if not row:
        result.error = f"Type 20 / {profile_id}: D-22 未表列 MEMBER {member_code}"
        return result
    if h_mm <= 0:
        result.error = (
            f"Type 20 / {profile_id}: H={h_mm}mm 超出 "
            f'{member_code} H(MAX)={row["H_MAX"]}mm'
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 20 / {profile_id}",
        source_ref=f"D-22 {member_code} H(MAX)",
        checks=(("H", h_mm, row["H_MAX"], True),),
    ):
        return result

    z_table = {float(key): value for key, value in config["Z_TABLE"].items()}
    z_mm = z_table.get(line_size) if line_size is not None else None
    if line_size is not None and z_mm is None:
        result.error = f'Type 20: supported_line_size_in={line_size:g}" 不在 Z table'
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
    add_steel_section_entry(
        result, row["section_type"], row["lookup_dim"], h_mm, material=material
    )
    entry = result.entries[-1]
    fab = config["fabrication_contract"]
    slot_width = rod_diameter + 3 if rod_diameter is not None else None
    blockers = []
    if z_mm is None:
        blockers.append("designation 不含 supported line size，缺 Z slot spacing")
    if slot_width is None:
        blockers.append("缺 U-bolt rod diameter，無法決定 slot width=rod+3")
    blockers.append("Slot detail 的80/30/30基準線需確認後才能輸出孔中心座標")
    entry.geometry.component_id = "D22-MEMBER-M"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "slotted_angle_member" if row["section_type"] == "Angle" else "slotted_channel_member"
    entry.geometry.shape_spec = f'{row["full_spec"]}; CUT H={h_mm}; 2-SLOT 60x{slot_width if slot_width else "ROD+3"}'
    entry.geometry.parameters = {
        "member_code": member_code,
        "full_section": row["full_spec"],
        "cut_length_H_mm": h_mm,
        "H_MAX_mm": row["H_MAX"],
        "figure": fig,
        "slot_count": fab["slot_count"],
        "slot_length_mm": fab["slot_length_mm"],
        "slot_half_length_mm": fab["slot_half_length_mm"],
        "slot_width_mm": slot_width,
        "slot_width_formula": fab["slot_width_formula"],
        "slot_center_spacing_Z_mm": z_mm,
        "supported_line_size_in": line_size,
        "raw_detail_dimensions_mm": [80, 30, 30],
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = blockers
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member_code}/FIG-{fig}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": entry.geometry.parameters,
        "not_furnished": fab["not_furnished"],
    }
    if z_mm is None or slot_width is None:
        result.warnings.append(
            "D-22 member重量可算，但加工slot需 supported_line_size_in 與 "
            "u_bolt_rod_diameter_mm"
        )
    result.evidence.extend([
        make_evidence("type20_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99),
        make_evidence("type20_slot_Z_mm", z_mm, "visual_transcription", source=profile["drawing"], confidence=0.99 if z_mm else 0.0),
    ])
    return result
