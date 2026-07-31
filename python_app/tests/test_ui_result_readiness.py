import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows
from ui.bom_detail_panel import BomDetailPanel, DETAIL_HEADERS
from ui.main_window import MainWindow, SidePanel
from ui.result_readiness import result_readiness, summarize_materials


_APP = QApplication.instance() or QApplication(sys.argv)


def test_readiness_helper_exposes_density_and_fabrication_as_separate_states():
    result = analyze_single(
        "51-1.1/2B",
        source_profile="cw_e25_24_hp6",
    )

    readiness = result_readiness(result)

    assert not result.error
    assert readiness.bom_label == "可用"
    assert readiness.fabrication_label == "可出圖"
    assert readiness.density_review_count == 1
    assert readiness.status_symbol == "⚠"
    assert "密度待核 1" in readiness.compact_label
    assert "中威" in readiness.source_label
    assert "Carbon Steel" in summarize_materials(result)


def test_readiness_distinguishes_warning_from_high_risk_issue():
    warning = analyze_single(
        "01-6B-16T",
        source_profile="cw_e25_24_hp6",
    )
    high = analyze_single(
        "10-3B-05U",
        source_profile="cw_e25_24_hp6",
        overrides={"connection": "elbow"},
    )

    warning_state = result_readiness(warning)
    high_state = result_readiness(high)

    assert warning_state.status_symbol == "⚠"
    assert warning_state.issue_severity == "warning"
    assert warning_state.bom_label == "可用"
    assert high_state.status_symbol == "▲"
    assert high_state.issue_severity == "high"
    assert high_state.bom_label == "待補"
    assert "高風險 ▲1" in high_state.compact_label


def test_bom_detail_shows_density_source_fabrication_and_review_only_filter():
    project = analyze_project_rows(
        [ProjectInputRow("01-2B-05A", overrides={"upper_material": "SUS304"})],
        source_profile="cw_e25_24_hp6",
    )
    panel = BomDetailPanel()
    try:
        panel.set_row_result(project.rows[0])

        assert panel.table.columnCount() == len(DETAIL_HEADERS)
        assert "加工 待補" in panel.readiness_label.text()
        assert panel.table.item(0, DETAIL_HEADERS.index("加工狀態")).text() == "⚠ 待補"
        assert panel.table.item(1, DETAIL_HEADERS.index("加工狀態")).text() == "✓ 可出圖"
        assert panel.table.item(1, DETAIL_HEADERS.index("密度(g/cm³)")).text() == "7.85"
        assert panel.table.isColumnHidden(DETAIL_HEADERS.index("來源圖面"))

        panel.review_only_checkbox.setChecked(True)
        _APP.processEvents()

        assert not panel.table.isRowHidden(0)
        assert panel.table.isRowHidden(1)

        panel.set_view_preset("查核")
        assert not panel.table.isColumnHidden(DETAIL_HEADERS.index("來源圖面"))
    finally:
        panel.close()


def test_main_readiness_filter_syncs_master_and_part_detail(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list(
            "01-2B-05A",
            overrides={"upper_material": "SUS304"},
        )
        window._add_item_to_list("51-1.1/2B")
        window._on_analyze()
        _APP.processEvents()

        readiness_filter = window.result_column_filters["readiness"]
        target = next(
            readiness_filter.itemText(index)
            for index in range(readiness_filter.count())
            if "密度待核 1" in readiness_filter.itemText(index)
        )
        readiness_filter.setCurrentText(target)
        _APP.processEvents()

        assert window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)

        window.result_views.setCurrentIndex(1)
        _APP.processEvents()
        visible_text = " ".join(
            window._result_row_text(row)
            for row in range(window.result_table.rowCount())
            if not window.result_table.isRowHidden(row)
        )
        assert "51-1.1/2b" in visible_text
        assert "01-2b-05a" not in visible_text
    finally:
        window.close()


def test_side_panel_marks_successful_but_review_required_result(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    panel = SidePanel()
    try:
        panel.show_item(0, "51-1.1/2B", {})
        result = analyze_single(
            "51-1.1/2B",
            source_profile="cw_e25_24_hp6",
        )
        panel.update_result(result)

        assert panel._detail_tabs.tabText(1) == "計算結果 ⚠"
        assert "密度待核 1" in panel._result_browser.toPlainText()
        assert "7.85 g/cm³" in panel._result_browser.toPlainText()
    finally:
        panel.close()
