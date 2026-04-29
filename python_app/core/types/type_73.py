"""
Type 73 calculator — Spring strap support (D-88/D-88A).

Format:
    73-{line_size}B-{S|G}

Example:
    73-6B-G

`S` denotes slide support and `G` denotes guide support. The drawing calls out
STRAP SEE M-53 and spring data on sheet D-88A.
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.type73_table import (
    build_type73_strap_item,
    estimate_type73_gusset_weight_kg,
    estimate_type73_stud_weight_kg,
    get_type73_bolt_count,
    get_type73_data,
    get_type73_spring_data,
)


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    part2 = get_part(fullstring, 2)
    part3 = (get_part(fullstring, 3) or "").upper()
    if not part2 or part3 not in {"S", "G"}:
        result.error = "格式錯誤，應為 73-{line_size}B-{S|G}，例如 73-6B-G"
        return result

    line_size = get_lookup_value(part2)
    row = get_type73_data(line_size)
    if not row:
        result.error = f'Type 73: 管徑 {part2} ({line_size:g}") 不在範圍 1"~24"'
        return result

    support_mode = "GUIDE" if part3 == "G" else "SLIDE"
    bolt_count = get_type73_bolt_count(line_size)

    strap = build_type73_strap_item(line_size)
    add_custom_entry(
        result,
        "STRAP",
        strap["spec"] if strap else f'M-53 STRAP, {row["line_size"]}',
        strap["material"] if strap else "A283-C",
        1,
        strap["unit_weight_kg"] if strap else 0.0,
        "PC",
        remark="SEE M-53; weight estimated from Type 73 A x steel bar size",
        category="鋼板類",
    )

    spring = get_type73_spring_data(row["spring_mark"])
    add_custom_entry(
        result,
        "SPRING COIL",
        (
            f'{row["spring_mark"]}, {spring["wire_dia_mm"]}W x '
            f'{spring["coil_id_mm"]}ID, k={spring["spring_constant_kg_per_mm"]}'
            if spring
            else row["spring_mark"]
        ),
        spring["material"] if spring else "ASTM A229 Class 1",
        bolt_count,
        spring["unit_weight_kg"] if spring else 0.0,
        "PC",
        remark="SEE D-88A spring coil table; unit weight calculated from wire geometry",
        category="彈簧類",
    )

    add_custom_entry(
        result,
        "STUD BOLT",
        f'{row["bolt_dia"]} x L~{row["G"]}mm',
        "Carbon Steel",
        bolt_count,
        estimate_type73_stud_weight_kg(row),
        "PC",
        remark=f'{row["bolt_arrangement"]}; D-88 dimension G used as estimated bolt length',
    )

    add_custom_entry(
        result,
        "WASHER",
        f'for {row["bolt_dia"]} stud bolt',
        "Carbon Steel",
        bolt_count * 2,
        0.05,
        "PC",
        remark="washer callout on D-88; unit weight placeholder",
    )

    gusset_weight = estimate_type73_gusset_weight_kg(row)
    if gusset_weight:
        add_custom_entry(
            result,
            "GUSSET",
            f'{row["E"]}x{row["H"]} triangular, t=same as {row["steel_bar_size"]}',
            "A36/SS400",
            2,
            gusset_weight,
            "PC",
            remark='for 6" and larger; estimated triangular plate weight',
            category="鋼板類",
        )

    result.warnings.append(
        "Type 73 PDF 無文字層；尺寸表由 rendered bitmap AI visual transcription，需 reviewer spot-check"
    )
    result.warnings.append(
        "Type 73 strap/stud/washer/gusset 重量為幾何估算；M-53 目前不是 weight-ready"
    )
    if support_mode == "GUIDE":
        result.warnings.append('GUIDE support: NOTE 3 hole length L=D+3, see D-88A detail C')
    else:
        result.warnings.append('SLIDE support: NOTE 3 hole length L=2D, see D-88A detail C')

    invariant_errors = validate_named_invariants(
        {"bolt_count": bolt_count, "spring_count": bolt_count, "plate_thickness": row["H"]},
        {
            "bolt_count_at_least_2": lambda x: x["bolt_count"] >= 2,
            "spring_count_matches_bolt_count": lambda x: x["spring_count"] == x["bolt_count"],
            "height_positive": lambda x: x["plate_thickness"] > 0,
        },
    )
    return apply_truth_contract(
        result,
        type_id="73",
        evidence=[
            make_evidence(
                "type73_dimensions",
                {"line_size": row["line_size"], "A": row["A"], "B": row["B"], "C": row["C"], "H": row["H"]},
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="D-88 table",
                confidence=0.68,
            ),
            make_evidence(
                "spring_data",
                row["spring_mark"],
                "visual_transcription",
                source="pdf_visual",
                page=2,
                note_ref="ENGINEERING DATA OF SPRING COILS",
                confidence=0.72,
            ),
            make_evidence(
                "strap_weight",
                strap["unit_weight_kg"] if strap else None,
                "geometry_estimate",
                source="formula",
                page=1,
                note_ref="STRAP SEE M-53",
                confidence=0.52,
                note="M-53 is dimension lookup-ready but not weight-ready",
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["Type 73 uses visual transcription and geometry-estimated weights"],
    )
