import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from core.calculator import (
    analyze_single,
    get_analysis_setting,
    set_analysis_setting,
    uses_global_upper_material,
)
from export.excel.confidence_summary import (
    build_export_context,
    final_export_allowed,
)
from ui.main_window import MainWindow, SidePanel, _RESULT_HEADERS


_APP = QApplication.instance() or QApplication(sys.argv)


def test_unknown_material_keeps_bom_equal_to_explicit_default():
    previous = get_analysis_setting("upper_material")
    set_analysis_setting("upper_material", "SUS304")
    try:
        explicit = analyze_single("01-2B-05A", {"upper_material": "SUS304"})
        assumed = analyze_single("01-2B-05A", {"upper_material_unknown": True})
    finally:
        set_analysis_setting("upper_material", previous)

    assert not explicit.error
    assert not assumed.error
    assert assumed.entries == explicit.entries
    assert assumed.total_weight == explicit.total_weight
    assert assumed.meta["truth_level"] == "估算"
    assert assumed.meta["requires_review"] is True
    assert assumed.evidence[-1]["field"] == "upper_material"
    assert assumed.evidence[-1]["value"] == "SUS304"
    assert assumed.evidence[-1]["basis"] == "assumption"
    assert assumed.evidence[-1]["confidence"] == 0.5


def test_unknown_material_flag_does_not_emit_material_sentinel(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    panel = SidePanel()
    emitted = []
    panel.overrideChanged.connect(lambda idx, values: emitted.append(values))

    panel.show_item(0, "01-2B-05A", {"upper_material_unknown": True})
    panel._on_field_changed()

    assert emitted[-1] == {
        "connection": "elbow",
        "upper_material_unknown": True,
    }
    assert "upper_material" not in emitted[-1]
    panel.close()


def test_global_upper_material_scope_and_internal_consumers_emit_evidence():
    assert uses_global_upper_material("01-2B-05A")
    assert uses_global_upper_material("01T-2B-05A")
    assert uses_global_upper_material("09-2B-05B")
    assert uses_global_upper_material("11-2B-06G")
    assert not uses_global_upper_material("51-1.1/2B")

    for designation in ("09-2B-05B", "11-2B-06G"):
        result = analyze_single(
            designation,
            {"upper_material_unknown": True},
        )
        assert not result.error
        assert result.evidence[-1]["field"] == "upper_material"
        assert result.evidence[-1]["basis"] == "assumption"


def test_unknown_material_marks_input_and_project_result(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list(
            "01-2B-05A",
            overrides={"upper_material_unknown": True},
        )
        assert "⚠ 材質未定" in window.item_list.item(0).text()

        window._on_analyze()
        designation_col = _RESULT_HEADERS.index("型號")
        assert window.result_table.item(0, designation_col).text() == "⚠ 01-2B-05A"
    finally:
        window.close()


def test_material_completion_and_pending_filter_follow_enabled_rows(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list(
            "01-2B-05A",
            overrides={"upper_material_unknown": True},
        )
        window._add_item_to_list("01-3B-05A", overrides={"upper_material": "SUS304"})
        window._add_item_to_list(
            "01-4B-05A",
            enabled=False,
            overrides={"upper_material_unknown": True},
        )

        assert window.summary_material_label.text() == "1/2"
        assert window.project_header.completion_label.text() == "材質確認：1/2"

        window._on_analyze()
        status_filter = window.result_column_filters["status"]
        status_filter.setCurrentIndex(status_filter.findData("⚠"))
        _APP.processEvents()

        visible_text = " ".join(
            window._result_row_text(row)
            for row in range(window.result_table.rowCount())
            if not window.result_table.isRowHidden(row)
        )
        assert "01-2b-05a" in visible_text
        assert "01-3b-05a" not in visible_text
        assert "01-4b-05a" not in visible_text
    finally:
        window.close()


def test_inherited_global_material_requires_explicit_project_confirmation(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._auto_analyze_timer.setInterval(10)
        window._add_item_to_list("01-2B-05A")
        window._add_item_to_list("01-3B-05A")

        assert "未確認" in window.material_combo.currentText()
        assert window.summary_material_label.text() == "0/2"
        assert window.project_header.completion_label.text() == "材質確認：0/2"

        window._on_analyze()
        estimate_context = build_export_context(
            window._project_result,
            mode="精算",
        )
        assert estimate_context["assumption_count"] == 2
        assert not final_export_allowed(estimate_context)

        window.material_combo.setCurrentText("SUS304")
        assert window.summary_material_label.text() == "2/2"
        assert window._project_result is None
        QTest.qWait(40)
        _APP.processEvents()

        confirmed_context = build_export_context(
            window._project_result,
            mode="精算",
        )
        assert confirmed_context["assumption_count"] == 0
        assert final_export_allowed(confirmed_context)
    finally:
        window.close()


def test_material_completion_excludes_types_that_do_not_use_global_material(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list("51-1.1/2B")

        assert window.summary_material_label.text() == "不適用"
        assert window.project_header.completion_label.text() == "材質確認：不適用"
    finally:
        window.close()


def test_batch_material_applies_only_to_selected_indexes(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        for index in range(25):
            window._add_item_to_list(
                "01-2B-05A",
                overrides={"connection": "tee", "upper_material_unknown": True},
            )

        window._apply_material_to_indices(list(range(20)), "SUS316")

        for index, row in enumerate(window._project_rows):
            overrides = row.overrides or {}
            assert overrides["connection"] == "tee"
            if index < 20:
                assert overrides["upper_material"] == "SUS316"
                assert "upper_material_unknown" not in overrides
            else:
                assert overrides["upper_material_unknown"] is True
    finally:
        window.close()


def test_review_mode_advances_to_next_pending_item(monkeypatch):
    monkeypatch.setattr(SidePanel, "_load_pdf_for_type", lambda self, type_code: None)
    window = MainWindow()
    try:
        window._add_item_to_list(
            "01-2B-05A", overrides={"upper_material_unknown": True}
        )
        window._add_item_to_list(
            "01-3B-05A", overrides={"upper_material_unknown": True}
        )
        window.item_list.setCurrentRow(0)
        window.side_panel.review_mode_checkbox.setChecked(True)

        window.side_panel._mat_combo.setCurrentText("SUS304")
        _APP.processEvents()

        assert window.item_list.currentRow() == 1
        assert (window._project_rows[0].overrides or {})["upper_material"] == "SUS304"
    finally:
        window.close()
