"""Type 120C cold hanger assembly (C-68)."""

from __future__ import annotations

import re

from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
    parse_positive_mm,
)
from ._cold_component_resolution import add_cold_support_core_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, "120C", source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    cradle_length_code = str(get_part(fullstring, 2) or "").strip().upper()
    cradle_no = str(get_part(fullstring, 3) or "").strip().upper()
    line_size = parse_pipe_size(get_part(fullstring, 4))
    rod_token = str(get_part(fullstring, 5) or "").strip()
    rod_size = get_lookup_value(rod_token)
    dim_h = parse_positive_mm(get_part(fullstring, 6))
    figure = str(get_part(fullstring, 7) or "").strip().upper()
    if (
        not re.fullmatch(r"[A-Z]+", cradle_length_code)
        or not re.fullmatch(r"CR\d+(?:\.\d+)?", cradle_no)
        or line_size is None
        or rod_size <= 0
        or dim_h is None
        or figure not in profile["figures"]
    ):
        result.error = (
            "Type 120C 格式應為 "
            "120C-{CRADLE LENGTH CODE}-{CR#}-{LINE}B-{ROD SIZE}-{H mm}-{A|B}"
        )
        return result
    turnbuckle_required = (
        dim_h > profile["turnbuckle_required_above_H_mm"]
    )
    figure_data = profile["figures"][figure]

    try:
        cold_core, core_blockers = add_cold_support_core_reference(
            result,
            type_id="120C",
            cradle_no=cradle_no,
            line_size_in=line_size,
            insulation_thickness_mm=(overrides or {}).get(
                "insulation_thickness_mm"
            ),
            allow_unlisted_pipe_size=True,
        )
    except ValueError as exc:
        result.error = f"Type 120C: {exc}"
        result.entries.clear()
        return result

    blockers = [
        "C-68 H is support assembly height, not M-22/M-23 finished rod cut",
        "N-17/N-18 clamp and C-24 cold-support geometry remain metadata-only",
        "M-21/M-22/M-23/M-25/M-28 finished hardware selection and supplier "
        "weights are not fully determined by designation",
        *core_blockers,
    ]
    parameters = {
        "cradle_length_code": cradle_length_code,
        "cradle_no": cradle_no,
        "line_size_in": line_size,
        "rod_size_in": rod_size,
        "H_mm": dim_h,
        "figure": figure,
        "hanger_chain": figure_data["hanger_chain"],
        "turnbuckle_required": turnbuckle_required,
        "turnbuckle_threshold_H_mm": profile[
            "turnbuckle_required_above_H_mm"
        ],
        "weld_mm": profile["weld_mm"],
        "resolved_components": cold_core,
    }
    add_cold_reference(
        result,
        name=f"C-68 TYPE 120C FIG-{figure} HANGER ASSEMBLY",
        component_id=f"C68-TYPE120C-FIG-{figure}",
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=(
            f"{cradle_length_code}-{cradle_no}; {line_size:g}in; "
            f"ROD={rod_token}; H={dim_h}; FIG-{figure}"
        ),
    )
    return finalize_cold_result(
        result,
        type_id="120C",
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key="type120c_c68_hanger",
    )
