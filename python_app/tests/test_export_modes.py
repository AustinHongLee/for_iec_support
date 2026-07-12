import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.project_aggregation import ProjectInputRow, analyze_project_rows
from export.excel.confidence_summary import (
    build_export_context,
    final_export_allowed,
    project_assumption_rows,
)
from export.excel.workbook import build_project_workbook
from ui.main_window import MainWindow


_APP = QApplication.instance() or QApplication(sys.argv)


def _project_with_unknown_material():
    return analyze_project_rows(
        [
            ProjectInputRow(
                "01-2B-05A",
                overrides={"upper_material_unknown": True},
            )
        ]
    )


def test_export_context_enforces_final_exception_reason():
    project = _project_with_unknown_material()
    assumptions = project_assumption_rows(project)
    assert assumptions == [
        {
            "designation": "01-2B-05A",
            "field": "upper_material",
            "value": "SUS304",
            "note": "材質未確認,以預設值概算",
        }
    ]

    estimate = build_export_context(project, mode="概算")
    blocked_final = build_export_context(project, mode="精算")
    allowed_final = build_export_context(
        project,
        mode="精算",
        exception_reason="業主要求先行估價，待圖面回覆後補正",
    )

    assert estimate["assumption_count"] == 1
    assert final_export_allowed(estimate)
    assert not final_export_allowed(blocked_final)
    assert final_export_allowed(allowed_final)


def test_estimate_workbook_has_cover_warning_and_assumption_summary():
    project = _project_with_unknown_material()
    context = build_export_context(project, mode="概算")
    workbook = build_project_workbook(project, export_context=context)

    assert workbook["長官-摘要"]["A5"].value == "概算版：含 1 筆假設值，不得作為發包依據"
    values = [
        cell.value
        for row in workbook["計算標準與假設"].iter_rows()
        for cell in row
    ]
    assert "本次匯出假設值彙總" in " ".join(str(value) for value in values if value)
    assert "upper_material" in values
    assert "SUS304" in values


def test_project_mode_selector_is_enabled_and_defaults_to_estimate():
    window = MainWindow()
    try:
        assert window.project_header.mode_combo.isEnabled()
        assert window.project_header.mode_combo.currentText() == "概算"
    finally:
        window.close()
