"""Structured, non-fatal calculation issues and release gates.

An issue may allow a calculation to finish while still preventing the result
from being treated as released BOM or fabrication information.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


ISSUE_SEVERITY_ORDER = {
    "info": 0,
    "warning": 1,
    "high": 2,
    "error": 3,
}

ISSUE_SEVERITY_LABEL_ZH = {
    "info": "提示",
    "warning": "警示",
    "high": "高風險",
    "error": "錯誤",
}

# Guardrails for drawing-envelope extrapolation.  Both the relative and
# absolute differences are checked so a generous limit does not hide a large
# dimensional change, and a small limit is not allowed to expand many times.
ENVELOPE_WARNING_MAX_EXCESS_RATIO = 0.10
ENVELOPE_WARNING_MAX_EXCESS_MM = 100.0
ENVELOPE_HIGH_MAX_ACTUAL_RATIO = 2.0
ENVELOPE_HIGH_MAX_EXCESS_MM = 2000.0


def _normalized_severity(value: object) -> str:
    severity = str(value or "warning").strip().lower()
    return severity if severity in ISSUE_SEVERITY_ORDER else "warning"


def classify_upper_limit(
    actual: float,
    limit: float,
    *,
    inclusive: bool = True,
) -> dict[str, Any] | None:
    """Classify a drawing upper-limit overrun with a finite hard-stop guardrail.

    ``warning`` is reserved for a difference no greater than both 10% and
    100 mm.  ``high`` permits engineering review up to 2x the documented limit
    and at most 2000 mm beyond it.  Anything larger remains a hard error.
    """

    actual_value = float(actual)
    limit_value = float(limit)
    violates = actual_value > limit_value if inclusive else actual_value >= limit_value
    if not violates:
        return None
    if limit_value <= 0:
        return {
            "severity": "error",
            "actual": actual_value,
            "limit": limit_value,
            "excess_mm": actual_value - limit_value,
            "excess_ratio": None,
        }

    excess = max(0.0, actual_value - limit_value)
    excess_ratio = excess / limit_value
    if (
        excess <= ENVELOPE_WARNING_MAX_EXCESS_MM + 1e-9
        and excess_ratio <= ENVELOPE_WARNING_MAX_EXCESS_RATIO + 1e-9
    ):
        severity = "warning"
    elif (
        actual_value <= limit_value * ENVELOPE_HIGH_MAX_ACTUAL_RATIO
        and excess <= ENVELOPE_HIGH_MAX_EXCESS_MM
    ):
        severity = "high"
    else:
        severity = "error"
    return {
        "severity": severity,
        "actual": actual_value,
        "limit": limit_value,
        "excess_mm": excess,
        "excess_ratio": excess_ratio,
        "policy": {
            "warning_max_excess_ratio": ENVELOPE_WARNING_MAX_EXCESS_RATIO,
            "warning_max_excess_mm": ENVELOPE_WARNING_MAX_EXCESS_MM,
            "high_max_actual_ratio": ENVELOPE_HIGH_MAX_ACTUAL_RATIO,
            "high_max_excess_mm": ENVELOPE_HIGH_MAX_EXCESS_MM,
        },
    }


def combine_limit_checks(
    checks: Iterable[tuple[str, float, float, bool]],
) -> dict[str, Any] | None:
    """Return the highest classification from ``(name, actual, limit, inclusive)``."""

    exceeded: list[dict[str, Any]] = []
    for name, actual, limit, inclusive in checks:
        classification = classify_upper_limit(
            actual, limit, inclusive=bool(inclusive)
        )
        if classification is None:
            continue
        classification["dimension"] = str(name)
        exceeded.append(classification)
    if not exceeded:
        return None
    highest = max(
        exceeded,
        key=lambda item: ISSUE_SEVERITY_ORDER.get(
            _normalized_severity(item.get("severity")), 1
        ),
    )
    return {
        "severity": highest["severity"],
        "exceeded": exceeded,
    }


def register_source_envelope(
    result: Any,
    *,
    type_label: str,
    source_ref: str,
    checks: Iterable[tuple[str, float, float, bool]],
    review_note: str = "",
) -> bool:
    """Register a finite source-envelope extrapolation.

    Returns ``True`` when calculation may continue.  Excessive extrapolation
    becomes a regular result error and returns ``False``.
    """

    classification = combine_limit_checks(checks)
    if classification is None:
        return True

    descriptions = []
    for item in classification["exceeded"]:
        excess_ratio = item.get("excess_ratio")
        percent = (
            f"+{float(excess_ratio) * 100:.1f}%"
            if excess_ratio is not None
            else "比例無法判定"
        )
        descriptions.append(
            f"{item['dimension']}={item['actual']:g}mm "
            f"(上限 {item['limit']:g}mm，超出 {item['excess_mm']:g}mm/{percent})"
        )
    detail = "、".join(descriptions)
    severity = classification["severity"]
    if severity == "error":
        result.error = (
            f"{type_label}: {detail} 超出 {source_ref} 的有限外插護欄；"
            "為避免公式無限制擴張，停止計算"
        )
        return False

    label = ISSUE_SEVERITY_LABEL_ZH[severity]
    release_note = (
        "可計算並產生暫估 BOM，但須工程確認後才可正式下料/出加工圖"
        if severity == "high"
        else "計算放行；超出來源標準範圍，正式加工前仍需確認"
    )
    review_suffix = f"；{str(review_note).strip()}" if str(review_note).strip() else ""
    add_issue(
        result,
        code="SOURCE_ENVELOPE_EXTRAPOLATION",
        severity=severity,
        message=(
            f"{type_label}: {detail} 超出 {source_ref}；"
            f"{release_note}{review_suffix}"
        ),
        scope="source_envelope",
        calculation_allowed=True,
        bom_allowed=severity != "high",
        fabrication_allowed=False,
        source=source_ref,
    )
    result.meta.setdefault("source_envelope", classification)
    return True


def register_host_m42_variance(
    result: Any,
    *,
    type_label: str,
    source_ref: str,
    letter: str,
    host_allowed: Iterable[str],
) -> None:
    """Allow a source-defined M-42 type that the host Type drawing did not list."""

    allowed_text = "/".join(str(value) for value in host_allowed)
    add_issue(
        result,
        code="HOST_M42_NOT_LISTED",
        severity="high",
        message=(
            f"{type_label}: 主體圖 {source_ref} 僅列 M-42 {allowed_text}，"
            f"本筆 M-42 {str(letter).upper()} 依同來源 M-42 標準暫算；"
            "須工程確認組合適用性後才可正式 BOM／下料／出加工圖"
        ),
        scope="host_component_mismatch",
        calculation_allowed=True,
        bom_allowed=False,
        fabrication_allowed=False,
        source=source_ref,
    )


def issues_for(result: Any) -> list[dict[str, Any]]:
    meta = getattr(result, "meta", None)
    if not isinstance(meta, dict):
        return []
    raw_issues = meta.get("issues")
    if not isinstance(raw_issues, list):
        return []
    return [issue for issue in raw_issues if isinstance(issue, dict)]


def add_issue(
    result: Any,
    *,
    code: str,
    severity: str,
    message: str,
    scope: str,
    calculation_allowed: bool = True,
    bom_allowed: bool = True,
    fabrication_allowed: bool = False,
    source: str = "",
) -> dict[str, Any]:
    """Attach one structured issue and keep the legacy warning list useful."""

    issue = {
        "code": str(code).strip(),
        "severity": _normalized_severity(severity),
        "message": str(message).strip(),
        "scope": str(scope).strip(),
        "calculation_allowed": bool(calculation_allowed),
        "bom_allowed": bool(bom_allowed),
        "fabrication_allowed": bool(fabrication_allowed),
    }
    if source:
        issue["source"] = str(source).strip()

    if not isinstance(getattr(result, "meta", None), dict):
        result.meta = {}
    issues = result.meta.setdefault("issues", [])
    if not isinstance(issues, list):
        issues = []
        result.meta["issues"] = issues

    duplicate = next(
        (
            existing
            for existing in issues
            if isinstance(existing, dict)
            and existing.get("code") == issue["code"]
            and existing.get("message") == issue["message"]
        ),
        None,
    )
    if duplicate is not None:
        return duplicate

    issues.append(issue)
    warnings = getattr(result, "warnings", None)
    if isinstance(warnings, list) and issue["message"] not in warnings:
        warnings.append(issue["message"])
    return issue


def highest_issue(result_or_issues: Any) -> dict[str, Any] | None:
    if isinstance(result_or_issues, Iterable) and not isinstance(
        result_or_issues, (str, bytes, dict)
    ):
        issues = [item for item in result_or_issues if isinstance(item, dict)]
    else:
        issues = issues_for(result_or_issues)
    if not issues:
        return None
    return max(
        issues,
        key=lambda issue: ISSUE_SEVERITY_ORDER.get(
            _normalized_severity(issue.get("severity")), 1
        ),
    )


def issue_counts(result: Any) -> dict[str, int]:
    counts = {severity: 0 for severity in ISSUE_SEVERITY_ORDER}
    for issue in issues_for(result):
        counts[_normalized_severity(issue.get("severity"))] += 1
    return counts


def apply_issue_gates(result: Any) -> Any:
    """Reflect structured issues in the existing fabrication readiness model."""

    issues = issues_for(result)
    if not issues:
        return result

    highest = highest_issue(issues)
    result.meta["requires_review"] = True
    result.meta["issue_summary"] = {
        "highest_severity": (
            _normalized_severity(highest.get("severity")) if highest else ""
        ),
        "counts": issue_counts(result),
    }

    fabrication = result.meta.get("fabrication")
    if not isinstance(fabrication, dict):
        fabrication = {}
        result.meta["fabrication"] = fabrication

    blockers = fabrication.setdefault("blockers", [])
    if not isinstance(blockers, list):
        blockers = []
        fabrication["blockers"] = blockers

    if any(not bool(issue.get("bom_allowed", True)) for issue in issues):
        fabrication["bom_ready"] = False
    if any(not bool(issue.get("fabrication_allowed", True)) for issue in issues):
        fabrication["fabrication_ready"] = False

    for issue in issues:
        if bool(issue.get("fabrication_allowed", True)):
            continue
        message = str(issue.get("message") or "").strip()
        if message and message not in blockers:
            blockers.append(message)
    return result
