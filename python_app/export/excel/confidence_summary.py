"""Project confidence summaries for manager-facing Excel sheets."""

from __future__ import annotations

from core.project_aggregation import ProjectAnalysisResult, ProjectRowResult
from core.issues import issues_for
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


def project_issue_rows(project: ProjectAnalysisResult) -> list[dict]:
    rows = []
    for row_result in project.rows:
        designation = (
            row_result.input_row.display_designation
            or row_result.input_row.designation
        )
        for issue in issues_for(row_result.single_result):
            rows.append(
                {
                    "designation": designation,
                    "severity": issue.get("severity", "warning"),
                    "code": issue.get("code", ""),
                    "message": issue.get("message", ""),
                    "bom_allowed": bool(issue.get("bom_allowed", True)),
                    "fabrication_allowed": bool(
                        issue.get("fabrication_allowed", True)
                    ),
                }
            )
    return rows


def build_export_context(
    project: ProjectAnalysisResult,
    *,
    mode: str,
    exception_reason: str = "",
) -> dict:
    from core.source_profiles import get_source_profile

    normalized_mode = "final" if mode in {"final", "精算"} else "estimate"
    assumptions = project_assumption_rows(project)
    issues = project_issue_rows(project)
    high_issues = [issue for issue in issues if issue["severity"] == "high"]
    warning_issues = [
        issue for issue in issues if issue["severity"] in {"warning", "info"}
    ]
    source_profile_id = str(project.source_profile or "")
    source_profile_label = ""
    if source_profile_id:
        source_profile_label = get_source_profile(
            source_profile_id
        ).label_zh
    source_override_rows = [
        {
            "designation": (
                row.input_row.display_designation
                or row.input_row.designation
            ),
            "source_profile": row.input_row.source_profile,
            "source_profile_label": row.single_result.meta.get(
                "source_profile_label",
                row.input_row.source_profile,
            ),
        }
        for row in project.rows
        if row.input_row.source_profile
    ]
    source_routing_counts: dict[str, dict] = {}
    for row in project.rows:
        actual_id = str(
            row.single_result.meta.get("source_profile") or ""
        )
        if not actual_id:
            continue
        actual_label = str(
            row.single_result.meta.get("source_profile_label") or actual_id
        )
        item = source_routing_counts.setdefault(
            actual_id,
            {"source_profile": actual_id, "label": actual_label, "rows": 0},
        )
        item["rows"] += 1
    return {
        "mode": normalized_mode,
        "mode_label": "精算" if normalized_mode == "final" else "概算",
        "assumption_rows": assumptions,
        "assumption_count": len(assumptions),
        "issue_rows": issues,
        "high_issue_count": len(high_issues),
        "warning_issue_count": len(warning_issues),
        "exception_reason": exception_reason.strip(),
        "source_profile": source_profile_id,
        "source_profile_label": source_profile_label,
        "source_override_rows": source_override_rows,
        "source_routing": list(source_routing_counts.values()),
    }


def final_export_allowed(context: dict) -> bool:
    if context.get("mode") != "final":
        return True
    if not context.get("assumption_count") and not context.get("high_issue_count"):
        return True
    return bool(str(context.get("exception_reason") or "").strip())
