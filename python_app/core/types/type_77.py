"""
Type 77 calculator — Large-pipe saddle support (D-92).

Format:
    77-{line_size}B[(anchor_type)] or 77-{line_size}B-(anchor_type)

Example:
    77-26B-(A)
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.type77_table import get_type77_data


def _parse_line_and_anchor(fullstring: str) -> tuple[str, str]:
    part2 = get_part(fullstring, 2) or ""
    line_token, anchor = extract_parts(part2)
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        anchor = part3
    return line_token, anchor.strip()


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    line_token, anchor = _parse_line_and_anchor(fullstring)
    if not line_token:
        result.error = "格式錯誤，應為 77-{line_size}B[(A)]，例如 77-26B-(A)"
        return result

    line_size = get_lookup_value(line_token)
    row = get_type77_data(line_size)
    if not row:
        result.error = f'Type 77: 管徑 {line_token} ({line_size:g}") 不在範圍 26"~40"'
        return result

    add_custom_entry(
        result,
        "SADDLE",
        f'A={row["A"]} B={row["B"]} C={row["C"]} T={row["T"]} H={row["H"]}',
        "Same/similar to pipe",
        1,
        row["unit_weight_kg"],
        "PC",
        remark="D-92 saddle; weight estimated from bounding geometry",
        category="鋼板類",
    )
    result.warnings.append(
        "Type 77 PDF 無文字層；尺寸表由 rendered bitmap AI visual transcription，需 reviewer spot-check"
    )
    result.warnings.append("Type 77 saddle weight is estimated; drawing has no unit-weight table")
    if anchor:
        result.warnings.append(f"{anchor}: anchor type noted by designation; see D-80A table B")

    invariant_errors = validate_named_invariants(
        {"A": row["A"], "C": row["C"], "T": row["T"], "H": row["H"]},
        {
            "plate_thickness_positive": lambda x: x["T"] > 0,
            "height_positive": lambda x: x["H"] > 0,
            "saddle_length_ge_base": lambda x: x["C"] >= x["A"],
        },
    )
    return apply_truth_contract(
        result,
        type_id="77",
        evidence=[
            make_evidence(
                "saddle_dimensions",
                {"line_size": row["line_size"], "A": row["A"], "B": row["B"], "C": row["C"], "T": row["T"], "H": row["H"]},
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="D-92 table",
                confidence=0.7,
            ),
            make_evidence(
                "saddle_weight",
                row["unit_weight_kg"],
                "geometry_estimate",
                source="formula",
                page=1,
                note="Bounding geometry estimate; source drawing has no unit-weight table",
                confidence=0.55,
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["Type 77 weight is a bounding geometry estimate and must be reviewed before production use"],
    )
