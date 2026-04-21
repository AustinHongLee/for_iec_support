"""
Type 72 calculator — Strap support (D-87).

Designation:
    72-{line_size}B

Example:
    72-2B

The drawing references M-54 STRAP FIG.2, which is table-backed by
`data.m54_table`.
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.m45_table import get_m45_by_type
from data.m54_table import build_m54_item
from data.type72_table import get_type72_data


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "格式錯誤，應為 72-{line_size}B，例如 72-2B"
        return result

    line_size = get_lookup_value(part2)
    row = get_type72_data(line_size)
    if not row:
        result.error = f"Type 72: 管徑 {part2} ({line_size:g}\") 不在範圍 3/4\"~4\""
        return result

    strap = build_m54_item(line_size, fig_no=2)
    add_custom_entry(
        result,
        "STRAP",
        strap["spec"] if strap else f"M-54 FIG.2, {row['line_size']}, B={row['B']} C={row['C']} T={row['T']}",
        strap["material"] if strap else "Carbon Steel",
        1,
        strap["unit_weight_kg"] if strap else 0.0,
        "PC",
        remark="SEE M-54; weight calculated from M-54 BxCxT minus Fig.2 holes",
        category="鋼板類",
    )
    if not strap:
        result.warnings.append("M-54 table lookup failed；Type 72 STRAP 重量無法精算")

    eb = get_m45_by_type("EB-3/8")
    add_custom_entry(
        result,
        "EXP. BOLT",
        eb["type"] if eb else 'EB-3/8"',
        "SUS304",
        2,
        1.0,
        "SET",
        remark='2-phi11 holes; for EB-3/8" EXP. BOLT (M-45); weight estimated at 1.0 kg/SET, M-45 has no weight column',
    )
    if not eb:
        result.warnings.append("M-45 table 找不到 EB-3/8，expansion bolt 以預設 1kg/SET 估算")

    invariant_errors = validate_named_invariants(
        {"hole_count": 2, "bolt_count": 2, "plate_thickness": row["T"]},
        {
            "bolt_count_at_least_2": lambda x: x["bolt_count"] >= 2,
            "hole_count_matches_bolt_count": lambda x: x["hole_count"] == x["bolt_count"],
            "plate_thickness_positive": lambda x: x["plate_thickness"] > 0,
        },
    )
    return apply_truth_contract(
        result,
        type_id="72",
        evidence=[
            make_evidence(
                "strap_dimensions",
                {"line_size": row["line_size"], "B": row["B"], "C": row["C"], "T": row["T"]},
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="STRAP FIG.2 SEE M-54",
                confidence=0.78,
                note="M-54 table came from rendered vector-PDF visual transcription",
            ),
            make_evidence(
                "strap_weight",
                strap["unit_weight_kg"] if strap else None,
                "formula",
                source="formula",
                page=1,
                note_ref="2-phi11 bolt holes",
                confidence=0.74,
                note="Calculated from M-54 B*C*T minus Fig.2 holes; source dimensions still visual-transcribed",
            ),
            make_evidence(
                "expansion_bolt",
                "EB-3/8 x2",
                "standard_table" if eb else "assumption",
                source="standard_table" if eb else "missing_component_table",
                page=1,
                note_ref='FOR EB-3/8" EXP. BOLT (M-45)',
                confidence=0.86 if eb else 0.45,
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["M-54 / Type 72 dimensions are visual-transcribed; reviewer spot-check required"],
    )
