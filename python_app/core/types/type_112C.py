"""Type 112C diagonal vessel cold-support assembly (C-55)."""

from __future__ import annotations

from ..models import AnalysisResult
from ..parser import get_part
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
    loaded = load_cold_profile(result, "112C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    dim_b = parse_positive_mm(get_part(fullstring, 2))
    dim_c = parse_positive_mm(get_part(fullstring, 3))
    if dim_b is None or dim_c is None:
        result.error = "Type 112C 格式應為 112C-{B mm}-{C mm}"
        return result
    try:
        orientation = float(overrides.get(
            "orientation_angle_deg",
            profile["orientation_default_deg"],
        ))
    except (TypeError, ValueError):
        result.error = "Type 112C: orientation_angle_deg 必須為數值"
        return result

    insulation_thickness = overrides.get("insulation_thickness_mm")
    clip, clip_blockers = add_n12_clip_reference(
        result,
        clip_type=3,
        insulation_thickness_mm=insulation_thickness,
    )
    wood_blocks = []
    component_blockers = list(clip_blockers)
    for block_no in (2, 3, 4):
        wood, wood_blockers = add_n28_wood_block_entry(result, block_no)
        wood_blocks.append(wood)
        component_blockers.extend(wood_blockers)

    blockers = [
        "C180/L130 brace finished cuts and end fit-up are not uniquely "
        "dimensioned；不得用 45-degree envelope 推算",
        *component_blockers,
    ]
    parameters = {
        "B_mm": dim_b,
        "C_mm": dim_c,
        "orientation_angle_deg": orientation,
        "sections": profile["sections"],
        "references": profile["references"],
        "stud_bolt": profile["stud_bolt"],
        "stud_hole_diameter_mm": profile["stud_hole_diameter_mm"],
        "weld_mm": profile["weld_mm"],
        "insulation_thickness_mm": insulation_thickness,
        "resolved_components": {
            "N-12A": clip,
            "N-28": wood_blocks,
        },
    }
    add_cold_reference(
        result,
        name="C-55 TYPE 112C COLD-SUPPORT ASSEMBLY",
        component_id="C55-TYPE112C-ASSEMBLY",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=f"B={dim_b}; C={dim_c}; ORIENT={orientation:g}deg",
    )
    return finalize_cold_result(
        result,
        type_id="112C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type112c_c55_assembly",
    )
