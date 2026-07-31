"""Type 114C wall-clip cold-support assembly (C-57~C-59)."""

from __future__ import annotations

import re

from ..models import AnalysisResult
from ..parser import get_part
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
    parse_positive_mm,
)
from ._cold_component_resolution import (
    add_cold_interface_component,
    add_cold_restraint_component,
    add_cold_support_core_reference,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, "114C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_length_code = str(get_part(fullstring, 2) or "").strip().upper()
    cradle_no = str(get_part(fullstring, 3) or "").strip().upper()
    line_size = parse_pipe_size(get_part(fullstring, 4))
    dim_c = parse_positive_mm(get_part(fullstring, 5))
    if (
        not re.fullmatch(r"[A-Z]+", cradle_length_code)
        or not re.fullmatch(r"CR\d+(?:\.\d+)?", cradle_no)
        or line_size is None
        or dim_c is None
    ):
        result.error = (
            "Type 114C 格式應為 "
            "114C-{CRADLE LENGTH CODE}-{CR#}-{LINE}B-{C mm}"
        )
        return result
    branch_name = None
    branch = None
    for name, candidate in profile["branches"].items():
        if line_size in candidate["sizes"]:
            branch_name = name
            branch = candidate
            break
    if not branch:
        result.error = f'Type 114C: C-57~C-59 未表列 {line_size:g}" branch'
        return result
    if dim_c > branch["C_max_mm"]:
        result.error = (
            f"Type 114C / {line_size:g}\": C 必須 <= "
            f"{branch['C_max_mm']} mm"
        )
        return result

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="114C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
            allow_unlisted_pipe_size=True,
        )
    except ValueError as exc:
        result.error = f"Type 114C: {exc}"
        result.entries.clear()
        return result
    selection = cold_core["selection"]
    dimension_b_formula = branch.get("dimension_B_formula")
    dimension_b_mm = (
        selection["F_mm"] + 13
        if (
            dimension_b_formula == "F + 13"
            and selection.get("F_mm") is not None
        )
        else None
    )
    restraint_blockers = []
    if branch_name in {"small_2_and_under", "three_four"}:
        component_id = (
            "N-7A"
            if branch_name == "small_2_and_under"
            else "N-8"
        )
        try:
            restraint, restraint_blockers = add_cold_restraint_component(
                result,
                type_id="114C",
                component_id=component_id,
                cradle_no=cradle_no,
            )
        except ValueError as exc:
            result.error = f"Type 114C: {exc}"
            result.entries.clear()
            return result
        cold_core[component_id] = restraint
    clip_component_id = (
        "N-14"
        if branch["clip_reference"].startswith("N-14")
        else "N-13"
    )
    clip, clip_blockers = add_cold_interface_component(
        result,
        type_id="114C",
        component_id=clip_component_id,
        host_parameters={
            "line_size_in": line_size,
            "C_mm": dim_c,
            "B_mm": dimension_b_mm,
            "insulation_thickness_mm": selection.get(
                "insulation_thickness_mm"
            ),
            "theta_deg": None,
            "vessel_radius_mm": None,
        },
    )
    cold_core[clip_component_id] = clip

    blockers = [
        "C is an assembly reach, not a proven finished cut for the listed angles",
        *core_blockers,
        *restraint_blockers,
        *clip_blockers,
    ]
    parameters = {
        "cradle_length_code": cradle_length_code,
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "C_mm": dim_c,
        "C_max_mm": branch["C_max_mm"],
        "branch": branch_name,
        "sections": branch["sections"],
        "support_reference": branch["support_reference"],
        "clip_reference": branch["clip_reference"],
        "dimension_B_formula": dimension_b_formula,
        "dimension_B_mm": dimension_b_mm,
        "cradle_length_reference": profile["cradle_length_reference"],
        "stud_hole_diameter_mm": profile["stud_hole_diameter_mm"],
        "weld_mm": profile["weld_mm"],
        "resolved_components": cold_core,
    }
    add_cold_reference(
        result,
        name="C-57~C-59 TYPE 114C COLD-SUPPORT ASSEMBLY",
        component_id="C57-C59-TYPE114C-ASSEMBLY",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=(
            f"{cradle_length_code}-{cradle_no}; {line_size:g}in; "
            f"C={dim_c}; BRANCH={branch_name}"
        ),
    )
    return finalize_cold_result(
        result,
        type_id="114C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type114c_c57_c59_assembly",
    )
