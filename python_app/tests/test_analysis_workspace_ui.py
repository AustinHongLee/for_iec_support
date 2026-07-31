import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton

from core.calculator import get_analysis_setting, set_analysis_setting
from ui.main_window import MainWindow, SidePanel


_APP = QApplication.instance() or QApplication(sys.argv)


def _window(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    return MainWindow()


def test_input_list_uses_two_line_rows_and_its_own_filter(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list(
            "01-2B-05A",
            drawing_line_number="DL-001",
            serial="S-001",
            quantity=3,
        )
        window._add_item_to_list("51-1.1/2B", drawing_line_number="DL-002")

        assert "\n" in window.item_list.item(0).text()
        assert window.item_list.item(0).text().splitlines()[0].startswith("01-2B-05A")
        assert "DL-001" in window.item_list.item(0).text()
        assert "01-2B-05A" in window.item_list.item(0).text()
        assert window.item_list.item(0).sizeHint().height() >= 48

        window.input_filter.setText("DL-002")
        _APP.processEvents()

        assert window.item_list.item(0).isHidden()
        assert not window.item_list.item(1).isHidden()
        assert window.input_filter_count.text() == "1/2 筆"
    finally:
        window.close()


def test_result_column_filters_are_independent(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list(
            "01-2B-05A",
            drawing_line_number="DL-A",
            serial="S-001",
            overrides={"upper_material_unknown": True},
        )
        window._add_item_to_list(
            "51-1.1/2B",
            drawing_line_number="DL-B",
            serial="S-002",
            overrides={"upper_material": "SUS304"},
        )
        window._on_analyze()
        _APP.processEvents()

        window.result_column_filters["drawing"].setEditText("DL-B")
        _APP.processEvents()
        assert window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)
        assert not window.active_filter_bar.isHidden()
        chip = next(
            button
            for button in window.active_filter_bar.findChildren(QPushButton)
            if "Drawing: DL-B" in button.text()
        )

        window.result_filter_input.setText("DL-A")
        _APP.processEvents()
        assert window.result_locator_count_label.text() == "篩選外 1 筆"
        assert window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)

        chip.click()
        _APP.processEvents()
        assert window.result_filter_input.text() == "DL-A"
        assert window.result_locator_count_label.text() == "第 1/1 筆"
        assert window.active_filter_bar.isHidden()
        assert not window.support_master_table.isRowHidden(0)
        assert not window.support_master_table.isRowHidden(1)

        window.result_column_filters["drawing"].setEditText("DL-B")
        window._clear_result_filters()
        assert window.result_filter_input.text() == "DL-A"
        assert window.result_locator_count_label.text() == "第 1/1 筆"
        assert window.active_filter_bar.isHidden()
        status = window.result_column_filters["status"]
        status.setCurrentIndex(status.findData("⚠"))
        _APP.processEvents()
        assert not window.support_master_table.isRowHidden(0)
        assert window.support_master_table.isRowHidden(1)
    finally:
        window.close()


def test_csv_and_text_import_reports_keep_source_row_problem_details(monkeypatch):
    window = _window(monkeypatch)
    try:
        csv_rows = window._read_project_rows_csv(
            [
                "型號,數量,單位,Drawing line number,流水號.sort",
                "01-2B-05A,,,DL-001,1",
                ",3,組,DL-002,2",
                "57-1B-A,1.5,組,DL-003,3",
            ]
        )
        assert len(csv_rows) == 1
        assert window._last_import_report["skipped_missing_designation"] == 1
        assert window._last_import_report["skipped_invalid_quantity"] == 1
        assert any(
            problem["row"] == 3
            and problem["field"] == "型號"
            and "DL-002" in problem["raw"]
            for problem in window._last_import_report["problems"]
        )

        text_rows = window._read_project_rows_text(
            ["57-1B-A", "01-2B-05A 0"]
        )
        assert len(text_rows) == 1
        assert window._last_import_report["skipped_invalid_quantity"] == 1
        assert any(
            problem["row"] == 2
            and problem["field"] == "數量"
            and "01-2B-05A 0" in problem["raw"]
            for problem in window._last_import_report["problems"]
        )
    finally:
        window.close()


def test_override_change_reanalyzes_automatically_after_first_run(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._auto_analyze_timer.setInterval(10)
        window._add_item_to_list("01-2B-05A")
        window.item_list.setCurrentRow(0)
        window._on_analyze()
        original_result = window._project_result

        window._on_override_changed(0, {"connection": "tee"})
        assert window._project_result is None
        QTest.qWait(40)
        _APP.processEvents()

        assert window._project_result is not None
        assert window._project_result is not original_result
        assert window._project_rows[0].overrides == {"connection": "tee"}
        assert "結果已更新" in window.side_panel._apply_status_label.text()
    finally:
        window.close()


def test_global_material_change_invalidates_and_reanalyzes(monkeypatch):
    previous = get_analysis_setting("upper_material")
    set_analysis_setting("upper_material", "SUS304")
    window = _window(monkeypatch)
    try:
        window._auto_analyze_timer.setInterval(10)
        window._add_item_to_list("01-2B-05A")
        window._on_analyze()
        original_result = window._project_result
        original_weight = original_result.total_weight

        window.material_combo.setCurrentText("A53Gr.B")
        assert window._project_result is None
        assert not window.btn_export.isEnabled()
        QTest.qWait(40)
        _APP.processEvents()

        assert window._project_result is not None
        assert window._project_result is not original_result
        assert window._project_result.total_weight != original_weight
        assert window.btn_export.isEnabled()
    finally:
        window.close()
        set_analysis_setting("upper_material", previous)


def test_saved_type_config_invalidates_affected_project_and_reanalyzes(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._auto_analyze_timer.setInterval(10)
        window._add_item_to_list("01-2B-05A")
        window._on_analyze()
        original_result = window._project_result

        window.data_maintenance_page.configSaved.emit("01")
        assert window._project_result is None
        assert not window.btn_export.isEnabled()
        QTest.qWait(40)
        _APP.processEvents()

        assert window._project_result is not None
        assert window._project_result is not original_result
        assert window.btn_export.isEnabled()
    finally:
        window.close()


def test_export_readiness_explains_analysis_assumptions_and_final_gate(monkeypatch):
    window = _window(monkeypatch)
    try:
        assert window.export_readiness_label.text() == "尚未建立清單"

        window._add_item_to_list("01-2B-05A")
        assert window.export_readiness_label.text() == "待分析"

        window._on_analyze()
        _APP.processEvents()
        assert window.export_readiness_label.text() == "概算可匯出：含 1 筆假設"
        assert "假設值：1 筆" in window.export_readiness_label.toolTip()

        window.project_header.mode_combo.setCurrentText("精算")
        _APP.processEvents()
        assert window.export_readiness_label.text() == "精算未就緒：1 筆假設"
        assert "例外放行原因" in window.export_readiness_label.toolTip()

        window.material_combo.setCurrentText("SUS304")
        window._auto_analyze_timer.setInterval(10)
        QTest.qWait(40)
        _APP.processEvents()
        assert (
            window.export_readiness_label.text()
            == "BOM 可匯出：1 筆加工／密度待核"
        )
        assert "不代表這些支撐已可直接出加工圖" in (
            window.export_readiness_label.toolTip()
        )
    finally:
        window.close()


def test_invalidated_result_is_visibly_stale(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list("51-1.1/2B")
        window._on_analyze()
        window._invalidate_analysis_outputs("測試設定已變更")

        assert window.export_readiness_label.text() == "結果已過期"
        assert "舊結果不可匯出" in window.export_readiness_label.toolTip()
        assert not window.btn_export.isEnabled()
    finally:
        window.close()


def test_auto_reanalysis_shows_total_weight_before_and_after(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._auto_analyze_timer.setInterval(10)
        window.material_combo.setCurrentText("SUS304")
        window._add_item_to_list("01-2B-05A")
        window._on_analyze()
        previous = window._project_result.total_weight

        window.material_combo.setCurrentText("A53Gr.B")
        QTest.qWait(40)
        _APP.processEvents()
        current = window._project_result.total_weight

        assert current != previous
        assert not window.weight_delta_label.isHidden()
        assert f"{previous:.3f} → {current:.3f} kg" in window.weight_delta_label.text()
        assert "%" in window.weight_delta_label.text()
        assert "總重量差異" in window.weight_delta_label.toolTip()
        assert "%" in window.weight_delta_label.toolTip()
        assert "全域上段管材質" in window.weight_delta_label.toolTip()
    finally:
        window.close()


def test_one_step_undo_restores_only_the_latest_project_change(monkeypatch):
    window = _window(monkeypatch)
    try:
        assert not window.btn_undo.isEnabled()
        window._add_item_to_list("01-2B-05A")
        window._add_item_to_list("57-1B-A")
        assert len(window._project_rows) == 2
        assert window.btn_undo.isEnabled()
        assert "新增支撐" in window.btn_undo.toolTip()

        window._on_undo()
        assert [row.designation for row in window._project_rows] == ["01-2B-05A"]
        assert window.item_list.count() == 1
        assert not window.btn_undo.isEnabled()
        assert "已復原" in window.statusBar().currentMessage()

        window._on_undo()
        assert [row.designation for row in window._project_rows] == ["01-2B-05A"]
    finally:
        window.close()


def test_undo_override_restores_row_and_reanalyzes_automatically(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._auto_analyze_timer.setInterval(10)
        window._add_item_to_list("01-2B-05A")
        window.item_list.setCurrentRow(0)
        window._on_analyze()
        original_weight = window._project_result.total_weight

        window._on_override_changed(0, {"connection": "tee"})
        QTest.qWait(40)
        _APP.processEvents()
        assert window._project_rows[0].overrides == {"connection": "tee"}
        assert window.btn_undo.isEnabled()

        window._on_undo()
        assert window._project_rows[0].overrides is None
        assert window._project_result is None
        QTest.qWait(40)
        _APP.processEvents()

        assert window._project_result is not None
        assert window._project_result.total_weight == original_weight
        assert not window.btn_undo.isEnabled()
        assert "已復原" in window.statusBar().currentMessage()
        assert "結果已更新" in window.side_panel._apply_status_label.text()
    finally:
        window.close()


def test_undo_global_material_restores_unconfirmed_project_state(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list("01-2B-05A")
        window.material_combo.setCurrentText("SUS304")
        assert window._global_material_confirmed
        assert "變更全域材質" in window.btn_undo.toolTip()

        window._on_undo()
        assert not window._global_material_confirmed
        assert "未確認" in window.material_combo.currentText()
        assert window.summary_material_label.text() == "0/1"
        assert [row.designation for row in window._project_rows] == ["01-2B-05A"]
    finally:
        window.close()


def test_undo_restores_rows_after_confirmed_clear_all(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list("01-2B-05A")
        window._add_item_to_list("57-1B-A")
        monkeypatch.setattr(
            QMessageBox,
            "question",
            lambda *args, **kwargs: QMessageBox.StandardButton.Yes,
        )

        window._on_clear_all()
        assert not window._project_rows
        assert window.item_list.count() == 0
        assert "全部清除" in window.btn_undo.toolTip()

        window._on_undo()
        assert [row.designation for row in window._project_rows] == [
            "01-2B-05A",
            "57-1B-A",
        ]
        assert window.item_list.count() == 2
    finally:
        window.close()


def test_side_panel_separates_correction_result_and_logic(monkeypatch):
    window = _window(monkeypatch)
    try:
        window._add_item_to_list("01-2B-05A")
        window.item_list.setCurrentRow(0)
        _APP.processEvents()

        assert window.side_panel._detail_tabs.count() == 3
        assert [
            window.side_panel._detail_tabs.tabText(index)
            for index in range(3)
        ] == ["修正", "計算結果", "計算說明"]
        assert "自動重新計算" in window.side_panel._apply_status_label.text()
    finally:
        window.close()
