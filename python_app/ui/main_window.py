"""
PyQt6 主視窗
IEC 管架支撐分析工具

三面板佈局:
  左: 輸入清單 (QListWidget, 可勾選/點選)
  中: 結果表格
  右: Side Panel (選中項目的設定, 可單筆覆寫)
"""
import json
import os
from dataclasses import replace
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QSplitter, QGroupBox, QMessageBox,
    QComboBox, QHeaderView, QStatusBar, QTabWidget, QSpinBox,
    QDoubleSpinBox, QLineEdit, QFormLayout, QDialog,
    QListWidget, QListWidgetItem, QRadioButton, QButtonGroup,
    QFrame, QScrollArea, QTextBrowser, QInputDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon, QImage, QPixmap, QShortcut, QKeySequence

try:
    import fitz  # PyMuPDF
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False

from core.calculator import (
    analyze_single, get_supported_types,
    set_analysis_setting, get_analysis_setting,
)
from core.models import AnalysisResult
from core.parser import get_type_code, get_part, get_lookup_value
from core.project_aggregation import ProjectInputRow, analyze_project_rows
from core.config_loader import load_config, get_type_table_as_dict
from ui.type_manager import TypeManagerWidget, load_catalog
from ui.ontology_browser import OntologyBrowserWidget
from ui.material_cutting_page import MaterialCuttingPage

# PDF/資源路徑
_UI_DIR = os.path.dirname(os.path.abspath(__file__))
_APP_DIR = os.path.dirname(_UI_DIR)
_PDF_DIR = os.path.join(_APP_DIR, "assets", "Type")

