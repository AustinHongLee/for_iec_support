"""
Type 78 calculator — Small-pipe strap anchor/support (D-93).

Format:
    78-{line_size}B[(anchor_type)]

Example:
    78-2B(A)

The drawing calls out STRAP FIG.1 SEE M-54.
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.m54_table import build_m54_item


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    part2 = get_part(fullstring, 2) or ""
    line_token, anchor = extract_parts(part2)
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        anchor = part3
    if not line_token:
        result.error = "格式錯誤，應為 78-{line_size}B[(A)]，例如 78-2B(A)"
        return result

    line_size = get_lookup_value(line_token)
    strap = build_m54_item(line_size, fig_no=1)
    if not strap:
        result.error = f'Type 78: 管徑 {line_token} ({line_size:g}") 不在範圍 3/4"~4"'
        return result

    add_custom_entry(
        result,
        "STRAP",
        strap["spec"],
        strap["material"],
        1,
        strap["unit_weight_kg"],
        "PC",
        remark="STRAP FIG.1 SEE M-54; no Fig.2 bolt-hole deduction",
        category="鋼板類",
    )
    if anchor:
        result.warnings.append(f"{anchor}: IF USED AS ANCHOR is a weld/detail note; no extra BOM item added")

    invariant_errors = validate_named_invariants(
        {"unit_weight": strap["unit_weight_kg"]},
        {"strap_weight_positive": lambda x: x["unit_weight"] > 0},
    )
    return apply_truth_contract(
        result,
        type_id="78",
        evidence=[
            make_evidence(
                "strap_fig",
                "M-54 FIG.1",
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="STRAP FIG. 1 SEE M-54",
                confidence=0.78,
                note="M-54 is table-backed but currently from visual transcription",
            ),
            make_evidence(
                "strap_weight",
                strap["unit_weight_kg"],
                "formula",
                source="formula",
                page=1,
                note_ref="M-54 Fig.1 no Fig.2 hole deduction",
                confidence=0.74,
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["Type 78 depends on M-54 visual-transcribed dimensions"],
    )
