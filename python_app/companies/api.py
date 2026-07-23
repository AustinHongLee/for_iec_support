"""公司模板統一入口：依 company 切換判讀邏輯。

單筆:
    from companies import api
    result = api.analyze("FS12W-2-1300H-400L", company="EKO")

專案級（灌進既有 10 分頁 Excel）:
    project = api.analyze_project(rows, company="EKO")
    api.export_project(rows, "out.xlsx", company="EKO")

回傳 core.models.AnalysisResult / ProjectAnalysisResult，與既有 IEC Type 流程
相同的資料模型，因此可直接餵給既有重量彙總與 Excel 匯出，無需修改 core/export。
"""
from .registry import get_analyzer, COMPANY_NAMES


def analyze(fullstring, company="EKO", overrides=None):
    fn = get_analyzer(company)
    if fn is None:
        from core.models import AnalysisResult
        r = AnalysisResult(fullstring=fullstring)
        r.error = f"未知公司模板 {company!r} (可用: {sorted(COMPANY_NAMES)})"
        return r
    return fn(fullstring, overrides)


def companies():
    return dict(COMPANY_NAMES)


def analyze_project(rows, company="EKO"):
    """以指定公司模板判讀一批 ProjectInputRow，回傳 ProjectAnalysisResult。

    rows: list[core.project_aggregation.ProjectInputRow]
    透過 analyze_project_rows 的 calculate_type 注入點切換判讀函式，
    不修改 core.project_aggregation。
    """
    from core.project_aggregation import analyze_project_rows
    analyzer = get_analyzer(company)
    if analyzer is None:
        raise ValueError(f"未知公司模板 {company!r} (可用: {sorted(COMPANY_NAMES)})")
    return analyze_project_rows(rows, calculate_type=analyzer)


def export_project(rows, filepath, company="EKO", export_context=None):
    """判讀一批 rows 並輸出既有 10 分頁 workbook。回傳 ProjectAnalysisResult。"""
    from export.excel.workbook import export_project_workbook
    project = analyze_project(rows, company=company)
    export_project_workbook(project, filepath, export_context=export_context)
    return project
