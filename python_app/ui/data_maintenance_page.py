"""Safe UI and pure helpers for maintaining JSON-backed Type data."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import date
import json

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QHeaderView,
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
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.config_loader import list_configs, load_config, save_config, validate_config
from core.config_sanity import SanityIssue, check_config_sanity
from ui.theme import TOKENS


EDITABLE_SCALAR_FIELDS = ("h_limit", "h_unit_mm", "applicable_range")
SCALAR_FIELD_LABELS = {
    "h_limit": "H 適用上限",
    "h_unit_mm": "H 代碼單位 (mm)",
    "applicable_range": "適用範圍",
}
TABLE_FIELD_LABELS = {
    "line_size": "主管徑",
    "pipe_size": "支撐管徑",
    "schedule": "Schedule",
    "L": "L (mm)",
}
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

_VALIDATION_COMMANDS = """python -m compileall -q python_app
python python_app\\validate_tables.py
python python_app\\validate_tables.py | Select-String '^X'
python -m pytest -q"""


def validation_commands() -> str:
    return _VALIDATION_COMMANDS


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
    configSaved = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._type_id = ""
        self._original = None
        self._scalar_edits = {}
        self._building = False
        self._last_changes: list[ConfigDiff] = []
        self._review_timer = QTimer(self)
        self._review_timer.setSingleShot(True)
        self._review_timer.setInterval(220)
        self._review_timer.timeout.connect(self._refresh_review)
        self._build_ui()
        self._load_type_list()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 10, 12, 10)
        outer.setSpacing(8)

        page_header = QFrame()
        page_header.setStyleSheet(
            f"QFrame {{ background: {TOKENS['color']['summary_bg']}; "
            f"border: 1px solid {TOKENS['color']['summary_border']}; "
            f"border-radius: {TOKENS['radius']['md']}px; }}"
        )
        page_header_layout = QHBoxLayout(page_header)
        page_header_layout.setContentsMargins(14, 9, 14, 9)
        heading_block = QVBoxLayout()
        heading = QLabel("Type 計算資料維護")
        heading.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {TOKENS['color']['primary_dark']}; "
            "border: none;"
        )
        subtitle = QLabel(
            "只開放已確認的常數與查表資料；儲存前會自動檢查、顯示差異並要求圖號與版次。"
        )
        subtitle.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']}; border: none;"
        )
        heading_block.addWidget(heading)
        heading_block.addWidget(subtitle)
        page_header_layout.addLayout(heading_block, 1)
        layer_badge = QLabel("基準資料")
        layer_badge.setToolTip("公司變體 overlay 尚未啟用，目前只能維護基準資料")
        layer_badge.setStyleSheet(
            f"color: {TOKENS['color']['primary_dark']}; "
            f"background: {TOKENS['color']['primary_weak']}; border: none; "
            f"border-radius: {TOKENS['radius']['sm']}px; padding: 5px 10px; font-weight: bold;"
        )
        page_header_layout.addWidget(layer_badge)
        outer.addWidget(page_header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        nav = QFrame()
        nav.setMinimumWidth(270)
        nav.setMaximumWidth(380)
        nav_layout = QVBoxLayout(nav)
        nav_layout.setContentsMargins(0, 0, 4, 0)
        nav_title_row = QHBoxLayout()
        nav_title = QLabel("選擇 Type")
        nav_title.setStyleSheet(
            f"font-weight: bold; color: {TOKENS['color']['primary']};"
        )
        nav_title_row.addWidget(nav_title)
        nav_title_row.addStretch()
        self.type_count_label = QLabel("0 個")
        self.type_count_label.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']};"
        )
        nav_title_row.addWidget(self.type_count_label)
        nav_layout.addLayout(nav_title_row)
        self.type_search = QLineEdit()
        self.type_search.setPlaceholderText("搜尋 Type 編號或名稱")
        self.type_search.setClearButtonEnabled(True)
        self.type_search.textChanged.connect(self._apply_type_filter)
        nav_layout.addWidget(self.type_search)
        self.type_list = QListWidget()
        self.type_list.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.type_list.currentItemChanged.connect(self._on_type_selected)
        nav_layout.addWidget(self.type_list, 1)
        splitter.addWidget(nav)

        editor = QWidget()
        editor_layout = QVBoxLayout(editor)
        editor_layout.setContentsMargins(6, 0, 0, 0)
        editor_layout.setSpacing(8)

        self.type_header = QFrame()
        self.type_header.setStyleSheet(
            f"QFrame {{ background: {TOKENS['color']['surface']}; "
            f"border: 1px solid {TOKENS['color']['border_soft']}; "
            f"border-radius: {TOKENS['radius']['md']}px; }}"
        )
        type_header_layout = QVBoxLayout(self.type_header)
        type_header_layout.setContentsMargins(12, 8, 12, 8)
        self.type_title_label = QLabel("尚未選擇 Type")
        self.type_title_label.setStyleSheet(
            f"font-size: 15px; font-weight: bold; color: {TOKENS['color']['primary_dark']}; border: none;"
        )
        self.type_meta_label = QLabel("")
        self.type_meta_label.setWordWrap(True)
        self.type_meta_label.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']}; border: none;"
        )
        type_header_layout.addWidget(self.type_title_label)
        type_header_layout.addWidget(self.type_meta_label)
        editor_layout.addWidget(self.type_header)

        self.editor_tabs = QTabWidget()
        data_page = QWidget()
        data_layout = QVBoxLayout(data_page)
        data_layout.setContentsMargins(6, 6, 6, 6)

        self.scalar_group = QGroupBox("可編輯常數")
        self.scalar_form = QFormLayout(self.scalar_group)
        data_layout.addWidget(self.scalar_group)

        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectItems
        )
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.itemChanged.connect(self._schedule_review)
        data_layout.addWidget(self.table, 1)
        self.editor_tabs.addTab(data_page, "可編輯資料")

        structure_page = QWidget()
        structure_layout = QVBoxLayout(structure_page)
        structure_layout.setContentsMargins(6, 6, 6, 6)
        structure_hint = QLabel("結構與公式欄位僅供核對，本頁不能修改。")
        structure_hint.setStyleSheet(
            f"color: {TOKENS['color']['text_muted']};"
        )
        structure_layout.addWidget(structure_hint)
        self.readonly_browser = QTextBrowser()
        self.readonly_browser.setFontFamily("Consolas")
        self.readonly_browser.setStyleSheet(
            f"background: {TOKENS['color']['surface']}; color: {TOKENS['color']['ink']};"
        )
        structure_layout.addWidget(self.readonly_browser, 1)
        self.editor_tabs.addTab(structure_page, "結構資料（唯讀）")
        editor_layout.addWidget(self.editor_tabs, 1)

        review_group = QGroupBox("變更確認與儲存")
        review_layout = QVBoxLayout(review_group)
        review_body = QHBoxLayout()

        diff_block = QVBoxLayout()
        self.change_status_label = QLabel("尚未修改")
        self.change_status_label.setStyleSheet(
            f"font-weight: bold; color: {TOKENS['color']['text_muted']};"
        )
        diff_block.addWidget(self.change_status_label)
        self.issues_label = QLabel("選取 Type 後即可編輯")
        self.issues_label.setWordWrap(True)
        diff_block.addWidget(self.issues_label)
        diff_title = QLabel("即時差異")
        diff_title.setStyleSheet(
            f"font-weight: bold; color: {TOKENS['color']['primary']};"
        )
        diff_block.addWidget(diff_title)
        self.diff_browser = QTextBrowser()
        self.diff_browser.setMinimumHeight(100)
        self.diff_browser.setStyleSheet(
            f"background: {TOKENS['color']['surface']}; color: {TOKENS['color']['ink']};"
        )
        diff_block.addWidget(self.diff_browser, 1)
        review_body.addLayout(diff_block, 3)

        evidence_group = QGroupBox("變更依據（儲存必填）")
        evidence_form = QFormLayout(evidence_group)
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("圖號＋版次，例如 STM-05.01 Rev.2")
        self.source_edit.textChanged.connect(self._schedule_review)
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("說明改了什麼，以及為什麼修改")
        self.description_edit.setMaximumHeight(85)
        self.description_edit.textChanged.connect(self._schedule_review)
        evidence_form.addRow("圖號＋版次：", self.source_edit)
        evidence_form.addRow("修改說明：", self.description_edit)

        self.confirm_large_change_checkbox = QCheckBox(
            "我已核對原圖，確認此大幅變動"
        )
        self.confirm_large_change_checkbox.setVisible(False)
        self.confirm_large_change_checkbox.toggled.connect(self._schedule_review)
        evidence_form.addRow("", self.confirm_large_change_checkbox)
        review_body.addWidget(evidence_group, 2)
        review_layout.addLayout(review_body, 1)

        buttons = QHBoxLayout()
        self.reset_button = QPushButton("復原未儲存變更")
        self.reset_button.clicked.connect(self._on_reset_changes)
        self.reset_button.setEnabled(False)
        self.save_button = QPushButton("儲存變更")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setEnabled(False)
        buttons.addWidget(self.reset_button)
        buttons.addStretch()
        buttons.addWidget(self.save_button)
        review_layout.addLayout(buttons)
        editor_layout.addWidget(review_group)

        splitter.addWidget(editor)
        splitter.setSizes([300, 1200])
        outer.addWidget(splitter, 1)

    def _load_type_list(self):
        self.type_list.clear()
        for item in editable_config_summaries():
            widget = QListWidgetItem(
                f"Type {item['type_id']} — {item.get('name', '')}"
            )
            widget.setData(Qt.ItemDataRole.UserRole, item["type_id"])
            self.type_list.addItem(widget)
        self._apply_type_filter()
        if self.type_list.count():
            self.type_list.setCurrentRow(0)

    def _apply_type_filter(self):
        query = self.type_search.text().strip().casefold()
        terms = [term for term in query.split() if term]
        visible = 0
        for index in range(self.type_list.count()):
            item = self.type_list.item(index)
            show = all(term in item.text().casefold() for term in terms)
            item.setHidden(not show)
            visible += int(show)
        total = self.type_list.count()
        self.type_count_label.setText(
            f"{visible}/{total} 個" if query else f"{total} 個"
        )

    def _clear_scalar_form(self):
        while self.scalar_form.rowCount():
            self.scalar_form.removeRow(0)
        self._scalar_edits = {}

    def _on_type_selected(self, current, previous=None):
        if current is None:
            return
        if previous is not None and self._last_changes:
            reply = QMessageBox.question(
                self,
                "放棄未儲存變更？",
                f"Type {self._type_id} 尚有 {len(self._last_changes)} 項變更。\n"
                "切換 Type 會放棄這些變更，是否繼續？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                self.type_list.blockSignals(True)
                self.type_list.setCurrentItem(previous)
                self.type_list.blockSignals(False)
                return
        type_id = str(current.data(Qt.ItemDataRole.UserRole))
        config = load_config(type_id, strict=True)
        self._type_id = type_id
        self._original = deepcopy(config)
        self._populate(config)

    def _populate(self, config: dict):
        self._building = True
        self.table.blockSignals(True)
        self._clear_scalar_form()
        for field in EDITABLE_SCALAR_FIELDS:
            if field not in config:
                continue
            edit = QLineEdit(str(config[field]))
            edit.textChanged.connect(self._schedule_review)
            edit.setToolTip(f"設定鍵：{field}")
            self.scalar_form.addRow(
                f"{SCALAR_FIELD_LABELS.get(field, field)}：", edit
            )
            self._scalar_edits[field] = edit
        self.scalar_group.setVisible(bool(self._scalar_edits))

        headers = table_headers(config)
        rows = config.get("table", [])
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(
            [TABLE_FIELD_LABELS.get(header, header) for header in headers]
        )
        for index, field in enumerate(headers):
            header_item = self.table.horizontalHeaderItem(index)
            if header_item is not None:
                header_item.setToolTip(f"設定鍵：{field}")
        self.table.setRowCount(len(rows))
        for row_index, row in enumerate(rows):
            for col_index, field in enumerate(headers):
                item = QTableWidgetItem(str(row.get(field, "")))
                item.setToolTip(f"{field}｜原始值：{row.get(field, '')}")
                self.table.setItem(row_index, col_index, item)

        structure = readonly_structure(config)
        self.readonly_browser.setPlainText(
            json.dumps(structure, ensure_ascii=False, indent=2)
        )
        self.type_title_label.setText(
            f"Type {self._type_id} — {config.get('name') or '未命名型號'}"
        )
        source = config.get("source") or "未記錄"
        version = config.get("version") or "?"
        updated = config.get("data_updated_at") or config.get("last_modified") or "未記錄"
        self.type_meta_label.setText(
            f"資料版本 {version}　｜　最後更新 {updated}　｜　來源 {source}"
        )
        self.source_edit.clear()
        self.description_edit.clear()
        self.confirm_large_change_checkbox.setChecked(False)
        self.confirm_large_change_checkbox.setVisible(False)
        self.editor_tabs.setCurrentIndex(0)
        self.table.blockSignals(False)
        self._building = False
        self._refresh_review()

    def _schedule_review(self, *_args):
        if not self._building:
            self._review_timer.start()

    def _refresh_review(self):
        if self._building or self._original is None:
            return
        try:
            candidate = self._candidate()
            changes = diff_configs(self._original, candidate)
            schema_issues = validate_config(candidate)
            sanity_issues = check_config_sanity(
                candidate, original=self._original
            )
        except (TypeError, ValueError) as exc:
            self._last_changes = [ConfigDiff("輸入格式", "有效值", str(exc))]
            self.change_status_label.setText("輸入格式有誤")
            self.change_status_label.setStyleSheet(
                f"font-weight: bold; color: {TOKENS['color']['status_error']};"
            )
            self.issues_label.setText(
                f'<span style="color:{TOKENS["color"]["status_error"]}">● {exc}</span>'
            )
            self.diff_browser.setPlainText("請先修正輸入格式，才能產生差異。")
            self.reset_button.setEnabled(True)
            self.save_button.setEnabled(False)
            return

        self._last_changes = changes
        self._apply_change_highlights(candidate)
        self._show_validation(schema_issues, sanity_issues)
        self.diff_browser.setPlainText(
            "\n".join(change.format() for change in changes)
            if changes
            else "尚未修改任何資料。"
        )

        errors = schema_issues + [
            issue.message for issue in sanity_issues if issue.severity == "error"
        ]
        warnings = [
            issue for issue in sanity_issues if issue.severity == "warning"
        ]
        evidence_ready = bool(
            self.source_edit.text().strip()
            and self.description_edit.toPlainText().strip()
        )
        warning_confirmed = not warnings or self.confirm_large_change_checkbox.isChecked()
        ready = bool(changes) and not errors and warning_confirmed and evidence_ready

        if not changes:
            message = "尚未修改"
            color = TOKENS["color"]["text_muted"]
        elif errors:
            message = f"{len(changes)} 項變更，目前有錯誤"
            color = TOKENS["color"]["status_error"]
        elif warnings and not warning_confirmed:
            message = f"{len(changes)} 項變更，需確認大幅變動"
            color = TOKENS["color"]["status_warn"]
        elif not evidence_ready:
            message = f"{len(changes)} 項變更，補齊圖號／版次與說明後即可儲存"
            color = TOKENS["color"]["status_warn"]
        else:
            message = f"{len(changes)} 項變更，已通過檢查，可安全儲存"
            color = TOKENS["color"]["status_ok"]
        self.change_status_label.setText(message)
        self.change_status_label.setStyleSheet(
            f"font-weight: bold; color: {color};"
        )
        self.reset_button.setEnabled(bool(changes))
        self.save_button.setEnabled(ready)

    def _apply_change_highlights(self, candidate: dict):
        changed_background = QColor(TOKENS["color"]["primary_weak"])
        normal_background = QColor(Qt.GlobalColor.transparent)
        for field, edit in self._scalar_edits.items():
            changed = candidate.get(field) != self._original.get(field)
            edit.setStyleSheet(
                (
                    f"background: {TOKENS['color']['primary_weak']}; "
                    f"border-color: {TOKENS['color']['status_warn']};"
                )
                if changed
                else ""
            )

        headers = table_headers(self._original)
        original_rows = self._original.get("table", [])
        candidate_rows = candidate.get("table", [])
        self.table.blockSignals(True)
        try:
            for row_index in range(self.table.rowCount()):
                for col_index, field in enumerate(headers):
                    item = self.table.item(row_index, col_index)
                    if item is None:
                        continue
                    before = original_rows[row_index].get(field, "")
                    after = candidate_rows[row_index].get(field, "")
                    changed = before != after
                    item.setBackground(
                        changed_background if changed else normal_background
                    )
                    item.setToolTip(
                        f"{field}｜原始值：{before}"
                        + (f"｜目前值：{after}" if changed else "")
                    )
        finally:
            self.table.blockSignals(False)

    def _on_reset_changes(self):
        if self._original is None or not self._last_changes:
            return
        reply = QMessageBox.question(
            self,
            "復原未儲存變更",
            f"確定放棄目前 {len(self._last_changes)} 項未儲存變更？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._populate(self._original)

    def _candidate(self) -> dict:
        if self._original is None:
            raise ValueError("尚未選擇 Type")
        scalars = {}
        for field, edit in self._scalar_edits.items():
            text = edit.text()
            try:
                scalars[field] = _coerce_text(text, self._original[field])
            except ValueError as exc:
                label = SCALAR_FIELD_LABELS.get(field, field)
                raise ValueError(
                    f"「{label}」格式不正確，目前輸入「{text or '空白'}」"
                ) from exc

        headers = table_headers(self._original)
        rows = []
        original_rows = self._original.get("table", [])
        for row_index in range(self.table.rowCount()):
            row = {}
            for col_index, field in enumerate(headers):
                item = self.table.item(row_index, col_index)
                text = item.text() if item else ""
                exemplar = original_rows[row_index].get(field, "")
                try:
                    row[field] = _coerce_text(text, exemplar)
                except ValueError as exc:
                    label = TABLE_FIELD_LABELS.get(field, field)
                    raise ValueError(
                        f"第 {row_index + 1} 列「{label}」格式不正確，"
                        f"目前輸入「{text or '空白'}」"
                    ) from exc
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
        if lines:
            self.issues_label.setText("<br>".join(lines))
        else:
            self.issues_label.setText(
                f'<span style="color:{TOKENS["color"]["status_ok"]}">✓ 自動檢查通過</span>'
            )
        has_warning = any(issue.severity == "warning" for issue in sanity_issues)
        self.confirm_large_change_checkbox.setVisible(has_warning)
        if not has_warning:
            self.confirm_large_change_checkbox.blockSignals(True)
            self.confirm_large_change_checkbox.setChecked(False)
            self.confirm_large_change_checkbox.blockSignals(False)

    def _show_issues(self, issues: list[str]) -> None:
        self._show_validation(issues, [])

    def _on_check(self):
        self._refresh_review()
        if self.save_button.isEnabled() or not self._last_changes:
            self.statusMessage.emit(f"Type {self._type_id} config 檢查通過")

    def _on_diff(self):
        self._refresh_review()

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
        self._show_golden_guidance()
        self.configSaved.emit(self._type_id)

    def _show_golden_guidance(self) -> None:
        message = QMessageBox(self)
        message.setWindowTitle("資料已變更 — 請驗證基線")
        message.setIcon(QMessageBox.Icon.Warning)
        message.setText(
            f"型號 {self._type_id} 資料已變更。請立即執行基線驗證；"
            "若 golden 轉紅且此變更係刻意，依裁決流程更新基線並記錄依據。"
        )
        copy_button = message.addButton(
            "複製驗證指令", QMessageBox.ButtonRole.ActionRole
        )
        message.addButton(QMessageBox.StandardButton.Ok)
        message.exec()
        if message.clickedButton() is copy_button:
            QApplication.clipboard().setText(validation_commands())
