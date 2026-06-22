import openpyxl

from core.project_aggregation import ProjectInputRow, analyze_project_rows
from export.excel_export import (
    FULL_WORKBOOK_SHEETS,
    WORKBOOK_PACKAGE_PROFILES,
    export_project_workbook_package,
)


def _sample_project():
    return analyze_project_rows(
        [
            ProjectInputRow("51-1.1/2B", 10, drawing_line_number="DL-001", serial="S-001"),
            ProjectInputRow("54-10B-A-150-250", 3, drawing_line_number="DL-002", serial="S-002"),
        ]
    )


def _internal_link_sheet(target: str) -> str | None:
    if not target.startswith("#'") or "'!" not in target:
        return None
    return target[2:].split("'!", 1)[0]


def test_project_workbook_package_exports_role_focused_files(tmp_path):
    exported = export_project_workbook_package(_sample_project(), tmp_path)

    assert tuple(exported) == tuple(WORKBOOK_PACKAGE_PROFILES)
    assert set(path.name for path in exported.values()) == {
        "完整活頁簿.xlsx",
        "長官業主包.xlsx",
        "工程明細包.xlsx",
        "採購材料包.xlsx",
        "下料製造包.xlsx",
    }

    for label, expected_sheets in WORKBOOK_PACKAGE_PROFILES.items():
        path = exported[label]
        assert path.exists(), label
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        try:
            assert tuple(wb.sheetnames) == expected_sheets
        finally:
            wb.close()


def test_complete_workbook_package_keeps_full_sheet_order(tmp_path):
    exported = export_project_workbook_package(_sample_project(), tmp_path)
    wb = openpyxl.load_workbook(exported["完整活頁簿"], read_only=True, data_only=True)
    try:
        assert tuple(wb.sheetnames) == FULL_WORKBOOK_SHEETS
    finally:
        wb.close()


def test_package_internal_links_only_target_included_sheets(tmp_path):
    exported = export_project_workbook_package(_sample_project(), tmp_path)

    for label, path in exported.items():
        wb = openpyxl.load_workbook(path, data_only=True)
        try:
            sheet_names = set(wb.sheetnames)
            for ws in wb.worksheets:
                for row in ws.iter_rows():
                    for cell in row:
                        if not cell.hyperlink:
                            continue
                        sheet = _internal_link_sheet(cell.hyperlink.target)
                        if sheet:
                            assert sheet in sheet_names, f"{label}: {ws.title}!{cell.coordinate} -> {sheet}"
        finally:
            wb.close()
