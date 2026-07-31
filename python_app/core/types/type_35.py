"""Type 35 source-aware single-member support (D-40)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_source_envelope
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("35", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 35: 尚未建立來源 profile {profile_id}"
        return result

    parts = str(fullstring).split("-")
    if len(parts) != 3 or len(parts[2]) < 2:
        result.error = "Type 35: 格式應為 35-{M}-{HH}{A/B}"
        return result
    member = parts[1].upper()
    fig = parts[2][-1].upper()
    try:
        h_mm = int(parts[2][:-1]) * 100
    except ValueError:
        h_mm = 0
    if fig not in ("A", "B") or h_mm <= 0:
        result.error = "Type 35: 第三段需為正整數H與Fig A/B，例如05A"
        return result

    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 35 / {profile_id}: D-40未表列 MEMBER {member}"
        return result
    h_max = row.get(fig)
    if h_max is None:
        result.error = f"Type 35 / {profile_id}: D-40未提供 {member} FIG-{fig}"
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 35 / {profile_id}",
        source_ref=f"D-40 {member} FIG-{fig} H(MAX)",
        checks=(("H", h_mm, h_max, True),),
    ):
        return result

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    blocker = "existing surface接合位置與現場裁切條件需施工量測確認"
    add_steel_section_entry(
        result, row["section_type"], row["lookup_dim"], h_mm, material=material
    )
    entry = result.entries[-1]
    entry.geometry.component_id = f"D40-MEMBER-FIG-{fig}"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "field_cut_stock_section"
    entry.geometry.shape_spec = f'{row["full_spec"]}; CUT H={h_mm}; FIG-{fig}'
    entry.geometry.parameters = {
        "H_mm": h_mm,
        "figure": fig,
        "quantity": 1,
        "fillet_weld_mm": config["fabrication_contract"]["fillet_weld_mm"],
        "existing_surface_interface": True,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(entry, f"FIG-{fig}單支構件，現場裁切H={h_mm}")
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": [blocker],
    }
    result.evidence.append(
        make_evidence(
            "type35_member_row",
            row,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
