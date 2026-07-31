"""Type 115C existing-surface cold support (C-60/C-61)."""

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
    add_cold_restraint_component,
    add_cold_support_core_reference,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, "115C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_token = str(get_part(fullstring, 2) or "").strip().upper()
    match = re.fullmatch(r"([A-Z]+)(CR\d+(?:\.\d+)?)", cradle_token)
    line_size = parse_pipe_size(get_part(fullstring, 3))
    dim_c = parse_positive_mm(get_part(fullstring, 4))
    if not match or line_size is None or dim_c is None:
        result.error = (
            "Type 115C 格式應為 "
            "115C-{CRADLE LENGTH CODE}{CR#}-{LINE}B-{C mm}"
        )
        return result
    if dim_c > profile["C_max_mm"]:
        result.error = f"Type 115C: C 必須 <= {profile['C_max_mm']} mm"
        return result
    cradle_length_code, cradle_no = match.groups()
    branch_name = None
    branch = None
    for name, candidate in profile["branches"].items():
        if line_size in candidate["sizes"]:
            branch_name = name
            branch = candidate
            break
    if not branch:
        result.error = f'Type 115C: C-60/C-61 未表列 {line_size:g}" branch'
        return result

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="115C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
            allow_unlisted_pipe_size=True,
        )
    except ValueError as exc:
        result.error = f"Type 115C: {exc}"
        result.entries.clear()
        return result
    selection = cold_core["selection"]
    restraint_blockers = []
    restraint_component = (
        "N-7A"
        if branch_name == "small_2_and_under"
        else "N-8"
        if branch_name == "three_four"
        else None
    )
    if restraint_component:
        try:
            restraint, restraint_blockers = add_cold_restraint_component(
                result,
                type_id="115C",
                component_id=restraint_component,
                cradle_no=cradle_no,
            )
        except ValueError as exc:
            result.error = f"Type 115C: {exc}"
            result.entries.clear()
            return result
        cold_core[restraint_component] = restraint
    dimension_b_mm = None
    if (
        selection.get("F_mm") is not None
        and branch["dimension_B_formula"]
    ):
        offset = 3 if branch["dimension_B_formula"] == "F + 3" else 13
        dimension_b_mm = selection["F_mm"] + offset

    blockers = [
        "C is the distance from existing surface to pipe centerline, not "
        "a proven finished cut for every listed angle",
        f"{branch['support_reference']} remains reference-only",
        *core_blockers,
        *restraint_blockers,
    ]
    parameters = {
        "cradle_length_code": cradle_length_code,
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "C_mm": dim_c,
        "C_max_mm": profile["C_max_mm"],
        "branch": branch_name,
        "sections": branch["sections"],
        "support_reference": branch["support_reference"],
        "dimension_B_formula": branch["dimension_B_formula"],
        "dimension_B_mm": dimension_b_mm,
        "cradle_length_reference": profile["cradle_length_reference"],
        "interface": "existing surface",
        "weld_mm": profile["weld_mm"],
        "resolved_components": cold_core,
    }
    add_cold_reference(
        result,
        name="C-60/C-61 TYPE 115C COLD-SUPPORT ASSEMBLY",
        component_id="C60-C61-TYPE115C-ASSEMBLY",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=(
            f"{cradle_length_code}{cradle_no}; {line_size:g}in; "
            f"C={dim_c}; BRANCH={branch_name}"
        ),
    )
    return finalize_cold_result(
        result,
        type_id="115C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type115c_c60_c61_assembly",
    )
