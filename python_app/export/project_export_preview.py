"""Headless export preview summaries for project workbook/UI flows."""

from dataclasses import dataclass

from core.material_summary import aggregate_project
from core.parser import get_type_code
from core.project_aggregation import ProjectAnalysisResult

from .excel.confidence_summary import (
    format_confidence_counts,
    project_confidence_counts,
    review_required_count,
)
from .excel.leader_sheets import _leader_procurement_stats
from .excel.navigation import workbook_navigation
from .excel.workbook import _build_cutting_plans


@dataclass(frozen=True)
class ProjectExportPreview:
    """Small, user-facing summary of what an export is about to contain."""

    export_label: str
    row_count: int
    support_count: int
    type_count: int
    success_count: int
    error_count: int
    warning_count: int
    review_required_count: int
    confidence_summary: str
    confirm_count: int
    unmatched_count: int
    material_line_count: int
    linear_material_count: int
    cutting_plan_count: int
    total_bars: int
    total_weight: float
    sheet_names: tuple[str, ...] = ()

    @property
    def needs_attention(self) -> bool:
        return bool(self.error_count or self.review_required_count or self.confirm_count or self.unmatched_count)


def build_project_export_preview(
    project: ProjectAnalysisResult,
    *,
    export_label: str,
    include_workbook_sheets: bool,
) -> ProjectExportPreview:
    """Build export preview metrics without opening UI dialogs or saving files."""
    summary = aggregate_project(project)
    cutting_plans = _build_cutting_plans(summary)
    _, _, leader_details = _leader_procurement_stats(project)

    success_count = sum(1 for row in project.rows if not row.single_result.error)
    error_count = len(project.rows) - success_count
    type_count = len({get_type_code(row.input_row.designation) or "未解析" for row in project.rows})
    confidence_counts = project_confidence_counts(project)
    confirm_count = sum(1 for detail in leader_details if detail.status == "需確認")
    unmatched_count = sum(1 for detail in leader_details if detail.status == "未納入")
    total_bars = sum(plan.total_bars for plan in cutting_plans)
    sheet_names: tuple[str, ...] = ()
    if include_workbook_sheets:
        sheet_names = tuple(item.sheet for item in workbook_navigation(total_bars))

    return ProjectExportPreview(
        export_label=export_label,
        row_count=len(project.rows),
        support_count=project.total_support_count,
        type_count=type_count,
        success_count=success_count,
        error_count=error_count,
        warning_count=len(project.warnings),
        review_required_count=review_required_count(project),
        confidence_summary=format_confidence_counts(confidence_counts),
        confirm_count=confirm_count,
        unmatched_count=unmatched_count,
        material_line_count=len(summary.lines),
        linear_material_count=len(summary.get_linear_lines()),
        cutting_plan_count=len(cutting_plans),
        total_bars=total_bars,
        total_weight=summary.total_weight,
        sheet_names=sheet_names,
    )


def format_project_export_preview(preview: ProjectExportPreview) -> str:
    """Format a compact confirmation message for the export dialog."""
    lines = [
        f"即將匯出：{preview.export_label}",
        "",
        f"輸入列：{preview.row_count} 列，支撐 {preview.support_count} 組，Type {preview.type_count} 種",
        f"計算狀態：成功 {preview.success_count}，錯誤 {preview.error_count}，警告 {preview.warning_count}",
        f"資料信心：{preview.confidence_summary}；需複核 {preview.review_required_count} 列",
        f"分類狀態：需確認 {preview.confirm_count}，未納入 {preview.unmatched_count}",
        f"材料合計：{preview.material_line_count} 項，總重 {preview.total_weight:,.2f} kg",
        f"下料摘要：線材 {preview.linear_material_count} 種，下料計畫 {preview.cutting_plan_count} 組，原料 {preview.total_bars} 根",
    ]
    if preview.sheet_names:
        lines.extend(["", "Workbook 分頁：", "、".join(preview.sheet_names)])

    lines.extend(
        [
            "",
            "若數字看起來不對，請先取消並回到分析結果修正。",
            "確認繼續匯出？",
        ]
    )
    return "\n".join(lines)
