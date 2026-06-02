"""Renderers for project weight detail sheets."""

from core.parser import get_type_code
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
    from openpyxl.utils import get_column_letter

    styles = _styles()
    last_col_letter = get_column_letter(len(PROJECT_HEADERS))
    _setup_sheet(
        ws,
        "重量分析明細",
        f"{last_col_letter}1",
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
            values = [
                input_row.serial,
                input_row.quantity,
                input_row.unit or "組",
                input_row.designation,
                get_type_code(input_row.designation),
                "錯誤",
                single_result.error,
            ] + [""] * (len(PROJECT_HEADERS) - 7)
            for col, value in enumerate(values, 1):
                ws.cell(row=row, column=col, value=value)
            error_rows.append(row)
            row += 1
            continue

        for single_entry, scaled_entry in zip(single_result.entries, scaled_result.entries):
            values = [
                input_row.serial,
                input_row.quantity,
                input_row.unit or "組",
                input_row.designation,                                  # 型號 - 每列填滿
                get_type_code(input_row.designation),
                single_entry.item_no,
                single_entry.name,
                single_entry.display_spec,
                single_entry.material,
                single_entry.length,
                single_entry.width if single_entry.width else "",
                single_entry.quantity,                                   # 單件數量
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
            2: NUMFMT["QTY_INT"],
            10: NUMFMT["LEN_MM"],
            11: NUMFMT["LEN_MM"],
            12: NUMFMT["QTY_INT"],
            13: NUMFMT["QTY_INT"],
            14: NUMFMT["WEIGHT_KG"],
            15: NUMFMT["WEIGHT_KG"],
        },
        widths=[12, 8, 7, 20, 8, 7, 16, 22, 14, 12, 12, 10, 10, 14, 14, 10, 14, 14, 28, 12, 34],
    )
    for error_row in error_rows:
        for col in range(1, len(PROJECT_HEADERS) + 1):
            cell = ws.cell(row=error_row, column=col)
            cell.fill = styles["bad_fill"]
            cell.border = styles["border"]
        apply_status_fill(ws.cell(row=error_row, column=6), "錯誤", set_font=True)
    if last_row >= 4:
        add_color_scale(ws, f"O4:O{last_row}", "weight")
    set_print_layout(ws, title_rows="3:3", area=f"A1:{last_col_letter}{last_row}", footer_title="重量分析")
