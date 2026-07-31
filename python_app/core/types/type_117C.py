"""Type 117C cold cantilever with end plate (C-64)."""

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
    loaded = load_cold_profile(result, "117C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    member_code = str(get_part(fullstring, 2) or "").strip().upper()
    dim_b = parse_positive_mm(get_part(fullstring, 3))
    dim_c = parse_positive_mm(get_part(fullstring, 4))
    member = profile["members"].get(member_code)
    if not member or dim_b is None or dim_c is None:
        result.error = "Type 117C 格式應為 117C-{L50|L75}-{B mm}-{C mm}"
        return result
    cut_length = dim_c - profile["end_plate_thickness_mm"]
    if cut_length <= 0:
        result.error = "Type 117C: C 必須大於 9t end plate"
        return result

    material_blocker = (
        "C-64 does not identify Member M steel grade；stock weight is "
        "calculated but material approval is required"
    )
    add_steel_section_entry(
        result,
        member["kind"],
        member["spec"],
        cut_length,
        1,
        "MATERIAL NOT SPECIFIED IN C-64",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "C64-MEMBER-M"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "cold_cantilever_member_with_end_plate"
    entry.geometry.shape_spec = (
        f"{member['source_spec']}; CUT={dim_c}-"
        f"{profile['end_plate_thickness_mm']}={cut_length}"
    )
    entry.geometry.parameters = {
        "member_code": member_code,
        "source_section": member["source_spec"],
        "assembly_C_mm": dim_c,
        "end_plate_thickness_mm": profile["end_plate_thickness_mm"],
        "cut_length_mm": cut_length,
        "cut_formula": "C - 9t end plate",
        "weld_mm": profile["weld_mm"],
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [material_blocker]
    set_remark(entry, material_blocker)

    insulation_thickness = overrides.get("insulation_thickness_mm")
    clip, clip_blockers = add_n12_clip_reference(
        result,
        clip_type=1,
        insulation_thickness_mm=insulation_thickness,
    )
    wood, wood_blockers = add_n28_wood_block_entry(result, 1)
    assembly_blockers = [
        "C-64 gives end-plate B and 9t but does not dimension its second "
        "in-plane side；plate weight/blank remains unresolved",
        *clip_blockers,
        *wood_blockers,
    ]
    ref_parameters = {
        "B_mm": dim_b,
        "C_mm": dim_c,
        "end_plate_thickness_mm": profile["end_plate_thickness_mm"],
        "end_plate_other_side_mm": None,
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
        name="C-64 END PLATE / CLIP / WOOD-BLOCK ASSEMBLY",
        component_id="C64-END-PLATE-N12-N28",
        profile=profile,
        parameters=ref_parameters,
        blockers=assembly_blockers,
        spec=f"B={dim_b}; 9t END PLATE; C={dim_c}",
    )
    blockers = [material_blocker, *assembly_blockers]
    parameters = {
        **ref_parameters,
        "member_section": member["source_spec"],
        "member_cut_length_mm": cut_length,
    }
    return finalize_cold_result(
        result,
        type_id="117C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type117c_c64_cantilever",
    )
