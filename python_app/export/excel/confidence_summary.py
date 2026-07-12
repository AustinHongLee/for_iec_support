"""Project confidence summaries for manager-facing Excel sheets."""

from __future__ import annotations

from core.project_aggregation import ProjectAnalysisResult, ProjectRowResult
from core.truth import TRUTH_DERIVED, TRUTH_ESTIMATED, TRUTH_EXACT, TRUTH_UNKNOWN


TRUTH_ERROR = "錯誤"
CONFIDENCE_LEVELS = (TRUTH_EXACT, TRUTH_DERIVED, TRUTH_ESTIMATED, TRUTH_UNKNOWN, TRUTH_ERROR)
_WORST_FIRST = (TRUTH_ERROR, TRUTH_UNKNOWN, TRUTH_ESTIMATED, TRUTH_DERIVED, TRUTH_EXACT)


def confidence_level_for_row(row_result: ProjectRowResult) -> str:
    """Return the display confidence level already carried by AnalysisResult.meta."""
    if row_result.single_result.error:
        return TRUTH_ERROR
    level = str((row_result.single_result.meta or {}).get("truth_level") or TRUTH_UNKNOWN)
    return level if level in CONFIDENCE_LEVELS else TRUTH_UNKNOWN


def project_confidence_counts(project: ProjectAnalysisResult) -> dict[str, int]:
    counts = {level: 0 for level in CONFIDENCE_LEVELS}
    for row_result in project.rows:
        counts[confidence_level_for_row(row_result)] += 1
    return counts


def worst_confidence_level(counts: dict[str, int]) -> str:
    for level in _WORST_FIRST:
        if counts.get(level, 0):
            return level
    return TRUTH_UNKNOWN


def review_required_count(project: ProjectAnalysisResult) -> int:
    total = 0
    for row_result in project.rows:
        if row_result.single_result.error or (row_result.single_result.meta or {}).get("requires_review"):
            total += 1
    return total


def format_confidence_counts(counts: dict[str, int]) -> str:
    parts = [f"{level} {counts[level]}" for level in CONFIDENCE_LEVELS if counts.get(level, 0)]
    return " / ".join(parts) if parts else "無資料"


def project_assumption_rows(project: ProjectAnalysisResult) -> list[dict]:
    rows = []
    for row_result in project.rows:
        designation = (
            row_result.input_row.display_designation
            or row_result.input_row.designation
        )
        for evidence in row_result.single_result.evidence or []:
            if evidence.get("basis") != "assumption":
                continue
            rows.append(
                {
                    "designation": designation,
                    "field": evidence.get("field", ""),
                    "value": evidence.get("value", ""),
                    "note": evidence.get("note", ""),
                }
            )
    return rows


def build_export_context(
    project: ProjectAnalysisResult,
    *,
    mode: str,
    exception_reason: str = "",
) -> dict:
    normalized_mode = "final" if mode in {"final", "精算"} else "estimate"
    assumptions = project_assumption_rows(project)
    return {
        "mode": normalized_mode,
        "mode_label": "精算" if normalized_mode == "final" else "概算",
        "assumption_rows": assumptions,
        "assumption_count": len(assumptions),
        "exception_reason": exception_reason.strip(),
    }


def final_export_allowed(context: dict) -> bool:
    if context.get("mode") != "final" or not context.get("assumption_count"):
        return True
    return bool(str(context.get("exception_reason") or "").strip())
