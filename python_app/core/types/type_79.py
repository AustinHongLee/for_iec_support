"""
Type 79 calculator — U-band support (D-94).

Format:
    79-{line_size}B[(anchor_type)]

Example:
    79-8B(A)
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.m55_table import build_m55_item, get_m55_by_line_size


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    part2 = get_part(fullstring, 2) or ""
    line_token, anchor = extract_parts(part2)
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        anchor = part3
    if not line_token:
        result.error = "格式錯誤，應為 79-{line_size}B[(A)]，例如 79-8B(A)"
        return result

    line_size = get_lookup_value(line_token)
    row = get_m55_by_line_size(line_size)
    if not row:
        result.error = f'Type 79: 管徑 {line_token} ({line_size:g}") 不在範圍 5"~24"'
        return result
    dims = row["dimensions_mm"]
    item = build_m55_item(line_size)

    add_custom_entry(
        result,
        item["name"],
        item["spec"],
        item["material"],
        item["quantity"],
        item["unit_weight_kg"],
        item["unit"],
        remark=item["remark"],
        category=item["category"],
    )
    result.warnings.append(
        "M-55 table 已接線，但 PDF 無 source unit-weight；U-BAND 重量仍為 B x E x T blank 幾何估算"
    )
    result.warnings.append(
        "M-55 PDF 無文字層；尺寸表由 rendered bitmap AI visual transcription，需 reviewer spot-check"
    )
    if anchor:
        result.warnings.append(f"{anchor}: IF USED AS ANCHOR is a weld/detail note; no extra BOM item added")

    invariant_errors = validate_named_invariants(
        {"A": dims["A"], "B": dims["B"], "E": dims["E"], "T": dims["T"]},
        {
            "plate_thickness_positive": lambda x: x["T"] > 0,
            "u_band_blank_width_positive": lambda x: x["E"] > 0,
            "u_band_length_ge_pipe_span": lambda x: x["B"] >= x["A"],
        },
    )
    return apply_truth_contract(
        result,
        type_id="79",
        evidence=[
            make_evidence(
                "u_band_dimensions",
                {"line_size": row["line_size"], "A": dims["A"], "B": dims["B"], "E": dims["E"], "T": dims["T"]},
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="M-55 table",
                confidence=0.7,
            ),
            make_evidence(
                "u_band_weight",
                row["unit_weight_kg"],
                "geometry_estimate",
                source="formula",
                page=1,
                note="Estimated from M-55 B*E*T blank; source has no unit-weight column",
                confidence=0.5,
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["M-55 dimensions are table-backed but AI visual-transcribed; U-BAND weight remains estimated"],
    )
