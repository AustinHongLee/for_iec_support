"""
Excel 匯出模組
"""
from typing import List
from core.models import AnalysisResult
from core.project_aggregation import ProjectAnalysisResult
from core.material_summary import aggregate_project, MaterialSummary
from core.cutting_optimizer import CuttingPlan, optimize_from_summary

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

SUMMARY_HEADERS = [
    "品名", "規格", "材質", "屬性", "需求總長(mm)", "需求件數/數量",
    "總重(kg)", "原料長度(mm)", "建議採購量", "單位", "來源編碼",
]

CUTTING_HEADERS = [
    "材料", "原料 #", "切割段", "需求長(mm)", "含損耗(mm)",
    "累計(mm)", "餘料(mm)", "使用率", "用於",
]

VISUAL_SLOT_COUNT = 30


def _styles():
    from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

    thin = Side(style="thin", color="D9E2F3")
    return {
        "title_fill": PatternFill("solid", fgColor="17365D"),
        "section_fill": PatternFill("solid", fgColor="D9EAF7"),
        "header_fill": PatternFill("solid", fgColor="1F4E78"),
        "subheader_fill": PatternFill("solid", fgColor="D6DCE4"),
        "ok_fill": PatternFill("solid", fgColor="C6EFCE"),
        "warn_fill": PatternFill("solid", fgColor="FFEB9C"),
        "bad_fill": PatternFill("solid", fgColor="FFC7CE"),
        "used_fill": PatternFill("solid", fgColor="5B9BD5"),
        "remnant_fill": PatternFill("solid", fgColor="A9D18E"),
        "border": Border(left=thin, right=thin, top=thin, bottom=thin),
        "title_font": Font(bold=True, color="FFFFFF", size=16),
        "header_font": Font(bold=True, color="FFFFFF"),
        "section_font": Font(bold=True, color="17365D"),
        "bold_font": Font(bold=True),
        "center": Alignment(horizontal="center", vertical="center"),
        "right": Alignment(horizontal="right", vertical="center"),
        "wrap": Alignment(vertical="top", wrap_text=True),
    }


def _setup_sheet(ws, title: str, merge_to: str = "K1"):
    styles = _styles()
    ws.sheet_view.showGridLines = False
    ws.merge_cells(f"A1:{merge_to}")
    cell = ws["A1"]
    cell.value = title
    cell.font = styles["title_font"]
    cell.fill = styles["title_fill"]
    cell.alignment = styles["center"]
    ws.row_dimensions[1].height = 28


def _write_headers(ws, row: int, headers: list[str]):
    styles = _styles()
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=header)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]


def _apply_table_style(ws, min_row: int, max_row: int, max_col: int):
    styles = _styles()
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=1, max_col=max_col):
        for cell in row:
            cell.border = styles["border"]
            if cell.row > min_row:
                cell.alignment = styles["wrap"]


def _set_widths(ws, widths: list[float]):
    from openpyxl.utils import get_column_letter

    for index, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(index)].width = width


def _format_number_columns(ws, row_start: int, row_end: int, columns: list[int], fmt: str):
    for row in range(row_start, row_end + 1):
        for col in columns:
            ws.cell(row=row, column=col).number_format = fmt


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
            ws.cell(row=row, column=18, value=entry.display_remark)
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
            ws.cell(row=row, column=17, value=single_entry.display_remark)
            row += 1

    _format_sheet(ws, PROJECT_HEADERS)

    wb.save(filepath)


def export_project_workbook(project: ProjectAnalysisResult, filepath: str):
    """
    匯出專案級整合 workbook。

    Sheets:
      1. 專案摘要
      2. 重量分析
      3. 材料合計
      4. 下料明細
      5. 下料圖示
    """
    import openpyxl

    summary = aggregate_project(project)
    cutting_plans = _build_cutting_plans(summary)

    wb = openpyxl.Workbook()
    _write_project_summary_sheet(wb.active, project, summary, cutting_plans)
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


