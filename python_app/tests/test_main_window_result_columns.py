import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from ui.main_window import (
    MainWindow,
    _RESULT_DEFAULT_VISIBLE_HEADERS,
    _RESULT_HEADERS,
)
from ui.theme import TOKENS


def test_result_table_hides_advanced_columns_by_default():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    app.processEvents()

    try:
        for index, header in enumerate(_RESULT_HEADERS):
            expected_hidden = header not in _RESULT_DEFAULT_VISIBLE_HEADERS
            assert window.result_table.isColumnHidden(index) is expected_hidden

        window.show_advanced_columns_checkbox.setChecked(True)
        app.processEvents()

        assert not any(
            window.result_table.isColumnHidden(index)
            for index in range(len(_RESULT_HEADERS))
        )
    finally:
        window.close()


def test_result_summary_uses_metric_theme_tokens():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    try:
        assert window.total_weight_label.font().pointSize() == TOKENS["font"]["metric_primary"]
        assert window.summary_success_label.font().pointSize() == TOKENS["font"]["metric_value"]
    finally:
        window.close()


def test_hidden_result_columns_still_hold_searchable_data():
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()

    try:
        window._add_item_to_list(
            "51-1.1/2B",
            quantity=2,
            serial="S-001",
            drawing_line_number="DL-001",
        )
        window._on_analyze()
        app.processEvents()

        assert window.result_table.rowCount() > 0
        assert window.result_table.isColumnHidden(_RESULT_HEADERS.index("流水號.sort"))
        assert window.result_table.item(0, _RESULT_HEADERS.index("流水號.sort")).text() == "S-001"

        window.result_filter_input.setText("S-001")
        app.processEvents()

        visible_rows = [
            row for row in range(window.result_table.rowCount())
            if not window.result_table.isRowHidden(row)
        ]
        assert visible_rows
    finally:
        window.close()
