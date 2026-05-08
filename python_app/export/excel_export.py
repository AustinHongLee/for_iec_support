"""
Excel 匯出模組
"""
from dataclasses import dataclass
from typing import List
from core.models import AnalysisResult
from core.project_aggregation import ProjectAnalysisResult
from core.material_summary import aggregate_project, MaterialSummary
from core.cutting_optimizer import CuttingPlan, optimize_from_summary
from core.parser import get_lookup_value, get_part

# 表頭定義 (對應 VBA 的 headers)
HEADERS = [
    "材料描述欄", "項次", "品名", "尺寸/規格", "長度", "寬度",
    "材質", "數量", "每米重", "單重", "總重小計", "單位",
    "係數", "長度小計", "數量小計", "總重合計", "屬性", "備註"
]

PROJECT_HEADERS = [
    "型號", "組數", "項次", "品名", "規格", "材質",
    "長度(mm)", "寬度(mm)",
    "單件數量", "單件重量(kg)", "總數量", "總重量(kg)", "屬性", "備註",
]

SUMMARY_HEADERS = [
    "品名", "規格", "材質", "屬性", "需求總長(mm)", "需求件數/數量",
    "總重(kg)", "原料長度(mm)", "建議採購量", "單位", "來源編碼",
]

CUTTING_HEADERS = [
    "材料", "原料 #", "切割段", "需求長(mm)", "含損耗(mm)",
    "累計(mm)", "餘料(mm)", "使用率", "用於",
]

LEADER_STAT_HEADERS = ["項目", "工事內容", "單位", "數量"]

VISUAL_SLOT_COUNT = 30


@dataclass(frozen=True)
class LeaderStatRow:
    item: str
    label: str
    unit: str
    key: str


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
    """匯出 project-aware 分析結果（平坦表格，每列填滿型號/組數）。"""
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
            ws.cell(row=row, column=1, value=input_row.designation)   # 每列填滿
            ws.cell(row=row, column=2, value=input_row.quantity)       # 每列填滿
            ws.cell(row=row, column=3, value=single_entry.item_no)
            ws.cell(row=row, column=4, value=single_entry.name)
            ws.cell(row=row, column=5, value=single_entry.spec)
            ws.cell(row=row, column=6, value=single_entry.material)
            ws.cell(row=row, column=7, value=single_entry.length)
            ws.cell(row=row, column=8, value=single_entry.width if single_entry.width else "")
            ws.cell(row=row, column=9, value=single_entry.quantity)
            ws.cell(row=row, column=10, value=single_entry.weight_output)
            ws.cell(row=row, column=11, value=scaled_entry.quantity)
            ws.cell(row=row, column=12, value=scaled_entry.weight_output)
            ws.cell(row=row, column=13, value=single_entry.category)
            ws.cell(row=row, column=14, value=single_entry.display_remark)
            row += 1

    _format_sheet(ws, PROJECT_HEADERS)

    wb.save(filepath)


def export_project_workbook(project: ProjectAnalysisResult, filepath: str):
    """
    匯出專案級整合 workbook。

    Sheets:
      1. 專案摘要
      2. 計算依據  (Flat pivot-friendly table)
      3. 計算說明  (Static manager/client reference page)
      4. 長官統計
      5. 重量分析
      6. 材料合計
      7. 下料明細
      8. 下料圖示
    """
    import openpyxl

    summary = aggregate_project(project)
    cutting_plans = _build_cutting_plans(summary)

    wb = openpyxl.Workbook()
    _write_project_summary_sheet(wb.active, project, summary, cutting_plans)
    _write_calculation_basis_sheet(wb.create_sheet("計算依據"), project)
    _write_calc_reference_sheet(wb.create_sheet("計算說明"), project)
    _write_leader_procurement_sheet(wb.create_sheet("長官統計"), project)
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
    ws.cell(row=12, column=1, value="長官統計：急件採購/製裝數量彙總")
    ws.cell(row=13, column=1, value="材料合計：採購清單與來源追蹤")
    ws.cell(row=14, column=1, value="下料明細：每根原料的切割順序")
    ws.cell(row=15, column=1, value="下料圖示：以比例色塊顯示每根原料使用狀態")
    ws.cell(row=16, column=1, value="注意事項").font = styles["section_font"]
    ws.cell(row=17, column=1, value="材料與重量仍以各 Type calculator 與 component table 為準。")
    ws.cell(row=18, column=1, value="下料圖示為規劃輔助；現場仍需依實際餘料與鋸口條件確認。")

    _set_widths(ws, [18, 10, 8, 18, 10, 8, 18, 10])
    for row_idx in range(3, 8):
        for col_idx in range(1, 9):
            ws.cell(row_idx, col_idx).border = styles["border"]


