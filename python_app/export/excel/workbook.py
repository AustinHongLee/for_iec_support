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

    wb.save(filepath)


def _build_cutting_plans(summary: MaterialSummary) -> list[CuttingPlan]:
    plans: list[CuttingPlan] = []
    for ln in summary.get_linear_lines():
        plan = optimize_from_summary(ln)
        if plan and plan.total_pieces > 0:
            plans.append(plan)
    return plans
