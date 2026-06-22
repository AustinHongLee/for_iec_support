"""Minimal manager-facing cover sheet for project workbook exports."""

from core.material_summary import MaterialSummary
from core.parser import get_type_code
from core.project_aggregation import ProjectAnalysisResult

from .confidence_summary import (
    format_confidence_counts,
    project_confidence_counts,
    review_required_count,
    worst_confidence_level,
)
from .leader_sheets import _boss_summary_rows, _leader_procurement_stats
from .navigation import workbook_navigation
from .styles import (
    COLORS,
    FONT_CJK,
    NUMFMT,
    apply_confidence_fill,
    _set_widths,
    _setup_sheet,
    _styles,
    set_print_layout,
)


def _project_type_count(project: ProjectAnalysisResult) -> int:
    types = {
        get_type_code(row_result.input_row.designation) or "未解析"
        for row_result in project.rows
    }
    return len(types)


def _cover_support_rows(stats: dict[str, float], details: list) -> list[dict]:
    boss_rows = _boss_summary_rows(stats)

    def sum_groups(*groups: str) -> float:
        return sum(float(row["qty"] or 0) for row in boss_rows if row["group"] in groups)

    def qty(key: str) -> float:
        return float(stats.get(key, 0.0))

    rows = [
        {
            "item": "管支撐製裝 <=15Kg",
            "qty": qty("cs_support_le15"),
            "unit": "組",
            "where": "長官-支撐分類",
            "note": "合約項目第 5 類",
        },
        {
            "item": "管支撐製裝 >15Kg",
            "qty": qty("cs_support_gt15"),
            "unit": "KG",
            "where": "長官-支撐分類",
            "note": "合約項目第 5 類",
        },
        {
            "item": "U-Bolt & Band",
            "qty": sum_groups("2"),
            "unit": "組",
            "where": "長官-支撐分類",
            "note": "依管徑與材質分段",
        },
        {
            "item": "Pipe Shoe / 保冷支撐座",
            "qty": sum_groups("3", "4"),
            "unit": "組",
            "where": "長官-支撐分類",
            "note": "依管徑與材質分段",
        },
    ]
    confirm_count = sum(1 for detail in details if detail.status == "需確認")
    unmatched_count = sum(1 for detail in details if detail.status == "未納入")
    if confirm_count:
        rows.append(
            {
                "item": "需人工確認分類",
                "qty": confirm_count,
                "unit": "筆",
                "where": "查核-支撐明細",
                "note": "需確認是否新增分類規則",
            }
        )
    if unmatched_count:
        rows.append(
            {
                "item": "未納入分類",
                "qty": unmatched_count,
                "unit": "筆",
                "where": "查核-支撐明細",
                "note": "目前不列入長官摘要統計",
            }
        )
    return [row for row in rows if row["qty"] or row["item"].startswith("管支撐製裝")]


def _write_link_cell(ws, row: int, column: int, sheet_name: str, label: str | None = None) -> None:
    cell = ws.cell(row=row, column=column, value=label or sheet_name)
    cell.hyperlink = f"#'{sheet_name}'!A1"
    cell.style = "Hyperlink"