def _leader_stat_template() -> list[LeaderStatRow]:
    return [
        LeaderStatRow("1", 'U-Bolt & Band  <= 6" 熱浸鍍鋅', "組", "uband_hdg_le6"),
        LeaderStatRow("1", 'U-Bolt & Band  >= 8" 熱浸鍍鋅', "組", "uband_hdg_ge8"),
        LeaderStatRow("1", 'U-Bolt & Band  <= 6" (SUS 304)', "組", "uband_304_le6"),
        LeaderStatRow("1", 'U-Bolt & Band  >= 8" (SUS 304)', "組", "uband_304_ge8"),
        LeaderStatRow("2", '管鞋(PIPE SHOE) <=4" 熱浸鍍鋅', "組", "shoe_hdg_le4"),
        LeaderStatRow("2", '管鞋(PIPE SHOE) 5"~10" 熱浸鍍鋅', "組", "shoe_hdg_5_10"),
        LeaderStatRow("2", '管鞋(PIPE SHOE) 12"~24" 熱浸鍍鋅', "組", "shoe_hdg_12_24"),
        LeaderStatRow("2", '管鞋(PIPE SHOE) >=26" 熱浸鍍鋅', "組", "shoe_hdg_ge26"),
        LeaderStatRow("2", "保冷支撐座(長春帶料)", "組", "cold_support"),
        LeaderStatRow("3", '管鞋(PIPE SHOE) <=4" (SUS 304)', "組", "shoe_304_le4"),
        LeaderStatRow("3", '管鞋(PIPE SHOE) 5"~10" (SUS 304)', "組", "shoe_304_5_10"),
        LeaderStatRow("3", '管鞋(PIPE SHOE) 12"~24" (SUS 304)', "組", "shoe_304_12_24"),
        LeaderStatRow("4", "CS(熱鍍鋅)管支撐(Pipe Support)製裝 <=15kg", "組", "cs_support_le15"),
        LeaderStatRow("4", "CS(熱鍍鋅)管支撐(Pipe Support)製裝 >15kg", "KG", "cs_support_gt15"),
    ]


def _parse_designation_type(designation: str) -> str:
    return (get_part(designation, 1) or "").strip()


def _parse_designation_pipe_size(designation: str) -> float | None:
    token = (get_part(designation, 2) or "").strip()
    if not token:
        return None
    token = token.split("(")[0].replace('"', "").strip()
    if token.upper().endswith("B"):
        token = token[:-1]
    try:
        return float(get_lookup_value(token))
    except (TypeError, ValueError):
        return None


def _is_304_material(material: str) -> bool:
    return "304" in str(material or "").upper().replace(" ", "")


def _is_ubolt_or_band_entry(name: str) -> bool:
    upper = str(name or "").upper().replace(" ", "")
    return "U-BOLT" in upper or "UBOLT" in upper or "U-BAND" in upper or "UBAND" in upper


def _support_has_304_material(row_result) -> bool:
    return any(_is_304_material(entry.material) for entry in row_result.scaled_result.entries)


def _is_cold_support_type(type_id: str) -> bool:
    return type_id.endswith("C") and type_id[:-1].isdigit()


def _leader_size_bucket(size: float | None, buckets: tuple[tuple[str, float, float], ...]) -> str | None:
    if size is None:
        return None
    for key, lower, upper in buckets:
        if lower <= size <= upper:
            return key
    return None


