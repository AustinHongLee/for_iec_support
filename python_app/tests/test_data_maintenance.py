import os
from copy import deepcopy
from datetime import date

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from core import config_loader
from ui.data_maintenance_page import (
    DataMaintenancePage,
    build_candidate_config,
    diff_configs,
    editable_config_summaries,
    prepare_config_for_save,
    validation_commands,
)
from ui.theme import TOKENS


def _maintenance_page():
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    page = DataMaintenancePage()
    app.processEvents()
    return app, page


def test_toolbar_data_entry_switches_to_maintenance_page():
    from PyQt6.QtWidgets import QApplication
    from ui.main_window import MainWindow

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    try:
        window.main_tabs.setCurrentIndex(0)
        window.btn_config.click()
        app.processEvents()
        assert window.main_tabs.currentWidget() is window.data_maintenance_page
        assert "數據維護" in window.statusBar().currentMessage()
    finally:
        window.close()


def test_numeric_type_summaries_exclude_special_configs():
    type_ids = {str(item["type_id"]) for item in editable_config_summaries()}

    assert "01" in type_ids
    assert "PENETRATION HOLE" not in type_ids
    assert all(type_id.isdigit() for type_id in type_ids)


def test_type01_table_diff_and_required_evidence(tmp_path, monkeypatch):
    original = deepcopy(config_loader.load_config("01", strict=True))
    rows = deepcopy(original["table"])
    target = next(row for row in rows if row["line_size"] == 12)
    target["L"] = 372
    candidate = build_candidate_config(
        original,
        scalar_values={
            field: original[field]
            for field in ("h_limit", "h_unit_mm", "applicable_range")
        },
        table_rows=rows,
    )

    changes = diff_configs(original, candidate)
    l_change = next(change for change in changes if change.path == "line_size=12:L")
    assert l_change.before == 370
    assert l_change.after == 372
    assert l_change.percent == (2 / 370 * 100)

    prepared, issues = prepare_config_for_save(
        original,
        candidate,
        source_reference="",
        description="intentional update",
    )
    assert "更新依據（圖號＋版次）為必填" in issues

    prepared, issues = prepare_config_for_save(
        original,
        candidate,
        source_reference="STM-05.01 Rev.2",
        description="update L from revised drawing",
        today=date(2026, 7, 13),
    )
    assert issues == []
    assert prepared["data_updated_at"] == "2026-07-13"
    assert "STM-05.01 Rev.2" in prepared["data_update_note"]

    temp_config = tmp_path / "type_01.json"
    monkeypatch.setattr(
        config_loader,
        "_config_path",
        lambda type_id, must_exist=True: str(temp_config),
    )
    monkeypatch.setattr(config_loader.getpass, "getuser", lambda: "test-user")
    config_loader.save_config("01", prepared, prepared["data_update_note"])
    reloaded = config_loader.load_config("01", strict=True)

    assert next(row for row in reloaded["table"] if row["line_size"] == 12)["L"] == 372
    assert reloaded["change_log"][-1]["by"] == "test-user"
    assert reloaded["data_updated_at"] == "2026-07-13"


def test_prepare_rejects_no_data_change():
    original = config_loader.load_config("01", strict=True)
    prepared, issues = prepare_config_for_save(
        original,
        deepcopy(original),
        source_reference="STM-05.01 Rev.1",
        description="no-op",
    )

    assert prepared["data_update_note"]
    assert "沒有可儲存的資料變更" in issues


def test_golden_guidance_exposes_the_four_validation_commands():
    commands = validation_commands().splitlines()

    assert commands == [
        "python -m compileall -q python_app",
        "python python_app\\validate_tables.py",
        "python python_app\\validate_tables.py | Select-String '^X'",
        "python -m pytest -q",
    ]


def test_maintenance_type_search_filters_navigation():
    app, page = _maintenance_page()
    try:
        total = page.type_list.count()
        page.type_search.setText("Type 01")
        app.processEvents()

        visible = [
            page.type_list.item(index)
            for index in range(total)
            if not page.type_list.item(index).isHidden()
        ]
        assert visible
        assert all("Type 01" in item.text() for item in visible)
        assert page.type_count_label.text() == f"{len(visible)}/{total} 個"
    finally:
        page.close()


def test_table_edit_updates_diff_highlight_and_save_readiness():
    app, page = _maintenance_page()
    try:
        headers = [
            page.table.horizontalHeaderItem(index).toolTip().removeprefix("設定鍵：")
            for index in range(page.table.columnCount())
        ]
        l_column = headers.index("L")
        item = page.table.item(0, l_column)
        original = int(item.text())
        item.setText(str(original + 1))
        page._refresh_review()

        assert len(page._last_changes) == 1
        assert "L" in page.diff_browser.toPlainText()
        assert (
            item.background().color().name()
            == TOKENS["color"]["primary_weak"].lower()
        )
        assert page.reset_button.isEnabled()
        assert not page.save_button.isEnabled()
        assert "補齊" in page.change_status_label.text()

        page.source_edit.setText("STM-05.01 Rev.2")
        page.description_edit.setPlainText("依新版原圖微調 L 尺寸")
        page._refresh_review()

        assert page.save_button.isEnabled()
        assert "可安全儲存" in page.change_status_label.text()
    finally:
        page.close()


def test_invalid_numeric_cell_blocks_save_with_clear_status():
    app, page = _maintenance_page()
    try:
        headers = [
            page.table.horizontalHeaderItem(index).toolTip().removeprefix("設定鍵：")
            for index in range(page.table.columnCount())
        ]
        l_column = headers.index("L")
        page.table.item(0, l_column).setText("不是數字")
        page.source_edit.setText("STM-05.01 Rev.2")
        page.description_edit.setPlainText("測試錯誤輸入")
        page._refresh_review()

        assert page.change_status_label.text() == "輸入格式有誤"
        assert "請先修正輸入格式" in page.diff_browser.toPlainText()
        assert "第 1 列「L (mm)」格式不正確" in page.issues_label.text()
        assert not page.save_button.isEnabled()
        assert page.reset_button.isEnabled()
    finally:
        page.close()
