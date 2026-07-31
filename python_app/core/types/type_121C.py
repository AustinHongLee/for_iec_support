"""Type 121C large-bore cold guide (C-69/C-70)."""

from __future__ import annotations

import re

from ..models import AnalysisResult, set_remark
from ..parser import get_part
from ..steel import add_steel_section_entry
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
    loaded = load_cold_profile(result, "121C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_length_code = str(get_part(fullstring, 2) or "").strip().upper()
    cradle_no = str(get_part(fullstring, 3) or "").strip().upper()
    line_size = parse_pipe_size(get_part(fullstring, 4))
    guide_code = str(get_part(fullstring, 5) or "").strip().upper()
    row = profile["rows"].get(cradle_no)
    if (
        not re.fullmatch(r"[A-Z]+", cradle_length_code)
        or not row
        or line_size is None
        or line_size < profile["minimum_pipe_size_in"]
        or guide_code != "G"
    ):
        result.error = (
            "Type 121C 格式應為 "
            "121C-{CRADLE LENGTH CODE}-{CR32~CR46}-{LINE>=30}B-G"
        )
        return result

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="121C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
        )
    except ValueError as exc:
        result.error = f"Type 121C: {exc}"
        result.entries.clear()
        return result

    member = profile["member_q"]
    material_blocker = (
        "C-69/C-70 do not identify Member Q steel grade；stock weight is "
        "calculated but material approval is required"
    )
    add_steel_section_entry(
        result,
        member["kind"],
        member["spec"],
        row["member_q_length_mm"],
        member["quantity"],
        "MATERIAL NOT SPECIFIED IN C-69/C-70",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "C70-MEMBER-Q-GUIDES"
    entry.geometry.source_drawing = profile["drawing"]
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "paired_cold_support_guide_members"
    entry.geometry.shape_spec = (
        f"{member['source_spec']}; L={row['member_q_length_mm']}; "
        f"QTY{member['quantity']}"
    )
    entry.geometry.parameters = {
        "cradle_no": cradle_no,
        "source_section": member["source_spec"],
        "cut_length_mm": row["member_q_length_mm"],
        "piece_count": member["quantity"],
        "guide_required": True,
        **row,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [material_blocker]
    set_remark(entry, material_blocker)

    assembly_blockers = [
        "C-70 gives 6t stiffener thickness and h1/h2 but not complete X/Y "
        "plate net contours/widths；plate weight remains unresolved",
        *core_blockers,
    ]
    ref_parameters = {
        "cradle_length_code": cradle_length_code,
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "guide_code": guide_code,
        **row,
        "references": profile["references"],
        "stiffener_plate_thickness_mm": profile[
            "stiffener_plate_thickness_mm"
        ],
        "weld_mm": profile["weld_mm"],
        "resolved_components": cold_core,
    }
    add_cold_reference(
        result,
        name="C-69/C-70 COLD CRADLE / GUIDE PLATE ASSEMBLY",
        component_id="C69-C70-COLD-GUIDE-ASSEMBLY",
        profile=profile,
        parameters=ref_parameters,
        blockers=assembly_blockers,
        spec=(
            f"{cradle_length_code}-{cradle_no}; {line_size:g}in; "
            f"W={row['W_mm']}; H={row['H_mm']}"
        ),
    )
    blockers = [material_blocker, *assembly_blockers]
    parameters = {
        **ref_parameters,
        "member_q_section": member["source_spec"],
        "member_q_quantity": member["quantity"],
    }
    return finalize_cold_result(
        result,
        type_id="121C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type121c_c69_c70_guide",
    )