def _leader_procurement_stats(project: ProjectAnalysisResult) -> dict[str, float]:
    stats = {row.key: 0.0 for row in _leader_stat_template()}
    pipe_shoe_types = {"52", "53", "54", "55", "66", "67", "80", "85"}

    for row_result in project.rows:
        if row_result.single_result.error:
            continue

        designation = row_result.input_row.designation
        project_qty = row_result.input_row.quantity
        type_id = _parse_designation_type(designation)
        pipe_size = _parse_designation_pipe_size(designation)

        for entry in row_result.scaled_result.entries:
            if not _is_ubolt_or_band_entry(entry.name):
                continue
            material_key = "304" if _is_304_material(entry.material) else "hdg"
            bucket = _leader_size_bucket(pipe_size, (
                ("le6", 0.0, 6.0),
                ("ge8", 8.0, 999.0),
            ))
            if bucket:
                stats[f"uband_{material_key}_{bucket}"] += entry.quantity

        if type_id in pipe_shoe_types:
            material_key = "304" if _support_has_304_material(row_result) else "hdg"
            bucket = _leader_size_bucket(pipe_size, (
                ("le4", 0.0, 4.0),
                ("5_10", 5.0, 10.0),
                ("12_24", 12.0, 24.0),
                ("ge26", 26.0, 999.0),
            ))
            if bucket and f"shoe_{material_key}_{bucket}" in stats:
                stats[f"shoe_{material_key}_{bucket}"] += project_qty

        if _is_cold_support_type(type_id):
            stats["cold_support"] += project_qty

        if not _support_has_304_material(row_result):
            single_weight = row_result.single_result.total_weight
            scaled_weight = row_result.scaled_result.total_weight
            if single_weight <= 15:
                stats["cs_support_le15"] += project_qty
            else:
                stats["cs_support_gt15"] += scaled_weight

    return stats


def _write_leader_procurement_sheet(ws, project: ProjectAnalysisResult):
    styles = _styles()
    rows = _leader_stat_template()
    stats = _leader_procurement_stats(project)

    _setup_sheet(ws, "長官急件統計", "D1")
    ws.cell(row=2, column=1, value="材質統計規則：除明細材質含 304 者歸 SUS304，其餘視為熱浸鍍鋅。")
    ws.cell(row=2, column=1).font = styles["section_font"]
    ws.merge_cells("A2:D2")
    _write_headers(ws, 3, LEADER_STAT_HEADERS)

    start_row = 4
    for offset, stat_row in enumerate(rows):
        row = start_row + offset
        value = stats.get(stat_row.key, 0.0)
        if stat_row.unit == "組":
            value = int(value)
        else:
            value = round(value, 2)
        values = [stat_row.item, stat_row.label, stat_row.unit, value]
        for col, cell_value in enumerate(values, 1):
            ws.cell(row=row, column=col, value=cell_value)

    item_start: dict[str, int] = {}
    item_end: dict[str, int] = {}
    for offset, stat_row in enumerate(rows):
        row = start_row + offset
        item_start.setdefault(stat_row.item, row)
        item_end[stat_row.item] = row
    for item, first_row in item_start.items():
        last_row = item_end[item]
        if last_row > first_row:
            ws.merge_cells(start_row=first_row, start_column=1, end_row=last_row, end_column=1)
        ws.cell(first_row, 1).alignment = styles["center"]

    last_row = start_row + len(rows) - 1
    _apply_table_style(ws, 3, last_row, len(LEADER_STAT_HEADERS))
    for row in range(start_row, last_row + 1):
        ws.cell(row=row, column=3).alignment = styles["center"]
        ws.cell(row=row, column=4).alignment = styles["right"]
        ws.cell(row=row, column=4).number_format = "0.00" if ws.cell(row=row, column=3).value == "KG" else "0"
    ws.freeze_panes = "A4"
    _set_widths(ws, [8, 44, 10, 14])


def _write_project_weight_sheet(ws, project: ProjectAnalysisResult):
    _setup_sheet(ws, "重量分析明細", "N1")
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
                input_row.designation,                                  # 型號 - 每列填滿
                input_row.quantity,                                     # 組數 - 每列填滿
                single_entry.item_no,
                single_entry.name,
                single_entry.spec,
                single_entry.material,
                single_entry.length,
                single_entry.width if single_entry.width else "",
                single_entry.quantity,                                   # 單件數量
                single_entry.weight_output,                             # 單件重量(kg)
                scaled_entry.quantity,                                  # 總數量
                scaled_entry.weight_output,                             # 總重量(kg)
                single_entry.category,
                single_entry.display_remark,
            ]
            for col, value in enumerate(values, 1):
                ws.cell(row=row, column=col, value=value)
            row += 1

    last_row = max(row - 1, 3)
    _apply_table_style(ws, 3, last_row, len(PROJECT_HEADERS))
    _format_number_columns(ws, 4, last_row, [7, 8, 10, 12], "0.00")
    ws.freeze_panes = "A4"
    ws.auto_filter.ref = f"A3:N{last_row}"
    _set_widths(ws, [20, 8, 8, 16, 22, 14, 12, 12, 10, 14, 10, 14, 10, 36])


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



