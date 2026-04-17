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
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QSplitter, QGroupBox, QMessageBox,
    QComboBox, QHeaderView, QStatusBar, QTabWidget, QSpinBox,
    QDoubleSpinBox, QLineEdit, QFormLayout, QDialog,
    QListWidget, QListWidgetItem, QRadioButton, QButtonGroup,
    QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QIcon

from core.calculator import (
    analyze_batch, analyze_single, get_supported_types,
    set_analysis_setting, get_analysis_setting,
)
from core.models import AnalysisResult
from core.parser import get_type_code, get_part, get_lookup_value
from core.config_loader import load_config, get_type_table_as_dict
from ui.type_manager import TypeManagerWidget
from ui.ontology_browser import OntologyBrowserWidget
from ui.material_cutting_page import MaterialCuttingPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IEC 管架支撐分析工具 (Python Edition)")
        self.setMinimumSize(1300, 720)
        self._items = []           # list of item strings
        self._item_enabled = {}    # {index: bool}
        self._overrides = {}       # {index: dict}  第二層覆寫
        self._results = []
        self._selected_index = -1
        self._init_ui()

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

    def _build_analysis_page(self) -> QWidget:
        """建構分析頁面 (原始三面板)"""
        page = QWidget()
        page_layout = QVBoxLayout(page)

        # ── 頂部工具列 ──
        toolbar = QHBoxLayout()
        supported = get_supported_types()
        info_label = QLabel(f"已支援 Type: {', '.join(supported)}")
        info_label.setStyleSheet("color: #555; font-size: 11px;")
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
        self.item_list.setFont(QFont("Consolas", 10))
        layout.addWidget(self.item_list)

        # 按鈕列
        btn_row1 = QHBoxLayout()
        btn_batch = QPushButton("批次貼上...")
        btn_batch.clicked.connect(self._on_batch_paste)
        btn_row1.addWidget(btn_batch)
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
            "QPushButton { background-color: #4CAF50; color: white; "
            "padding: 8px; font-size: 14px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )
        self.btn_analyze.clicked.connect(self._on_analyze)
        layout.addWidget(self.btn_analyze)

        return panel

    def _build_center_panel(self):
        panel = QGroupBox("分析結果")
        layout = QVBoxLayout(panel)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(12)
        self.result_table.setHorizontalHeaderLabels([
            "描述", "項次", "品名", "尺寸/規格", "長度(mm)", "寬度(mm)",
            "材質", "數量", "單重(kg)", "總重(kg)", "單位", "屬性",
        ])
        self.result_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.result_table.setAlternatingRowColors(True)
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
        self.total_weight_label = QLabel("總重量: -- kg")
        self.total_weight_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        export_row.addWidget(self.total_weight_label)
        layout.addLayout(export_row)

        return panel

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

    def _add_item_to_list(self, text: str):
        idx = len(self._items)
        self._items.append(text)
        self._item_enabled[idx] = True
        item_widget = QListWidgetItem(text)
        item_widget.setCheckState(Qt.CheckState.Checked)
        self._update_item_display(idx, item_widget)
        self.item_list.addItem(item_widget)

    def _update_item_display(self, idx: int, item_widget: QListWidgetItem = None):
        """更新清單顯示文字 (有覆寫時加標記)"""
        if item_widget is None:
            item_widget = self.item_list.item(idx)
        if item_widget is None:
            return
        text = self._items[idx]
        overrides = self._overrides.get(idx, {})
        tags = []
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
        btn = QPushButton("加入清單")
        btn.clicked.connect(dlg.accept)
        lay.addWidget(btn)
        if dlg.exec():
            for line in text_edit.toPlainText().split("\n"):
                line = line.strip()
                if line:
                    self._add_item_to_list(line)

    def _on_load_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "載入支撐清單", "",
            "文字檔 (*.txt);;CSV (*.csv);;所有檔案 (*)"
        )
        if filepath:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self._add_item_to_list(line)
            self.statusBar().showMessage(f"已載入: {filepath}")

    def _on_delete_item(self):
        row = self.item_list.currentRow()
        if row < 0:
            return
        self.item_list.takeItem(row)
        self._items.pop(row)
        # 重建 index mapping
        new_enabled = {}
        new_overrides = {}
        for i in range(len(self._items)):
            old_i = i if i < row else i + 1
            new_enabled[i] = self._item_enabled.get(old_i, True)
            if old_i in self._overrides:
                new_overrides[i] = self._overrides[old_i]
        self._item_enabled = new_enabled
        self._overrides = new_overrides
        self._selected_index = -1
        self.side_panel.clear_panel()

    def _on_clear_all(self):
        self.item_list.clear()
        self._items.clear()
        self._item_enabled.clear()
        self._overrides.clear()
        self._results.clear()
        self._selected_index = -1
        self.result_table.setRowCount(0)
        self.btn_export.setEnabled(False)
        self.total_weight_label.setText("總重量: -- kg")
        self.side_panel.clear_panel()
        self.statusBar().showMessage("已清除")

    def _on_item_selected(self, row):
        """清單項目被點選 → 更新 Side Panel"""
        if row < 0 or row >= len(self._items):
            self._selected_index = -1
            self.side_panel.clear_panel()
            return
        # 同步 checkbox 狀態
        item_widget = self.item_list.item(row)
        self._item_enabled[row] = (
            item_widget.checkState() == Qt.CheckState.Checked
        )
        self._selected_index = row
        self.side_panel.show_item(
            row, self._items[row], self._overrides.get(row, {})
        )

    def _on_override_changed(self, idx: int, overrides: dict):
        """Side Panel 發出覆寫變更"""
        # 移除空值
        clean = {k: v for k, v in overrides.items() if v}
        if clean:
            self._overrides[idx] = clean
        elif idx in self._overrides:
            del self._overrides[idx]
        self._update_item_display(idx)

    # ══════════════════════════════════════════
    #  分析
    # ══════════════════════════════════════════
    def _on_analyze(self):
        if not self._items:
            QMessageBox.warning(self, "提示", "請先新增支撐編碼")
            return

        # 同步 checkbox 狀態
        for i in range(self.item_list.count()):
            w = self.item_list.item(i)
            self._item_enabled[i] = (w.checkState() == Qt.CheckState.Checked)

        # 過濾啟用項目
        active_items = []
        active_overrides = {}
        active_idx_map = {}  # new_idx -> original_idx
        for i, text in enumerate(self._items):
            if self._item_enabled.get(i, True):
                new_i = len(active_items)
                active_items.append(text)
                active_idx_map[new_i] = i
                if i in self._overrides:
                    active_overrides[new_i] = self._overrides[i]

        self._results = analyze_batch(active_items, active_overrides)
        self._display_results()
        self.btn_export.setEnabled(True)

        error_count = sum(1 for r in self._results if r.error)
        self.statusBar().showMessage(
            f"分析完成: {len(self._results)} 筆 "
            f"(成功 {len(self._results) - error_count}, 錯誤 {error_count})"
        )

        # 啟用材料合計 Tab
        self.material_cutting_page.set_results_ready(True)

    def _display_results(self):
        self.result_table.setRowCount(0)
        total_weight = 0.0

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
                from export.excel_export import export_to_excel
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
    """右側設定面板: 顯示選中項目的查表值, 允許單筆覆寫"""

    overrideChanged = pyqtSignal(int, dict)

    def __init__(self):
        super().__init__("項目設定")
        self._idx = -1
        self._overrides = {}
        self._building = False   # 避免 build 時觸發 signal
        self.setMinimumWidth(260)

        self._layout = QVBoxLayout(self)

        self._placeholder = QLabel("← 點選左側項目\n   以檢視/覆寫設定")
        self._placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._placeholder.setStyleSheet("color: #999; font-size: 12px;")
        self._layout.addWidget(self._placeholder)
        self._layout.addStretch()

        # 動態元件容器
        self._form_widgets = []

    def clear_panel(self):
        self._idx = -1
        self._clear_form()
        self._placeholder.show()

    def _clear_form(self):
        for w in self._form_widgets:
            self._layout.removeWidget(w)
            w.deleteLater()
        self._form_widgets.clear()

    def show_item(self, idx: int, item_text: str, current_overrides: dict):
        self._building = True
        self._idx = idx
        self._overrides = dict(current_overrides)
        self._clear_form()
        self._placeholder.hide()

        type_code = get_type_code(item_text)

        # ── 標題 ──
        title = QLabel(f"📌 {item_text}")
        title.setWordWrap(True)
        title.setStyleSheet("font-weight: bold; font-size: 13px; padding: 4px;")
        self._add_widget(title)

        # ── Type 資訊 ──
        config = load_config(type_code.replace("T", ""))
        type_name = config.get("name", f"Type {type_code}") if config else f"Type {type_code}"
        info = QLabel(f"Type: {type_code} — {type_name}")
        info.setStyleSheet("color: #666; font-size: 11px; padding-bottom: 6px;")
        self._add_widget(info)

        self._add_separator()

        # ── Type 01/01T: 接入方式 + 查表值 ──
        if type_code in ("01", "01T"):
            self._build_type01_panel(item_text, type_code, current_overrides, config)
        else:
            self._build_generic_panel(item_text, type_code, current_overrides)

        # ── 還原按鈕 ──
        self._add_separator()
        btn_reset = QPushButton("↩ 還原為 Type 預設")
        btn_reset.clicked.connect(self._on_reset)
        self._add_widget(btn_reset)

        self._layout.addStretch()
        self._form_widgets.append(self._layout.itemAt(self._layout.count() - 1))

        self._building = False

    def _build_type01_panel(self, item_text, type_code, overrides, config):
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
        self._add_widget(conn_group)

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
        mat_lay.addWidget(self._mat_combo)
        hint = QLabel("空白=跟隨全域設定")
        hint.setStyleSheet("color: #999; font-size: 10px;")
        mat_lay.addWidget(hint)
        self._add_widget(mat_group)

        # 查表值
        part2 = get_part(item_text, 2)
        try:
            line_size = int(get_lookup_value(part2))
        except (ValueError, TypeError):
            line_size = 0

        table_group = QGroupBox("查表值 (留空=用 Config 預設)")
        form = QFormLayout(table_group)

        # 從 config 讀預設
        cfg_table = get_type_table_as_dict("01") or {}
        row = cfg_table.get(line_size, {})
        default_pipe = row.get("pipe_size", "?")
        default_sch = row.get("schedule", "?")
        default_L = row.get("L", "?")

        self._pipe_edit = QLineEdit(overrides.get("pipe_size", ""))
        self._pipe_edit.setPlaceholderText(f"預設: {default_pipe}")
        self._pipe_edit.textChanged.connect(self._on_field_changed)
        form.addRow(f"支撐管徑:", self._pipe_edit)

        self._sch_edit = QLineEdit(overrides.get("schedule", ""))
        self._sch_edit.setPlaceholderText(f"預設: {default_sch}")
        self._sch_edit.textChanged.connect(self._on_field_changed)
        form.addRow(f"Schedule:", self._sch_edit)

        self._l_edit = QLineEdit(str(overrides["l_value"]) if overrides.get("l_value") else "")
        self._l_edit.setPlaceholderText(f"預設: {default_L}")
        self._l_edit.textChanged.connect(self._on_field_changed)
        form.addRow(f"L 值 (mm):", self._l_edit)

        # 顯示解析出的其他資訊 (唯讀)
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

        self._add_widget(table_group)

    def _build_generic_panel(self, item_text, type_code, overrides):
        """其他 Type 的通用面板 (目前只有材質覆寫)"""
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
        mat_lay.addWidget(self._mat_combo)
        hint = QLabel("空白=跟隨全域設定")
        hint.setStyleSheet("color: #999; font-size: 10px;")
        mat_lay.addWidget(hint)
        self._add_widget(mat_group)

        # 未來擴充: 其他 Type 的自訂欄位

    def _add_widget(self, w):
        self._layout.insertWidget(self._layout.count() - 1, w)
        self._form_widgets.append(w)

    def _add_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self._add_widget(line)

    def _on_field_changed(self):
        """任何欄位變更, 收集覆寫並發信號"""
        if self._building or self._idx < 0:
            return

        overrides = {}

        # 接入方式 (Type 01 only)
        if hasattr(self, "_rb_tee") and self._rb_tee is not None:
            if self._rb_tee.isChecked():
                overrides["connection"] = "tee"
            elif self._rb_elbow.isChecked():
                overrides["connection"] = "elbow"

        # 材質
        if hasattr(self, "_mat_combo"):
            mat = self._mat_combo.currentText().strip()
            if mat:
                overrides["upper_material"] = mat

        # 查表值覆寫 (Type 01)
        if hasattr(self, "_pipe_edit"):
            v = self._pipe_edit.text().strip()
            if v:
                overrides["pipe_size"] = v
        if hasattr(self, "_sch_edit"):
            v = self._sch_edit.text().strip()
            if v:
                overrides["schedule"] = v
        if hasattr(self, "_l_edit"):
            v = self._l_edit.text().strip()
            if v:
                try:
                    overrides["l_value"] = int(v)
                except ValueError:
                    pass

        self._overrides = overrides
        self.overrideChanged.emit(self._idx, overrides)

    def _on_reset(self):
        """還原為預設"""
        if self._idx < 0:
            return
        self._overrides = {}
        self.overrideChanged.emit(self._idx, {})
        # 通知主視窗取得最新 item_text 刷新面板
        parent = self.parent()
        if parent and hasattr(parent, "parent"):
            mw = parent.parent()
            if hasattr(mw, "_items") and self._idx < len(mw._items):
                self.show_item(self._idx, mw._items[self._idx], {})


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
