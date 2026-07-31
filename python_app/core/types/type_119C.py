"""Type 119C nozzle cold-support assembly (C-67)."""

from __future__ import annotations

import re

from data.cold_support_core_tables import SMALL_PIPE_SIZES

from ..models import AnalysisResult
from ..parser import get_part
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
)
from ._cold_component_resolution import add_cold_support_core_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, "119C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_no = str(get_part(fullstring, 2) or "").strip().upper()
    line_size = parse_pipe_size(get_part(fullstring, 3))
    if not re.fullmatch(r"CR\d+(?:\.\d+)?", cradle_no) or line_size is None:
        result.error = "Type 119C 格式應為 119C-{CR#}-{LINE}B"
        return result
    member_section = None
    branch_name = None
    for name, branch in profile["member_q_branches"].items():
        if line_size in branch["sizes"]:
            member_section = branch["section"]
            branch_name = name
            break
    if not member_section:
        result.error = f'Type 119C: C-67 僅表列 1/2"~24"，收到 {line_size:g}"'
        return result

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="119C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
            cradle_length_mm=profile["envelope_mm"]["cradle"],
        )
    except ValueError as exc:
        if line_size in SMALL_PIPE_SIZES:
            result.error = f"Type 119C: {exc}"
            result.entries.clear()
            return result
        cold_core = {
            "selection": {
                "lookup_ready": False,
                "cradle_no": cradle_no,
                "pipe_size_in": line_size,
                "reason": "C-67 permits the pipe-size range, but N-20~N-23 has no explicit row for this nominal size",
            }
        }
        core_blockers = [
            f"N-20~N-23 exact cradle row unresolved: {exc}",
            "C-67 host range accepts this nominal size, but F/H/allowable load and insulation thickness cannot be inferred",
        ]

    blockers = [
        "Member Q is cut/formed around the cold-support cradle；"
        "section selection alone does not define developed cut length",
        *core_blockers,
    ]
    parameters = {
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "member_q_branch": branch_name,
        "member_q_section": member_section,
        "member_q_cut_length_mm": None,
        "envelope_mm": profile["envelope_mm"],
        "resolved_components": cold_core,
        "references": profile["references"],
        "weld_mm": profile["weld_mm"],
    }
    add_cold_reference(
        result,
        name="C-67 TYPE 119C NOZZLE COLD-SUPPORT ASSEMBLY",
        component_id="C67-TYPE119C-ASSEMBLY",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=f"{cradle_no}; {line_size:g}in; MEMBER Q={member_section}",
    )
    return finalize_cold_result(
        result,
        type_id="119C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type119c_c67_nozzle_support",
    )