def _write_manager_cover_sheet(ws, project: ProjectAnalysisResult, summary: MaterialSummary) -> None:
    """長官摘要 - one-page reading path and high-level support quantities."""
    import datetime as _dt
    from openpyxl.styles import Alignment, Font, PatternFill

    styles = _styles()
    stats, _, details = _leader_procurement_stats(project)
    type_count = _project_type_count(project)
    cover_rows = _cover_support_rows(stats, details)
    confidence_counts = project_confidence_counts(project)
    worst_confidence = worst_confidence_level(confidence_counts)
    cover_rows.append(
        {
            "item": "資料可信度",
            "qty": review_required_count(project),
            "unit": "列",
            "where": "計算標準與假設",
            "note": f"最低 {worst_confidence}；{format_confidence_counts(confidence_counts)}",
            "confidence_level": worst_confidence,
        }
    )

    ws.title = "長官-摘要"
    subtitle = (
        f"製表日期 {_dt.date.today():%Y-%m-%d}    "
        f"支撐 {project.total_support_count:,} 組    "
        f"使用 Type {type_count:,} 種    "
        f"全案總重 {summary.total_weight:,.2f} kg"
    )
    _setup_sheet(ws, "長官摘要", "H1", subtitle=subtitle, audience="主管 / 業主", freeze_title=False)
    _set_widths(ws, [22, 14, 10, 18, 22, 22, 14, 14])
    ws.sheet_view.zoomScale = 105

    ws.merge_cells("A4:H4")
    intro = ws["A4"]
    intro.value = "本頁只放快速結論；合約項目分段請看「長官-支撐分類」，型號與判定依據請看「查核-支撐明細」。"
    intro.font = Font(name=FONT_CJK, size=11, color=COLORS["ink"])
    intro.fill = styles["subtitle_fill"]
    intro.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[4].height = 28

    header_row = 6
    headers = ["項目", "數量", "單位", "詳細位置", "備註"]
    for col in range(1, 9):
        cell = ws.cell(row=header_row, column=col)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    for col, header in enumerate(headers, start=1):
        ws.cell(row=header_row, column=col, value=header)
    ws.merge_cells(start_row=header_row, start_column=5, end_row=header_row, end_column=8)
    ws.row_dimensions[header_row].height = 24

    row = header_row + 1
    for item in cover_rows:
        ws.cell(row=row, column=1, value=item["item"])
        ws.cell(row=row, column=2, value=round(item["qty"], 2) if item["unit"] == "KG" else int(item["qty"]))
        ws.cell(row=row, column=3, value=item["unit"])
        _write_link_cell(ws, row, 4, item["where"])
        ws.merge_cells(start_row=row, start_column=5, end_row=row, end_column=8)
        ws.cell(row=row, column=5, value=item["note"])
        for col in range(1, 9):
            cell = ws.cell(row=row, column=col)
            cell.border = styles["border"]
            cell.font = Font(name=FONT_CJK, size=12 if col in (1, 2) else 10, color=COLORS["ink"])
            cell.alignment = Alignment(
                horizontal="right" if col == 2 else "center" if col in (3, 4) else "left",
                vertical="center",
                wrap_text=True,
                indent=1 if col in (1, 5) else 0,
            )
        ws.cell(row=row, column=4).font = Font(name=FONT_CJK, size=10, color="0563C1", underline="single")
        ws.cell(row=row, column=2).font = Font(name="Calibri", bold=True, size=16, color=COLORS["accent"])
        ws.cell(row=row, column=2).number_format = NUMFMT["WEIGHT_KG"] if item["unit"] == "KG" else NUMFMT["QTY_INT"]
        if item.get("confidence_level"):
            apply_confidence_fill(ws.cell(row=row, column=5), item["confidence_level"])
        if (row - header_row) % 2 == 0:
            for col in range(1, 9):
                if not (item.get("confidence_level") and col == 5):
                    ws.cell(row=row, column=col).fill = styles["zebra_fill"]
        ws.row_dimensions[row].height = 30
        row += 1

    row += 2
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    guide = ws.cell(row=row, column=1, value="分頁索引")
    guide.font = styles["section_font"]
    guide.fill = styles["section_fill"]
    guide.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[row].height = 24
    row += 1

    for col in range(1, 9):
        cell = ws.cell(row=row, column=col)
        cell.fill = styles["header_fill"]
        cell.font = styles["header_font"]
        cell.alignment = styles["center"]
        cell.border = styles["border"]
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
    ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
    ws.merge_cells(start_row=row, start_column=7, end_row=row, end_column=8)
    ws.cell(row=row, column=1, value="分頁")
    ws.cell(row=row, column=3, value="適合查看")
    ws.cell(row=row, column=7, value="角色 / 列印")
    ws.row_dimensions[row].height = 22
    row += 1

    for nav_item in workbook_navigation():
        for col in range(1, 9):
            cell = ws.cell(row=row, column=col)
            cell.border = styles["border"]
            cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
            if (row - header_row) % 2 == 0:
                cell.fill = styles["zebra_fill"]
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=2)
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=6)
        ws.merge_cells(start_row=row, start_column=7, end_row=row, end_column=8)
        _write_link_cell(ws, row, 1, nav_item.sheet)
        ws.cell(row=row, column=3, value=nav_item.purpose)
        ws.cell(row=row, column=7, value=f"{nav_item.audience} / {nav_item.print_note}")
        ws.cell(row=row, column=1).font = Font(name=FONT_CJK, size=10, color="0563C1", underline="single")
        ws.cell(row=row, column=3).font = Font(name=FONT_CJK, size=9, color=COLORS["text_mute"])
        ws.cell(row=row, column=7).font = Font(name=FONT_CJK, size=9, color=COLORS["text_mute"])
        ws.row_dimensions[row].height = 28
        row += 1

    row += 2
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=8)
    note = ws.cell(row=row, column=1, value="註：長官摘要不列型號來源；若數字需要追溯，請直接進入查核分頁。")
    note.font = Font(name=FONT_CJK, size=10, italic=True, color=COLORS["text_mute"])
    note.fill = PatternFill("solid", fgColor="FFFFFF")
    note.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[row].height = 24

    set_print_layout(ws, orientation="portrait", title_rows=None, area=f"A1:H{row}", footer_title="長官摘要")
