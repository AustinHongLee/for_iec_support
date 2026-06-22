import os
import tempfile

import openpyxl

from core.project_aggregation import ProjectInputRow, analyze_project_rows
from export.excel.headers import LEADER_DETAIL_HEADERS, PROJECT_HEADERS, _CALC_BASIS_HEADERS
from export.excel_export import export_project_to_excel, export_project_workbook


def _header_map(ws, row: int) -> dict[str, int]:
    values = [ws.cell(row=row, column=col).value for col in range(1, ws.max_column + 1)]
    return {header: index + 1 for index, header in enumerate(values) if header}


def _exported_workbook(project, exporter):
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    try:
        exporter(project, path)
        return openpyxl.load_workbook(path, data_only=True)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _sample_project():
    return analyze_project_rows(
        [
            ProjectInputRow(
                "51-1.1/2B",
                10,
                drawing_line_number="DL-001",
                serial="S-001",
            )
        ]
    )


def test_flat_project_export_headers_align_with_values():
    wb = _exported_workbook(_sample_project(), export_project_to_excel)
    ws = wb["Project_Weight_Analysis"]

    assert [ws.cell(row=1, column=col).value for col in range(1, len(PROJECT_HEADERS) + 1)] == PROJECT_HEADERS
    columns = _header_map(ws, 1)
    assert ws.cell(row=2, column=columns["型號"]).value == "51-1.1/2B"
    assert ws.cell(row=2, column=columns["來源圖號"]).value == "DL-001"
    assert ws.cell(row=2, column=columns["流水號"]).value == "S-001"
    assert ws.cell(row=2, column=columns["輸入數量"]).value == 10
    assert ws.cell(row=2, column=columns["輸入單位"]).value == "組"


def test_workbook_project_weight_headers_align_with_values():
    wb = _exported_workbook(_sample_project(), export_project_workbook)
    ws = wb["重量分析"]

    assert [ws.cell(row=3, column=col).value for col in range(1, len(PROJECT_HEADERS) + 1)] == PROJECT_HEADERS
    columns = _header_map(ws, 3)
    assert ws.cell(row=4, column=columns["型號"]).value == "51-1.1/2B"
    assert ws.cell(row=4, column=columns["來源圖號"]).value == "DL-001"
    assert ws.cell(row=4, column=columns["流水號"]).value == "S-001"
    assert ws.cell(row=4, column=columns["輸入數量"]).value == 10
    assert ws.cell(row=4, column=columns["輸入單位"]).value == "組"


def test_calculation_basis_headers_align_with_subtotal_trace_values():
    wb = _exported_workbook(_sample_project(), export_project_workbook)
    ws = wb["重量明細表"]

    assert [ws.cell(row=3, column=col).value for col in range(1, len(_CALC_BASIS_HEADERS) + 1)] == _CALC_BASIS_HEADERS
    columns = _header_map(ws, 3)
    subtotal_row = next(
        row for row in range(4, ws.max_row + 1)
        if ws.cell(row=row, column=columns["列型"]).value == "小計"
    )
    assert ws.cell(row=subtotal_row, column=columns["型號"]).value == "小計 51-1.1/2B"
    assert ws.cell(row=subtotal_row, column=columns["來源圖號"]).value == "DL-001"
    assert ws.cell(row=subtotal_row, column=columns["流水號"]).value == "S-001"
    assert ws.cell(row=subtotal_row, column=columns["輸入數量"]).value == 10
    assert ws.cell(row=subtotal_row, column=columns["輸入單位"]).value == "組"


def test_leader_detail_headers_align_with_trace_values():
    wb = _exported_workbook(_sample_project(), export_project_workbook)
    ws = wb["查核-支撐明細"]

    assert [ws.cell(row=3, column=col).value for col in range(1, len(LEADER_DETAIL_HEADERS) + 1)] == LEADER_DETAIL_HEADERS
    columns = _header_map(ws, 3)
    detail_row = next(
        row for row in range(4, ws.max_row + 1)
        if ws.cell(row=row, column=columns["型號"]).value == "51-1.1/2B"
    )
    assert ws.cell(row=detail_row, column=columns["來源圖號"]).value == "DL-001"
    assert ws.cell(row=detail_row, column=columns["流水號"]).value == "S-001"
    assert ws.cell(row=detail_row, column=columns["數量"]).value == 10
    assert ws.cell(row=detail_row, column=columns["單位"]).value == "組"
