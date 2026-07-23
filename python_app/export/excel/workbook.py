"""Project workbook orchestration."""

from pathlib import Path

from core.cutting_optimizer import CuttingPlan, optimize_from_summary
from core.material_summary import MaterialSummary, aggregate_project
from core.project_aggregation import ProjectAnalysisResult

from .calculation_sheets import (
    _write_calc_reference_sheet,
    _write_calculation_basis_sheet,
    _write_unit_weight_sheet,
)
from .cutting_sheets import _write_cutting_detail_sheet, _write_cutting_visual_sheet
from .leader_sheets import _write_leader_detail_sheet, _write_leader_procurement_sheet
from .manager_cover_sheet import _write_manager_cover_sheet
from .material_sheets import _write_material_summary_sheet
from .project_summary_sheet import _write_project_summary_sheet
from .weight_sheets import _write_project_weight_sheet


FULL_WORKBOOK_SHEETS = (
    "長官-摘要",
    "專案摘要",
    "重量明細表",
    "單組重量明細",
    "計算標準與假設",
    "長官-支撐分類",
    "查核-支撐明細",
    "重量分析",
    "材料合計",
    "下料明細",
    "下料圖示",
)

WORKBOOK_PACKAGE_PROFILES = {
    "完整活頁簿": FULL_WORKBOOK_SHEETS,
    "長官業主包": (
        "長官-摘要",
        "專案摘要",
        "單組重量明細",
        "長官-支撐分類",
        "查核-支撐明細",
    ),
    "工程明細包": (
        "專案摘要",
        "重量明細表",
        "單組重量明細",
        "計算標準與假設",
        "重量分析",
    ),
    "採購材料包": (
        "材料合計",
        "長官-支撐分類",
        "查核-支撐明細",
    ),
    "下料製造包": (
        "材料合計",
        "下料明細",
        "下料圖示",
    ),
}


def export_project_workbook(
    project: ProjectAnalysisResult,
    filepath: str,
    *,
    export_context: dict | None = None,
):
    """
    匯出專案級整合 workbook。

    Sheets:
      1. 長官-摘要
      2. 專案摘要
      3. 重量明細表  (Flat pivot-friendly table)
      4. 計算標準與假設  (Static manager/client reference page)
      5. 長官-支撐分類
      6. 查核-支撐明細
      7. 重量分析
      8. 材料合計
      9. 下料明細
      10. 下料圖示
    """
    wb = build_project_workbook(
        project, FULL_WORKBOOK_SHEETS, export_context=export_context
    )
    wb.save(filepath)


def export_project_workbook_package(
    project: ProjectAnalysisResult,
    output_dir: str | Path,
    *,
    export_context: dict | None = None,
) -> dict[str, Path]:
    """Export the complete workbook plus role-focused workbook packages."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    exported: dict[str, Path] = {}
    for label, sheets in WORKBOOK_PACKAGE_PROFILES.items():
        path = target_dir / f"{label}.xlsx"
        wb = build_project_workbook(
            project, sheets, export_context=export_context
        )
        wb.save(path)
        exported[label] = path
    return exported


def build_project_workbook(
    project: ProjectAnalysisResult,
    sheets: tuple[str, ...] = FULL_WORKBOOK_SHEETS,
    *,
    export_context: dict | None = None,
):
    """Build a project workbook containing only the requested sheets."""
    import openpyxl

    summary = aggregate_project(project)
    cutting_plans = _build_cutting_plans(summary)

    wb = openpyxl.Workbook()
    for index, sheet_name in enumerate(sheets):
        ws = wb.active if index == 0 else wb.create_sheet(sheet_name)
        ws.title = sheet_name
        _write_project_sheet(
            ws,
            sheet_name,
            project,
            summary,
            cutting_plans,
            tuple(sheets),
            export_context=export_context,
        )

    _polish_workbook(wb)
    return wb


def _write_project_sheet(
    ws,
    sheet_name: str,
    project: ProjectAnalysisResult,
    summary: MaterialSummary,
    cutting_plans: list[CuttingPlan],
    available_sheets: tuple[str, ...],
    *,
    export_context: dict | None = None,
) -> None:
    if sheet_name == "長官-摘要":
        _write_manager_cover_sheet(
            ws,
            project,
            summary,
            available_sheets=available_sheets,
            export_context=export_context,
        )
    elif sheet_name == "專案摘要":
        _write_project_summary_sheet(ws, project, summary, cutting_plans, available_sheets=available_sheets)
    elif sheet_name == "重量明細表":
        _write_calculation_basis_sheet(ws, project)
    elif sheet_name == "單組重量明細":
        _write_unit_weight_sheet(ws, project)
    elif sheet_name == "計算標準與假設":
        _write_calc_reference_sheet(ws, project, export_context=export_context)
    elif sheet_name == "長官-支撐分類":
        _write_leader_procurement_sheet(ws, project)
    elif sheet_name == "查核-支撐明細":
        _write_leader_detail_sheet(ws, project)
    elif sheet_name == "重量分析":
        _write_project_weight_sheet(ws, project)
    elif sheet_name == "材料合計":
        _write_material_summary_sheet(ws, summary)
    elif sheet_name == "下料明細":
        _write_cutting_detail_sheet(ws, cutting_plans)
    elif sheet_name == "下料圖示":
        _write_cutting_visual_sheet(ws, cutting_plans)
    else:
        raise ValueError(f"Unknown project workbook sheet: {sheet_name}")


def _build_cutting_plans(summary: MaterialSummary) -> list[CuttingPlan]:
    plans: list[CuttingPlan] = []
    for ln in summary.get_linear_lines():
        plan = optimize_from_summary(ln)
        if plan and plan.total_pieces > 0:
            plans.append(plan)
    return plans


def _polish_workbook(wb) -> None:
    """Apply workbook-level visual cues after all sheets are rendered."""
    tab_colors = {
        "長官-摘要": "1F3864",
        "專案摘要": "1F3864",
        "重量明細表": "2E5395",
        "單組重量明細": "5B9BD5",
        "計算標準與假設": "DEE3EE",
        "長官-支撐分類": "BF8F00",
        "查核-支撐明細": "ED7D31",
        "重量分析": "4472C4",
        "材料合計": "70AD47",
        "下料明細": "A9D18E",
        "下料圖示": "4472C4",
    }
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 90 if ws.title in {"重量明細表", "單組重量明細", "查核-支撐明細"} else ws.sheet_view.zoomScale or 100
        ws.sheet_view.zoomScaleNormal = ws.sheet_view.zoomScale
        color = tab_colors.get(ws.title)
        if color:
            ws.sheet_properties.tabColor = color

    wb.active = 0
    wb.properties.title = "IEC 管架支撐材料/重量分析"
    wb.properties.subject = "Project material and weight analysis export"
    wb.properties.creator = "IEC Support Analyzer"
