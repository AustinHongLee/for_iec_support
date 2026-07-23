import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow, SidePanel
from ui.support_master_table import MASTER_HEADERS


_APP = QApplication.instance() or QApplication(sys.argv)


def test_master_detail_keeps_full_detail_table_and_syncs_selection(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list(
            "01-2B-05A",
            quantity=2,
            drawing_line_number="DL-001",
            serial="S-001",
            overrides={"upper_material_unknown": True},
        )
        window._add_item_to_list(
            "51-1.1/2B",
            drawing_line_number="DL-002",
            serial="S-002",
            overrides={"upper_material": "SUS304"},
        )
        window._on_analyze()
        _APP.processEvents()

        assert window.result_views.currentIndex() == 0
        assert window.support_master_table.rowCount() == 2
        assert [
            window.support_master_table.horizontalHeaderItem(index).text()
            for index in range(window.support_master_table.columnCount())
        ] == MASTER_HEADERS
        assert window.support_master_table.item(0, 0).text() == "⚠"
        assert window.support_master_table.item(0, 6).text().endswith("(假設)")
        assert window.support_master_table.item(1, 0).text() == "✓"
        assert window.result_table.rowCount() > 0

        window.support_master_table.selectRow(0)
        _APP.processEvents()
        assert window.item_list.currentRow() == 0
        assert window.bom_detail_panel.table.rowCount() > 0
        assert "01-2B-05A" in window.bom_detail_panel.title_label.text()
    finally:
        window.close()


def test_result_locator_selects_support_without_hiding_other_rows(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list("01-2B-05A", drawing_line_number="DL-001")
        window._add_item_to_list("51-1.1/2B", drawing_line_number="DL-002")

        window.result_filter_input.setText("DL-002")
        _APP.processEvents()

        assert not window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)
        assert window.support_master_table.currentRow() == 1
        assert window.item_list.currentRow() == 1
        assert window.result_locator_count_label.text() == "第 1/1 筆"
        assert window.result_filter_count_label.text() == "顯示 2/2 筆"

        window.result_filter_input.setText("DL-")
        _APP.processEvents()
        assert window.support_master_table.currentRow() == 0
        assert window.result_locator_count_label.text() == "第 1/2 筆"
        window._locate_next_result()
        assert window.support_master_table.currentRow() == 1
        assert window.result_locator_count_label.text() == "第 2/2 筆"
    finally:
        window.close()


def test_disabled_rows_keep_side_panel_and_detail_filters_on_project_index(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list("01-2B-05A", enabled=False)
        window._add_item_to_list(
            "01-3B-05A",
            overrides={"upper_material_unknown": True},
        )
        window._add_item_to_list(
            "01-4B-05A",
            overrides={"upper_material": "SUS304"},
        )
        window.item_list.setCurrentRow(1)
        window._on_analyze()
        _APP.processEvents()

        assert window.side_panel._current_result.fullstring == "01-3B-05A"

        status_filter = window.result_column_filters["status"]
        status_filter.setCurrentIndex(status_filter.findData("⚠"))
        _APP.processEvents()
        visible_text = " ".join(
            window._result_row_text(row)
            for row in range(window.result_table.rowCount())
            if not window.result_table.isRowHidden(row)
        )
        assert "01-3b-05a" in visible_text
        assert "01-4b-05a" not in visible_text
    finally:
        window.close()