# 結果表格群組背景色 (header_row_color, body_row_color)
_RESULT_GROUP_COLORS = [
    ("#E2EDF8", "#FAFCFE"),   # blue-gray
    ("#E8EEF5", "#FFFFFF"),   # cool gray
    ("#E5F0F4", "#FBFDFE"),   # steel blue
    ("#EDF1F6", "#FFFFFF"),   # neutral gray
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IEC 管架支撐分析工具 (Python Edition)")
        self.setMinimumSize(1300, 720)
        self._project_rows = []    # list[ProjectInputRow]
        self._results = []
        self._project_result = None
        self._selected_index = -1
        self._apply_stylesheet()
        self._init_ui()

    # ══════════════════════════════════════════
    #  全域樣式
    # ══════════════════════════════════════════
    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #F5F6FA;
            }
            QTabWidget::pane {
                border: 1px solid #C8CDD5;
                background: #FFFFFF;
                border-radius: 0 4px 4px 4px;
            }
            QTabBar::tab {
                padding: 7px 18px;
                background: #E8ECF1;
                color: #555;
                border: 1px solid #C8CDD5;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                font-size: 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #FFFFFF;
                color: #1565C0;
                font-weight: bold;
                border-bottom: 2px solid #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background: #DDE3EC;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #333;
                border: 1px solid #C8CDD5;
                border-radius: 6px;
                margin-top: 18px;
                padding: 12px 8px 8px 8px;
                background: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #1565C0;
                font-size: 12px;
            }
            QPushButton {
                padding: 5px 12px;
                border: 1px solid #B8C0CC;
                border-radius: 4px;
                background-color: #F0F2F5;
                color: #333;
                font-size: 12px;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                border-color: #8898B0;
            }
            QPushButton:pressed {
                background-color: #D0DAEA;
            }
            QPushButton:disabled {
                color: #AAA;
                background-color: #EAEAEA;
                border-color: #D0D0D0;
            }
            QLineEdit, QComboBox {
                border: 1px solid #C0C8D4;
                border-radius: 4px;
                padding: 4px 8px;
                background: #FFFFFF;
                color: #222;
                selection-background-color: #BBDEFB;
                font-size: 12px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #1565C0;
            }
            QListWidget {
                border: 1px solid #C0C8D4;
                border-radius: 4px;
                background: #FFFFFF;
                outline: none;
            }
            QListWidget::item {
                padding: 3px 6px;
                border-bottom: 1px solid #EEF0F3;
            }
            QListWidget::item:selected {
                background: #BBDEFB;
                color: #0D47A1;
                border-radius: 2px;
            }
            QListWidget::item:hover:!selected {
                background: #E8F0F8;
            }
            QTableWidget {
                border: 1px solid #C0C8D4;
                border-radius: 4px;
                gridline-color: #E4E8EE;
                background: #FFFFFF;
                alternate-background-color: #F8FAFB;
                selection-background-color: #BBDEFB;
                font-size: 11px;
            }
            QHeaderView::section {
                background-color: #EEF2F8;
                color: #2C3E60;
                font-weight: bold;
                font-size: 11px;
                border: none;
                border-right: 1px solid #D2D8E2;
                border-bottom: 1px solid #BBDEFB;
                padding: 5px 8px;
            }
            QScrollBar:vertical {
                width: 10px;
                background: #F0F2F5;
            }
            QScrollBar::handle:vertical {
                background: #C0CBD8;
                border-radius: 5px;
                min-height: 20px;
            }
            QStatusBar {
                color: #666;
                font-size: 12px;
                background: #F0F2F5;
                border-top: 1px solid #D0D5DC;
            }
            QSplitter::handle {
                background: #D0D5DC;
                width: 2px;
            }
        """)

    # ══════════════════════════════════════════
    #  UI 初始化
    # ══════════════════════════════════════════
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)

        # ── 主 Tab ──
        self.main_tabs = QTabWidget()
        self.main_tabs.setFont(QFont("Microsoft JhengHei UI", 10))

        # Tab 1: 分析頁面
        analysis_page = self._build_analysis_page()
        self.main_tabs.addTab(analysis_page, "📊 重量分析")

        # Tab 2: 材料合計 / 下料
        self.material_cutting_page = MaterialCuttingPage()
        self.material_cutting_page.btn_generate.clicked.connect(self._on_generate_material)
        self.main_tabs.addTab(self.material_cutting_page, "📦 材料合計 / 下料")

        # Tab 3: Type 管理器
        self.type_manager = TypeManagerWidget()
        self.main_tabs.addTab(self.type_manager, "📋 Type 總覽")

        # Tab 4: 支撐架構
        self.ontology_browser = OntologyBrowserWidget()
        self.main_tabs.addTab(self.ontology_browser, "🌳 支撐架構")

        main_layout.addWidget(self.main_tabs)
        self.statusBar().showMessage("就緒 — 新增支撐編碼後按「開始分析」")
        self._install_shortcuts()

    def _install_shortcuts(self):
        """Keyboard shortcuts for high-volume input work."""
        self._shortcuts = [
            QShortcut(
                QKeySequence("Delete"),
                self.item_list,
                activated=self._on_delete_item,
            ),
            QShortcut(
                QKeySequence("F2"),
                self.item_list,
                activated=self._on_edit_current_item,
            ),
            QShortcut(
                QKeySequence("Ctrl+Return"),
                self,
                activated=self._on_batch_paste,
            ),
            QShortcut(
                QKeySequence("Ctrl+Enter"),
                self,
                activated=self._on_batch_paste,
            ),
        ]

    def _build_analysis_page(self) -> QWidget:
        """建構分析頁面 (原始三面板)"""
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # ── 頂部工具列 ──
        toolbar = QHBoxLayout()
        supported = get_supported_types()
        info_label = QLabel(f"已支援 Type: {', '.join(supported)}")
        info_label.setStyleSheet("color: #555; font-size: 12px;")
        toolbar.addWidget(info_label)
        toolbar.addStretch()

        toolbar.addWidget(QLabel("全域上段管材質:"))
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "SUS304", "SUS316", "A53Gr.B", "A106Gr.B",
            "A335-P11", "A335-P22", "A312-TP304", "A312-TP316",
        ])
        self.material_combo.setEditable(True)
        self.material_combo.setCurrentText("SUS304")
        self.material_combo.currentTextChanged.connect(self._on_material_changed)
        toolbar.addWidget(self.material_combo)

        self.btn_config = QPushButton("⚙ Type 資料管理")
        self.btn_config.clicked.connect(self._on_open_config)
        toolbar.addWidget(self.btn_config)

        page_layout.addLayout(toolbar)

        # ── 三面板 ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # [左] 輸入清單
        left_panel = self._build_left_panel()
        splitter.addWidget(left_panel)

        # [中] 結果表格
        center_panel = self._build_center_panel()
        splitter.addWidget(center_panel)

        # [右] Side Panel
        self.side_panel = SidePanel()
        self.side_panel.overrideChanged.connect(self._on_override_changed)
        splitter.addWidget(self.side_panel)

        splitter.setSizes([260, 680, 300])
        page_layout.addWidget(splitter)

        return page

    def _build_left_panel(self):
        panel = QGroupBox("輸入清單")
        layout = QVBoxLayout(panel)

        # 新增列
        add_row = QHBoxLayout()
        self.add_input = QLineEdit()
        self.add_input.setPlaceholderText("輸入編碼, e.g. 01-2B-05A")
        self.add_input.setFont(QFont("Consolas", 11))
        self.add_input.returnPressed.connect(self._on_add_item)
        add_row.addWidget(self.add_input)
        btn_add = QPushButton("+")
        btn_add.setFixedWidth(32)
        btn_add.clicked.connect(self._on_add_item)
        add_row.addWidget(btn_add)
        layout.addLayout(add_row)

        # 清單
        self.item_list = QListWidget()
        self.item_list.currentRowChanged.connect(self._on_item_selected)
        self.item_list.itemChanged.connect(self._on_item_check_changed)
        self.item_list.setFont(QFont("Consolas", 10))
        layout.addWidget(self.item_list)

        # 按鈕列
        btn_row1 = QHBoxLayout()
        btn_batch = QPushButton("批次貼上...")
        btn_batch.clicked.connect(self._on_batch_paste)
        btn_row1.addWidget(btn_batch)
        btn_qty = QPushButton("設定組數...")
        btn_qty.clicked.connect(self._on_set_quantities)
        btn_row1.addWidget(btn_qty)
        btn_load = QPushButton("從檔案載入...")
        btn_load.clicked.connect(self._on_load_file)
        btn_row1.addWidget(btn_load)
        layout.addLayout(btn_row1)

        btn_row2 = QHBoxLayout()
        btn_del = QPushButton("刪除選中")
        btn_del.clicked.connect(self._on_delete_item)
        btn_row2.addWidget(btn_del)
        btn_clear = QPushButton("全部清除")
        btn_clear.clicked.connect(self._on_clear_all)
        btn_row2.addWidget(btn_clear)
        layout.addLayout(btn_row2)

        # 分析按鈕
        self.btn_analyze = QPushButton("▶ 開始分析")
        self.btn_analyze.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; "
            "border: 1px solid #1565C0; padding: 8px; "
            "font-size: 14px; font-weight: bold; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1565C0; }"
            "QPushButton:pressed { background-color: #0D47A1; }"
            "QPushButton:disabled { background-color: #B0BEC5; "
            "border-color: #90A4AE; color: #ECEFF1; }"
        )
        self.btn_analyze.clicked.connect(self._on_analyze)
        layout.addWidget(self.btn_analyze)

        return panel

    def _build_center_panel(self):
        panel = QGroupBox("分析結果")
        layout = QVBoxLayout(panel)

        self.result_table = QTableWidget()
        self._set_project_result_headers()
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.result_table.setAlternatingRowColors(False)
        self.result_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.result_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.result_table.verticalHeader().setDefaultSectionSize(22)
        self.result_table.verticalHeader().setVisible(False)
        layout.addWidget(self.result_table)

        # 匯出列
        export_row = QHBoxLayout()
        self.export_format = QComboBox()
        self.export_format.addItems(["Excel (.xlsx)", "CSV (.csv)", "PDF (.pdf)"])
        export_row.addWidget(QLabel("匯出格式:"))
        export_row.addWidget(self.export_format)
        self.btn_export = QPushButton("匯出結果")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._on_export)
        export_row.addWidget(self.btn_export)
        export_row.addStretch()
        self.total_weight_label = QLabel("  總重量: -- kg  ")
        self.total_weight_label.setFont(QFont("Microsoft JhengHei UI", 12, QFont.Weight.Bold))
        self.total_weight_label.setStyleSheet(
            "color: #0D47A1; background: #EAF4FF;"
            "border: 1px solid #BBDEFB; border-radius: 6px;"
            "padding: 4px 12px;"
        )
        self.total_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        export_row.addWidget(self.total_weight_label)
        layout.addLayout(export_row)

        return panel

    def _set_project_result_headers(self):
        """Result table columns: simplified 13-column pivot-friendly layout."""
        self.result_table.setColumnCount(13)
        self.result_table.setHorizontalHeaderLabels([
            "型號", "組數", "項次", "品名", "規格",
            "材質", "長度(mm)", "寬度(mm)",
            "單件數量", "總數量", "總重(kg)", "屬性", "備註",
        ])

    # ══════════════════════════════════════════
    #  清單操作
    # ══════════════════════════════════════════
    def _on_add_item(self):
        text = self.add_input.text().strip()
        if not text:
            return
        self._add_item_to_list(text)
        self.add_input.clear()
        self.add_input.setFocus()

    def _add_item_to_list(self, text: str, invalidate: bool = True):
        idx = len(self._project_rows)
        self._project_rows.append(ProjectInputRow(designation=text))
        item_widget = QListWidgetItem(text)
        item_widget.setCheckState(Qt.CheckState.Checked)
        self._update_item_display(idx, item_widget)
        self.item_list.addItem(item_widget)
        if invalidate:
            self._invalidate_analysis_outputs("輸入清單已變更，請重新分析")

    def _update_item_display(self, idx: int, item_widget: QListWidgetItem = None):
        """更新清單顯示文字 (有覆寫時加標記)"""
        if item_widget is None:
            item_widget = self.item_list.item(idx)
        if item_widget is None:
            return
        row = self._project_rows[idx]
        text = row.designation
        overrides = row.overrides or {}
        tags = []
        if row.quantity != 1:
            tags.append(f"{row.quantity}組")
        if overrides.get("connection"):
            tags.append("Tee" if overrides["connection"] == "tee" else "Elbow")
        if overrides.get("upper_material"):
            tags.append(overrides["upper_material"])
        if any(overrides.get(k) for k in ("pipe_size", "schedule", "l_value")):
            tags.append("自訂值")

        if tags:
            item_widget.setText(f"{text}  ◆ [{', '.join(tags)}]")
            item_widget.setForeground(QColor("#1565C0"))
        else:
            item_widget.setText(text)
            item_widget.setForeground(QColor("black"))

    def _refresh_item_list_display(self):
        """Refresh all list labels and checkbox states from project rows."""
        self.item_list.blockSignals(True)
        for idx, row in enumerate(self._project_rows):
            item_widget = self.item_list.item(idx)
            if item_widget is None:
                continue
            item_widget.setCheckState(
                Qt.CheckState.Checked if row.enabled else Qt.CheckState.Unchecked
            )
            self._update_item_display(idx, item_widget)
        self.item_list.blockSignals(False)

    def _on_batch_paste(self):
        """批次貼上多筆"""
        dlg = QDialog(self)
        dlg.setWindowTitle("批次貼上")
        dlg.setMinimumSize(400, 300)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("每行一筆支撐編碼:"))
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Consolas", 11))
        text_edit.setPlaceholderText(
            "01-2B-05A\n01-3B-08B\n05-L50-05L\n16-4B-08"
        )
        lay.addWidget(text_edit)
        count_label = QLabel("已輸入 0 筆")
        count_label.setStyleSheet("color: #666; font-size: 12px;")
        lay.addWidget(count_label)
        btn = QPushButton("加入清單")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)

        def parse_lines() -> list[str]:
            return [
                line.strip()
                for line in text_edit.toPlainText().splitlines()
                if line.strip()
            ]

        def duplicate_count(lines: list[str]) -> int:
            seen = {row.designation.casefold() for row in self._project_rows}
            pasted = set()
            duplicates = 0
            for line in lines:
                key = line.casefold()
                if key in seen or key in pasted:
                    duplicates += 1
                pasted.add(key)
            return duplicates

        def update_count():
            lines = parse_lines()
            dupes = duplicate_count(lines)
            if dupes:
                count_label.setText(f"已輸入 {len(lines)} 筆；其中 {dupes} 筆重複")
                count_label.setStyleSheet("color: #E65100; font-size: 12px;")
            else:
                count_label.setText(f"已輸入 {len(lines)} 筆")
                count_label.setStyleSheet("color: #666; font-size: 12px;")

        text_edit.textChanged.connect(update_count)
        if dlg.exec():
            lines = parse_lines()
            if not lines:
                return
            for line in lines:
                self._add_item_to_list(line, invalidate=False)
            self._invalidate_analysis_outputs("批次貼上已加入清單，請重新分析")
            self.statusBar().showMessage(f"已加入 {len(lines)} 筆支撐編碼")

    def _on_load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "載入支撐清單", "",
            "文字檔 (*.txt);;CSV (*.csv);;所有檔案 (*)"
        )
        if filepath:
            added = 0
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._add_item_to_list(line, invalidate=False)
                        added += 1
            if added:
                self._invalidate_analysis_outputs("載入檔案已更新清單，請重新分析")
            self.statusBar().showMessage(f"已載入 {added} 筆: {filepath}")

    def _on_set_quantities(self):
        """Two-stage quantity editor: designation list stays unchanged."""
        if not self._project_rows:
            QMessageBox.warning(self, "提示", "請先新增支撐編碼")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("設定組數")
        dlg.setMinimumSize(520, 420)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("手動修改 quantity，或在下方逐列貼入組數。"))

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["designation", "quantity"])
        table.setRowCount(len(self._project_rows))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        for idx, row in enumerate(self._project_rows):
            desig_item = QTableWidgetItem(row.designation)
            desig_item.setFlags(desig_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            table.setItem(idx, 0, desig_item)
            table.setItem(idx, 1, QTableWidgetItem(str(row.quantity)))

        lay.addWidget(table)

        lay.addWidget(QLabel("批次貼入組數 (每行一個數字，逐列對應目前清單):"))
        qty_text = QTextEdit()
        qty_text.setPlaceholderText("2\n1\n1\n4")
        qty_text.setMaximumHeight(90)
        lay.addWidget(qty_text)

        btn_row = QHBoxLayout()
        btn_apply = QPushButton("套用批次組數")
        btn_ok = QPushButton("確定")
        btn_cancel = QPushButton("取消")
        btn_row.addWidget(btn_apply)
        btn_row.addStretch()
        btn_row.addWidget(btn_ok)
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

        def parse_quantity(text: str, row_number: int) -> int:
            try:
                value = int(text.strip())
            except ValueError as exc:
                raise ValueError(f"第 {row_number} 列組數不是整數: {text!r}") from exc
            if value <= 0:
                raise ValueError(f"第 {row_number} 列組數必須大於 0")
            return value

        def apply_batch_quantities():
            lines = [line.strip() for line in qty_text.toPlainText().splitlines() if line.strip()]
            if not lines:
                return
            if len(lines) > len(self._project_rows):
                QMessageBox.warning(
                    dlg,
                    "組數列數過多",
                    f"貼入 {len(lines)} 列組數，但目前只有 {len(self._project_rows)} 筆項目。",
                )
                return
            try:
                quantities = [parse_quantity(line, idx + 1) for idx, line in enumerate(lines)]
            except ValueError as exc:
                QMessageBox.warning(dlg, "組數格式錯誤", str(exc))
                return
            for idx, quantity in enumerate(quantities):
                table.setItem(idx, 1, QTableWidgetItem(str(quantity)))

        btn_apply.clicked.connect(apply_batch_quantities)
        btn_ok.clicked.connect(dlg.accept)
        btn_cancel.clicked.connect(dlg.reject)

        if not dlg.exec():
            return

        updated_rows = []
        try:
            for idx, row in enumerate(self._project_rows):
                qty_item = table.item(idx, 1)
                quantity = parse_quantity(qty_item.text() if qty_item else "", idx + 1)
                updated_rows.append(replace(row, quantity=quantity))
        except ValueError as exc:
            QMessageBox.warning(self, "組數格式錯誤", str(exc))
            return

        self._project_rows = updated_rows
        self._refresh_item_list_display()
        self._clear_analysis_outputs()
        total_supports = sum(row.quantity for row in self._project_rows if row.enabled)
        self.statusBar().showMessage(f"已更新組數，啟用項目合計 {total_supports} 組")

    def _clear_analysis_outputs(self):
        """Clear stale analysis/material outputs after project inputs change."""
        self._results.clear()
        self._project_result = None
        self.result_table.setRowCount(0)
        self.btn_export.setEnabled(False)
        self.total_weight_label.setText("總重量: -- kg")
        self.material_cutting_page.set_results_ready(False)
        self.material_cutting_page.clear_outputs()
        self.side_panel.mark_result_stale()

    def _invalidate_analysis_outputs(self, message: str = ""):
        """Invalidate analysis/material outputs after input rows change."""
        had_outputs = (
            bool(self._results)
            or self._project_result is not None
            or self.result_table.rowCount() > 0
        )
        self._clear_analysis_outputs()
        if message:
            suffix = "，已清除舊結果" if had_outputs else ""
            self.statusBar().showMessage(f"{message}{suffix}")

    def _on_item_check_changed(self, item: QListWidgetItem):
        row = self.item_list.row(item)
        if row < 0 or row >= len(self._project_rows):
            return
        enabled = item.checkState() == Qt.CheckState.Checked
        if self._project_rows[row].enabled == enabled:
            return
        self._project_rows[row] = replace(self._project_rows[row], enabled=enabled)
        self._invalidate_analysis_outputs("啟用項目已變更，請重新分析")

    def _on_edit_current_item(self):
        row = self.item_list.currentRow()
        if row < 0 or row >= len(self._project_rows):
            return
        old_designation = self._project_rows[row].designation
        new_designation, accepted = QInputDialog.getText(
            self,
            "編輯支撐編碼",
            "支撐編碼:",
            text=old_designation,
        )
        if not accepted:
            return
        new_designation = new_designation.strip()
        if not new_designation or new_designation == old_designation:
            return
        overrides = self._project_rows[row].overrides
        if get_type_code(new_designation) != get_type_code(old_designation):
            overrides = None
        self._project_rows[row] = replace(
            self._project_rows[row],
            designation=new_designation,
            overrides=overrides,
        )
        self._update_item_display(row)
        self.side_panel.show_item(
            row,
            new_designation,
            self._project_rows[row].overrides or {},
        )
        self._invalidate_analysis_outputs("支撐編碼已編輯，請重新分析")

    def _on_delete_item(self):
        row = self.item_list.currentRow()
        if row < 0:
            return
        deleted_designation = self._project_rows[row].designation
        self.item_list.blockSignals(True)
        self.item_list.takeItem(row)
        self.item_list.blockSignals(False)
        self._project_rows.pop(row)
        self._selected_index = -1
        self._refresh_item_list_display()
        self._invalidate_analysis_outputs("輸入清單已變更，請重新分析")
        if self._project_rows:
            self.item_list.setCurrentRow(min(row, len(self._project_rows) - 1))
        else:
            self.side_panel.clear_panel()
        self.statusBar().showMessage(f"已刪除 {deleted_designation}，請重新分析")

    def _on_clear_all(self):
        if not self._project_rows and not self._results:
            return
        reply = QMessageBox.question(
            self,
            "確認全部清除",
            "確定要清除所有支撐編碼與目前分析結果嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self.item_list.clear()
        self._project_rows.clear()
        self._clear_analysis_outputs()
        self._selected_index = -1
        self.side_panel.clear_panel()
        self.statusBar().showMessage("已清除")

    def _on_item_selected(self, row):
        """清單項目被點選 → 更新 Side Panel"""
        if row < 0 or row >= len(self._project_rows):
            self._selected_index = -1
            self.side_panel.clear_panel()
            return
        # 同步 checkbox 狀態
        item_widget = self.item_list.item(row)
        self._project_rows[row] = replace(
            self._project_rows[row],
            enabled=item_widget.checkState() == Qt.CheckState.Checked,
        )
        self._selected_index = row
        project_row = self._project_rows[row]
        self.side_panel.show_item(
            row, project_row.designation, project_row.overrides or {}
        )
        # 若已有分析結果，一併顯示
        if 0 <= row < len(self._results):
            self.side_panel.update_result(self._results[row])

    def _on_override_changed(self, idx: int, overrides: dict):
        """Side Panel 發出覆寫變更"""
        # 移除空值
        clean = {k: v for k, v in overrides.items() if v}
        if 0 <= idx < len(self._project_rows):
            old_clean = self._project_rows[idx].overrides or {}
            if old_clean == clean:
                return
            self._project_rows[idx] = replace(
                self._project_rows[idx],
                overrides=clean or None,
            )
            self._update_item_display(idx)
            self._invalidate_analysis_outputs("覆寫設定已變更，請重新分析")

    # ══════════════════════════════════════════
    #  分析
    # ══════════════════════════════════════════
    def _on_analyze(self):
        if not self._project_rows:
            QMessageBox.warning(self, "提示", "請先新增支撐編碼")
            return

        # 同步 checkbox 狀態
        for i in range(self.item_list.count()):
            w = self.item_list.item(i)
            self._project_rows[i] = replace(
                self._project_rows[i],
                enabled=w.checkState() == Qt.CheckState.Checked,
            )

        self._project_result = analyze_project_rows(self._project_rows)
        self._results = [row.scaled_result for row in self._project_result.rows]
        self._display_results()
        self.btn_export.setEnabled(True)

        error_count = sum(1 for r in self._results if r.error)
        self.statusBar().showMessage(
            f"分析完成: {len(self._results)} 筆 / "
            f"{self._project_result.total_support_count} 組 "
            f"(成功 {len(self._results) - error_count}, 錯誤 {error_count})"
        )

        # 更新 side panel 的計算結果
        if 0 <= self._selected_index < len(self._results):
            self.side_panel.update_result(self._results[self._selected_index])

        # 啟用材料合計 Tab
        self.material_cutting_page.set_results_ready(True)

    def _display_results(self):
        self.result_table.setRowCount(0)
        total_weight = 0.0

        if self._project_result is not None:
            self._display_project_results()
            return

        for result in self._results:
            if result.error:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                desc = QTableWidgetItem(result.fullstring)
                desc.setForeground(QColor("red"))
                self.result_table.setItem(row, 0, desc)
                err = QTableWidgetItem(f"錯誤: {result.error}")
                err.setForeground(QColor("red"))
                self.result_table.setItem(row, 2, err)
                continue

            for entry in result.entries:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                self.result_table.setItem(row, 0, QTableWidgetItem(
                    result.fullstring if entry.item_no == 1 else ""
                ))
                self.result_table.setItem(row, 1, QTableWidgetItem(str(entry.item_no)))
                self.result_table.setItem(row, 2, QTableWidgetItem(entry.name))
                self.result_table.setItem(row, 3, QTableWidgetItem(entry.spec))
                self.result_table.setItem(row, 4, QTableWidgetItem(str(entry.length)))
                self.result_table.setItem(row, 5, QTableWidgetItem(
                    str(entry.width) if entry.width else ""
                ))
                self.result_table.setItem(row, 6, QTableWidgetItem(entry.material))
                self.result_table.setItem(row, 7, QTableWidgetItem(str(entry.quantity)))
                self.result_table.setItem(row, 8, QTableWidgetItem(f"{entry.unit_weight:.2f}"))
                self.result_table.setItem(row, 9, QTableWidgetItem(f"{entry.weight_output:.2f}"))
                self.result_table.setItem(row, 10, QTableWidgetItem(entry.unit))
                self.result_table.setItem(row, 11, QTableWidgetItem(entry.category))
                total_weight += entry.weight_output

        self.total_weight_label.setText(f"總重量: {total_weight:.2f} kg")

    def _display_project_results(self):
        """Display project results in simplified 13-column flat layout with visual grouping."""
        # 數字欄 (右對齊): 長度(6), 寬度(7), 單件數(8), 總數(9), 總重(10)
        RIGHT_ALIGN = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        CENTER = Qt.AlignmentFlag.AlignCenter
        LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        # col_idx → alignment
        COL_ALIGN = {0: LEFT, 1: CENTER, 2: CENTER, 3: LEFT, 4: LEFT,
                     5: CENTER, 6: RIGHT_ALIGN, 7: RIGHT_ALIGN, 8: CENTER, 9: CENTER,
                     10: RIGHT_ALIGN, 11: CENTER, 12: LEFT}

        total_weight = 0.0
        g_idx = 0  # 群組色輪 index

        for row_result in self._project_result.rows:
            input_row = row_result.input_row
            single_result = row_result.single_result
            scaled_result = row_result.scaled_result
            hdr_color, body_color = _RESULT_GROUP_COLORS[g_idx % len(_RESULT_GROUP_COLORS)]
            g_idx += 1

            if single_result.error:
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                err_bg = QColor("#FDE8E8")
                err_fg = QColor("#C62828")
                for col in range(13):
                    cell = QTableWidgetItem()
                    cell.setBackground(err_bg)
                    self.result_table.setItem(row, col, cell)
                desc = self.result_table.item(row, 0)
                desc.setText(input_row.designation)
                desc.setForeground(err_fg)
                desc.setFont(QFont("Microsoft JhengHei UI", 10, QFont.Weight.Bold))
                self.result_table.item(row, 1).setText(str(input_row.quantity))
                err_cell = self.result_table.item(row, 3)
                err_cell.setText(f"⚠ {single_result.error}")
                err_cell.setForeground(err_fg)
                continue

            is_first = True
            group_weight = 0.0
            group_start_row = self.result_table.rowCount()

            for single_entry, scaled_entry in zip(single_result.entries, scaled_result.entries):
                row = self.result_table.rowCount()
                self.result_table.insertRow(row)
                bg = QColor(hdr_color if is_first else body_color)

                values = [
                    input_row.designation if is_first else "",           # 0 型號
                    str(input_row.quantity) if is_first else "",          # 1 組數
                    str(single_entry.item_no),                            # 2 項次
                    single_entry.name,                                    # 3 品名
                    single_entry.spec,                                    # 4 規格
                    single_entry.material,                                # 5 材質
                    str(single_entry.length) if single_entry.length else "",  # 6 長度
                    str(single_entry.width)  if single_entry.width  else "",  # 7 寬度
                    str(single_entry.quantity),                           # 8 單件數量
                    str(scaled_entry.quantity),                           # 9 總數量
                    f"{scaled_entry.weight_output:.3f}",                  # 10 總重
                    single_entry.category,                                # 11 屬性
                    single_entry.display_remark,                          # 12 備註
                ]
                for col, val in enumerate(values):
                    item = QTableWidgetItem(val)
                    item.setBackground(bg)
                    item.setTextAlignment(COL_ALIGN.get(col, LEFT))
                    if col == 0 and is_first:
                        item.setFont(QFont("Microsoft JhengHei UI", 10, QFont.Weight.Bold))
                        item.setForeground(QColor("#1A3A6B"))
                    elif col == 10:
                        item.setFont(QFont("Microsoft JhengHei UI", 10, QFont.Weight.Bold))
                    self.result_table.setItem(row, col, item)

                group_weight += scaled_entry.weight_output
                total_weight += scaled_entry.weight_output
                is_first = False

            # ── 群組小計列 ─────────────────────────────────────
            sub_row = self.result_table.rowCount()
            self.result_table.insertRow(sub_row)
            sub_bg = QColor(hdr_color)
            sub_label = QTableWidgetItem(
                f"  {input_row.designation}  合計 ({input_row.quantity} 組)"
            )
            sub_label.setBackground(sub_bg)
            sub_label.setForeground(QColor("#1A3A6B"))
            sub_label.setFont(QFont("Microsoft JhengHei UI", 10, QFont.Weight.Bold))
            sub_label.setTextAlignment(LEFT)
            self.result_table.setItem(sub_row, 0, sub_label)
            for col in range(1, 13):
                filler = QTableWidgetItem("")
                filler.setBackground(sub_bg)
                self.result_table.setItem(sub_row, col, filler)
            sub_wt = self.result_table.item(sub_row, 10)
            sub_wt.setText(f"{group_weight:.3f}")
            sub_wt.setTextAlignment(RIGHT_ALIGN)
            sub_wt.setForeground(QColor("#1A3A6B"))
            self.result_table.setRowHeight(sub_row, 20)

        self.total_weight_label.setText(f"  專案總重量:  {total_weight:.3f} kg  ")

    # ══════════════════════════════════════════
    #  匯出 / 設定
    # ══════════════════════════════════════════
    def _on_export(self):
        if not self._results:
            return
        fmt = self.export_format.currentText()
        if "xlsx" in fmt:
            filt, ext = "Excel (*.xlsx)", ".xlsx"
        elif "csv" in fmt:
            filt, ext = "CSV (*.csv)", ".csv"
        else:
            filt, ext = "PDF (*.pdf)", ".pdf"

        filepath, _ = QFileDialog.getSaveFileName(
            self, "匯出結果", f"analysis_result{ext}", filt
        )
        if not filepath:
            return
        try:
            if ext == ".xlsx":
                from export.excel_export import (
                    export_project_workbook,
                    export_to_excel,
                )
                if self._project_result is not None:
                    export_project_workbook(self._project_result, filepath)
                else:
                    export_to_excel(self._results, filepath)
            elif ext == ".csv":
                from export.csv_export import export_to_csv
                export_to_csv(self._results, filepath)
            else:
                from export.pdf_export import export_to_pdf
                export_to_pdf(self._results, filepath)
            QMessageBox.information(self, "匯出成功", f"已匯出至:\n{filepath}")
            self.statusBar().showMessage(f"已匯出: {filepath}")
        except ImportError as e:
            QMessageBox.warning(self, "缺少套件",
                f"匯出失敗，請安裝必要套件:\n{e}\n\n"
                "pip install openpyxl reportlab")
        except Exception as e:
            QMessageBox.critical(self, "匯出錯誤", str(e))

    def _on_generate_material(self):
        """材料合計 Tab 按下產生按鈕"""
        if not self._results:
            QMessageBox.warning(self, "提示", "請先在重量分析頁完成分析")
            return
        if self._project_result is not None:
            self.material_cutting_page.generate_project(self._project_result)
        else:
            self.material_cutting_page.generate(self._results)
        self.main_tabs.setCurrentWidget(self.material_cutting_page)

    def _on_material_changed(self, text):
        set_analysis_setting("upper_material", text)
        self.statusBar().showMessage(f"全域上段管材質: {text}")

    def _on_open_config(self):
        dialog = ConfigDialog(self)
        dialog.exec()


# ══════════════════════════════════════════════════
#  Side Panel — 單筆項目覆寫設定
# ══════════════════════════════════════════════════
class SidePanel(QGroupBox):
    """右側面板：上半 PDF 圖面預覽（可縮放/滑動），下半計算明細與覆寫設定"""

    overrideChanged = pyqtSignal(int, dict)
    _catalog_cache: list = []   # 類別層級快取，避免重複讀檔

    # ── 常用按鈕樣式 ─────────────────────────────────────────
    _ZOOM_BTN = (
        "QPushButton { font-size: 13px; font-weight: bold; background: #EEEEEE; "
        "border: 1px solid #CCC; color: #333; padding: 0; }"
        "QPushButton:hover { background: #BDBDBD; }"
    )
    _ZOOM_FIT_BTN = (
        "QPushButton { font-size: 10px; background: #EEEEEE; "
        "border: 1px solid #CCC; color: #333; padding: 0 6px; }"
        "QPushButton:hover { background: #BDBDBD; }"
    )

    def __init__(self):
        super().__init__("項目設定")
        self._idx = -1
        self._overrides = {}
        self._building = False
        self._preview_pixmap = None
        self._zoom_level = 1.0
        self._current_type_code = ""
        # form widget refs (reset each show_item call)
        self._rb_elbow = None
        self._rb_tee = None
        self._mat_combo = None
        self._pipe_edit = None
        self._sch_edit = None
        self._l_edit = None
        self._result_browser = None
        self._btn_inventor = None
        self._current_result = None
        self._current_designation = ""
        self.setMinimumWidth(280)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 16, 4, 4)
        outer.setSpacing(0)

        # placeholder（未選中時顯示）
        self._placeholder = QLabel("← 點選左側項目\n   以檢視詳情")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #999; font-size: 12px;")
        outer.addWidget(self._placeholder)

        # 主分割器（垂直）
        self._splitter = QSplitter(Qt.Orientation.Vertical)
        self._splitter.setHandleWidth(5)
        self._splitter.setStyleSheet(
            "QSplitter::handle { background: #DDE3EC; }"
        )
        self._splitter.setVisible(False)
        outer.addWidget(self._splitter)

        self._build_pdf_panel()
        self._build_detail_panel()
        self._splitter.setSizes([400, 320])

    # ══════════════════════════════════════════
    #  PDF 預覽面板（上半）
    # ══════════════════════════════════════════
    def _build_pdf_panel(self):
        pane = QWidget()
        pane.setStyleSheet("background: white;")
        vbox = QVBoxLayout(pane)
        vbox.setContentsMargins(2, 2, 2, 2)
        vbox.setSpacing(3)

        # 縮放控制列
        zrow = QHBoxLayout()
        zrow.setSpacing(4)
        lbl = QLabel("圖面預覽")
        lbl.setFont(QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #555;")
        zrow.addWidget(lbl)
        zrow.addStretch()

        self._btn_zoom_out = QPushButton("－")
        self._btn_zoom_out.setFixedSize(26, 24)
        self._btn_zoom_out.setStyleSheet(self._ZOOM_BTN)

        self._lbl_zoom_pct = QLabel("—")
        self._lbl_zoom_pct.setFont(QFont("Consolas", 9))
        self._lbl_zoom_pct.setStyleSheet("color: #555;")
        self._lbl_zoom_pct.setFixedWidth(44)
        self._lbl_zoom_pct.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._btn_zoom_in = QPushButton("＋")
        self._btn_zoom_in.setFixedSize(26, 24)
        self._btn_zoom_in.setStyleSheet(self._ZOOM_BTN)

        self._btn_zoom_fit = QPushButton("適合寬度")
        self._btn_zoom_fit.setFixedHeight(24)
        self._btn_zoom_fit.setStyleSheet(self._ZOOM_FIT_BTN)

        zrow.addWidget(self._btn_zoom_out)
        zrow.addWidget(self._lbl_zoom_pct)
        zrow.addWidget(self._btn_zoom_in)
        zrow.addWidget(self._btn_zoom_fit)
        vbox.addLayout(zrow)

        # 可捲動的圖片區
        self._pdf_scroll = QScrollArea()
        self._pdf_scroll.setWidgetResizable(False)
        self._pdf_scroll.setStyleSheet(
            "QScrollArea { background: white; border: 1px solid #E0E0E0; }"
            "QScrollBar:vertical { width: 8px; } QScrollBar:horizontal { height: 8px; }"
        )
        self._lbl_pdf = QLabel("選擇項目後顯示圖面")
        self._lbl_pdf.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_pdf.setMinimumSize(100, 80)
        self._lbl_pdf.setStyleSheet(
            "background: white; color: #AAA; font-size: 11px; padding: 12px;"
        )
        self._pdf_scroll.setWidget(self._lbl_pdf)
        vbox.addWidget(self._pdf_scroll)

        self._btn_zoom_in.clicked.connect(lambda: self._zoom_preview(0.15))
        self._btn_zoom_out.clicked.connect(lambda: self._zoom_preview(-0.15))
        self._btn_zoom_fit.clicked.connect(self._zoom_fit)

        self._splitter.addWidget(pane)

    # ══════════════════════════════════════════
    #  計算明細 + 覆寫設定面板（下半）
    # ══════════════════════════════════════════
    def _build_detail_panel(self):
        pane = QWidget()
        pane.setStyleSheet("background: white;")
        vbox = QVBoxLayout(pane)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self._detail_scroll = QScrollArea()
        self._detail_scroll.setWidgetResizable(True)
        self._detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._detail_scroll.setStyleSheet(
            "QScrollArea { background: white; } QScrollBar:vertical { width: 8px; }"
        )
        self._detail_content = QWidget()
        self._detail_content.setStyleSheet("background: white;")
        self._detail_layout = QVBoxLayout(self._detail_content)
        self._detail_layout.setContentsMargins(8, 8, 8, 8)
        self._detail_layout.setSpacing(8)
        self._detail_layout.addStretch()

        self._detail_scroll.setWidget(self._detail_content)
        vbox.addWidget(self._detail_scroll)
        self._splitter.addWidget(pane)

        self._detail_widgets: list = []

    # ══════════════════════════════════════════
    #  PDF 渲染 / 縮放
    # ══════════════════════════════════════════
    def _load_pdf_for_type(self, type_code: str):
        """根據 type_code 找 PDF 並渲染第一頁"""
        self._preview_pixmap = None

        cat_entry = self._get_catalog_entry(type_code)
        pdf_file = cat_entry.get("pdf_file", "") or f"{type_code.zfill(2)}.pdf"

        pdf_path = os.path.join(_PDF_DIR, pdf_file)
        if _FITZ_AVAILABLE and os.path.exists(pdf_path):
            try:
                doc = fitz.open(pdf_path)
                page = doc[0]
                mat = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=mat)
                img = QImage(
                    pix.samples, pix.width, pix.height,
                    pix.stride, QImage.Format.Format_RGB888,
                )
                self._preview_pixmap = QPixmap.fromImage(img)
                doc.close()
                self._zoom_fit()
                return
            except Exception:
                pass

        # fallback
        self._lbl_pdf.clear()
        self._lbl_pdf.setMinimumSize(100, 80)
        self._lbl_pdf.setText(
            f"尚無此 Type 的 PDF\n({pdf_file})"
            if _FITZ_AVAILABLE else
            "PyMuPDF 未安裝，無法顯示 PDF 預覽"
        )
        self._lbl_pdf.setStyleSheet(
            "background: #FAFAFA; color: #AAA; font-size: 11px; padding: 12px;"
        )
        self._lbl_zoom_pct.setText("—")

    def _apply_zoom(self):
        if not self._preview_pixmap:
            return
        new_w = int(self._preview_pixmap.width() * self._zoom_level)
        scaled = self._preview_pixmap.scaledToWidth(
            max(60, new_w), Qt.TransformationMode.SmoothTransformation
        )
        self._lbl_pdf.setPixmap(scaled)
        self._lbl_pdf.resize(scaled.size())
        self._lbl_pdf.setStyleSheet("background: white;")
        self._lbl_zoom_pct.setText(f"{int(self._zoom_level * 100)}%")

    def _zoom_preview(self, delta: float):
        self._zoom_level = max(0.2, min(3.0, self._zoom_level + delta))
        self._apply_zoom()

    def _zoom_fit(self):
        if not self._preview_pixmap:
            return
        avail = self._pdf_scroll.viewport().width() - 4
        if avail <= 0:
            avail = 270
        self._zoom_level = max(0.2, min(3.0, avail / max(1, self._preview_pixmap.width())))
        self._apply_zoom()

    # ══════════════════════════════════════════
    #  型錄查詢
    # ══════════════════════════════════════════
    @classmethod
    def _get_catalog_entry(cls, type_code: str) -> dict:
        if not cls._catalog_cache:
            try:
                cls._catalog_cache = load_catalog()
            except Exception:
                return {}
        tc = type_code.lstrip("0") or "0"
        for entry in cls._catalog_cache:
            tid = entry.get("type_id", "")
            if tid == type_code or tid.lstrip("0") == tc:
                return entry
        return {}

    # ══════════════════════════════════════════
    #  下半動態內容管理
    # ══════════════════════════════════════════
    def _clear_detail(self):
        for w in self._detail_widgets:
            self._detail_layout.removeWidget(w)
            w.deleteLater()
        self._detail_widgets.clear()
        # 重置 form widget 參照
        self._rb_elbow = None
        self._rb_tee = None
        self._mat_combo = None
        self._pipe_edit = None
        self._sch_edit = None
        self._l_edit = None
        self._result_browser = None
        self._btn_inventor = None

    def _add_dw(self, w: QWidget):
        """插入在 stretch 之前"""
        self._detail_layout.insertWidget(self._detail_layout.count() - 1, w)
        self._detail_widgets.append(w)

    def _add_sep(self):
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        self._add_dw(sep)

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "font-weight: bold; font-size: 11px; color: #1565C0; "
            "padding: 4px 0 2px 0;"
        )
        return lbl

    # ══════════════════════════════════════════
    #  Public API
    # ══════════════════════════════════════════
    def clear_panel(self):
        self._idx = -1
        self._current_type_code = ""
        self._preview_pixmap = None
        self._lbl_pdf.clear()
        self._lbl_pdf.setText("選擇項目後顯示圖面")
        self._lbl_pdf.setStyleSheet(
            "background: white; color: #AAA; font-size: 11px; padding: 12px;"
        )
        self._lbl_zoom_pct.setText("—")
        self._clear_detail()
        self._splitter.setVisible(False)
        self._placeholder.setVisible(True)

    def mark_result_stale(self):
        """Clear only the calculated-detail area when inputs changed."""
        self._current_result = None
        if self._btn_inventor:
            self._btn_inventor.setEnabled(False)
        if self._result_browser is not None:
            self._result_browser.setHtml(
                '<p style="color:#AAA; font-size:10pt;">'
                '（輸入已變更，請重新執行分析）</p>'
            )

    def show_item(self, idx: int, item_text: str, current_overrides: dict):
        self._building = True
        self._idx = idx
        self._overrides = dict(current_overrides)
        self._current_designation = item_text
        self._current_result = None
        self._clear_detail()
        self._placeholder.setVisible(False)
        self._splitter.setVisible(True)

        type_code = get_type_code(item_text)
        self._current_type_code = type_code

        # ── 載入 PDF 預覽 ──
        self._load_pdf_for_type(type_code)

        # ── 標題 ──
        title = QLabel(f"📌 {item_text}")
        title.setWordWrap(True)
        title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px 0;")
        self._add_dw(title)

        # ── Type 資訊 ──
        cat = self._get_catalog_entry(type_code)
        config = load_config(type_code.replace("T", ""))
        type_name = (
            cat.get("name_zh")
            or (config.get("name") if config else "")
            or f"Type {type_code}"
        )
        info_lbl = QLabel(f"Type {type_code}  ·  {type_name}")
        info_lbl.setStyleSheet("color: #666; font-size: 11px; padding-bottom: 2px;")
        self._add_dw(info_lbl)

        self._add_sep()

        # ── 覆寫設定 ──
        self._add_dw(self._section_label("覆寫設定"))
        if type_code in ("01", "01T"):
            self._build_type01_form(item_text, type_code, current_overrides, config)
        else:
            self._build_generic_form(current_overrides)

        # ── 還原按鈕 ──
        btn_reset = QPushButton("↩ 還原為 Type 預設")
        btn_reset.clicked.connect(self._on_reset)
        self._add_dw(btn_reset)

        self._add_sep()

        # ── 計算邏輯 ──
        self._add_dw(self._section_label("計算邏輯"))
        calc_logic = cat.get("calc_logic", "")
        if not calc_logic and config:
            calc_logic = config.get("calc_logic", "")
        calc_browser = QTextBrowser()
        calc_browser.setFont(QFont("Consolas", 10))
        calc_browser.setStyleSheet(
            "QTextBrowser { border: 1px solid #E0E0E0; background: #FAFAFA; "
            "color: #212121; padding: 8px; border-radius: 4px; }"
        )
        calc_browser.setMinimumHeight(70)
        calc_browser.setMaximumHeight(220)
        if calc_logic:
            calc_browser.setPlainText(calc_logic)
        else:
            calc_browser.setHtml(
                '<p style="color:#AAA; font-size:10pt;">（尚未填寫計算邏輯）</p>'
            )
        self._add_dw(calc_browser)

        self._add_sep()

        # ── 計算結果（等候 update_result 填入）──
        self._add_dw(self._section_label("計算結果"))
        self._result_browser = QTextBrowser()
        self._result_browser.setFont(QFont("Microsoft JhengHei UI", 10))
        self._result_browser.setStyleSheet(
            "QTextBrowser { border: 1px solid #E0E0E0; background: #F8FFF8; "
            "color: #222; padding: 8px; border-radius: 4px; }"
        )
        self._result_browser.setMinimumHeight(60)
        self._result_browser.setHtml(
            '<p style="color:#AAA; font-size:10pt;">'
            '（尚未計算，請按「▶ 開始分析」）</p>'
        )
        self._add_dw(self._result_browser)

        # ── Inventor 匯出（僅 Pipe Shoe 家族）────────────────────────────────
        from core.pipe_shoe_engine import PIPE_SHOE_TYPE_IDS
        if type_code in PIPE_SHOE_TYPE_IDS:
            self._add_sep()
            self._btn_inventor = QPushButton("📐 匯出 Inventor 參數 (CSV)")
            self._btn_inventor.setEnabled(False)   # 計算完成後才啟用
            self._btn_inventor.setToolTip(
                "執行計算後可匯出 Inventor iLogic 可讀的 CSV 參數檔案"
            )
            self._btn_inventor.setStyleSheet(
                "QPushButton { background: #1565C0; color: white; font-size: 10pt; "
                "padding: 5px 10px; border-radius: 4px; border: none; }"
                "QPushButton:hover  { background: #1976D2; }"
                "QPushButton:disabled { background: #B0BEC5; color: #ECEFF1; }"
            )
            self._btn_inventor.clicked.connect(self._on_export_inventor)
            self._add_dw(self._btn_inventor)

        self._building = False

    def update_result(self, result):
        """分析完成後由 MainWindow 呼叫，填入計算結果"""
        self._current_result = result
        if self._result_browser is None:
            return
        if result is None or result.error:
            msg = result.error if result else "無結果"
            self._result_browser.setHtml(
                f'<p style="color:#D32F2F; font-size:10pt;">錯誤: {msg}</p>'
            )
            if self._btn_inventor:
                self._btn_inventor.setEnabled(False)
            return

        html = (
            '<style>'
            'table { border-collapse: collapse; width: 100%; font-size: 10pt; }'
            'th { background: #E3F0FF; color: #1565C0; padding: 4px 6px;'
            '     border-bottom: 2px solid #90C2F0; text-align: left; }'
            'td { padding: 3px 6px; border-bottom: 1px solid #EEF0F3; vertical-align: top; }'
            'tr:nth-child(even) td { background: #F8FAFB; }'
            '.r { text-align: right; }'
            '.c { text-align: center; }'
            '</style>'
        )
        html += (
            f'<p style="font-weight:bold; color:#333; margin-bottom:6px;">'
            f'總重量: <span style="color:#1565C0;">{result.total_weight:.2f} kg</span></p>'
        )
        html += (
            '<table><tr>'
            '<th>#</th><th>品名</th><th>公式 / 備註</th>'
            '<th>材質</th><th class="r">L(mm)</th>'
            '<th class="c">數</th><th class="r">重(kg)</th>'
            '</tr>'
        )
        for e in result.entries:
            formula = (
                (e.geometry.formula if e.geometry and e.geometry.formula else "")
                or e.remark or "—"
            )
            html += (
                f'<tr>'
                f'<td class="c">{e.item_no}</td>'
                f'<td>{e.name}</td>'
                f'<td style="font-family:Consolas; font-size:9pt;">{formula}</td>'
                f'<td>{e.material}</td>'
                f'<td class="r">{e.length:.0f}</td>'
                f'<td class="c">{e.quantity}</td>'
                f'<td class="r">{e.weight_output:.3f}</td>'
                f'</tr>'
            )
        html += '</table>'
        if result.warnings:
            html += (
                '<p style="color:#E65100; font-size:9pt; margin-top:6px;">⚠ '
                + '<br>'.join(result.warnings)
                + '</p>'
            )
        self._result_browser.setHtml(html)

        # 計算成功後啟用 Inventor 匯出按鈕
        if self._btn_inventor:
            self._btn_inventor.setEnabled(True)

    # ══════════════════════════════════════════
    #  Inventor 參數匯出
    # ══════════════════════════════════════════
    def _on_export_inventor(self):
        """匯出 Pipe Shoe 計算結果為 Inventor iLogic CSV 參數檔案。"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from core.pipe_shoe_engine import PIPE_SHOE_TYPE_IDS
        from export.inventor_params import (
            export_ilogic_snippet,
            export_to_csv,
            extract_params,
        )

        designation = self._current_designation
        type_code = self._current_type_code

        if type_code not in PIPE_SHOE_TYPE_IDS:
            return

        default_stem = designation.replace("/", "_").replace("-", "_")
        csv_path, _ = QFileDialog.getSaveFileName(
            self,
            "匯出 Inventor 參數 CSV",
            f"{default_stem}_inventor.csv",
            "CSV 檔案 (*.csv)",
        )
        if not csv_path:
            return

        try:
            params = extract_params(designation, type_code)
            if params is None:
                QMessageBox.warning(self, "匯出失敗", "無法取得計算參數，請先執行分析。")
                return

            export_to_csv(params, csv_path)

            vb_path = os.path.splitext(csv_path)[0] + "_iLogic_LoadParams.vb"
            export_ilogic_snippet(vb_path, csv_path)

            warn_html = (
                "<br><br><b>⚠ 計算警告：</b><br>" + "<br>".join(params["warnings"])
                if params["warnings"] else ""
            )
            QMessageBox.information(
                self,
                "匯出完成",
                f"<b>CSV 參數檔案已儲存：</b><br>{csv_path}"
                f"<br><br><b>iLogic 讀取範本：</b><br>{vb_path}"
                f"<br><br>在 Inventor 中開啟 iLogic Rule Editor，"
                f"貼入 .vb 檔的程式碼後執行即可套用參數。"
                f"{warn_html}",
            )
        except Exception as exc:
            QMessageBox.critical(self, "匯出錯誤", str(exc))

    # ══════════════════════════════════════════
    #  覆寫設定表單
    # ══════════════════════════════════════════
    def _build_type01_form(self, item_text, type_code, overrides, config):
        # 接入方式
        conn_group = QGroupBox("接入方式")
        conn_lay = QHBoxLayout(conn_group)
        self._rb_elbow = QRadioButton("Elbow (彎頭)")
        self._rb_tee = QRadioButton("Tee (三通)")
        effective_conn = overrides.get("connection")
        if effective_conn == "tee" or (not effective_conn and type_code == "01T"):
            self._rb_tee.setChecked(True)
        else:
            self._rb_elbow.setChecked(True)
        self._rb_elbow.toggled.connect(self._on_field_changed)
        self._rb_tee.toggled.connect(self._on_field_changed)
        conn_lay.addWidget(self._rb_elbow)
        conn_lay.addWidget(self._rb_tee)
        self._add_dw(conn_group)

        # 材質
        mat_group = QGroupBox("上段管材質")
        mat_lay = QHBoxLayout(mat_group)
        self._mat_combo = QComboBox()
        self._mat_combo.addItems([
            "", "SUS304", "SUS316", "A53Gr.B", "A106Gr.B",
            "A335-P11", "A335-P22", "A312-TP304", "A312-TP316",
        ])
        self._mat_combo.setEditable(True)
        self._mat_combo.setCurrentText(overrides.get("upper_material", ""))
        self._mat_combo.currentTextChanged.connect(self._on_field_changed)
        hint = QLabel("空白=跟隨全域")
        hint.setStyleSheet("color: #999; font-size: 10px;")
        mat_lay.addWidget(self._mat_combo)
        mat_lay.addWidget(hint)
        self._add_dw(mat_group)

        # 查表值覆寫
        part2 = get_part(item_text, 2)
        try:
            line_size = int(get_lookup_value(part2))
        except (ValueError, TypeError):
            line_size = 0
        cfg_table = get_type_table_as_dict("01") or {}
        row_data = cfg_table.get(line_size, {})

        table_group = QGroupBox("查表值 (留空=用 Config 預設)")
        form = QFormLayout(table_group)

        self._pipe_edit = QLineEdit(overrides.get("pipe_size", ""))
        self._pipe_edit.setPlaceholderText(f"預設: {row_data.get('pipe_size', '?')}")
        self._pipe_edit.textChanged.connect(self._on_field_changed)
        form.addRow("支撐管徑:", self._pipe_edit)

        self._sch_edit = QLineEdit(overrides.get("schedule", ""))
        self._sch_edit.setPlaceholderText(f"預設: {row_data.get('schedule', '?')}")
        self._sch_edit.textChanged.connect(self._on_field_changed)
        form.addRow("Schedule:", self._sch_edit)

        self._l_edit = QLineEdit(
            str(overrides["l_value"]) if overrides.get("l_value") else ""
        )
        self._l_edit.setPlaceholderText(f"預設: {row_data.get('L', '?')}")
        self._l_edit.textChanged.connect(self._on_field_changed)
        form.addRow("L 值 (mm):", self._l_edit)

        part3 = get_part(item_text, 3) or ""
        if part3:
            letter = part3[-1] if part3[-1].isalpha() else ""
            h_code = part3[:-1] if letter else part3
            try:
                h_mm = int(h_code) * 100
            except ValueError:
                h_mm = 0
            form.addRow("H 高度:", QLabel(f"{h_mm} mm"))
            form.addRow("M42 底板:", QLabel(f"代碼 {letter}" if letter else "無"))

        self._add_dw(table_group)

    def _build_generic_form(self, overrides):
        mat_group = QGroupBox("上段管材質")
        mat_lay = QHBoxLayout(mat_group)
        self._mat_combo = QComboBox()
        self._mat_combo.addItems([
            "", "SUS304", "SUS316", "A53Gr.B", "A106Gr.B",
            "A335-P11", "A335-P22", "A312-TP304", "A312-TP316",
        ])
        self._mat_combo.setEditable(True)
        self._mat_combo.setCurrentText(overrides.get("upper_material", ""))
        self._mat_combo.currentTextChanged.connect(self._on_field_changed)
        hint = QLabel("空白=跟隨全域")
        hint.setStyleSheet("color: #999; font-size: 10px;")
        mat_lay.addWidget(self._mat_combo)
        mat_lay.addWidget(hint)
        self._add_dw(mat_group)

    # ══════════════════════════════════════════
    #  欄位變更 / 還原
    # ══════════════════════════════════════════
    def _on_field_changed(self):
        if self._building or self._idx < 0:
            return
        overrides = {}
        if self._rb_tee is not None:
            overrides["connection"] = "tee" if self._rb_tee.isChecked() else "elbow"
        if self._mat_combo is not None:
            mat = self._mat_combo.currentText().strip()
            if mat:
                overrides["upper_material"] = mat
        if self._pipe_edit is not None:
            v = self._pipe_edit.text().strip()
            if v:
                overrides["pipe_size"] = v
        if self._sch_edit is not None:
            v = self._sch_edit.text().strip()
            if v:
                overrides["schedule"] = v
        if self._l_edit is not None:
            v = self._l_edit.text().strip()
            if v:
                try:
                    overrides["l_value"] = int(v)
                except ValueError:
                    pass
        self._overrides = overrides
        self.overrideChanged.emit(self._idx, overrides)

    def _on_reset(self):
        if self._idx < 0:
            return
        self._overrides = {}
        self.overrideChanged.emit(self._idx, {})
        parent = self.parent()
        if parent and hasattr(parent, "parent"):
            mw = parent.parent()
            if hasattr(mw, "_project_rows") and self._idx < len(mw._project_rows):
                row = mw._project_rows[self._idx]
                self.show_item(self._idx, row.designation, {})


