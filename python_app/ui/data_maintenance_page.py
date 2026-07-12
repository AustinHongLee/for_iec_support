"""Safe UI and pure helpers for maintaining JSON-backed Type data."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.config_loader import list_configs, load_config, save_config, validate_config
from core.config_sanity import SanityIssue, check_config_sanity
from ui.theme import TOKENS


EDITABLE_SCALAR_FIELDS = ("h_limit", "h_unit_mm", "applicable_range")
_METADATA_FIELDS = {
    "type_id",
    "name",
    "source",
    "version",
    "last_modified",
    "change_log",
    "data_updated_at",
    "data_update_note",
}


@dataclass(frozen=True)
class ConfigDiff:
    path: str
    before: object
    after: object
    percent: float | None = None

    def format(self) -> str:
        suffix = f" ({self.percent:+.1f}%)" if self.percent is not None else ""
        return f"{self.path}: {self.before!s} → {self.after!s}{suffix}"


def editable_config_summaries() -> list[dict]:
    """Return only numeric Type configs supported by config_loader."""
    summaries = []
    for item in list_configs():
        type_id = str(item.get("type_id", "")).strip()
        if type_id.isdigit() and load_config(type_id) is not None:
            summaries.append(item)
    return summaries


def table_headers(config: dict) -> list[str]:
    headers = []
    for row in config.get("table", []):
        if not isinstance(row, dict):
            continue
        for key in row:
            if key not in headers:
                headers.append(key)
    return headers


def build_candidate_config(
    original: dict,
    *,
    scalar_values: dict[str, object],
    table_rows: list[dict],
) -> dict:
    candidate = deepcopy(original)
    for field in EDITABLE_SCALAR_FIELDS:
        if field in original and field in scalar_values:
            candidate[field] = scalar_values[field]
    if "table" in original:
        candidate["table"] = deepcopy(table_rows)
    return candidate


def _percent_change(before, after) -> float | None:
    if (
        isinstance(before, (int, float))
        and not isinstance(before, bool)
        and isinstance(after, (int, float))
        and not isinstance(after, bool)
        and before != 0
    ):
        return (float(after) - float(before)) / abs(float(before)) * 100
    return None


def diff_configs(original: dict, candidate: dict) -> list[ConfigDiff]:
    changes = []
    for field in EDITABLE_SCALAR_FIELDS:
        if field in original and original.get(field) != candidate.get(field):
            changes.append(
                ConfigDiff(
                    field,
                    original.get(field),
                    candidate.get(field),
                    _percent_change(original.get(field), candidate.get(field)),
                )
            )

    original_rows = original.get("table", [])
    candidate_rows = candidate.get("table", [])
    max_rows = max(len(original_rows), len(candidate_rows))
    for index in range(max_rows):
        before_row = original_rows[index] if index < len(original_rows) else {}
        after_row = candidate_rows[index] if index < len(candidate_rows) else {}
        row_label = after_row.get("line_size", before_row.get("line_size", index + 1))
        for field in dict.fromkeys([*before_row.keys(), *after_row.keys()]):
            before = before_row.get(field)
            after = after_row.get(field)
            if before != after:
                changes.append(
                    ConfigDiff(
                        f"line_size={row_label}:{field}",
                        before,
                        after,
                        _percent_change(before, after),
                    )
                )
    return changes


def prepare_config_for_save(
    original: dict,
    candidate: dict,
    *,
    source_reference: str,
    description: str,
    today: date | None = None,
) -> tuple[dict, list[str]]:
    source_reference = source_reference.strip()
    description = description.strip()
    issues = []
    if not source_reference:
        issues.append("更新依據（圖號＋版次）為必填")
    if not description:
        issues.append("說明為必填")
    if issues:
        return deepcopy(candidate), issues

    prepared = deepcopy(candidate)
    prepared["data_updated_at"] = (today or date.today()).isoformat()
    prepared["data_update_note"] = f"{source_reference}｜{description}"
    issues.extend(validate_config(prepared))
    if not diff_configs(original, prepared):
        issues.append("沒有可儲存的資料變更")
    return prepared, issues


def readonly_structure(config: dict) -> dict:
    excluded = set(EDITABLE_SCALAR_FIELDS) | _METADATA_FIELDS | {"table"}
    return {key: value for key, value in config.items() if key not in excluded}


def _coerce_text(text: str, exemplar):
    text = text.strip()
    if isinstance(exemplar, bool):
        return text.casefold() in {"1", "true", "yes", "是"}
    if isinstance(exemplar, int) and not isinstance(exemplar, bool):
        return int(text)
    if isinstance(exemplar, float):
        return float(text)
    return text


class DataMaintenancePage(QWidget):
    statusMessage = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._type_id = ""
        self._original = None
        self._scalar_edits = {}
        self._build_ui()
        self._load_type_list()

    def _build_ui(self):
        outer = QVBoxLayout(self)

        layer_row = QHBoxLayout()
        layer_row.addWidget(QLabel("資料層："))
        self.layer_combo = QComboBox()
        self.layer_combo.addItem("基準資料")
        self.layer_combo.setEnabled(False)
        self.layer_combo.setToolTip("變體 overlay 尚未啟用")
        layer_row.addWidget(self.layer_combo)
        layer_row.addStretch()
        outer.addLayout(layer_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.type_list = QListWidget()
        self.type_list.currentItemChanged.connect(self._on_type_selected)
        splitter.addWidget(self.type_list)

        editor = QWidget()
        editor_layout = QVBoxLayout(editor)

        self.scalar_group = QGroupBox("可編輯常數")
        self.scalar_form = QFormLayout(self.scalar_group)
        editor_layout.addWidget(self.scalar_group)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        editor_layout.addWidget(self.table, 2)

        self.readonly_browser = QTextBrowser()
        self.readonly_browser.setMinimumHeight(100)
        editor_layout.addWidget(self.readonly_browser, 1)

        evidence_group = QGroupBox("更新依據")
        evidence_form = QFormLayout(evidence_group)
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("圖號＋版次，例如 STM-05.01 Rev.2")
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(70)
        evidence_form.addRow("更新依據（必填）：", self.source_edit)
        evidence_form.addRow("說明（必填）：", self.description_edit)
        editor_layout.addWidget(evidence_group)

        self.issues_label = QLabel("")
        self.issues_label.setWordWrap(True)
        self.issues_label.setStyleSheet(
            f"color: {TOKENS['color']['status_error']};"
        )
        editor_layout.addWidget(self.issues_label)

        self.confirm_large_change_checkbox = QCheckBox("我確認此變動")
        self.confirm_large_change_checkbox.setVisible(False)
        editor_layout.addWidget(self.confirm_large_change_checkbox)

        self.diff_browser = QTextBrowser()
        self.diff_browser.setMinimumHeight(90)
        editor_layout.addWidget(self.diff_browser)

        buttons = QHBoxLayout()
        self.check_button = QPushButton("檢查")
        self.check_button.clicked.connect(self._on_check)
        self.diff_button = QPushButton("差異預覽")
        self.diff_button.clicked.connect(self._on_diff)
        self.save_button = QPushButton("儲存")
        self.save_button.clicked.connect(self._on_save)
        buttons.addWidget(self.check_button)
        buttons.addWidget(self.diff_button)
        buttons.addStretch()
        buttons.addWidget(self.save_button)
        editor_layout.addLayout(buttons)

        splitter.addWidget(editor)
        splitter.setSizes([220, 980])
        outer.addWidget(splitter)

    def _load_type_list(self):
        for item in editable_config_summaries():
            widget = QListWidgetItem(
                f"Type {item['type_id']} — {item.get('name', '')}"
            )
            widget.setData(Qt.ItemDataRole.UserRole, item["type_id"])
            self.type_list.addItem(widget)
        if self.type_list.count():
            self.type_list.setCurrentRow(0)

    def _clear_scalar_form(self):
        while self.scalar_form.rowCount():
            self.scalar_form.removeRow(0)
        self._scalar_edits = {}

    def _on_type_selected(self, current, previous=None):
        if current is None:
            return
        type_id = str(current.data(Qt.ItemDataRole.UserRole))
        config = load_config(type_id, strict=True)
        self._type_id = type_id
        self._original = deepcopy(config)
        self._populate(config)

    def _populate(self, config: dict):
        self._clear_scalar_form()
        for field in EDITABLE_SCALAR_FIELDS:
            if field not in config:
                continue
            edit = QLineEdit(str(config[field]))
            self.scalar_form.addRow(f"{field}：", edit)
            self._scalar_edits[field] = edit

        headers = table_headers(config)
        rows = config.get("table", [])
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, field in enumerate(headers):
                self.table.setItem(
                    row_index, col_index, QTableWidgetItem(str(row.get(field, "")))
                )

        structure = readonly_structure(config)
        self.readonly_browser.setPlainText(
            "其餘結構欄位（唯讀）\n" + json.dumps(structure, ensure_ascii=False, indent=2)
        )
        self.source_edit.clear()
        self.description_edit.clear()
        self.issues_label.clear()
        self.confirm_large_change_checkbox.setChecked(False)
        self.confirm_large_change_checkbox.setVisible(False)
        self.diff_browser.clear()

    def _candidate(self) -> dict:
        if self._original is None:
            raise ValueError("尚未選擇 Type")
        scalars = {}
        for field, edit in self._scalar_edits.items():
            scalars[field] = _coerce_text(edit.text(), self._original[field])

        headers = table_headers(self._original)
        rows = []
        original_rows = self._original.get("table", [])
        for row_index in range(self.table.rowCount()):
            row = {}
            for col_index, field in enumerate(headers):
                item = self.table.item(row_index, col_index)
                text = item.text() if item else ""
                exemplar = original_rows[row_index].get(field, "")
                row[field] = _coerce_text(text, exemplar)
            rows.append(row)
        return build_candidate_config(
            self._original,
            scalar_values=scalars,
            table_rows=rows,
        )

    def _show_validation(
        self, schema_issues: list[str], sanity_issues: list[SanityIssue]
    ) -> None:
        red = TOKENS["color"]["status_error"]
        yellow = TOKENS["color"]["status_warn"]
        lines = [f'<span style="color:{red}">● {issue}</span>' for issue in schema_issues]
        for issue in sanity_issues:
            color = yellow if issue.severity == "warning" else red
            lines.append(
                f'<span style="color:{color}">● {issue.message}</span>'
            )
        self.issues_label.setText("<br>".join(lines))
        has_warning = any(issue.severity == "warning" for issue in sanity_issues)
        self.confirm_large_change_checkbox.setVisible(has_warning)
        if not has_warning:
            self.confirm_large_change_checkbox.setChecked(False)

    def _show_issues(self, issues: list[str]) -> None:
        self._show_validation(issues, [])

    def _on_check(self):
        try:
            candidate = self._candidate()
            issues = validate_config(candidate)
            sanity = check_config_sanity(candidate, original=self._original)
        except (TypeError, ValueError) as exc:
            issues = [str(exc)]
            sanity = []
        self._show_validation(issues, sanity)
        if not issues and not sanity:
            self.statusMessage.emit(f"Type {self._type_id} config 檢查通過")

    def _on_diff(self):
        try:
            changes = diff_configs(self._original, self._candidate())
        except (TypeError, ValueError) as exc:
            self._show_issues([str(exc)])
            return
        self.diff_browser.setPlainText(
            "\n".join(change.format() for change in changes) or "沒有資料變更"
        )

    def _on_save(self):
        try:
            candidate = self._candidate()
        except (TypeError, ValueError) as exc:
            self._show_issues([str(exc)])
            return
        prepared, issues = prepare_config_for_save(
            self._original,
            candidate,
            source_reference=self.source_edit.text(),
            description=self.description_edit.toPlainText(),
        )
        if issues:
            self._show_issues(issues)
            return

        sanity = check_config_sanity(prepared, original=self._original)
        errors = [issue for issue in sanity if issue.severity == "error"]
        warnings = [issue for issue in sanity if issue.severity == "warning"]
        if errors or (warnings and not self.confirm_large_change_checkbox.isChecked()):
            self._show_validation([], sanity)
            if warnings and not errors:
                self.statusMessage.emit("大幅變動需勾選「我確認此變動」才能儲存")
            return

        changes = diff_configs(self._original, prepared)
        preview = "\n".join(change.format() for change in changes)
        self.diff_browser.setPlainText(preview)
        reply = QMessageBox.question(
            self,
            "確認儲存 Type 資料",
            f"即將寫入 Type {self._type_id}：\n\n{preview}\n\n確認儲存？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        save_config(
            self._type_id,
            prepared,
            change_desc=prepared["data_update_note"],
        )
        self._original = deepcopy(load_config(self._type_id, strict=True))
        self._populate(self._original)
        self.statusMessage.emit(f"Type {self._type_id} 資料已儲存")
