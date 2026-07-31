"""BOM detail view for the selected support master row."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from export.excel.column_roles import VALID_ROLES, role_of
from ui.result_readiness import entry_readiness, result_readiness
from ui.theme import TOKENS


DETAIL_HEADERS = [
    "品名",
    "規格",
    "材質",
    "密度狀態",
    "加工狀態",
    "尺寸",
    "數量",
    "單重",
    "總重",
    "屬性",
    "密度(g/cm³)",
    "項次",
    "計算說明",
    "來源圖面",
]
_DEFAULT_VISIBLE_COUNT = 7

VIEW_ROLE_SETS = {
    "工程": {"manager", "engineer"},
    "採購": {"manager", "procure"},
    "查核": set(VALID_ROLES),
}
VIEW_EXTRA_HEADERS = {
    "工程": set(),
    "採購": {
        "品名", "規格", "材質", "單位", "單件數量", "總數量",
        "總重", "總重(kg)", "密度狀態", "加工狀態",
    },
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
        self.readiness_label = QLabel("BOM／加工成熟度會在分析後顯示")
        self.readiness_label.setWordWrap(True)
        self.readiness_label.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']}; "
            f"background: {TOKENS['color']['surface_soft']}; "
            f"border: 1px solid {TOKENS['color']['border_soft']}; "
            "border-radius: 5px; padding: 5px 8px;"
        )
        layout.addWidget(self.readiness_label)
        controls = QHBoxLayout()
        self.show_all_checkbox = QCheckBox("顯示全部欄")
        self.show_all_checkbox.toggled.connect(self._apply_column_visibility)
        controls.addWidget(self.show_all_checkbox)
        self.review_only_checkbox = QCheckBox("只看待確認零件")
        self.review_only_checkbox.setToolTip(
            "僅顯示加工資料有缺口，或密度仍待覆核的零件"
        )
        self.review_only_checkbox.toggled.connect(self._apply_row_filter)
        controls.addWidget(self.review_only_checkbox)
        controls.addStretch()
        layout.addLayout(controls)
        self.table = QTableWidget()
        self.table.setColumnCount(len(DETAIL_HEADERS))
        self.table.setHorizontalHeaderLabels(DETAIL_HEADERS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        layout.addWidget(self.table)
        self._view_preset = "工程"
        self._row_needs_review: list[bool] = []
        self._apply_column_visibility()

    def clear_result(self):
        self.title_label.setText("選取支撐後顯示 BOM 明細")
        self.readiness_label.setText("BOM／加工成熟度會在分析後顯示")
        self.readiness_label.setToolTip("")
        self.readiness_label.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']}; "
            f"background: {TOKENS['color']['surface_soft']}; "
            f"border: 1px solid {TOKENS['color']['border_soft']}; "
            "border-radius: 5px; padding: 5px 8px;"
        )
        self.table.setRowCount(0)
        self._row_needs_review = []

    def set_row_result(self, row_result) -> None:
        if row_result is None:
            self.clear_result()
            return
        designation = row_result.input_row.display_designation or row_result.input_row.designation
        self.title_label.setText(f"{designation} — BOM 明細")
        single = row_result.single_result
        scaled = row_result.scaled_result
        if single.error:
            self.readiness_label.setText("✗ 計算錯誤，未產生 BOM")
            self.readiness_label.setStyleSheet(
                "color: #991B1B; background: #FDE8E8; "
                "border: 1px solid #F5B8B8; border-radius: 5px; padding: 5px 8px;"
            )
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(single.error))
            self._row_needs_review = [True]
            return
        readiness = result_readiness(single)
        self.readiness_label.setText(readiness.compact_label)
        self.readiness_label.setToolTip(readiness.tooltip)
        if readiness.needs_attention:
            readiness_style = (
                f"color: {TOKENS['color']['status_warn']}; background: #FFF7E6; "
                "border: 1px solid #F4D6B4; border-radius: 5px; "
                "padding: 5px 8px; font-weight: 600;"
            )
        else:
            readiness_style = (
                f"color: {TOKENS['color']['status_ok']}; background: #E9F9EE; "
                "border: 1px solid #BBEFCB; border-radius: 5px; "
                "padding: 5px 8px; font-weight: 600;"
            )
        self.readiness_label.setStyleSheet(readiness_style)
        self.table.setRowCount(len(single.entries))
        self._row_needs_review = []
        source_drawing = readiness.source_drawing
        for row, (entry, scaled_entry) in enumerate(zip(single.entries, scaled.entries)):
            entry_state = entry_readiness(entry)
            self._row_needs_review.append(entry_state.needs_attention)
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
                entry.material,
                entry_state.density_label,
                entry_state.fabrication_label,
                size,
                scaled_entry.quantity,
                f"{entry.unit_weight:.3f}",
                f"{scaled_entry.weight_output:.3f}",
                entry.category,
                f"{entry.density_g_cm3:g}" if entry.density_g_cm3 else "—",
                entry.item_no,
                entry.display_remark,
                entry.geometry.source_drawing or source_drawing or "—",
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if entry_state.tooltip and column in (3, 4, 10):
                    item.setToolTip(entry_state.tooltip)
                if entry_state.needs_attention and column in (3, 4):
                    item.setBackground(QColor("#FFF7E6"))
                    item.setForeground(QColor(TOKENS["color"]["status_warn"]))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                if column in (3, 4, 6, 7, 8, 10):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, column, item)
        self._apply_row_filter()

    def _apply_column_visibility(self):
        show_all = self.show_all_checkbox.isChecked()
        for column, header in enumerate(DETAIL_HEADERS):
            visible = is_header_visible_for_view(header, self._view_preset)
            self.table.setColumnHidden(column, not show_all and not visible)

    def set_view_preset(self, view: str) -> None:
        self._view_preset = view if view in VIEW_ROLE_SETS else "工程"
        self._apply_column_visibility()

    def _apply_row_filter(self):
        review_only = self.review_only_checkbox.isChecked()
        for row in range(self.table.rowCount()):
            needs_review = (
                self._row_needs_review[row]
                if row < len(self._row_needs_review)
                else False
            )
            self.table.setRowHidden(row, review_only and not needs_review)
