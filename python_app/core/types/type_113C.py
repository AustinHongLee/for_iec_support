"""Type 113C cold-service cantilever member (C-56)."""

from __future__ import annotations

from ..models import AnalysisResult, set_remark
from ..parser import get_part
from ..steel import add_steel_section_entry
from ._cold_component_resolution import (
    add_n12_clip_reference,
    add_n28_wood_block_entry,
)
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_positive_mm,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    loaded = load_cold_profile(result, "113C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    member_code = str(get_part(fullstring, 2) or "").strip().upper()
    length = parse_positive_mm(get_part(fullstring, 3))
    member = profile["members"].get(member_code)
    if not member or length is None:
        result.error = "Type 113C 格式應為 113C-{L50|L75|C100}-{C mm}"
        return result

    material_blocker = (
        "C-56 does not identify Member M steel grade；section stock weight "
        "is calculated but material must be approved before release"
    )
    add_steel_section_entry(
        result,
        member["kind"],
        member["spec"],
        length,
        1,
        "MATERIAL NOT SPECIFIED IN C-56",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "C56-MEMBER-M"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "cold_support_cantilever_member"
    entry.geometry.shape_spec = f"{member['source_spec']}; CUT C={length}"
    entry.geometry.parameters = {
        "member_code": member_code,
        "source_section": member["source_spec"],
        "cut_length_C_mm": length,
        "square_cut_ends": True,
        "weld_mm": profile["weld_mm"],
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [material_blocker]
    set_remark(entry, material_blocker)

    maximum_load_kg = (
        profile["maximum_moment_kg_m"] / (length / 1000)
    )
    insulation_thickness = overrides.get("insulation_thickness_mm")
    clip, clip_blockers = add_n12_clip_reference(
        result,
        clip_type=1,
        insulation_thickness_mm=insulation_thickness,
    )
    wood, wood_blockers = add_n28_wood_block_entry(result, 1)
    assembly_blockers = [
        "actual support load P is not encoded；must verify P*C <= 40 kg-m",
        *clip_blockers,
        *wood_blockers,
    ]
    ref_parameters = {
        "member_code": member_code,
        "C_mm": length,
        "maximum_moment_kg_m": profile["maximum_moment_kg_m"],
        "maximum_load_at_C_kg": maximum_load_kg,
        "references": profile["references"],
        "stud_bolt": profile["stud_bolt"],
        "stud_hole_diameter_mm": profile["stud_hole_diameter_mm"],
        "insulation_thickness_mm": insulation_thickness,
        "resolved_components": {
            "N-12": clip,
            "N-28": [wood],
        },
    }
    add_cold_reference(
        result,
        name="C-56 CLIP / WOOD-BLOCK CONNECTION",
        component_id="C56-N12-N28-CONNECTION",
        profile=profile,
        parameters=ref_parameters,
        blockers=assembly_blockers,
    )
    blockers = [material_blocker, *assembly_blockers]
    parameters = {
        **ref_parameters,
        "member_section": member["source_spec"],
        "member_cut_length_mm": length,
    }
    return finalize_cold_result(
        result,
        type_id="113C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type113c_c56_cantilever",
    )
