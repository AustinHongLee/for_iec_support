"""Renderer for the project summary dashboard sheet."""

from core.cutting_optimizer import CuttingPlan
from core.material_summary import MaterialSummary
from core.project_aggregation import ProjectAnalysisResult

from .styles import (
    NUMFMT,
    _add_data_bar,
    _kpi_card,
    _section_header,
    _set_widths,
    _setup_sheet,
    _styles,
    set_print_layout,
)


def _write_project_summary_sheet(ws, project: ProjectAnalysisResult, summary: MaterialSummary, plans: list[CuttingPlan]):
    """專案摘要 — 長官第一眼看的儀表板頁。

    版面：
      R1     主標題列（深靛底白字 18pt）
      R2     副標題列（製表日期 + 系統版本 + 總重）
      R3     空
      R4     ▌ 關鍵指標
      R5~R7  KPI 卡片第一列 × 4 個（支撐組數 / 材料種類 / 專案總重 / 平均單組重）
      R8     空
      R9~R11 KPI 卡片第二列 × 4 個（下料材料 / 建議原料根數 / 下料段數 / 平均使用率）
      R12    空
      R13    ▌ 重型支撐 Top 5
      R14    表頭
      R15~19 Top 5 資料 + 條形視覺
      R20    空
      R21    ▌ 材料重量分佈（Top 8 by 總重）
      R22    表頭
      R23~30 資料 + 條形視覺
      R31    空
      R32    ▌ Workbook 索引（各分頁用途）
      R33    表頭
      R34~42 各 sheet 一列
      R43    空
      R44    ▌ 注意事項
      R45~47 注意事項條列
    """
    import datetime as _dt
    from openpyxl.styles import Alignment, Font

    styles = _styles()
    ws.title = "專案摘要"

    # === R1 主標題 + R2 副標題 ====================================
    today_str = _dt.date.today().strftime("%Y-%m-%d")
    subtitle = (
        f"製表日期 {today_str}    "
        f"全案總重 {summary.total_weight:,.2f} kg    "
        f"支撐 {project.total_support_count} 組    "
        f"材料 {len(summary.lines)} 項"
    )
    _setup_sheet(ws, "專案材料統計總覽", "L1", subtitle=subtitle, freeze_title=True)

    # 欄寬：12 個欄（3 欄一組 × 4 組 KPI）
    _set_widths(ws, [16, 9, 5, 16, 9, 5, 16, 9, 5, 16, 9, 5])

    # === KPI 計算 ================================================
    total_bars = sum(plan.total_bars for plan in plans)
    total_cut_pieces = sum(plan.total_pieces for plan in plans)
    avg_util = (
        sum(plan.avg_utilization for plan in plans) / len(plans)
        if plans else 0.0
    )
    successful_rows = [r for r in project.rows if not r.single_result.error]
    avg_unit_weight = (
        sum(r.single_result.total_weight for r in successful_rows) / len(successful_rows)
        if successful_rows else 0.0
    )
    try:
        from .leader_sheets import _leader_procurement_stats
        _, _, leader_details = _leader_procurement_stats(project)
        confirm_count = sum(1 for detail in leader_details if detail.status == "需確認")
    except Exception:
        confirm_count = 0

    # === R4 區塊標題 + R5~R7 第一列 KPI ===========================
    _section_header(ws, 4, "關鍵指標", span_cols=12)

    row_kpi_1 = 5
    _kpi_card(ws, row_kpi_1, 1, "支撐總組數",
              project.total_support_count, "組",
              note="本批設計含支撐總數", accent=True, value_format=NUMFMT["QTY_INT"])
    _kpi_card(ws, row_kpi_1, 4, "材料種類",
              len(summary.lines), "項",
              note="合計表獨立材料品項", value_format=NUMFMT["QTY_INT"])
    _kpi_card(ws, row_kpi_1, 7, "專案總重",
              round(summary.total_weight, 2), "kg",
              note="全案累計總重", accent=True, value_format=NUMFMT["WEIGHT_KG"])
    _kpi_card(ws, row_kpi_1, 10, "平均單組重",
              round(avg_unit_weight, 2), "kg/組",
              note=f"成功項 {len(successful_rows)} 組之均值", value_format=NUMFMT["WEIGHT_KG"])

    # === R9~R11 第二列 KPI =======================================
    row_kpi_2 = 9
    _kpi_card(ws, row_kpi_2, 1, "下料材料",
              len(plans), "種",
              note="需切割的線性材料種類", value_format=NUMFMT["QTY_INT"])
    _kpi_card(ws, row_kpi_2, 4, "建議原料根數",
              total_bars, "根",
              note="依下料規劃所需原料數", accent=True, value_format=NUMFMT["QTY_INT"])
    _kpi_card(ws, row_kpi_2, 7, "下料段數",
              total_cut_pieces, "段",
              note="所有原料切割段累計", value_format=NUMFMT["QTY_INT"])
    _kpi_card(ws, row_kpi_2, 10, "平均使用率",
              round(avg_util, 1) / 100 if avg_util else 0, "",
              note="原料切割平均利用率", accent=True, value_format=NUMFMT["PCT"])

    # === R13~R17 品質與異常 KPI ==================================
    quality_section_row = 13
    _section_header(ws, quality_section_row, "品質與異常", span_cols=12)
    row_kpi_3 = quality_section_row + 1
    _kpi_card(ws, row_kpi_3, 1, "錯誤項目",
              len(project.errors), "項",
              note="重量分析失敗項目", value_format=NUMFMT["QTY_INT"],
              tone="bad" if project.errors else "neutral")
    _kpi_card(ws, row_kpi_3, 4, "需確認分類",
              confirm_count, "筆",
              note="支撐統計明細需確認", value_format=NUMFMT["QTY_INT"],
              tone="warn" if confirm_count else "neutral")
    _kpi_card(ws, row_kpi_3, 7, "資料健康度",
              1 if not project.errors and confirm_count == 0 else 0, "",
              note="1=無錯誤且無需確認", value_format=NUMFMT["QTY_INT"],
              accent=not project.errors and confirm_count == 0)
    ws.merge_cells(start_row=row_kpi_3 + 3, start_column=1, end_row=row_kpi_3 + 3, end_column=12)
    guide = ws.cell(row=row_kpi_3 + 3, column=1, value="→ 詳見「支撐統計明細」與「重量明細表」")
    guide.font = styles["kpi_note_font"]
    guide.alignment = Alignment(horizontal="left", vertical="center", indent=1)

    # === Top 5 重型支撐 ===================================
    top_section_row = 19
    _section_header(ws, top_section_row, "重型支撐 Top 5（依單組重）", span_cols=12)

    top5 = sorted(
        successful_rows,
        key=lambda r: r.single_result.total_weight,
        reverse=True,
    )[:5]

    top5_headers = ["排名", "型號", "組數", "單組重 (kg)", "累計重 (kg)", "佔比"]
    header_row = top_section_row + 1
    for col, h in enumerate(top5_headers, 1):
        cell = ws.cell(row=header_row, column=col, value=h)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    ws.row_dimensions[header_row].height = 24
    # 將後面欄合併為條形圖視覺欄
    ws.merge_cells(start_row=header_row, start_column=7, end_row=header_row, end_column=12)
    bar_h = ws.cell(row=header_row, column=7, value="視覺比例")
    bar_h.fill = styles["header_fill"]
    bar_h.font = styles["header_font"]
    bar_h.alignment = styles["center"]
    bar_h.border = styles["border"]

    total_proj = summary.total_weight if summary.total_weight > 0 else 1.0
    for idx, r in enumerate(top5, start=1):
        rr = header_row + idx
        unit_w = r.single_result.total_weight
        total_w = r.scaled_result.total_weight
        pct = total_w / total_proj
        values = [
            idx,
            r.input_row.designation,
            r.input_row.quantity,
            round(unit_w, 2),
            round(total_w, 2),
            pct,
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=rr, column=col, value=val)
            cell.border = styles["border"]
            cell.alignment = styles["center"] if col in (1, 2) else styles["right"]
        ws.cell(rr, 4).number_format = NUMFMT["WEIGHT_KG"]
        ws.cell(rr, 5).number_format = NUMFMT["WEIGHT_KG"]
        ws.cell(rr, 6).number_format = NUMFMT["PCT"]
        ws.row_dimensions[rr].height = 20
        # 視覺欄：用值寫入隱藏值，套 data bar
        ws.merge_cells(start_row=rr, start_column=7, end_row=rr, end_column=12)
        bcell = ws.cell(row=rr, column=7, value=round(total_w, 2))
        bcell.border = styles["border"]
        bcell.number_format = NUMFMT["WEIGHT_KG"]
        bcell.alignment = styles["right"]

    if top5:
        _add_data_bar(ws, f"G{header_row + 1}:G{header_row + len(top5)}", color="BF8F00")

    # === R21~R30 材料重量分佈 Top 8 ===============================
    mat_section_row = header_row + 7
    _section_header(ws, mat_section_row, "材料重量分佈 Top 8（依總重）", span_cols=12)

    top_mats = sorted(summary.lines, key=lambda ln: ln.total_weight, reverse=True)[:8]
    mat_headers = ["#", "品名", "規格", "材質", "總重 (kg)", "佔比"]
    mat_header_row = mat_section_row + 1
    for col, h in enumerate(mat_headers, 1):
        cell = ws.cell(row=mat_header_row, column=col, value=h)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    ws.row_dimensions[mat_header_row].height = 24
    ws.merge_cells(start_row=mat_header_row, start_column=7, end_row=mat_header_row, end_column=12)
    mb_h = ws.cell(row=mat_header_row, column=7, value="視覺比例")
    mb_h.fill = styles["header_fill"]
    mb_h.font = styles["header_font"]
    mb_h.alignment = styles["center"]
    mb_h.border = styles["border"]

    for idx, ln in enumerate(top_mats, start=1):
        rr = mat_header_row + idx
        pct = ln.total_weight / total_proj
        values = [
            idx,
            ln.name,
            ln.spec,
            ln.material,
            round(ln.total_weight, 2),
            pct,
        ]
        for col, val in enumerate(values, 1):
            cell = ws.cell(row=rr, column=col, value=val)
            cell.border = styles["border"]
            cell.alignment = styles["center"] if col in (1, 2, 3, 4) else styles["right"]
        ws.cell(rr, 5).number_format = NUMFMT["WEIGHT_KG"]
        ws.cell(rr, 6).number_format = NUMFMT["PCT"]
        ws.row_dimensions[rr].height = 20
        ws.merge_cells(start_row=rr, start_column=7, end_row=rr, end_column=12)
        bcell = ws.cell(row=rr, column=7, value=round(ln.total_weight, 2))
        bcell.border = styles["border"]
        bcell.number_format = NUMFMT["WEIGHT_KG"]
        bcell.alignment = styles["right"]

    if top_mats:
        _add_data_bar(ws, f"G{mat_header_row + 1}:G{mat_header_row + len(top_mats)}", color="4472C4")

    # === R32~R42 Workbook 索引 ====================================
    index_section_row = mat_header_row + 10
    _section_header(ws, index_section_row, "Workbook 索引（各分頁用途）", span_cols=12)

    idx_headers = ["#", "分頁名稱", "主要用途", "資料量"]
    idx_header_row = index_section_row + 1
    # 合併寬欄位
    for col, h in enumerate(idx_headers, 1):
        cell = ws.cell(row=idx_header_row, column=col, value=h)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    # 第 3 欄合併到 11、第 4 欄落 12
    ws.merge_cells(start_row=idx_header_row, start_column=3, end_row=idx_header_row, end_column=11)
    ws.cell(idx_header_row, 3).value = "主要用途"
    ws.cell(idx_header_row, 3).fill = styles["header_fill"]
    ws.cell(idx_header_row, 3).font = styles["header_font"]
    ws.cell(idx_header_row, 3).alignment = styles["center"]
    ws.cell(idx_header_row, 12).value = "資料量"
    ws.cell(idx_header_row, 12).fill = styles["header_fill"]
    ws.cell(idx_header_row, 12).font = styles["header_font"]
    ws.cell(idx_header_row, 12).alignment = styles["center"]
    ws.cell(idx_header_row, 12).border = styles["border"]
    ws.row_dimensions[idx_header_row].height = 24

    workbook_index = [
        ("專案摘要", "長官第一眼總覽：KPI、Top 5、材料分佈", "本頁"),
        ("重量明細表", "單件 × 組數 × 總重 平表（樞紐分析用）", f"{len(project.rows)} 支撐"),
        ("計算標準與假設", "材料計算所依引用標準與資料狀態圖例", "靜態說明"),
        ("支撐分類統計", "U-Bolt/Pipe Shoe/管支撐製裝採購數量彙總", "依規則"),
        ("支撐統計明細", "命中、需確認、未納入的逐筆查核表", "依規則"),
        ("重量分析", "單件與總量並列、按 entry 展開", f"{len(project.rows)} 列"),
        ("材料合計", "依材質聚合的採購清單", f"{len(summary.lines)} 項"),
        ("下料明細", "每根原料的切割順序與餘料", f"{len(plans)} 種材料"),
        ("下料圖示", "原料使用率視覺化條塊", f"{sum(p.total_bars for p in plans)} 根原料"),
    ]
    for idx, (name, purpose, count) in enumerate(workbook_index, start=1):
        rr = idx_header_row + idx
        ws.cell(rr, 1, idx).alignment = styles["center"]
        name_cell = ws.cell(rr, 2, name)
        name_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        name_cell.font = Font(name="Microsoft JhengHei", bold=True, color="1F3864", underline="single")
        name_cell.hyperlink = f"#'{name}'!A1"
        name_cell.style = "Hyperlink"
        ws.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=11)
        ws.cell(rr, 3, purpose).alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.cell(rr, 12, count).alignment = styles["center"]
        for c in (1, 2, 3, 12):
            ws.cell(rr, c).border = styles["border"]
        ws.row_dimensions[rr].height = 20
        # zebra
        if idx % 2 == 0:
            for c in (1, 2, 3, 12):
                ws.cell(rr, c).fill = styles["zebra_fill"]

    # === R44~ 注意事項 ============================================
    note_section_row = idx_header_row + len(workbook_index) + 2
    _section_header(ws, note_section_row, "注意事項", span_cols=12)
    notes = [
        "本表所有材料與重量以各 Type calculator 與 component table 計算為準。",
        "下料圖示為現場規劃輔助；實際餘料與鋸口條件仍需現場確認。",
        "若 KPI 與其他分頁加總有微小差異，係四捨五入造成；以「材料合計」分頁為基準。",
        "支撐分類統計如有未命中項，請至「支撐統計明細」查核並回饋規則維護人員。",
    ]
    for i, note in enumerate(notes):
        rr = note_section_row + 1 + i
        ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=12)
        cell = ws.cell(rr, 1, value=f"・{note}")
        cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        cell.font = Font(name="Calibri", size=10, color="595959")
        ws.row_dimensions[rr].height = 18
    set_print_layout(ws, title_rows=None, area=f"A1:L{note_section_row + len(notes)}", footer_title="專案摘要")
