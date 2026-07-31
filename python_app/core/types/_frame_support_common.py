"""Shared source-aware engine for D-36/D-37/D-38/D-39 frame supports."""
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


def _parse(type_id: str, fullstring: str):
    parts = str(fullstring).split("-")
    if len(parts) != 3 or len(parts[2]) != 4 or not parts[2].isdigit():
        raise ValueError(f"格式應為 {type_id}-{{M}}-{{LL}}{{HH}}")
    l_mm = int(parts[2][:2]) * 100
    h_mm = int(parts[2][2:]) * 100
    if l_mm <= 0 or h_mm <= 0:
        raise ValueError("L與H必須大於0")
    return parts[1].upper(), l_mm, h_mm


def calculate_frame(type_id: str, fullstring: str, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config(type_id, strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type {type_id}: 尚未建立來源 profile {profile_id}"
        return result
    try:
        member, l_mm, h_mm = _parse(type_id, fullstring)
    except ValueError as exc:
        result.error = f"Type {type_id}: {exc}"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type {type_id} / {profile_id}: 原圖未表列 MEMBER {member}"
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type {type_id} / {profile_id}",
        source_ref=f"{profile['drawing']} {member} L/H(MAX)",
        checks=(
            ("L", l_mm, row["L_MAX"], True),
            ("H", h_mm, row["H_MAX"], True),
        ),
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
    contract = config["fabrication_contract"]
    blockers = [
        "原圖要求H/L依現場裁切，existing steel接合面需施工量測確認",
        "原圖只標6mm焊道，角部端切/貼合細節需加工圖展開",
    ]
    occurrence = {"H": 0, "L": 0}
    role_map = {
        "31": {"H": ("LEG", "立柱"), "L": ("TOP-BEAM", "上橫梁")},
        "32": {"H": ("HANGER-LEG", "吊腿"), "L": ("BOTTOM-BEAM", "下橫梁")},
        "33": {"H": ("END-POST", "右側立柱"), "L": ("BOTTOM-BEAM", "懸臂下梁")},
        "34": {"H": ("END-POST", "右側立柱"), "L": ("TOP-BEAM", "上橫梁")},
    }[type_id]
    for segment in contract["segments"]:
        occurrence[segment] += 1
        length = h_mm if segment == "H" else l_mm
        role_code, role_zh = role_map[segment]
        suffix = f"-{occurrence[segment]}" if contract["segments"].count(segment) > 1 else ""
        add_steel_section_entry(
            result, row["section_type"], row["lookup_dim"], length, material=material
        )
        entry = result.entries[-1]
        entry.geometry.component_id = f"D{int(type_id)+5}-{role_code}{suffix}"
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "field_cut_stock_section"
        entry.geometry.shape_spec = f"{row['full_spec']}; CUT {segment}={length}"
        entry.geometry.parameters = {
            "layout": contract["layout"],
            "segment": segment,
            "cut_length_mm": length,
            "assembly_L_mm": l_mm,
            "assembly_H_mm": h_mm,
            "fillet_weld_mm": contract["fillet_weld_mm"],
            "existing_steel_interface": True,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]
        set_remark(
            entry,
            f"{role_zh}，現場裁切{segment}={length}",
            f"{role_code}, field cut {segment}={length}",
        )

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member}/{contract['layout']}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "L_mm": l_mm,
        "H_mm": h_mm,
    }
    result.warnings.append("型鋼BOM可算；existing steel接合面與角部端切仍需加工圖確認")
    result.evidence.append(
        make_evidence(
            f"type{type_id}_member_row",
            row,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
