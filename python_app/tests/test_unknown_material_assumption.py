import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from core.calculator import (
    analyze_single,
    get_analysis_setting,
    set_analysis_setting,
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
