import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from export.excel.column_roles import role_of
from ui.bom_detail_panel import (
    BomDetailPanel,
    DETAIL_HEADERS,
    is_header_visible_for_view,
)


_APP = QApplication.instance() or QApplication(sys.argv)


def test_ui_view_presets_read_column_roles():
    assert role_of("計算說明") == "trace"
    assert role_of("來源圖面") == "trace"
    assert role_of("密度狀態") == "engineer"
    assert not is_header_visible_for_view("計算說明", "工程")
    assert is_header_visible_for_view("計算說明", "查核")
    assert is_header_visible_for_view("材質", "採購")
    assert is_header_visible_for_view("密度狀態", "採購")


def test_bom_detail_switches_between_role_views_without_removing_columns():
    panel = BomDetailPanel()
    try:
        original_count = panel.table.columnCount()
        panel.set_view_preset("採購")
        assert panel.table.isColumnHidden(DETAIL_HEADERS.index("計算說明"))
        assert not panel.table.isColumnHidden(DETAIL_HEADERS.index("材質"))

        panel.set_view_preset("查核")
        assert not panel.table.isColumnHidden(DETAIL_HEADERS.index("計算說明"))
        assert panel.table.columnCount() == original_count == len(DETAIL_HEADERS)
    finally:
        panel.close()
