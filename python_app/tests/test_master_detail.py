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


def test_master_filter_operates_on_support_rows(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list("01-2B-05A", drawing_line_number="DL-001")
        window._add_item_to_list("51-1.1/2B", drawing_line_number="DL-002")

        window.result_filter_input.setText("DL-002")
        _APP.processEvents()

        assert window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)
        assert window.result_filter_count_label.text() == "顯示 1/2 筆"
    finally:
        window.close()
