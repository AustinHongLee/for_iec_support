"""Pure presentation helpers for calculation, BOM, and fabrication readiness."""

from __future__ import annotations

from dataclasses import dataclass

from core.issues import highest_issue, issues_for


def _unique_text(values) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return tuple(result)


def _flag_label(value, *, ready: str, blocked: str) -> str:
    if value is True:
        return ready
    if value is False:
        return blocked
    return "未標示"


@dataclass(frozen=True)
class ResultReadiness:
    status_symbol: str
    needs_attention: bool
    bom_label: str
    fabrication_label: str
    compact_label: str
    source_label: str
    source_drawing: str
    density_review_count: int
    issue_severity: str
    issue_count: int
    issue_messages: tuple[str, ...]
    blockers: tuple[str, ...]
    review_reasons: tuple[str, ...]

    @property
    def tooltip(self) -> str:
        lines = [
            f"BOM：{self.bom_label}",
            f"加工圖：{self.fabrication_label}",
        ]
        if self.density_review_count:
            lines.append(f"密度待覆核：{self.density_review_count} 項")
        if self.issue_messages:
            level = "高風險" if self.issue_severity == "high" else "警示"
            lines.append(f"{level}：")
            lines.extend(f"• {item}" for item in self.issue_messages)
        if self.source_label:
            lines.append(f"圖面來源：{self.source_label}")
        if self.source_drawing:
            lines.append(f"來源圖：{self.source_drawing}")
        if self.blockers:
            lines.append("待補資料：")
            lines.extend(f"• {item}" for item in self.blockers)
        if self.review_reasons:
            lines.append("其他覆核原因：")
            lines.extend(f"• {item}" for item in self.review_reasons)
        return "\n".join(lines)


@dataclass(frozen=True)
class EntryReadiness:
    fabrication_label: str
    density_label: str
    needs_attention: bool
    tooltip: str


def summarize_materials(result, *, limit: int = 2) -> str:
    """Summarize actual calculated entry materials for the master table."""
    materials = _unique_text(
        entry.material
        for entry in getattr(result, "entries", ())
        if getattr(entry, "material", "")
    )
    if not materials:
        return ""
    if len(materials) <= limit:
        return " / ".join(materials)
    return f"{' / '.join(materials[:limit])} +{len(materials) - limit}"


def entry_readiness(entry) -> EntryReadiness:
    geometry = getattr(entry, "geometry", None)
    blockers = _unique_text(
        getattr(geometry, "fabrication_blockers", ()) if geometry else ()
    )
    fabrication_ready = (
        getattr(geometry, "fabrication_ready", None) if geometry else None
    )
    if fabrication_ready is True:
        fabrication_label = "✓ 可出圖"
    elif blockers:
        fabrication_label = "⚠ 待補"
    else:
        fabrication_label = "— 未標示"

    density = float(getattr(entry, "density_g_cm3", 0.0) or 0.0)
    density_review = bool(getattr(entry, "density_requires_review", False))
    if density_review:
        density_label = "⚠ 待覆核"
    elif density > 0:
        density_label = "✓ 已確認"
    else:
        density_label = "— 不適用"

    lines = []
    density_source = str(getattr(entry, "density_source", "") or "").strip()
    if density > 0:
        lines.append(f"算重密度：{density:g} g/cm³")
    if density_source:
        lines.append(f"密度依據：{density_source}")
    if blockers:
        lines.append("加工待補：")
        lines.extend(f"• {item}" for item in blockers)
    return EntryReadiness(
        fabrication_label=fabrication_label,
        density_label=density_label,
        needs_attention=density_review or bool(blockers),
        tooltip="\n".join(lines),
    )


def result_readiness(result) -> ResultReadiness:
    """Build one support-level UI state without changing calculation truth."""
    if result is None:
        return ResultReadiness(
            status_symbol="—",
            needs_attention=False,
            bom_label="未分析",
            fabrication_label="未分析",
            compact_label="未分析",
            source_label="",
            source_drawing="",
            density_review_count=0,
            issue_severity="",
            issue_count=0,
            issue_messages=(),
            blockers=(),
            review_reasons=(),
        )
    if getattr(result, "error", ""):
        return ResultReadiness(
            status_symbol="✗",
            needs_attention=True,
            bom_label="計算錯誤",
            fabrication_label="計算錯誤",
            compact_label="計算錯誤",
            source_label="",
            source_drawing="",
            density_review_count=0,
            issue_severity="error",
            issue_count=1,
            issue_messages=(str(result.error),),
            blockers=(),
            review_reasons=(str(result.error),),
        )

    meta = getattr(result, "meta", {}) or {}
    fabrication = meta.get("fabrication") or {}
    meta_sources = meta.get("sources") or ()
    if isinstance(meta_sources, str):
        meta_sources = (meta_sources,)
    bom_flag = fabrication.get("bom_ready")
    fabrication_flag = fabrication.get("fabrication_ready")
    bom_label = _flag_label(bom_flag, ready="可用", blocked="待補")
    fabrication_label = _flag_label(
        fabrication_flag,
        ready="可出圖",
        blocked="待補",
    )
    density_review_count = sum(
        1
        for entry in getattr(result, "entries", ())
        if getattr(entry, "density_requires_review", False)
    )
    blockers = _unique_text(fabrication.get("blockers") or ())
    review_reasons = _unique_text(meta.get("review_reasons") or ())
    issues = issues_for(result)
    highest = highest_issue(issues)
    issue_severity = str((highest or {}).get("severity") or "")
    issue_messages = _unique_text(
        issue.get("message") for issue in issues if issue.get("message")
    )
    blockers = tuple(
        blocker for blocker in blockers if blocker not in set(issue_messages)
    )
    needs_attention = (
        bom_flag is False
        or fabrication_flag is False
        or density_review_count > 0
        or bool(issues)
    )
    compact_parts = [
        f"BOM {'✓' if bom_flag is True else '待補' if bom_flag is False else '—'}",
        (
            f"加工 {'✓' if fabrication_flag is True else '待補' if fabrication_flag is False else '—'}"
        ),
    ]
    if density_review_count:
        compact_parts.append(f"密度待核 {density_review_count}")
    if issues:
        compact_parts.append(
            f"{'高風險 ▲' if issue_severity == 'high' else '警示 ⚠'}{len(issues)}"
        )

    if issue_severity == "high":
        status_symbol = "▲"
    elif issue_severity in {"warning", "info"}:
        status_symbol = "⚠"
    else:
        status_symbol = "⚠" if needs_attention else "✓"

    return ResultReadiness(
        status_symbol=status_symbol,
        needs_attention=needs_attention,
        bom_label=bom_label,
        fabrication_label=fabrication_label,
        compact_label="｜".join(compact_parts),
        source_label=str(meta.get("source_profile_label") or "").strip(),
        source_drawing=str(
            fabrication.get("source_drawing")
            or (meta_sources[0] if meta_sources else "")
            or ""
        ).strip(),
        density_review_count=density_review_count,
        issue_severity=issue_severity,
        issue_count=len(issues),
        issue_messages=issue_messages,
        blockers=blockers,
        review_reasons=review_reasons,
    )
