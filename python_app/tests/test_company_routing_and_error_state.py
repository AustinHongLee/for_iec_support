import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from companies.registry import design_company_label
from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows
from ui.main_window import MainWindow
from ui.support_master_table import SupportMasterTable


def test_known_unimported_eko_model_is_not_mislabeled_as_iec():
    assert design_company_label("CS1G-2-30") == "益高"

    result = analyze_single("CS1G-2-30")

    assert result.error is not None
    assert "益高型號 CS1" in result.error
    assert "尚未匯入" in result.error
    assert "不會套用其他 Type 猜測" in result.error


def test_unknown_company_is_left_unresolved_instead_of_guessed():
    assert design_company_label("UNKNOWN-1") == "待判定"

    result = analyze_single("UNKNOWN-1")

    assert result.error is not None
    assert "找不到型號" in result.error
    assert "避免無依據判斷" in result.error


def test_numeric_type_remains_iec_company():
    assert design_company_label("51-1.1/2B") == "長春"


def test_error_row_has_prominent_background_and_company():
    app = QApplication.instance() or QApplication(sys.argv)
    table = SupportMasterTable()
    rows = [ProjectInputRow(designation="CS1G-2-30")]
    project_result = analyze_project_rows(rows)

    try:
        table.set_project(rows, project_result)

        assert table.item(0, 9).text() == "益高"
        assert table.item(0, 8).text().startswith("益高型號 CS1")
        assert table.item(0, 8).font().bold()
        assert table.item(0, 8).background().color().name().upper() == "#FFF0F0"
        assert table.rowHeight(0) == 32
    finally:
        table.close()


def test_main_window_shows_error_banner_and_error_status():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    try:
        window._add_item_to_list("CS1G-2-30")
        window._on_analyze()
        app.processEvents()

        assert window.analysis_error_banner.isVisibleTo(window)
        assert "分析未完成：1 筆無法計算" in window.analysis_error_banner_label.text()
        assert "分析未完成：1 筆錯誤" in window.statusBar().currentMessage()

        window.analysis_error_banner_btn.click()
        app.processEvents()
        assert window.result_column_filters["status"].currentData() == "✗"
    finally:
        window.close()