def _write_project_summary_sheet(ws, project: ProjectAnalysisResult, summary: MaterialSummary, plans: list[CuttingPlan]):
    styles = _styles()
    ws.title = "專案摘要"
    _setup_sheet(ws, "專案材料統計總覽", "H1")

    total_bars = sum(plan.total_bars for plan in plans)
    total_cut_pieces = sum(plan.total_pieces for plan in plans)
    kpis = [
        ("支撐總組數", project.total_support_count, "組"),
        ("材料種類", len(summary.lines), "項"),
        ("專案總重", round(summary.total_weight, 2), "kg"),
        ("下料材料", len(plans), "種"),
        ("建議原料根數", total_bars, "根"),
        ("下料段數", total_cut_pieces, "段"),
    ]
    row = 3
    for idx, (label, value, unit) in enumerate(kpis):
        base_col = 1 + (idx % 3) * 3
        base_row = row + (idx // 3) * 3
        ws.merge_cells(start_row=base_row, start_column=base_col, end_row=base_row, end_column=base_col + 1)
        ws.cell(base_row, base_col, label)
        ws.cell(base_row, base_col).font = styles["section_font"]
        ws.cell(base_row, base_col).fill = styles["section_fill"]
        ws.cell(base_row + 1, base_col, value)
        ws.cell(base_row + 1, base_col).font = styles["title_font"]
        ws.cell(base_row + 1, base_col).fill = styles["title_fill"]
        ws.cell(base_row + 1, base_col).alignment = styles["center"]
        ws.cell(base_row + 1, base_col + 1, unit)
        ws.cell(base_row + 1, base_col + 1).font = styles["bold_font"]
        ws.cell(base_row + 1, base_col + 1).alignment = styles["center"]

    ws.cell(row=10, column=1, value="Workbook 結構").font = styles["section_font"]
    ws.cell(row=11, column=1, value="重量分析：單件與專案總量對照")
    ws.cell(row=12, column=1, value="材料合計：採購清單與來源追蹤")
    ws.cell(row=13, column=1, value="下料明細：每根原料的切割順序")
    ws.cell(row=14, column=1, value="下料圖示：以比例色塊顯示每根原料使用狀態")
    ws.cell(row=16, column=1, value="注意事項").font = styles["section_font"]
    ws.cell(row=17, column=1, value="材料與重量仍以各 Type calculator 與 component table 為準。")
    ws.cell(row=18, column=1, value="下料圖示為規劃輔助；現場仍需依實際餘料與鋸口條件確認。")

    _set_widths(ws, [18, 10, 8, 18, 10, 8, 18, 10])
    for row_idx in range(3, 8):
        for col_idx in range(1, 9):
            ws.cell(row_idx, col_idx).border = styles["border"]


def _write_project_weight_sheet(ws, project: ProjectAnalysisResult):
    _setup_sheet(ws, "重量分析明細", "Q1")
    _write_headers(ws, 3, PROJECT_HEADERS)

    row = 4
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
            values = [
                input_row.designation if single_entry.item_no == 1 else "",
                input_row.quantity if single_entry.item_no == 1 else "",
                single_entry.item_no,
                single_entry.name,
                single_entry.spec,
                single_entry.length,
                single_entry.width if single_entry.width else "",
                single_entry.material,
                single_entry.quantity,
                single_entry.length_subtotal if single_entry.length_subtotal else "",
                single_entry.weight_output,
                scaled_entry.quantity,
                scaled_entry.length_subtotal if scaled_entry.length_subtotal else "",
                scaled_entry.weight_output,
                single_entry.unit,
                single_entry.category,
                single_entry.display_remark,
            ]
            for col, value in enumerate(values, 1):
                ws.cell(row=row, column=col, value=value)
            row += 1

    last_row = max(row - 1, 3)
    _apply_table_style(ws, 3, last_row, len(PROJECT_HEADERS))
    _format_number_columns(ws, 4, last_row, [6, 7, 10, 11, 13, 14], "0.00")
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:Q{last_row}"
    _set_widths(ws, [18, 8, 8, 16, 20, 12, 12, 14, 10, 14, 12, 10, 14, 12, 8, 10, 36])


def _write_material_summary_sheet(ws, summary: MaterialSummary):
    styles = _styles()
    _setup_sheet(ws, "材料合計與採購清單", "K1")
    _write_headers(ws, 3, SUMMARY_HEADERS)

    row = 4
    for ln in summary.lines:
        length_value = round(ln.total_length_mm, 1) if ln.aggregate_type == "linear" else ""
        qty_value = ln.piece_count if ln.aggregate_type == "linear" else ln.total_qty
        stock_length = round(ln.stock_length, 0) if ln.stock_length else ""
        sources = ", ".join(ln.source_fullstrings[:8])
        if len(ln.source_fullstrings) > 8:
            sources += f" ...+{len(ln.source_fullstrings) - 8}"
        values = [
            ln.name,
            ln.spec,
            ln.material,
            ln.category,
            length_value,
            qty_value,
            round(ln.total_weight, 2),
            stock_length,
            ln.purchase_qty,
            ln.purchase_unit,
            sources,
        ]
        for col, value in enumerate(values, 1):
            ws.cell(row=row, column=col, value=value)
        row += 1

    total_row = row + 1
    ws.cell(row=total_row, column=6, value="合計總重").font = styles["bold_font"]
    ws.cell(row=total_row, column=7, value=round(summary.total_weight, 2)).font = styles["bold_font"]

    last_row = max(row - 1, 3)
    _apply_table_style(ws, 3, last_row, len(SUMMARY_HEADERS))
    _format_number_columns(ws, 4, last_row, [5, 7, 8], "0.00")
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:K{last_row}"
    _set_widths(ws, [16, 22, 16, 10, 14, 12, 12, 12, 12, 8, 46])


def _write_cutting_detail_sheet(ws, plans: list[CuttingPlan]):
    styles = _styles()
    _setup_sheet(ws, "下料明細", "I1")

    row = 3
    if not plans:
        ws.cell(row=row, column=1, value="無線性材料需要下料。")
        return

    for plan in plans:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
        cell = ws.cell(row=row, column=1, value=f"{plan.name}  {plan.spec}  ({plan.material})")
        cell.fill = styles["title_fill"]
        cell.font = styles["header_font"]
        row += 1

        ws.cell(row=row, column=1, value="需求段數")
        ws.cell(row=row, column=2, value=plan.total_pieces)
        ws.cell(row=row, column=3, value="需求總長(mm)")
        ws.cell(row=row, column=4, value=round(plan.total_demand_length, 1))
        ws.cell(row=row, column=5, value="原料根數")
        ws.cell(row=row, column=6, value=plan.total_bars)
        ws.cell(row=row, column=7, value="平均使用率")
        ws.cell(row=row, column=8, value=f"{plan.avg_utilization:.1f}%")
        row += 1

        _write_headers(ws, row, CUTTING_HEADERS)
        header_row = row
        row += 1

        for bar_idx, bar in enumerate(plan.bars, start=1):
            cumulative = 0.0
            for piece_idx, piece in enumerate(bar.pieces, start=1):
                cumulative += piece.cut_length
                values = [
                    f"#{bar_idx}" if piece_idx == 1 else "",
                    f"段 {piece_idx}",
                    round(piece.demand_length, 1),
                    round(piece.cut_length, 1),
                    round(cumulative, 1),
                    "",
                    "",
                    "",
                    piece.source,
                ]
                for col, value in enumerate(values, 1):
                    ws.cell(row=row, column=col, value=value)
                row += 1

            note = "廢料" if bar.remnant < 100 else "短料" if bar.remnant < 300 else ""
            fill = styles["bad_fill"] if note == "廢料" else styles["warn_fill"] if note == "短料" else styles["ok_fill"]
            values = ["", "餘料", "", "", "", round(bar.remnant, 1), f"{bar.utilization:.1f}%", note, ""]
            for col, value in enumerate(values, 1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.fill = fill
            row += 1

        _apply_table_style(ws, header_row, row - 1, len(CUTTING_HEADERS))
        row += 1

    ws.freeze_panes = "A3"
    _set_widths(ws, [10, 10, 13, 13, 13, 12, 10, 10, 28])


def _write_cutting_visual_sheet(ws, plans: list[CuttingPlan]):
    styles = _styles()
    _setup_sheet(ws, "下料圖示", "AH1")
    ws.cell(row=2, column=1, value="每列代表一根原料；藍色=使用段，綠/黃/紅=餘料狀態。")
    ws.cell(row=2, column=1).font = styles["section_font"]

    headers = ["材料", "原料 #", "使用率", "餘料(mm)", "下料配置"] + ["" for _ in range(VISUAL_SLOT_COUNT - 1)] + ["用於"]
    _write_headers(ws, 4, headers)

    row = 5
    if not plans:
        ws.cell(row=row, column=1, value="無線性材料需要下料。")
        return

    for plan in plans:
        for bar_idx, bar in enumerate(plan.bars, start=1):
            used_ratio = 0 if bar.effective_length <= 0 else max(0, min(1, bar.used_length / bar.effective_length))
            used_slots = max(1, min(VISUAL_SLOT_COUNT, round(used_ratio * VISUAL_SLOT_COUNT))) if bar.pieces else 0
            remnant_fill = styles["bad_fill"] if bar.remnant < 100 else styles["warn_fill"] if bar.remnant < 300 else styles["remnant_fill"]

            ws.cell(row=row, column=1, value=f"{plan.name} {plan.spec} ({plan.material})")
            ws.cell(row=row, column=2, value=f"#{bar_idx}")
            ws.cell(row=row, column=3, value=f"{bar.utilization:.1f}%")
            ws.cell(row=row, column=4, value=round(bar.remnant, 1))

            for slot in range(VISUAL_SLOT_COUNT):
                cell = ws.cell(row=row, column=5 + slot)
                if slot < used_slots:
                    cell.fill = styles["used_fill"]
                else:
                    cell.fill = remnant_fill
                cell.border = styles["border"]

            pieces = " | ".join(f"{piece.demand_length:.0f}({piece.source})" for piece in bar.pieces)
            ws.cell(row=row, column=5 + VISUAL_SLOT_COUNT, value=pieces)
            row += 1

    from openpyxl.utils import get_column_letter
    for col in range(5, 5 + VISUAL_SLOT_COUNT):
        ws.column_dimensions[get_column_letter(col)].width = 2.2
    _set_widths(ws, [28, 10, 10, 12])
    ws.column_dimensions[get_column_letter(5 + VISUAL_SLOT_COUNT)].width = 54
    ws.freeze_panes = "A5"
