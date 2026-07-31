"""Compact one-row-per-support master table."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QAbstractItemView, QHeaderView, QTableWidget, QTableWidgetItem

from core.calculator import uses_global_upper_material
from core.source_profiles import source_profile_choices
from companies.registry import design_company_label
from ui.result_readiness import result_readiness, summarize_materials
from ui.theme import TOKENS


MASTER_HEADERS = [
    "狀態",
    "型號",
    "數量",
    "材質",
    "總重(kg)",
    "BOM/加工",
    "圖面來源",
    "Drawing line number",
    "流水號",
    "設計公司",
    "單位",
    "備註/錯誤摘要",
]


class SupportMasterTable(QTableWidget):
    supportSelected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_rows = []
        self._row_results = {}
        self._project_source_profile = ""
        self._global_material_confirmed = True
        self.setColumnCount(len(MASTER_HEADERS))
        self.setHorizontalHeaderLabels(MASTER_HEADERS)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)
        self.setWordWrap(False)
        self.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        widths = [54, 155, 54, 190, 88, 190, 170, 145, 82, 82, 50, 300]
        for index, width in enumerate(widths):
            self.setColumnWidth(index, width)
        self.itemSelectionChanged.connect(self._emit_selection)

    def set_project(
        self,
        rows,
        project_result=None,
        *,
        global_material="SUS304",
        global_material_confirmed=True,
    ) -> None:
        self.setUpdatesEnabled(False)
        try:
            self._project_rows = list(rows)
            self._global_material_confirmed = bool(global_material_confirmed)
            self._row_results = {}
            self._project_source_profile = (
                str(project_result.source_profile or "")
                if project_result is not None
                else ""
            )
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
                values, status, tooltips, readiness_attention = self._values(
                    row,
                    row_result,
                    global_material,
                )
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value))
                    item.setData(Qt.ItemDataRole.UserRole, index)
                    if column in (0, 2, 4, 5, 9, 10):
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    if column in tooltips:
                        item.setToolTip(tooltips[column])
                    if column == 0:
                        color = {
                            "✓": TOKENS["color"]["status_ok"],
                            "⚠": TOKENS["color"]["status_warn"],
                            "▲": TOKENS["color"]["status_high"],
                            "✗": TOKENS["color"]["status_error"],
                        }.get(status, TOKENS["color"]["text_muted"])
                        item.setForeground(QColor(color))
                        if status == "✗":
                            font = item.font()
                            font.setBold(True)
                            font.setPointSize(max(font.pointSize(), 10))
                            item.setFont(font)
                            item.setToolTip("錯誤：本列未能計算，未納入重量")
                    if status == "✗":
                        item.setBackground(QColor("#FFF0F0"))
                        if column == 11:
                            item.setForeground(QColor(TOKENS["color"]["status_error"]))
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                            item.setToolTip(str(value))
                    elif status == "⚠" and column in (0, 11):
                        item.setBackground(QColor("#FFF7E6"))
                        if column == 0:
                            item.setForeground(
                                QColor(TOKENS["color"]["status_warn"])
                            )
                    elif status == "▲" and column in (0, 5, 11):
                        item.setBackground(QColor("#FFF0E6"))
                        item.setForeground(QColor(TOKENS["color"]["status_high"]))
                        if column in (0, 11):
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                    if readiness_attention and column == 5:
                        item.setBackground(QColor("#FFF7E6"))
                        item.setForeground(
                            QColor(TOKENS["color"]["status_warn"])
                        )
                    self.setItem(index, column, item)
                self.setRowHeight(
                    index,
                    32 if status in {"✗", "⚠", "▲"} or readiness_attention else 28,
                )
        finally:
            self.setUpdatesEnabled(True)

    def _values(self, row, row_result, global_material: str):
        overrides = row.overrides or {}
        material_pending = self._material_pending(row)
        if material_pending:
            material = f"{global_material}(假設)"
        elif overrides.get("upper_material"):
            material = f"{overrides['upper_material']}(覆寫)"
        else:
            material = f"{global_material}(全域)"

        status = "—"
        total_weight = ""
        note = "未分析" if row.enabled else "未啟用"
        profile_labels = dict(source_profile_choices())
        company_label = design_company_label(
            row.designation,
            row.source_profile or self._project_source_profile,
        )
        source_profile = (
            row.source_profile or self._project_source_profile
            if company_label == "長春"
            else ""
        )
        source_label = profile_labels.get(source_profile, source_profile)
        readiness_label = "未分析"
        readiness_attention = False
        tooltips: dict[int, str] = {}
        if row_result is not None:
            result = row_result.single_result
            if result.error:
                status = "✗"
                note = result.error
            else:
                readiness = result_readiness(result)
                readiness_attention = readiness.needs_attention
                status_attention = (
                    material_pending
                    or readiness.bom_label == "待補"
                )
                if readiness.issue_severity == "high":
                    status = "▲"
                elif readiness.issue_count:
                    status = "⚠"
                else:
                    status = "⚠" if status_attention else "✓"
                total_weight = f"{row_result.scaled_result.total_weight:.3f}"
                actual_materials = summarize_materials(result)
                if not material_pending and actual_materials:
                    material = actual_materials
                source_label = readiness.source_label or source_label
                readiness_label = readiness.compact_label
                reasons = []
                reasons.extend(readiness.issue_messages)
                if material_pending:
                    reasons.append("全域材質尚未確認")
                reasons.extend(readiness.blockers)
                if readiness.density_review_count:
                    reasons.append(
                        f"{readiness.density_review_count} 項鋼板密度仍採未驗證預設值"
                    )
                reasons.extend(readiness.review_reasons)
                reasons.extend(result.warnings)
                note = next((str(item) for item in reasons if str(item).strip()), "")
                tooltips[0] = readiness.tooltip
                tooltips[3] = "\n".join(
                    f"• {item.material}"
                    for item in result.entries
                    if getattr(item, "material", "")
                )
                tooltips[6] = (
                    f"本列採用：{source_label or '未標示'}\n"
                    f"來源圖：{readiness.source_drawing or '未標示'}"
                )
                tooltips[5] = readiness.tooltip

        return [
            status,
            row.display_designation or row.designation,
            row.quantity,
            material,
            total_weight,
            readiness_label,
            source_label,
            row.drawing_line_number,
            row.serial,
            company_label,
            row.unit or "組",
            note,
        ], status, tooltips, readiness_attention

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

    def apply_filter(
        self,
        query: str,
        *,
        pending_only: bool = False,
        column_filters: dict[str, str] | None = None,
    ) -> int:
        terms = [term for term in query.casefold().split() if term]
        filters = {
            key: str(value).strip().casefold()
            for key, value in (column_filters or {}).items()
            if str(value).strip()
        }
        filter_columns = {
            "status": 0,
            "drawing": 7,
            "serial": 8,
            "designation": 1,
            "material": 3,
            "readiness": 5,
        }
        visible = 0
        for row_index, project_row in enumerate(self._project_rows):
            values = [
                self.item(row_index, column).text()
                for column in range(self.columnCount())
                if self.item(row_index, column) is not None
            ]
            text = " ".join(values).casefold()
            pending = self._material_pending(project_row)
            show = all(term in text for term in terms) and (not pending_only or pending)
            if show:
                for key, needle in filters.items():
                    column = filter_columns.get(key)
                    if column is None:
                        continue
                    item = self.item(row_index, column)
                    value = item.text().casefold() if item is not None else ""
                    if key == "status":
                        matches = value == needle
                    else:
                        matches = needle in value
                    if not matches:
                        show = False
                        break
            self.setRowHidden(row_index, not show)
            visible += int(show)
        return visible

    def _material_pending(self, row) -> bool:
        if not uses_global_upper_material(row.designation):
            return False
        overrides = row.overrides or {}
        if overrides.get("upper_material_unknown"):
            return True
        if overrides.get("upper_material"):
            return False
        return not self._global_material_confirmed

    def filter_options(self) -> dict[str, list[str]]:
        """Return unique values for Excel-like filter drop-downs."""
        columns = {
            "drawing": 7,
            "serial": 8,
            "designation": 1,
            "material": 3,
            "readiness": 5,
        }
        options = {}
        for key, column in columns.items():
            options[key] = sorted(
                {
                    self.item(row, column).text().strip()
                    for row in range(self.rowCount())
                    if self.item(row, column) is not None
                    and self.item(row, column).text().strip()
                },
                key=str.casefold,
            )
        return options

    def row_result(self, project_index: int):
        return self._row_results.get(project_index)
