"""Compact one-row-per-support master table."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from ui.theme import TOKENS


MASTER_HEADERS = [
    "狀態",
    "Drawing line number",
    "流水號",
    "型號",
    "數量",
    "單位",
    "材質",
    "總重(kg)",
    "備註/錯誤摘要",
]


class SupportMasterTable(QTableWidget):
    supportSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_rows = []
        self._row_results = {}
        self.setColumnCount(len(MASTER_HEADERS))
        self.setHorizontalHeaderLabels(MASTER_HEADERS)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        widths = [52, 150, 90, 155, 58, 52, 150, 90, 280]
        for index, width in enumerate(widths):
            self.setColumnWidth(index, width)
        self.itemSelectionChanged.connect(self._emit_selection)

    def set_project(self, rows, project_result=None, *, global_material="SUS304") -> None:
        self.setUpdatesEnabled(False)
        try:
            self._project_rows = list(rows)
            self._row_results = {}
            if project_result is not None:
                result_index = 0
                for project_index, row in enumerate(self._project_rows):
                    if not row.enabled:
                        continue
                    if result_index < len(project_result.rows):
                        self._row_results[project_index] = project_result.rows[result_index]
                    result_index += 1

            self.setRowCount(len(self._project_rows))
            for index, row in enumerate(self._project_rows):
                row_result = self._row_results.get(index)
                values, status = self._values(row, row_result, global_material)
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setData(Qt.ItemDataRole.UserRole, index)
                    if column in (0, 4, 5, 7):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if column == 0:
                        color = {
                            "✓": TOKENS["color"]["status_ok"],
                            "⚠": TOKENS["color"]["status_warn"],
                            "✗": TOKENS["color"]["status_error"],
                        }.get(status, TOKENS["color"]["text_muted"])
                        item.setForeground(QColor(color))
                    self.setItem(index, column, item)
                self.setRowHeight(index, 28)
        finally:
            self.setUpdatesEnabled(True)

    def _values(self, row, row_result, global_material: str):
        overrides = row.overrides or {}
        if overrides.get("upper_material_unknown"):
            material = f"{global_material}(假設)"
        elif overrides.get("upper_material"):
            material = f"{overrides['upper_material']}(覆寫)"
        else:
            material = f"{global_material}(全域)"

        status = "—"
        total_weight = ""
        note = "未分析" if row.enabled else "未啟用"
        if row_result is not None:
            result = row_result.single_result
            if result.error:
                status = "✗"
                note = result.error
            else:
                status = "⚠" if overrides.get("upper_material_unknown") else "✓"
                total_weight = f"{row_result.scaled_result.total_weight:.3f}"
                reasons = (result.meta or {}).get("review_reasons", [])
                note = reasons[0] if reasons else (result.warnings[0] if result.warnings else "")

        return [
            status,
            row.drawing_line_number,
            row.serial,
            row.display_designation or row.designation,
            row.quantity,
            row.unit or "組",
            material,
            total_weight,
            note,
        ], status

    def _emit_selection(self):
        selected = self.selectionModel().selectedRows()
        if not selected:
            return
        item = self.item(selected[0].row(), 0)
        if item is not None:
            self.supportSelected.emit(int(item.data(Qt.ItemDataRole.UserRole)))

    def select_support(self, project_index: int) -> None:
        if not (0 <= project_index < self.rowCount()):
            return
        self.blockSignals(True)
        try:
            self.selectRow(project_index)
        finally:
            self.blockSignals(False)

    def apply_filter(self, query: str, *, pending_only: bool = False) -> int:
        terms = [term for term in query.casefold().split() if term]
        visible = 0
        for row_index, project_row in enumerate(self._project_rows):
            text = " ".join(
                self.item(row_index, column).text()
                for column in range(self.columnCount())
                if self.item(row_index, column) is not None
            ).casefold()
            pending = bool((project_row.overrides or {}).get("upper_material_unknown"))
            show = all(term in text for term in terms) and (not pending_only or pending)
            self.setRowHidden(row_index, not show)
            visible += int(show)
        return visible

    def row_result(self, project_index: int):
        return self._row_results.get(project_index)
