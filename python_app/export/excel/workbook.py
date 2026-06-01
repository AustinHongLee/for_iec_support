"""Project workbook orchestration."""

from core.cutting_optimizer import CuttingPlan, optimize_from_summary
from core.material_summary import MaterialSummary, aggregate_project
from core.project_aggregation import ProjectAnalysisResult

from .calculation_sheets import _write_calc_reference_sheet, _write_calculation_basis_sheet
from .cutting_sheets import _write_cutting_detail_sheet, _write_cutting_visual_sheet
from .leader_sheets import _write_leader_detail_sheet, _write_leader_procurement_sheet
from .material_sheets import _write_material_summary_sheet
from .project_summary_sheet import _write_project_summary_sheet
from .weight_sheets import _write_project_weight_sheet


def export_project_workbook(project: ProjectAnalysisResult, filepath: str):
    """
    匯出專案級整合 workbook。

    Sheets:
      1. 專案摘要
      2. 重量明細表  (Flat pivot-friendly table)
      3. 計算標準與假設  (Static manager/client reference page)
      4. 支撐分類統計
      5. 支撐統計明細
      6. 重量分析
      7. 材料合計
      8. 下料明細
      9. 下料圖示
    """
    import openpyxl

    summary = aggregate_project(project)
    cutting_plans = _build_cutting_plans(summary)

    wb = openpyxl.Workbook()
    _write_project_summary_sheet(wb.active, project, summary, cutting_plans)
    _write_calculation_basis_sheet(wb.create_sheet("重量明細表"), project)
    _write_calc_reference_sheet(wb.create_sheet("計算標準與假設"), project)
    _write_leader_procurement_sheet(wb.create_sheet("支撐分類統計"), project)
    _write_leader_detail_sheet(wb.create_sheet("支撐統計明細"), project)
    _write_project_weight_sheet(wb.create_sheet("重量分析"), project)
    _write_material_summary_sheet(wb.create_sheet("材料合計"), summary)
    _write_cutting_detail_sheet(wb.create_sheet("下料明細"), cutting_plans)
    _write_cutting_visual_sheet(wb.create_sheet("下料圖示"), cutting_plans)

    _polish_workbook(wb)
    wb.save(filepath)


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
        "專案摘要": "1F3864",
        "重量明細表": "2E5395",
        "計算標準與假設": "DEE3EE",
        "支撐分類統計": "BF8F00",
        "支撐統計明細": "ED7D31",
        "重量分析": "4472C4",
        "材料合計": "70AD47",
        "下料明細": "A9D18E",
        "下料圖示": "4472C4",
    }
    for ws in wb.worksheets:
        ws.sheet_view.zoomScale = 90 if ws.title in {"重量明細表", "支撐統計明細"} else 100
        ws.sheet_view.zoomScaleNormal = ws.sheet_view.zoomScale
        color = tab_colors.get(ws.title)
        if color:
            ws.sheet_properties.tabColor = color

    wb.active = 0
    wb.properties.title = "IEC 管架支撐材料/重量分析"
    wb.properties.subject = "Project material and weight analysis export"
    wb.properties.creator = "IEC Support Analyzer"
