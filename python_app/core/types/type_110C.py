"""Type 110C opposed-clip trunnion cold support (C-53)."""

from __future__ import annotations

from ..models import AnalysisResult
from ..parser import get_part
from ._cold_component_resolution import (
    add_n12_clip_reference,
    add_n28_wood_block_entry,
    derive_insulation_thickness_mm,
)
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
    parse_positive_mm,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    loaded = load_cold_profile(result, "110C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    line_size = parse_pipe_size(get_part(fullstring, 2))
    dim_b = parse_positive_mm(get_part(fullstring, 3))
    dim_c = parse_positive_mm(get_part(fullstring, 4))
    if line_size is None or dim_b is None or dim_c is None:
        result.error = "Type 110C 格式應為 110C-{LINE}B-{B mm}-{C mm}"
        return result
    try:
        orientation = float(overrides.get(
            "orientation_angle_deg",
            profile["orientation_default_deg"],
        ))
    except (TypeError, ValueError):
        result.error = "Type 110C: orientation_angle_deg 必須為數值"
        return result

    try:
        insulation_thickness = derive_insulation_thickness_mm(
            line_size,
            dim_b,
        )
    except ValueError as exc:
        result.error = f"Type 110C: {exc}"
        return result
    if not 0 < insulation_thickness <= 300:
        result.error = (
            "Type 110C: B 與 line size 依 C-53 反算的 insulation "
            f"thickness={insulation_thickness:g} mm 不在 N-12A 0~300 mm"
        )
        return result
    clip, clip_blockers = add_n12_clip_reference(
        result,
        clip_type=2,
        insulation_thickness_mm=insulation_thickness,
    )
    wood, wood_blockers = add_n28_wood_block_entry(result, 1)

    blockers = [
        "opposed L100/L75 frame piece count and finished cuts are not "
        "uniquely encoded by B/C",
        "ending plate and trunnion pipe are OTHER SPECIFIED / project scope",
        *clip_blockers,
        *wood_blockers,
    ]
    parameters = {
        "line_size_in": line_size,
        "B_mm": dim_b,
        "C_mm": dim_c,
        "B_formula": profile["dimension_B_formula"],
        "orientation_angle_deg": orientation,
        "sections": profile["sections"],
        "references": profile["references"],
        "stud_bolt": profile["stud_bolt"],
        "stud_hole_diameter_mm": profile["stud_hole_diameter_mm"],
        "weld_mm": profile["weld_mm"],
        "insulation_thickness_mm": insulation_thickness,
        "resolved_components": {
            "N-12": clip,
            "N-28": [wood],
        },
    }
    add_cold_reference(
        result,
        name="C-53 TYPE 110C COLD-SUPPORT ASSEMBLY",
        component_id="C53-TYPE110C-ASSEMBLY",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=f'{line_size:g}" LINE; B={dim_b}; C={dim_c}; ORIENT={orientation:g}deg',
    )
    return finalize_cold_result(
        result,
        type_id="110C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type110c_c53_assembly",
    )
