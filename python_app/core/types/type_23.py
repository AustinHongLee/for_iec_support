"""Type 23 source-aware top-mounted cantilever support (D-25)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import register_source_envelope
from ..models import AnalysisResult
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("23", strict=True)
    if not config:
        raise FileNotFoundError("Type 23 設定檔遺失或損毀")
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 23 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config[profile["member_table"]], config


def _parse(fullstring, fig_l_map):
    parts = str(fullstring).split("-")
    if len(parts) not in (3, 4):
        raise ValueError("格式應為 23-{M}-{HH}{Fig}[-{LL}]")
    member = parts[1].upper()
    token = parts[2]
    if len(token) < 2 or token[-1].upper() not in fig_l_map or not token[:-1].isdigit():
        raise ValueError("第三段需為 H(100mm單位)+Fig A/B/C")
    fig = token[-1].upper()
    h_mm = int(token[:-1]) * 100
    if fig == "C":
        if len(parts) != 4 or not parts[3].isdigit():
            raise ValueError("Fig.C 需且只能有第四段 L(100mm單位)")
        l_mm = int(parts[3]) * 100
    else:
        if len(parts) != 3:
            raise ValueError("Fig.A/B 不得有第四段 L")
        l_mm = fig_l_map[fig]
    if h_mm <= 0 or l_mm <= 0:
        raise ValueError("H與L必須大於0")
    return member, fig, h_mm, l_mm


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, members, config = _load(source_profile)
        member, fig, h_mm, l_mm = _parse(fullstring, config["FIG_L_MAP"])
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 23: {exc}"
        return result

    row = members.get(member)
    if not row:
        result.error = f"Type 23 / {profile_id}: D-25 未表列 MEMBER {member}"
        return result
    checks = [("H", h_mm, row["H_MAX"], True)]
    if row["L_MAX"] is not None:
        checks.append(("L", l_mm, row["L_MAX"], True))
    if not register_source_envelope(
        result,
        type_label=f"Type 23 / {profile_id}",
        source_ref=f"D-25 {member} L/H(MAX)",
        checks=checks,
    ):
        return result

    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    fab = config["fabrication_contract"]
    blockers = [
        "D-25未給下角接頭的精確端部切削/貼合輪廓",
        "D-25下角接頭焊道未標焊腳尺寸",
        "管線僅示意坐落於水平member；止滑/固定方式未在D-25定義",
    ]
    for cid, segment, length in (
        ("D25-MEMBER-M-VERTICAL", "H", h_mm),
        ("D25-MEMBER-M-HORIZONTAL", "L", l_mm),
    ):
        add_steel_section_entry(result, row["section_type"], row["lookup_dim"], length, material=material)
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.shape_spec = f'{row["full_spec"]}; CUT {segment}={length}; TYPE-23 FIG-{fig}'
        entry.geometry.parameters = {
            "segment": segment, "cut_length_mm": length, "H_mm": h_mm, "L_mm": l_mm,
            "figure": fig, "supported_line_center_from_free_end_mm": fab["supported_line_center_from_free_end_mm"],
            "top_field_fillet_weld_mm": fab["top_field_fillet_weld_mm"],
            "top_weld_all_around": fab["top_weld_all_around"], "u_bolt_shown": False,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]

    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": profile["drawing"], "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig}", "bom_ready": True, "fabrication_ready": False,
        "blockers": blockers, "H_mm": h_mm, "L_mm": l_mm,
    }
    result.warnings.append("D-25型鋼BOM可算；下角接頭與管線固定方式仍是加工blocker")
    result.evidence.extend([
        make_evidence("type23_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99),
        make_evidence("type23_H_L_mm", {"H": h_mm, "L": l_mm, "figure": fig}, "formula", source=profile["drawing"], confidence=0.99),
    ])
    return result