# ══════════════════════════════════════════════════
#  Config 管理對話框
# ══════════════════════════════════════════════════
class ConfigDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Type 資料管理")
        self.setMinimumSize(800, 500)
        self._current_config = None
        self._current_type_id = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("選擇 Type:"))
        self.type_combo = QComboBox()
        self._load_config_list()
        self.type_combo.currentTextChanged.connect(self._on_type_selected)
        top_row.addWidget(self.type_combo)
        top_row.addStretch()
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #666;")
        top_row.addWidget(self.info_label)
        layout.addLayout(top_row)

        self.notes_label = QLabel("")
        self.notes_label.setWordWrap(True)
        self.notes_label.setStyleSheet(
            "background: #FFF9C4; padding: 8px; border-radius: 4px; font-size: 11px;"
        )
        layout.addWidget(self.notes_label)

        self.config_table = QTableWidget()
        self.config_table.setAlternatingRowColors(True)
        layout.addWidget(self.config_table)

        btn_row = QHBoxLayout()
        self.btn_save = QPushButton("💾 儲存變更")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_save.setEnabled(False)
        btn_row.addWidget(self.btn_save)
        self.btn_add_row = QPushButton("+ 新增列")
        self.btn_add_row.clicked.connect(lambda: self.config_table.insertRow(
            self.config_table.rowCount()))
        btn_row.addWidget(self.btn_add_row)
        self.btn_del_row = QPushButton("- 刪除列")
        self.btn_del_row.clicked.connect(lambda: self.config_table.removeRow(
            self.config_table.currentRow()) if self.config_table.currentRow() >= 0 else None)
        btn_row.addWidget(self.btn_del_row)
        btn_row.addStretch()
        btn_close = QPushButton("關閉")
        btn_close.clicked.connect(self.close)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

        if self.type_combo.count() > 0:
            self._on_type_selected(self.type_combo.currentText())

    def _load_config_list(self):
        from core.config_loader import list_configs
        for c in list_configs():
            self.type_combo.addItem(
                f"Type {c['type_id']} - {c['name']}", c["type_id"]
            )

    def _on_type_selected(self, text):
        type_id = self.type_combo.currentData()
        if not type_id:
            return
        self._current_config = load_config(type_id)
        self._current_type_id = type_id
        if not self._current_config:
            return
        cfg = self._current_config
        self.info_label.setText(
            f"圖號: {cfg.get('drawing_no', '?')} | "
            f"適用: {cfg.get('applicable_range', '?')} | "
            f"v{cfg.get('version', '?')}"
        )
        notes = cfg.get("notes", [])
        self.notes_label.setText("📌 " + "\n📌 ".join(notes) if notes else "")
        self._display_table(cfg.get("table", []))
        self.btn_save.setEnabled(True)
        self.config_table.cellChanged.connect(
            lambda: self.btn_save.setStyleSheet(
                "QPushButton { background-color: #FF9800; color: white; }"
            )
        )

    def _display_table(self, table):
        if not table:
            self.config_table.setRowCount(0)
            return
        headers = list(table[0].keys())
        self.config_table.blockSignals(True)
        self.config_table.setColumnCount(len(headers))
        self.config_table.setHorizontalHeaderLabels(headers)
        self.config_table.setRowCount(len(table))
        for r, row in enumerate(table):
            for c, key in enumerate(headers):
                self.config_table.setItem(r, c, QTableWidgetItem(str(row.get(key, ""))))
        self.config_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.config_table.blockSignals(False)

    def _on_save(self):
        if not self._current_config:
            return
        table = self._current_config.get("table", [])
        if not table:
            return
        headers = list(table[0].keys())
        new_table = []
        for r in range(self.config_table.rowCount()):
            row_data = {}
            for c, key in enumerate(headers):
                item = self.config_table.item(r, c)
                val = item.text() if item else ""
                try:
                    val = float(val) if "." in val else int(val)
                except ValueError:
                    pass
                row_data[key] = val
            new_table.append(row_data)
        self._current_config["table"] = new_table

        from core.config_loader import save_config
        save_config(self._current_type_id, self._current_config,
                    "GUI 手動修改資料表")
        self.btn_save.setStyleSheet("")
        QMessageBox.information(self, "已儲存",
                                f"Type {self._current_type_id} 設定已儲存")
