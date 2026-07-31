"""Type 22 source-aware ground cantilever U-bolt support (D-24)."""
from __future__ import annotations

import re

from ..config_loader import load_config
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import (
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..models import AnalysisResult
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _load(source_profile):
    config = load_config("22", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 22 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config[profile["member_table"]], config


def _parse(fullstring, profile, fig_l_map):
    parts = str(fullstring).split("-")
    member = parts[1].upper() if len(parts) > 1 else ""
    if profile["designation_style"] == "parenthesized":
        if len(parts) not in (3, 4):
            raise ValueError("中威格式應為 22-{M}-{HH}({Fig}){M42}[-{LL}]")
        match = re.fullmatch(r"(\d+)\(([ABCabc])\)([A-Za-z])", parts[2])
        if not match:
            raise ValueError("中威第三段應為 HH(Fig)M42，例如 05(A)L")
        h_digits, fig, letter = match.groups()
        extra = parts[3:]
    else:
        if len(parts) not in (4, 5):
            raise ValueError("中鼎格式應為 22-{M}-{HH}{Fig}-{M42}[-{LL}]")
        match = re.fullmatch(r"(\d+)([ABCabc])", parts[2])
        if not match or not re.fullmatch(r"[A-Za-z]", parts[3]):
            raise ValueError("中鼎第三/四段應為 HHFig-M42，例如 05A-L")
        h_digits, fig = match.groups()
        letter = parts[3]
        extra = parts[4:]
    fig, letter = fig.upper(), letter.upper()
    h_mm = int(h_digits) * 100
    if fig == "C":
        if len(extra) != 1 or not extra[0].isdigit():
            raise ValueError("Fig.C 需且只能有 L(100mm單位)")
        l_mm = int(extra[0]) * 100
    else:
        if extra:
            raise ValueError("Fig.A/B 不得另給 L")
        l_mm = fig_l_map[fig]
    if h_mm <= 0 or l_mm <= 0:
        raise ValueError("H與L必須大於0")
    return member, fig, letter, h_mm, l_mm


def _decorate_m42(entries, profile, fabrication_ready):
    for entry in entries:
        entry.geometry.source_drawing = profile["m42_drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.fabrication_ready = fabrication_ready
        if entry.category == "鋼板類":
            code = entry.name.split("_")[1].upper()
            entry.geometry.component_id = f"M42-PLATE-{code}"
            entry.geometry.shape_kind = "rectangular_base_plate"
            entry.geometry.shape_spec = entry.geometry.shape_spec or f"{entry.length:g}x{entry.width:g}x{entry.spec}t"
            entry.geometry.parameters.update({"length_mm": entry.length, "width_mm": entry.width, "thickness_mm": float(entry.spec)})
        elif entry.category == "螺栓類":
            entry.geometry.component_id = "M42-FASTENER"
            entry.geometry.shape_kind = "purchased_fastener"
            entry.geometry.parameters.update({"spec": entry.spec, "quantity": entry.quantity})


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    try:
        profile_id, profile, members, config = _load(source_profile)
        member, fig, letter, h_mm, l_mm = _parse(fullstring, profile, config["FIG_L_MAP"])
    except (IndexError, TypeError, ValueError) as exc:
        result.error = f"Type 22: {exc}"
        return result
    row = members.get(member)
    if not row:
        result.error = f"Type 22 / {profile_id}: D-24 未表列 MEMBER {member}"
        return result
    if letter not in profile["allowed_m42"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 22 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 22 / {profile_id}",
            source_ref="D-24",
            letter=letter,
            host_allowed=profile["allowed_m42"],
        )
    checks = [("H", h_mm, row["H_MAX"], True)]
    if row["L_MAX"] is not None:
        checks.append(("L", l_mm, row["L_MAX"], True))
    if not register_source_envelope(
        result,
        type_label=f"Type 22 / {profile_id}",
        source_ref=f"D-24 {member} L/H(MAX)",
        checks=checks,
    ):
        return result

    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    blockers = [
        "D-24未給上角接頭的精確端部切削/貼合輪廓與焊腳尺寸",
        "designation不含supported line size；D-68 U-bolt孔徑與孔距無法展開",
    ]
    for cid, segment, length in (("D24-MEMBER-M-VERTICAL", "H", h_mm), ("D24-MEMBER-M-HORIZONTAL", "L", l_mm)):
        add_steel_section_entry(result, row["section_type"], row["lookup_dim"], length, material=material)
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.shape_spec = f'{row["full_spec"]}; CUT {segment}={length}; TYPE-22 FIG-{fig}'
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]
        entry.geometry.parameters = {"segment": segment, "cut_length_mm": length, "H_mm": h_mm, "L_mm": l_mm, "figure": fig, "supported_line_center_from_free_end_mm": 100, "u_bolt_reference": "D-68", "u_bolt_furnished": False}

    before_m42 = len(result.entries)
    perform_action_by_letter(result, letter, row["full_spec"].replace("X", "*"), source_profile=profile_id)
    if result.error:
        result.entries.clear()
        return result
    if not row["m42_exact"]:
        blockers.append("C100未在既有M-43下部構件表列；目前C125 row僅為估算")
    _decorate_m42(result.entries[before_m42:], profile, row["m42_exact"])
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": profile["drawing"], "source_revision": profile["revision"],
        "branch": f"{member}/FIG-{fig}/M42-{letter}", "bom_ready": row["m42_exact"], "fabrication_ready": False,
        "blockers": blockers, "H_mm": h_mm, "L_mm": l_mm, "m42_type": letter,
    }
    result.warnings.append("D-24上角接頭與D-68孔位未完整；加工圖仍有blocker")
    result.evidence.extend([
        make_evidence("type22_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99),
        make_evidence("type22_designation", {"H": h_mm, "L": l_mm, "figure": fig, "m42": letter}, "formula", source=profile["drawing"], confidence=0.99),
    ])
    return result
