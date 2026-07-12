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

from export.excel.column_roles import VALID_ROLES, role_of


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

VIEW_ROLE_SETS = {
    "工程": {"manager", "engineer"},
    "採購": {"manager", "procure"},
    "查核": set(VALID_ROLES),
}
VIEW_EXTRA_HEADERS = {
    "工程": set(),
    "採購": {"品名", "規格", "材質", "單位", "單件數量", "總數量", "總重", "總重(kg)"},
    "查核": set(),
}
UI_ROLE_HEADER_ALIASES = {
    "Drawing line number": "來源圖號",
    "流水號.sort": "流水號",
    "Type": "型號類別",
}


def is_header_visible_for_view(header: str, view: str) -> bool:
    roles = VIEW_ROLE_SETS.get(view, VIEW_ROLE_SETS["工程"])
    extras = VIEW_EXTRA_HEADERS.get(view, set())
    role_header = UI_ROLE_HEADER_ALIASES.get(header, header)
    return role_of(role_header) in roles or header in extras


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
        self._view_preset = "工程"
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
        for column, header in enumerate(DETAIL_HEADERS):
            visible = is_header_visible_for_view(header, self._view_preset)
            self.table.setColumnHidden(column, not show_all and not visible)

    def set_view_preset(self, view: str) -> None:
        self._view_preset = view if view in VIEW_ROLE_SETS else "工程"
        self._apply_column_visibility()
