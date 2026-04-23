"""
Excel 匯出模組
"""
from typing import List
from core.models import AnalysisResult
from core.project_aggregation import ProjectAnalysisResult

# 表頭定義 (對應 VBA 的 headers)
HEADERS = [
    "材料描述欄", "項次", "品名", "尺寸/規格", "長度", "寬度",
    "材質", "數量", "每米重", "單重", "總重小計", "單位",
    "係數", "長度小計", "數量小計", "總重合計", "屬性", "備註"
]

PROJECT_HEADERS = [
    "型號", "組數", "項次", "品名", "尺寸/規格", "長度(mm)", "寬度(mm)",
    "材質", "單件數量", "單件長度小計", "單件重量",
    "總數量", "總長度小計", "總重量", "單位", "屬性", "備註",
]


def _format_sheet(ws, headers):
    from openpyxl.styles import Font, Alignment, PatternFill

    header_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    header_font = Font(bold=True)
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = min(max_length + 2, 30)


def export_to_excel(results: List[AnalysisResult], filepath: str):
    """匯出分析結果至 Excel"""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Weight_Analysis"

    _format_sheet(ws, HEADERS)

    # 資料
    row = 2
    for result in results:
        # 寫入原始字串到 A 欄
        ws.cell(row=row, column=1, value=result.fullstring)

        if result.error:
            ws.cell(row=row, column=2, value="Error")
            ws.cell(row=row, column=3, value=result.error)
            row += 1
            continue

        for entry in result.entries:
            ws.cell(row=row, column=1, value=result.fullstring if entry.item_no == 1 else "")
            ws.cell(row=row, column=2, value=entry.item_no)
            ws.cell(row=row, column=3, value=entry.name)
            ws.cell(row=row, column=4, value=entry.spec)
            ws.cell(row=row, column=5, value=entry.length)
            ws.cell(row=row, column=6, value=entry.width if entry.width else "")
            ws.cell(row=row, column=7, value=entry.material)
            ws.cell(row=row, column=8, value=entry.quantity)
            ws.cell(row=row, column=9, value=entry.weight_per_unit if entry.weight_per_unit else "")
            ws.cell(row=row, column=10, value=entry.unit_weight)
            ws.cell(row=row, column=11, value=entry.total_weight)
            ws.cell(row=row, column=12, value=entry.unit)
            ws.cell(row=row, column=13, value=entry.factor)
            ws.cell(row=row, column=14, value=entry.length_subtotal if entry.length_subtotal else "")
            ws.cell(row=row, column=15, value=entry.qty_subtotal if entry.qty_subtotal else "")
            ws.cell(row=row, column=16, value=entry.weight_output)
            ws.cell(row=row, column=17, value=entry.category)
            ws.cell(row=row, column=18, value=entry.remark if entry.remark else "")
            row += 1

    _format_sheet(ws, HEADERS)

    wb.save(filepath)


def export_project_to_excel(project: ProjectAnalysisResult, filepath: str):
    """匯出 project-aware 分析結果，保留單件欄區與專案總數欄區。"""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Project_Weight_Analysis"

    _format_sheet(ws, PROJECT_HEADERS)

    row = 2
    for row_result in project.rows:
        input_row = row_result.input_row
        single_result = row_result.single_result
        scaled_result = row_result.scaled_result

        if single_result.error:
            ws.cell(row=row, column=1, value=input_row.designation)
            ws.cell(row=row, column=2, value=input_row.quantity)
            ws.cell(row=row, column=3, value="Error")
            ws.cell(row=row, column=4, value=single_result.error)
            row += 1
            continue

        for single_entry, scaled_entry in zip(single_result.entries, scaled_result.entries):
            ws.cell(row=row, column=1, value=input_row.designation if single_entry.item_no == 1 else "")
            ws.cell(row=row, column=2, value=input_row.quantity if single_entry.item_no == 1 else "")
            ws.cell(row=row, column=3, value=single_entry.item_no)
            ws.cell(row=row, column=4, value=single_entry.name)
            ws.cell(row=row, column=5, value=single_entry.spec)
            ws.cell(row=row, column=6, value=single_entry.length)
            ws.cell(row=row, column=7, value=single_entry.width if single_entry.width else "")
            ws.cell(row=row, column=8, value=single_entry.material)
            ws.cell(row=row, column=9, value=single_entry.quantity)
            ws.cell(row=row, column=10, value=single_entry.length_subtotal if single_entry.length_subtotal else "")
            ws.cell(row=row, column=11, value=single_entry.weight_output)
            ws.cell(row=row, column=12, value=scaled_entry.quantity)
            ws.cell(row=row, column=13, value=scaled_entry.length_subtotal if scaled_entry.length_subtotal else "")
            ws.cell(row=row, column=14, value=scaled_entry.weight_output)
            ws.cell(row=row, column=15, value=single_entry.unit)
            ws.cell(row=row, column=16, value=single_entry.category)
            ws.cell(row=row, column=17, value=single_entry.remark if single_entry.remark else "")
            row += 1

    _format_sheet(ws, PROJECT_HEADERS)

    wb.save(filepath)
