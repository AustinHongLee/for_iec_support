"""Type 05 source-aware small-line support (Chung Wei D-5)."""
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
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.steel_sections import get_section_details


def _load(source_profile):
    config = load_config("05", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        raise ValueError(f"Type 05 尚未建立來源 profile: {profile_id}")
    return profile_id, profile, config


def _parse(fullstring):
    parts = str(fullstring).split("-")
    if len(parts) != 3:
        raise ValueError("格式應為 05-{M}-{HH}{M42}")
    member = parts[1].upper()
    token = parts[2].upper()
    if len(token) < 2 or not token[:-1].isdigit() or not token[-1].isalpha():
        raise ValueError("第三段應為高度(100mm)加 M-42 字母，例如 05L")
    return member, int(token[:-1]) * 100, token[-1]


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
        member, h_mm, letter = _parse(fullstring)
    except (TypeError, ValueError) as exc:
        result.error = f"Type 05: {exc}"
        return result

    limits = config["constraints"]
    if member not in limits["members"]:
        result.error = (
            f"Type 05 / {profile_id}: D-5 只允許 MEMBER "
            f"{'/'.join(limits['members'])}"
        )
        return result
    if h_mm <= 0:
        result.error = (
            f"Type 05 / {profile_id}: H={h_mm}mm 超出 D-5 "
            f"0<H≤{limits['H_max_mm']}mm"
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 05 / {profile_id}",
        source_ref="D-5 H上限",
        checks=(("H", h_mm, limits["H_max_mm"], True),),
    ):
        return result
    if letter not in limits["allowed_m42"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 05 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 05 / {profile_id}",
            source_ref="D-5",
            letter=letter,
            host_allowed=limits["allowed_m42"],
        )
    details = get_section_details(member)
    if not details:
        result.error = f"Type 05: steel table 無 {member}"
        return result

    ctx = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material",),
        legacy_material_kinds=(HardwareKind.STRUCTURAL_STRUT,),
    )
    steel_material = resolve_hardware_material(
        HardwareKind.STRUCTURAL_STRUT,
        service=ctx.service,
        overrides=ctx.material_overrides,
    )
    fab = config["fabrication_contract"]
    vertical_cut = h_mm - fab["top_offset_mm"]
    if vertical_cut <= 0:
        result.error = f"Type 05: H-15={vertical_cut}mm，垂直 member 無有效切長"
        return result
    section_dim = details["size"][1:]

    add_steel_section_entry(
        result, details["type"], section_dim, vertical_cut,
        material=steel_material,
    )
    vertical = result.entries[-1]
    vertical.geometry.component_id = "D5-VERTICAL-MEMBER-M"
    vertical.geometry.source_drawing = profile["drawing"]
    vertical.geometry.source_revision = profile["revision"]
    vertical.geometry.shape_kind = "stock_section_cut"
    vertical.geometry.shape_spec = f'{details["size"].replace("*", "X")}; CUT={vertical_cut}'
    vertical.geometry.formula = fab["vertical_formula"]
    vertical.geometry.parameters = {
        "H_mm": h_mm,
        "top_offset_mm": fab["top_offset_mm"],
        "cut_length_mm": vertical_cut,
        "weld_mm": fab["weld_mm"],
    }
    vertical.geometry.fabrication_ready = False
    vertical.geometry.fabrication_blockers = ["D-5 NOTE 1：H需現場切配"]
    set_remark(vertical, f"H={h_mm}-頂端偏移15；H現場切配")

    add_steel_section_entry(
        result,
        details["type"],
        section_dim,
        fab["horizontal_cut_length_mm"],
        material=steel_material,
    )
    horizontal = result.entries[-1]
    horizontal.geometry.component_id = "D5-HORIZONTAL-MEMBER-M"
    horizontal.geometry.source_drawing = profile["drawing"]
    horizontal.geometry.source_revision = profile["revision"]
    horizontal.geometry.shape_kind = "stock_section_with_ubolt_holes"
    horizontal.geometry.shape_spec = (
        f'{details["size"].replace("*", "X")}; CUT='
        f'{fab["horizontal_cut_length_mm"]}; D-68 U-BOLT HOLES'
    )
    horizontal.geometry.parameters = {
        "cut_length_mm": fab["horizontal_cut_length_mm"],
        "u_bolt_reference": fab["u_bolt_reference"],
        "u_bolt_furnished": fab["u_bolt_furnished"],
        "weld_mm": fab["weld_mm"],
    }
    horizontal.geometry.fabrication_ready = False
    horizontal.geometry.fabrication_blockers = [
        "D-68 U-bolt孔徑/孔距尚未在 Type 05 加工幾何展開"
    ]

    m42_start = len(result.entries)
    perform_action_by_letter(
        result, letter, details["size"], source_profile=profile_id
    )
    if result.error:
        result.entries.clear()
        return result
    _decorate_m42(result.entries[m42_start:], profile)

    blockers = [
        *vertical.geometry.fabrication_blockers,
        *horizontal.geometry.fabrication_blockers,
    ]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"{member}/M42-{letter}",
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": blockers,
        "not_furnished": ["STANDARD U-BOLT D-68"],
        "dimensions": {
            "H_mm": h_mm,
            "vertical_cut_length_mm": vertical_cut,
            "horizontal_cut_length_mm": fab["horizontal_cut_length_mm"],
        },
    }
    result.warnings.append(
        "D-5 H為現場切配；D-68 U-bolt 不供應，孔位需由 D-68 串接後才能出加工圖"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type05_constraints",
                limits,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
            make_evidence(
                "type05_vertical_cut_length_mm",
                vertical_cut,
                "formula",
                source=profile["drawing"],
                confidence=0.99,
                note="H - 15",
            ),
            make_evidence(
                "type05_horizontal_cut_length_mm",
                fab["horizontal_cut_length_mm"],
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.99,
            ),
        ]
    )
    return result
