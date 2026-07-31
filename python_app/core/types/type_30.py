"""Type 30 source-aware two-member support, Fig A/B (D-35)."""
from __future__ import annotations

from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import add_issue, register_source_envelope
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) not in (3, 4) or len(parts[2]) != 5:
        raise ValueError("格式應為 30-{M}-{LL}{HH}{A/B}[-{L1}{L2}]")
    token = parts[2]
    if not token[:4].isdigit() or token[-1].upper() not in ("A", "B"):
        raise ValueError("第三段需為4位L/H加Fig A或B")
    l_mm = int(token[:2]) * 100
    h_mm = int(token[2:4]) * 100
    if l_mm <= 0 or h_mm <= 15:
        raise ValueError("L必須大於0且H必須大於15mm")
    if len(parts) == 4:
        if len(parts[3]) != 4 or not parts[3].isdigit():
            raise ValueError("第四段需為2位L1+2位L2")
        l1 = int(parts[3][:2]) * 100
        l2 = int(parts[3][2:]) * 100
    else:
        l1 = l2 = l_mm / 2
    return parts[1].upper(), l_mm, h_mm, token[-1].upper(), l1, l2


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("30", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 30: 尚未建立來源 profile {profile_id}"
        return result
    try:
        member, l_mm, h_mm, fig, l1, l2 = _parse(fullstring)
    except ValueError as exc:
        result.error = f"Type 30: {exc}"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 30 / {profile_id}: D-35未表列 MEMBER {member}"
        return result
    if l1 + l2 != l_mm:
        add_issue(
            result,
            code="DESIGNATION_L1_L2_MISMATCH",
            severity="high",
            message=(
                f"Type 30 / {profile_id}: L1+L2={l1}+{l2}={l1+l2:g}mm，"
                f"不等於L={l_mm}mm；BOM暫按L/H計算，定位須確認"
            ),
            scope="designation_consistency",
            calculation_allowed=True,
            bom_allowed=False,
            fabrication_allowed=False,
            source="D-35",
        )
    if not register_source_envelope(
        result,
        type_label=f"Type 30 / {profile_id}",
        source_ref=f"D-35 {member} L/H(MAX)",
        checks=(
            ("L", l_mm, row["L_MAX"], True),
            ("H", h_mm, row["H_MAX"], True),
        ),
    ):
        return result
    contract = config["fabrication_contract"]
    post_cut = h_mm - contract["post_end_inset_mm"]
    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    blockers = [
        "D-35要求H/L依現場裁切，existing steel接合面需施工量測確認",
        "角鋼/槽鋼在圖示左右視圖的截面朝向未編入designation",
    ]
    for cid, role, length, segment in (
        ("D35-MEMBER-H", "立柱", post_cut, "H-15"),
        ("D35-MEMBER-L", "橫向承件", l_mm, "L"),
    ):
        add_steel_section_entry(result, row["section_type"], row["lookup_dim"], length, material=material)
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "field_cut_stock_section"
        entry.geometry.shape_spec = f"{row['full_spec']}; CUT={length}"
        entry.geometry.parameters = {
            "figure": fig, "segment": segment, "cut_length_mm": length,
            "assembly_H_mm": h_mm, "assembly_L_mm": l_mm,
            "L1_mm": l1, "L2_mm": l2,
            "post_end_inset_mm": contract["post_end_inset_mm"],
            "fillet_weld_mm": contract["fillet_weld_mm"],
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]
        set_remark(entry, f"Fig.{fig} {role}，切長={length}", f"Fig.{fig} {role}, cut={length}")
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": profile["drawing"], "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig}", "bom_ready": True, "fabrication_ready": False,
        "blockers": blockers, "L_mm": l_mm, "H_mm": h_mm, "L1_mm": l1, "L2_mm": l2,
    }
    result.warnings.append("型鋼BOM可算；existing steel接合面與截面朝向仍需加工圖確認")
    result.evidence.append(make_evidence("type30_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99))
    return result