# ══════════════════════════════════════════════════════════════════════
#  計算依據 Sheet  (Pivot-friendly flat table)
# ══════════════════════════════════════════════════════════════════════

_CALC_BASIS_HEADERS = [
    "型號", "組數", "可信度", "來源依據",
    "項次", "品名", "規格", "材質", "屬性",
    "單件數量", "計算式", "單件重(kg)", "單組重(kg)", "合計重(kg)",
]

_CONFIDENCE_FILL = {
    "精確": "C6EFCE",   # 綠
    "推導": "BDD7EE",   # 藍
    "估算": "FFEB9C",   # 黃
    "未知": "FFC7CE",   # 紅
}

_STANDARDS_TABLE = [
    ("管道重量",    "ASME B36.10M / JIS G3454",     "以管徑及 Schedule 查表取 kg/m，再乘以長度(m)"),
    ("不鏽鋼管道",  "ASME B36.19M / JIS G3459",     "SUS 系列管道；查表值已含不鏽鋼密度修正"),
    ("角鋼/槽鋼",   "JIS G3192 / CNS 2948",          "H 型鋼、角鋼、槽鋼查表取 kg/m，再乘以長度(m)"),
    ("鋼板",        "密度公式計算",                   "W = L × W × t(mm) × ρ ÷ 10⁶  [ρ = 7,850 kg/m³ (CS) / 7,930 kg/m³ (SUS)]"),
    ("膨脹螺栓",    "HILTI/RAWL 產品目錄",            "以管徑查標準五金組合重量（保守估算，不含埋入砂漿）"),
    ("自訂五金",    "工程判斷 / 廠商目錄",            "由計算程式依規格查表，如有疑義請參閱備註欄"),
    ("係數說明",    "factor = 1.0 (一般)",            "熱浸鍍鋅塗裝：+6%；特殊接頭：依廠商資料"),
    ("重量加總",    "單件重 × 組數 = 合計重",        "各項次合計後得本頁最右欄「合計重(kg)」"),
]


def _weight_formula_str(entry) -> str:
    """從 AnalysisEntry 欄位重建人類可讀的計算式。"""
    qty = entry.quantity
    uw = entry.unit_weight

    if entry.unit == "M" and entry.weight_per_unit and entry.weight_per_unit > 0:
        wpm = entry.weight_per_unit
        return (
            f"{qty}件 × {entry.length:.0f}mm ÷ 1,000"
            f" × {wpm:.3f} kg/m"
            f" = {uw:.3f} kg"
        )

    if entry.unit == "PC" and entry.width and entry.width > 0:
        try:
            t = float(entry.spec)
            density = 7.93 if "304" in entry.material else 7.85
            return (
                f"{qty}件 × {entry.length:.0f}×{entry.width:.0f}×{t:.0f}mm"
                f" × {density:.2f} t/m³"
                f" = {uw:.3f} kg"
            )
        except (ValueError, TypeError):
            return (
                f"{qty}件 × {entry.length:.0f}×{entry.width:.0f}mm"
                f" × t×ρ = {uw:.3f} kg"
            )

    if entry.unit in ("SET", "EA", "KG"):
        per = round(uw / qty, 3) if qty else uw
        return f"{qty} {entry.unit} @ {per:.3f} kg/{entry.unit} = {uw:.3f} kg"

    return f"{qty} × {uw:.3f} kg = {round(uw * qty, 3):.3f} kg"


def _confidence_label(meta: dict) -> str:
    return meta.get("truth_level", "未知")


def _source_label(meta: dict) -> str:
    labels = meta.get("source_labels") or meta.get("sources") or []
    return " / ".join(str(s) for s in labels[:3]) if labels else "未知來源"


