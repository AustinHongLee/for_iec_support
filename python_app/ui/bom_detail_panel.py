"""BOM detail view for the selected support master row."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


DETAIL_HEADERS = [
    "品名",
    "規格",
    "尺寸",
    "材質",
    "數量",
    "單重",
    "總重",
    "項次",
    "屬性",
    "計算說明",
]
_DEFAULT_VISIBLE_COUNT = 7


class BomDetailPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.title_label = QLabel("選取支撐後顯示 BOM 明細")
        layout.addWidget(self.title_label)
        self.show_all_checkbox = QCheckBox("顯示全部欄")
        self.show_all_checkbox.toggled.connect(self._apply_column_visibility)
        layout.addWidget(self.show_all_checkbox)
        self.table = QTableWidget()
        self.table.setColumnCount(len(DETAIL_HEADERS))
        self.table.setHorizontalHeaderLabels(DETAIL_HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.table)
        self._apply_column_visibility()

    def clear_result(self):
        self.title_label.setText("選取支撐後顯示 BOM 明細")
        self.table.setRowCount(0)

    def set_row_result(self, row_result) -> None:
        if row_result is None:
            self.clear_result()
            return
        designation = row_result.input_row.display_designation or row_result.input_row.designation
        self.title_label.setText(f"{designation} — BOM 明細")
        single = row_result.single_result
        scaled = row_result.scaled_result
        if single.error:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(single.error))
            return
        self.table.setRowCount(len(single.entries))
        for row, (entry, scaled_entry) in enumerate(zip(single.entries, scaled.entries)):
            size = " × ".join(
                part
                for part in (
                    f"L{entry.length:g}" if entry.length else "",
                    f"W{entry.width:g}" if entry.width else "",
                )
                if part
            )
            values = [
                entry.name,
                entry.display_spec,
                size,
                entry.material,
                scaled_entry.quantity,
                f"{entry.unit_weight:.3f}",
                f"{scaled_entry.weight_output:.3f}",
                entry.item_no,
                entry.category,
                entry.display_remark,
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))

    def _apply_column_visibility(self):
        show_all = self.show_all_checkbox.isChecked()
        for column in range(len(DETAIL_HEADERS)):
            self.table.setColumnHidden(
                column, not show_all and column >= _DEFAULT_VISIBLE_COUNT
            )
