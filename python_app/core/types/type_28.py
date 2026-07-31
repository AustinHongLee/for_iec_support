"""Type 28 source-aware portal frame with two M-42 feet (D-31)."""
from __future__ import annotations

from ..config_loader import load_config
from ..bom_policy import exclude_unresolved_entry, scale_entry_quantity
from ..hardware_material import HardwareKind, parse_hardware_material_context, resolve_hardware_material
from ..issues import (
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) != 3 or len(parts[2]) != 5 or not parts[2][:4].isdigit() or not parts[2][-1].isalpha():
        raise ValueError("格式應為 28-{M}-{LL}{HH}{M42}")
    l_mm = int(parts[2][:2]) * 100
    h_mm = int(parts[2][2:4]) * 100
    if l_mm <= 0 or h_mm <= 0:
        raise ValueError("L與H必須大於0")
    return parts[1].upper(), l_mm, h_mm, parts[2][-1].upper()


def _line_orientation(overrides):
    raw = str(overrides.get("line_orientation", "")).strip().upper()
    aliases = {"H": "HORIZONTAL", "HOR": "HORIZONTAL", "HORIZONTAL": "HORIZONTAL",
               "V": "VERTICAL", "VER": "VERTICAL", "VERTICAL": "VERTICAL"}
    if not raw:
        return None
    if raw not in aliases:
        raise ValueError("line_orientation只接受HORIZONTAL或VERTICAL")
    return aliases[raw]


def _decorate_m42(entries, profile):
    for index, entry in enumerate(entries, start=1):
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.component_id = f"D31-M42-BOTH-{index}"
        entry.geometry.parameters = dict(entry.geometry.parameters or {})
        entry.geometry.parameters["portal_legs"] = ["LEFT", "RIGHT"]
        entry.geometry.parameters["m42_set_count"] = 2


def calculate(fullstring, overrides=None, source_profile=None):
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("28", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 28: 尚未建立來源 profile {profile_id}"
        return result
    try:
        member, l_mm, h_mm, letter = _parse(fullstring)
        orientation = _line_orientation(overrides)
    except ValueError as exc:
        result.error = f"Type 28: {exc}"
        return result
    row = config[profile["table"]].get(member)
    if not row:
        result.error = f"Type 28 / {profile_id}: D-31未表列 MEMBER {member}"
        return result
    if letter not in profile["allowed_m42"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 28 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 28 / {profile_id}",
            source_ref="D-31",
            letter=letter,
            host_allowed=profile["allowed_m42"],
        )
    if not register_source_envelope(
        result,
        type_label=f"Type 28 / {profile_id}",
        source_ref=f"D-31 {member} L/H(MAX)",
        checks=(
            ("L", l_mm, row["L_MAX"], True),
            ("H", h_mm, row["H_MAX"], True),
        ),
    ):
        return result
    ctx = parse_hardware_material_context(overrides, legacy_material_keys=("material",), legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,))
    material = resolve_hardware_material(HardwareKind.STRUCTURAL_STRUT, service=ctx.service, overrides=ctx.material_overrides)
    layout = overrides.get("supported_line_layout")
    blockers = [
        "D-31要求H/L依現場裁切，門架角部端切/貼合需加工圖展開",
    ]
    if orientation is None:
        blockers.append("水平管/垂直管配置未編入designation；缺line_orientation")
    if not layout:
        blockers.append("管數、管徑與中心位置未編入designation；缺supported_line_layout")
    if orientation == "VERTICAL":
        blockers.append("垂直管用D-68 U-bolt且NOT FURNISHED；採購/孔位需另行展開")
    for cid, role, length, segment in (
        ("D31-LEFT-LEG", "左立柱", h_mm, "H"),
        ("D31-TOP-BEAM", "上橫梁", l_mm, "L"),
        ("D31-RIGHT-LEG", "右立柱", h_mm, "H"),
    ):
        add_steel_section_entry(result, row["section_type"], row["lookup_dim"], length, material=material)
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = profile["drawing"]
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "field_cut_stock_section"
        entry.geometry.shape_spec = f"{row['full_spec']}; CUT {segment}={length}"
        entry.geometry.parameters = {
            "segment": segment, "cut_length_mm": length, "assembly_L_mm": l_mm,
            "assembly_H_mm": h_mm, "line_orientation": orientation,
            "supported_line_layout": layout, "u_bolt_standard": "D-68" if orientation == "VERTICAL" else None,
            "u_bolt_furnished": False,
        }
        entry.geometry.fabrication_ready = False
        entry.geometry.fabrication_blockers = blockers[:]
        set_remark(entry, f"{role}，現場裁切{segment}={length}", f"{role}, field cut {segment}={length}")
    start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        row["full_spec"].replace("X", "*"),
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    m42_entries = list(result.entries[start:])
    _decorate_m42(m42_entries, profile)
    for entry in m42_entries:
        if entry.category == "螺栓類" and entry.unit_weight <= 0:
            exclude_unresolved_entry(
                result,
                entry,
                reason=(
                    f"M-42 fastener {entry.spec} 只有名義直徑、沒有長度；"
                    "左右兩組皆不以 0 kg 採購件列入材料 BOM"
                ),
            )
            continue
        scale_entry_quantity(entry, 2)
    m42_exact = member not in ("C100", "H250")
    if not m42_exact:
        blockers.append(f"{member}未在M-42精確member row表列，lower component需人工核對")
    result.meta["fabrication"] = {
        "source_profile": profile_id, "source_drawing": profile["drawing"], "source_revision": profile["revision"],
        "branch": f"{member}/M42-{letter}/{orientation or 'ORIENTATION-TBD'}",
        "bom_ready": m42_exact, "fabrication_ready": False, "blockers": blockers,
        "L_mm": l_mm, "H_mm": h_mm, "m42_sets": 2,
        "m42_bom_presentation": "one geometry row with quantity scaled for LEFT+RIGHT",
        "excluded_bom_components": result.meta.get("excluded_bom_components", []),
    }
    result.warnings.append("門架型鋼與兩組M-42已計；管線配置及角部端切仍需加工圖輸入")
    result.evidence.append(make_evidence("type28_member_row", row, "visual_transcription", source=profile["drawing"], confidence=0.99))
    return result
