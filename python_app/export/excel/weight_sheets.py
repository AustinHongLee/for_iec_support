"""Renderers for project weight detail sheets."""

from core.project_aggregation import ProjectAnalysisResult

from .headers import PROJECT_HEADERS
from .styles import (
    NUMFMT,
    add_color_scale,
    apply_report_table,
    apply_status_fill,
    set_print_layout,
    _setup_sheet,
    _styles,
)


def _write_project_weight_sheet(ws, project: ProjectAnalysisResult):
    styles = _styles()
    _setup_sheet(
        ws,
        "重量分析明細",
        "R1",
        subtitle=(
            f"工程審查明細    支撐 {project.total_support_count} 組    "
            f"型號列 {len(project.rows)}    全案總重 {project.total_weight:,.2f} kg"
        ),
        audience="工程 / 審查",
    )
    error_rows: list[int] = []

    row = 4
    for row_result in project.rows:
        input_row = row_result.input_row
        single_result = row_result.single_result
        scaled_result = row_result.scaled_result

        if single_result.error:
            ws.cell(row=row, column=1, value=input_row.designation)
            ws.cell(row=row, column=2, value="Error")
            ws.cell(row=row, column=3, value=single_result.error)
            ws.cell(row=row, column=9, value=input_row.quantity)
            error_rows.append(row)
            row += 1
            continue

        for single_entry, scaled_entry in zip(single_result.entries, scaled_result.entries):
            values = [
                input_row.designation,                                  # 型號 - 每列填滿
                single_entry.item_no,
                single_entry.name,
                single_entry.display_spec,
                single_entry.material,
                single_entry.length,
                single_entry.width if single_entry.width else "",
                single_entry.quantity,                                   # 單件數量
                input_row.quantity,                                      # 組數
                scaled_entry.quantity,                                  # 總數量
                single_entry.weight_output,                             # 單組重(kg)
                scaled_entry.weight_output,                             # 總重(kg)
                single_entry.category,
                single_entry.item_class,
                single_entry.manufacturing_type,
                single_entry.part_key,
                single_entry.stock_id,
                single_entry.display_remark,
            ]
            for col, value in enumerate(values, 1):
                ws.cell(row=row, column=col, value=value)
            row += 1

    last_row = max(row - 1, 3)
    apply_report_table(
        ws,
        3,
        PROJECT_HEADERS,
        4,
        last_row,
        col_formats={
            6: NUMFMT["LEN_MM"],
            7: NUMFMT["LEN_MM"],
            8: NUMFMT["QTY_INT"],
            9: NUMFMT["QTY_INT"],
            10: NUMFMT["QTY_INT"],
            11: NUMFMT["WEIGHT_KG"],
            12: NUMFMT["WEIGHT_KG"],
        },
        widths=[20, 8, 16, 22, 14, 12, 12, 10, 8, 10, 14, 14, 10, 14, 14, 28, 12, 34],
    )
    for error_row in error_rows:
        for col in range(1, len(PROJECT_HEADERS) + 1):
            cell = ws.cell(row=error_row, column=col)
            cell.fill = styles["bad_fill"]
            cell.border = styles["border"]
        apply_status_fill(ws.cell(row=error_row, column=2), "錯誤", set_font=True)
    if last_row >= 4:
        add_color_scale(ws, f"L4:L{last_row}", "weight")
    set_print_layout(ws, title_rows="3:3", area=f"A1:R{last_row}", footer_title="重量分析")
