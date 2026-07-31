"""Type 21 source-aware cantilever U-bolt support calculator (D-23)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import (
    HardwareKind,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from ..issues import register_source_envelope
from ..models import AnalysisResult
from ..parser import get_part
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("21", strict=True)
    if not config:
        raise FileNotFoundError("Type 21 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 21 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config[profile["member_table"]], config


def _parse_designation(fullstring, fig_l_map):
    parts = str(fullstring).split("-")
    member_code = str(get_part(fullstring, 2) or "").upper()
    token = str(get_part(fullstring, 3) or "")
    if len(token) < 2 or token[-1].upper() not in fig_l_map or not token[:-1].isdigit():
        raise ValueError("第三段需為 H(100mm單位)+Fig A/B/C")

    fig = token[-1].upper()
    h_mm = int(token[:-1]) * 100
    fixed_l = fig_l_map[fig]
    if fig == "C":
        if len(parts) != 4 or not parts[3].isdigit():
            raise ValueError("Fig.C 需且只能有第四段 L(100mm單位)")
        l_mm = int(parts[3]) * 100
    else:
        if len(parts) != 3:
            raise ValueError("Fig.A/B 不得有第四段 L")
        l_mm = fixed_l
    if h_mm <= 0 or l_mm <= 0:
        raise ValueError("H與L必須大於0")
    return member_code, fig, h_mm, l_mm


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, members, config = _load(source_profile)
        member_code, fig, h_mm, l_mm = _parse_designation(
            fullstring, config["FIG_L_MAP"]
        )
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 21: {exc}"
        return result

    row = members.get(member_code)
    if not row:
        result.error = (
            f"Type 21 / {profile_id}: D-23 未表列 MEMBER {member_code}"
        )
        return result
    checks = [("H", h_mm, row["H_MAX"], True)]
    if row["L_MAX"] is not None:
        checks.append(("L", l_mm, row["L_MAX"], True))
    if not register_source_envelope(
        result,
        type_label=f"Type 21 / {profile_id}",
        source_ref=f"D-23 {member_code} L/H(MAX)",
        checks=checks,
    ):
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
    fabrication = config["fabrication_contract"]
    blockers = [
        "D-23未給上角接頭的精確端部切削/貼合輪廓",
        "D-23上角接頭焊道未標焊腳尺寸",
        "designation不含supported line size；D-68 U-bolt孔徑與孔距無法展開",
    ]

    for component_id, segment, cut_length in (
        ("D23-MEMBER-M-VERTICAL", "H", h_mm),
        ("D23-MEMBER-M-HORIZONTAL", "L", l_mm),
    ):
        add_steel_section_entry(
            result,
            row["section_type"],
            row["lookup_dim"],
            cut_length,
            material=material,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = component_id
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "angle_member_cut"
        entry.geometry.shape_spec = (
            f'{row["full_spec"]}; CUT {segment}={cut_length}; '
            f"TYPE-21 FIG-{fig}"
        )
        entry.geometry.parameters = {
            "member_code": member_code,
            "full_section": row["full_spec"],
            "segment": segment,
            "cut_length_mm": cut_length,
            "H_mm": h_mm,
            "L_mm": l_mm,
            "H_MAX_mm": row["H_MAX"],
            "L_MAX_mm": row["L_MAX"],
            "figure": fig,
            "supported_line_center_from_free_end_mm": fabrication[
                "supported_line_center_from_free_end_mm"
            ],
            "base_field_fillet_weld_mm": fabrication[
                "base_field_fillet_weld_mm"
            ],
            "base_weld_all_around": fabrication["base_weld_all_around"],
            "upper_joint_weld_size_mm": fabrication["upper_joint_weld_size_mm"],
            "u_bolt_reference": fabrication["u_bolt_reference"],
            "u_bolt_furnished": fabrication["u_bolt_furnished"],
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member_code}/FIG-{fig}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly": {
            "vertical_cut_H_mm": h_mm,
            "horizontal_cut_L_mm": l_mm,
            "supported_line_center_from_free_end_mm": 100,
            "base_field_fillet_weld_mm": 6,
            "u_bolt_reference": "D-68",
            "u_bolt_furnished": False,
        },
    }
    result.warnings.append(
        "D-23型鋼BOM可算；上角接頭端部加工/焊腳與D-68 U-bolt孔位仍待補齊"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type21_member_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type21_H_L_mm",
                {"H": h_mm, "L": l_mm, "figure": fig},
                "formula",
                source=profile["drawing"],
                confidence=0.99,
                note_ref="DESIGNATION NOTE 1",
            ),
        ]
    )
    return result
