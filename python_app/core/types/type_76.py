"""
Type 76 calculator — Large-pipe 120-degree pad support (D-91).

Format:
    76-{line_size}B

Example:
    76-30B
"""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..truth import apply_truth_contract, make_evidence, validate_named_invariants
from data.type76_table import get_type76_data


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "格式錯誤，應為 76-{line_size}B，例如 76-30B"
        return result

    line_size = get_lookup_value(part2)
    row = get_type76_data(line_size)
    if not row:
        result.error = f'Type 76: 管徑 {part2} ({line_size:g}") 不在範圍 26"~42"'
        return result

    add_custom_entry(
        result,
        "PIPE PAD",
        (
            f'{row["pad_angle_deg"]}deg x {row["pad_length_mm"]}L x '
            f'{row["thickness_mm"]}t, OD={row["od_mm"]}'
        ),
        "Same as pipe / Carbon Steel",
        1,
        row["unit_weight_kg"],
        "PC",
        remark="pad cut from main pipe or fabricated from C/S plate, 12t min",
        category="鋼板類",
    )
    result.warnings.append(
        "Type 76 weight calculated from 120-degree arc x 400L x 12t minimum plate"
    )

    invariant_errors = validate_named_invariants(
        {
            "pad_angle_deg": row["pad_angle_deg"],
            "pad_length_mm": row["pad_length_mm"],
            "plate_thickness": row["thickness_mm"],
        },
        {
            "pad_angle_is_120deg": lambda x: x["pad_angle_deg"] == 120,
            "pad_length_positive": lambda x: x["pad_length_mm"] > 0,
            "plate_thickness_positive": lambda x: x["plate_thickness"] > 0,
        },
    )
    return apply_truth_contract(
        result,
        type_id="76",
        evidence=[
            make_evidence(
                "pad_geometry",
                {
                    "angle_deg": row["pad_angle_deg"],
                    "length_mm": row["pad_length_mm"],
                    "thickness_mm": row["thickness_mm"],
                },
                "visual_transcription",
                source="pdf_visual",
                page=1,
                note_ref="120deg / 400 / 12t MIN.",
                confidence=0.82,
            ),
            make_evidence(
                "pad_weight",
                row["unit_weight_kg"],
                "formula",
                source="formula",
                page=1,
                note_ref="PAD CUT FROM MAIN PIPE OR FAB. FROM C/S PLATE 12t MIN.",
                confidence=0.76,
            ),
        ],
        invariant_errors=invariant_errors,
        review_reasons=["Type 76 dimensions are visual-transcribed; formula uses 12t minimum, not actual pipe wall"],
    )
