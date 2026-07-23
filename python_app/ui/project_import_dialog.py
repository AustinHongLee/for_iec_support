"""Guided project-list import dialogs and pre-import completeness summary."""

from __future__ import annotations

import os

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from ui.theme import TOKENS


class ProjectImportGuideDialog(QDialog):
    """Explain what a project import is before opening a file picker."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_action: str | None = None
        self.setWindowTitle("匯入專案支撐清單")
        self.setMinimumWidth(650)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        title = QLabel("匯入的是「一列一筆支撐」的專案清單")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {TOKENS['color']['primary_dark']};"
        )
        layout.addWidget(title)

        intro = QLabel(
            "可直接使用原始 <b>Support MTO Excel</b>、本程式儲存的清單 CSV，"
            "或下載標準範本後填寫。匯入後才會進行各 Type 的重量與 BOM 分析。"
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        layout.addWidget(
            self._card(
                "必要資料",
                "<b>型號</b>：例如 57-1B-A、01-2B-05A<br>"
                "<b>數量</b>：大於 0 的整數",
                "ok",
            )
        )
        layout.addWidget(
            self._card(
                "建議一起匯入",
                "Drawing line number：保留原始圖面／管線來源<br>"
                "流水號.sort：保留專案排序與核對編號<br>"
                "單位：未提供時會使用「組」",
                "info",
            )
        )
        layout.addWidget(
            self._card(
                "特殊情況",
                "PENETRATION HOLE 除了型號與數量，還需要<b>管徑</b>；"
                "有保溫時再填<b>保溫厚度</b>。",
                "warn",
            )
        )

        button_row = QHBoxLayout()
        template_button = QPushButton("下載空白 Excel 範本")
        template_button.clicked.connect(lambda: self._select("template"))
        button_row.addWidget(template_button)
        button_row.addStretch()
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        choose_button = QPushButton("選擇 Excel／CSV")
        choose_button.setDefault(True)
        choose_button.clicked.connect(lambda: self._select("choose"))
        button_row.addWidget(cancel_button)
        button_row.addWidget(choose_button)
        layout.addLayout(button_row)

    def _select(self, action: str):
        self.selected_action = action
        self.accept()

    @staticmethod
    def _card(title: str, body: str, state: str) -> QFrame:
        frame = QFrame()
        color = TOKENS["color"].get(
            f"status_{state}", TOKENS["color"]["status_info"]
        )
        frame.setStyleSheet(
            f"QFrame {{ background: {TOKENS['color']['surface_soft']}; "
            f"border: 1px solid {TOKENS['color']['border_soft']}; "
            f"border-left: 4px solid {color}; "
            f"border-radius: {TOKENS['radius']['sm']}px; }}"
        )
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 8, 12, 8)
        heading = QLabel(title)
        heading.setStyleSheet(f"font-weight: bold; color: {color}; border: none;")
        body_label = QLabel(body)
        body_label.setWordWrap(True)
        body_label.setStyleSheet("border: none;")
        layout.addWidget(heading)
        layout.addWidget(body_label)
        return frame


class ProjectImportPreviewDialog(QDialog):
    """Show what will and will not be available after importing parsed rows."""

    def __init__(
        self,
        filepath: str,
        rows,
        *,
        existing_count: int = 0,
        import_report: dict | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.rows = list(rows)
        self.import_report = dict(import_report or {})
        self.problems = project_import_problems(
            self.rows, import_report=self.import_report
        )
        self.setWindowTitle("確認匯入內容")
        self.setMinimumWidth(980 if self.problems else 650)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        title = QLabel(f"準備匯入 {len(self.rows)} 筆支撐")
        title.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {TOKENS['color']['primary_dark']};"
        )
        layout.addWidget(title)
        path_label = QLabel(os.path.basename(filepath))
        path_label.setToolTip(filepath)
        path_label.setStyleSheet(f"color: {TOKENS['color']['text_muted']};")
        layout.addWidget(path_label)

        summary, warnings = summarize_project_rows(
            self.rows, import_report=import_report
        )
        self.summary_label = QLabel(summary)
        self.summary_label.setTextFormat(Qt.TextFormat.RichText)
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            f"background: {TOKENS['color']['surface_soft']}; "
            f"border: 1px solid {TOKENS['color']['border_soft']}; "
            f"border-radius: {TOKENS['radius']['sm']}px; padding: 10px;"
        )
        layout.addWidget(self.summary_label)

        self.warning_label = QLabel("<br>".join(warnings) if warnings else "資料完整，可保留來源追溯。")
        self.warning_label.setWordWrap(True)
        warning_color = (
            TOKENS["color"]["status_warn"]
            if warnings
            else TOKENS["color"]["status_ok"]
        )
        self.warning_label.setStyleSheet(f"color: {warning_color}; padding: 4px;")
        layout.addWidget(self.warning_label)

        self.problem_table = QTableWidget()
        self.problem_table.setColumnCount(5)
        self.problem_table.setHorizontalHeaderLabels(
            ["原檔列", "程度", "問題", "原始內容", "怎麼修正"]
        )
        self.problem_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.problem_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.problem_table.setAlternatingRowColors(True)
        self.problem_table.setWordWrap(False)
        self.problem_table.verticalHeader().setVisible(False)
        self.problem_table.setMinimumHeight(210)
        self.problem_table.setMaximumHeight(290)
        header = self.problem_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.problem_table.setColumnWidth(2, 260)
        self.problem_table.setColumnWidth(3, 260)

        problem_heading_row = QHBoxLayout()
        self.problem_heading = QLabel(f"問題列明細（{len(self.problems)} 項）")
        self.problem_heading.setStyleSheet("font-weight: bold;")
        problem_heading_row.addWidget(self.problem_heading)
        problem_heading_row.addStretch()
        self.copy_problems_button = QPushButton("複製問題清單")
        self.copy_problems_button.clicked.connect(self._copy_problems)
        problem_heading_row.addWidget(self.copy_problems_button)
        layout.addLayout(problem_heading_row)
        layout.addWidget(self.problem_table)
        self._populate_problem_table()
        self.problem_heading.setVisible(bool(self.problems))
        self.copy_problems_button.setVisible(bool(self.problems))
        self.problem_table.setVisible(bool(self.problems))

        self.replace_radio = QRadioButton(f"取代目前清單（目前 {existing_count} 筆）")
        self.append_radio = QRadioButton(f"追加到目前清單（匯入後 {existing_count + len(self.rows)} 筆）")
        if existing_count:
            self.replace_radio.setChecked(True)
            layout.addWidget(self.replace_radio)
            layout.addWidget(self.append_radio)
        else:
            self.replace_radio.setChecked(True)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_button = QPushButton("返回")
        cancel_button.clicked.connect(self.reject)
        import_button = QPushButton(f"匯入 {len(self.rows)} 筆")
        import_button.setDefault(True)
        import_button.clicked.connect(self.accept)
        buttons.addWidget(cancel_button)
        buttons.addWidget(import_button)
        layout.addLayout(buttons)

    @property
    def replace_existing(self) -> bool:
        return self.replace_radio.isChecked()

    def _populate_problem_table(self) -> None:
        severity_labels = {
            "error": ("不匯入／需補", TOKENS["color"]["status_error"]),
            "warning": ("需確認", TOKENS["color"]["status_warn"]),
            "info": ("已代入", TOKENS["color"]["status_info"]),
        }
        self.problem_table.setRowCount(len(self.problems))
        for row_index, problem in enumerate(self.problems):
            severity = str(problem.get("severity") or "warning")
            severity_text, severity_color = severity_labels.get(
                severity, severity_labels["warning"]
            )
            issue = str(problem.get("issue") or "")
            field = str(problem.get("field") or "")
            values = (
                str(problem.get("row") or "-"),
                severity_text,
                f"{field}：{issue}" if field else issue,
                str(problem.get("raw") or ""),
                str(problem.get("resolution") or ""),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                if column == 1:
                    item.setForeground(QColor(severity_color))
                self.problem_table.setItem(row_index, column, item)

    def _copy_problems(self) -> None:
        if not self.problems:
            return
        lines = ["原檔列\t程度\t欄位\t問題\t原始內容\t怎麼修正"]
        severity_labels = {
            "error": "不匯入／需補",
            "warning": "需確認",
            "info": "已代入",
        }
        for problem in self.problems:
            lines.append(
                "\t".join(
                    str(value).replace("\t", " ").replace("\n", " ")
                    for value in (
                        problem.get("row") or "-",
                        severity_labels.get(problem.get("severity"), "需確認"),
                        problem.get("field") or "",
                        problem.get("issue") or "",
                        problem.get("raw") or "",
                        problem.get("resolution") or "",
                    )
                )
            )
        QApplication.clipboard().setText("\n".join(lines))
        self.copy_problems_button.setText("已複製")


def project_import_problems(rows, *, import_report: dict | None = None) -> list[dict]:
    """Return source-row problems, with a fallback for callers without a parser report."""
    rows = list(rows)
    report = import_report or {}
    problems = [dict(problem) for problem in report.get("problems") or []]
    if not problems:
        for index, row in enumerate(rows, start=1):
            raw = (
                f"型號={row.designation}；數量={row.quantity}；"
                f"Drawing={row.drawing_line_number or '空白'}；流水號={row.serial or '空白'}"
            )
            if not row.drawing_line_number:
                problems.append(
                    {
                        "row": f"匯入第 {index} 筆",
                        "severity": "warning",
                        "field": "Drawing",
                        "issue": "缺少 Drawing line number；仍可計算但無法依圖面追溯",
                        "raw": raw,
                        "resolution": "回原檔填入圖面或管線群組編號。",
                    }
                )
            if not row.serial:
                problems.append(
                    {
                        "row": f"匯入第 {index} 筆",
                        "severity": "warning",
                        "field": "流水號",
                        "issue": "缺少流水號；仍可計算但逐筆核對較困難",
                        "raw": raw,
                        "resolution": "回原檔填入 MTO 流水號或專案排序編號。",
                    }
                )
    reported_hole_problems = sum(
        problem.get("field") == "管徑" for problem in problems
    )
    hole_index = 0
    for index, row in enumerate(rows, start=1):
        if (
            str(row.designation).strip().upper() == "PENETRATION HOLE"
            and not (row.overrides or {}).get("nominal_size")
        ):
            hole_index += 1
            if hole_index <= reported_hole_problems:
                continue
            problems.append(
                {
                    "row": f"匯入第 {index} 筆",
                    "severity": "error",
                    "field": "管徑",
                    "issue": "PENETRATION HOLE 缺少管徑；型號尚不完整",
                    "raw": f"型號={row.designation}；數量={row.quantity}",
                    "resolution": "在管徑欄填入例如 4、6 或 8。",
                }
            )
    return problems


def summarize_project_rows(
    rows, *, import_report: dict | None = None
) -> tuple[str, list[str]]:
    rows = list(rows)
    total = len(rows)
    drawing_count = sum(bool(row.drawing_line_number) for row in rows)
    serial_count = sum(bool(row.serial) for row in rows)
    holes = [row for row in rows if str(row.designation).strip().upper() == "PENETRATION HOLE"]
    incomplete_holes = sum(
        not bool((row.overrides or {}).get("nominal_size")) for row in holes
    )

    report = import_report or {}
    source_rows = int(report.get("source_rows") or total)
    skipped_missing = int(report.get("skipped_missing_designation") or 0)
    skipped_invalid_quantity = int(report.get("skipped_invalid_quantity") or 0)
    skipped_total = skipped_missing + skipped_invalid_quantity

    summary = (
        f"<b>匯入結果</b><br>"
        f"原檔資料列：{source_rows}　｜　即將匯入：{total}　｜　不匯入：{skipped_total}<br><br>"
        f"<b>必要欄位</b><br>"
        f"型號：{total}/{total} 筆　｜　數量：{total}/{total} 筆<br><br>"
        f"<b>來源追溯</b><br>"
        f"Drawing：{drawing_count}/{total} 筆　｜　流水號：{serial_count}/{total} 筆"
    )
    warnings = []
    if drawing_count < total:
        warnings.append(
            f"⚠ {total - drawing_count} 筆沒有 Drawing：仍可計算，但無法依原始圖面追溯。"
        )
    if serial_count < total:
        warnings.append(
            f"⚠ {total - serial_count} 筆沒有流水號：仍可計算，但專案排序與逐筆核對較困難。"
        )
    if incomplete_holes:
        warnings.append(
            f"⚠ {incomplete_holes} 筆 PENETRATION HOLE 缺少管徑，開孔型號不完整。"
        )
    skipped = int(report.get("skipped_missing_designation") or 0)
    invalid_quantity = int(report.get("skipped_invalid_quantity") or 0)
    quantity_defaulted = int(report.get("quantity_defaulted") or 0)
    unit_defaulted = int(report.get("unit_defaulted") or 0)
    if skipped:
        warnings.append(
            f"✗ {skipped} 列找不到型號，這些列不會匯入；請回原檔補上型號。"
        )
    if invalid_quantity:
        warnings.append(
            f"✗ {invalid_quantity} 列數量格式錯誤，這些列不會匯入；請改成大於 0 的整數。"
        )
    if quantity_defaulted:
        warnings.append(
            f"⚠ {quantity_defaulted} 筆數量空白，將暫時按 1 組匯入。"
        )
    if unit_defaulted:
        warnings.append(
            f"ℹ {unit_defaulted} 筆單位空白，將使用「組」。"
        )
    return summary, warnings