def _write_calculation_basis_sheet(ws, project: ProjectAnalysisResult):
    """
    計算依據 — 純 Flat 表，每行都填所有欄位，適合樞紐分析。
    Row 1: 大標題 (合併儲存格，僅裝飾用，不在資料範圍內)
    Row 2: 空白
    Row 3: 欄位標題
    Row 4+: 資料列 (一支料件一列)
    """
    from openpyxl.styles import Font, PatternFill, Alignment

    styles = _styles()
    ws.sheet_view.showGridLines = False

    # ── 標題列 (裝飾用，不影響樞紐範圍) ──────────────────────────
    n_cols = len(_CALC_BASIS_HEADERS)
    from openpyxl.utils import get_column_letter
    last_col_letter = get_column_letter(n_cols)
    ws.merge_cells(f"A1:{last_col_letter}1")
    ws["A1"] = "重量計算依據（逐項明細）"
    ws["A1"].font = styles["title_font"]
    ws["A1"].fill = styles["title_fill"]
    ws["A1"].alignment = styles["center"]
    ws.row_dimensions[1].height = 28

    # ── 欄位標題 (row 3) ──────────────────────────────────────────
    HEADER_ROW = 3
    _write_headers(ws, HEADER_ROW, _CALC_BASIS_HEADERS)

    # ── 資料列 ────────────────────────────────────────────────────
    data_row = HEADER_ROW + 1

    for row_result in project.rows:
        inp = row_result.input_row
        single = row_result.single_result
        scaled = row_result.scaled_result

        meta = single.meta or {}
        confidence = _confidence_label(meta)
        source = _source_label(meta)
        conf_color = _CONFIDENCE_FILL.get(confidence, "FFC7CE")
        conf_fill = PatternFill("solid", fgColor=conf_color)

        if single.error:
            # 錯誤列：填入型號、組數、錯誤說明
            vals = [inp.designation, inp.quantity, "錯誤", single.error] + [""] * (n_cols - 4)
            for col, val in enumerate(vals, 1):
                cell = ws.cell(row=data_row, column=col, value=val)
                cell.fill = PatternFill("solid", fgColor="FFC7CE")
                cell.border = styles["border"]
            data_row += 1
            continue

        for s_entry, sc_entry in zip(single.entries, scaled.entries):
            formula_str = _weight_formula_str(s_entry)
            single_unit_w = round(s_entry.unit_weight, 3)
            single_group_w = round(s_entry.weight_output, 3)   # 單組重 = unit_weight × quantity(件)
            total_w = round(sc_entry.weight_output, 3)          # 合計重 = single_group_w × 組數

            vals = [
                inp.designation,          # 型號
                inp.quantity,             # 組數
                confidence,               # 可信度
                source,                   # 來源依據
                s_entry.item_no,          # 項次
                s_entry.name,             # 品名
                s_entry.spec,             # 規格
                s_entry.material,         # 材質
                getattr(s_entry, "category", ""),  # 屬性
                s_entry.quantity,         # 單件數量
                formula_str,              # 計算式
                single_unit_w,            # 單件重(kg)
                single_group_w,           # 單組重(kg)
                total_w,                  # 合計重(kg)
            ]
            for col, val in enumerate(vals, 1):
                cell = ws.cell(row=data_row, column=col, value=val)
                cell.border = styles["border"]
                cell.alignment = Alignment(
                    vertical="center",
                    wrap_text=(col == 11),  # 計算式欄 wrap
                )
                if col == 3:   # 可信度欄著色
                    cell.fill = conf_fill
            ws.row_dimensions[data_row].height = 15
            data_row += 1

    last_data_row = data_row - 1

    # ── 凍結 & 篩選 ──────────────────────────────────────────────
    ws.freeze_panes = f"A{HEADER_ROW + 1}"
    if last_data_row >= HEADER_ROW + 1:
        ws.auto_filter.ref = f"A{HEADER_ROW}:{last_col_letter}{last_data_row}"

    # ── 欄寬 ─────────────────────────────────────────────────────
    col_widths = [20, 8, 10, 18, 7, 14, 16, 14, 10, 10, 46, 13, 13, 14]
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


# ══════════════════════════════════════════════════════════════════════
#  計算說明 Sheet  (Static manager/client reference page)
# ══════════════════════════════════════════════════════════════════════

def _write_calc_reference_sheet(ws, project: ProjectAnalysisResult):
    """
    計算說明 — 給長官或客戶看的靜態說明頁。
    包含：
      · 引用標準表
      · 可信度圖例
      · 各支撐小計彙整表
      · 全案合計
    """
    from openpyxl.styles import Font, PatternFill, Alignment

    styles = _styles()
    ws.sheet_view.showGridLines = False

    row = 1

    # ── 大標題 ────────────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    ws[f"A{row}"] = "重量計算依據說明書"
    ws[f"A{row}"].font = styles["title_font"]
    ws[f"A{row}"].fill = styles["title_fill"]
    ws[f"A{row}"].alignment = styles["center"]
    ws.row_dimensions[row].height = 28
    row += 1

    # ── 計算標準對照表 ────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    sec = ws[f"A{row}"]
    sec.value = "▌ 計算標準與假設"
    sec.font = styles["section_font"]
    sec.fill = styles["section_fill"]
    sec.alignment = Alignment(horizontal="left", vertical="center")
    row += 1

    std_headers = ["計算項目", "引用標準 / 依據", "計算方式說明"]
    for col, h in enumerate(std_headers, 1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.fill = styles["subheader_fill"]
        cell.font = styles["bold_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    row += 1

    for item, standard, desc in _STANDARDS_TABLE:
        for col, val in enumerate([item, standard, desc], 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.border = styles["border"]
            cell.alignment = Alignment(vertical="center", wrap_text=(col == 3))
        ws.row_dimensions[row].height = 18
        row += 1

    row += 1  # 空一列

    # ── 可信度圖例 ────────────────────────────────────────────────
    ws.cell(row=row, column=1, value="可信度說明：").font = styles["bold_font"]
    legends = [
        ("精確 — 直接查表", "C6EFCE"),
        ("推導 — 公式計算", "BDD7EE"),
        ("估算 — 工程假設", "FFEB9C"),
        ("未知 — 需複核",   "FFC7CE"),
    ]
    for col_off, (label, color) in enumerate(legends, 2):
        cell = ws.cell(row=row, column=col_off, value=label)
        cell.fill = PatternFill("solid", fgColor=color)
        cell.border = styles["border"]
        cell.alignment = styles["center"]
    row += 2

    # ── 各支撐彙整表 ─────────────────────────────────────────────
    ws.merge_cells(f"A{row}:F{row}")
    sec2 = ws[f"A{row}"]
    sec2.value = "▌ 各支撐重量彙整"
    sec2.font = styles["section_font"]
    sec2.fill = styles["section_fill"]
    sec2.alignment = Alignment(horizontal="left", vertical="center")
    row += 1

    summ_headers = ["型號", "組數", "可信度", "單組重(kg)", "合計重(kg)", "備註"]
    for col, h in enumerate(summ_headers, 1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.fill = styles["subheader_fill"]
        cell.font = styles["bold_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    row += 1

    grand_total = 0.0

    for row_result in project.rows:
        inp = row_result.input_row
        single = row_result.single_result
        scaled = row_result.scaled_result

        meta = single.meta or {}
        confidence = _confidence_label(meta)
        conf_color = _CONFIDENCE_FILL.get(confidence, "FFC7CE")

        if single.error:
            for col, val in enumerate([inp.designation, inp.quantity, "錯誤", "", "", single.error], 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.fill = PatternFill("solid", fgColor="FFC7CE")
                cell.border = styles["border"]
        else:
            single_total = round(single.total_weight, 3)
            scaled_total = round(scaled.total_weight, 3)
            grand_total += scaled_total
            remark = ""
            vals = [inp.designation, inp.quantity, confidence, single_total, scaled_total, remark]
            for col, val in enumerate(vals, 1):
                cell = ws.cell(row=row, column=col, value=val)
                cell.border = styles["border"]
                cell.alignment = styles["center"]
                if col == 3:
                    cell.fill = PatternFill("solid", fgColor=conf_color)
        row += 1

    # ── 全案合計列 ───────────────────────────────────────────────
    grand_fill = PatternFill("solid", fgColor="1F4E78")
    grand_font = Font(bold=True, color="FFFFFF")
    for col in range(1, 7):
        cell = ws.cell(row=row, column=col)
        cell.fill = grand_fill
        cell.font = grand_font
        cell.border = styles["border"]
        cell.alignment = styles["center"]
    ws.cell(row=row, column=1, value="■ 全案合計總重")
    ws.cell(row=row, column=5, value=round(grand_total, 3))
    ws.cell(row=row, column=5).number_format = "0.000"

    # ── 欄寬 ─────────────────────────────────────────────────────
    col_widths = [22, 8, 12, 14, 14, 36]
    from openpyxl.utils import get_column_letter
    for i, w in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    # 標準表第3欄較長
    ws.column_dimensions["C"].width = max(14, ws.column_dimensions["C"].width)
