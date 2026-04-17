"""
材料合計 / 下料計算 頁面 Widget

顯示:
  上半: 材料合計表 (QTableWidget)
  下半: 下料方案 (QTableWidget, 每種材料一區)
"""
from typing import List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QLabel, QGroupBox, QFileDialog,
    QMessageBox, QTextEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from core.models import AnalysisResult
from core.material_summary import aggregate, MaterialSummary, SummaryLine
from core.cutting_optimizer import CuttingPlan, optimize_from_summary


class MaterialCuttingPage(QWidget):
    """材料合計 + 下料計算 Tab 頁面"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._summary: MaterialSummary | None = None
        self._cutting_plans: List[CuttingPlan] = []
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # ── 頂部提示 ──
        hint = QLabel("先在「重量分析」頁完成分析，再按下方按鈕產生合計/下料方案")
        hint.setStyleSheet("color: #666; font-size: 11px; padding: 2px;")
        layout.addWidget(hint)

        # ── 按鈕列 ──
        btn_row = QHBoxLayout()

        self.btn_generate = QPushButton("▶ 產生材料合計 + 下料方案")
        self.btn_generate.setStyleSheet(
            "QPushButton { background-color: #1976D2; color: white; "
            "padding: 8px 16px; font-size: 13px; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1565C0; }"
            "QPushButton:disabled { background-color: #bbb; }"
        )
        self.btn_generate.setEnabled(False)
        btn_row.addWidget(self.btn_generate)

        self.btn_export = QPushButton("📥 匯出 Excel")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._on_export)
        btn_row.addWidget(self.btn_export)

        btn_row.addStretch()

        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("font-size: 12px; font-weight: bold;")
        btn_row.addWidget(self.lbl_status)

        layout.addLayout(btn_row)

        # ── 上下分割 ──
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 上半: 材料合計表
        summary_group = QGroupBox("材料合計表（採購清單）")
        summary_lay = QVBoxLayout(summary_group)
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(10)
        self.summary_table.setHorizontalHeaderLabels([
            "品名", "規格", "材質", "屬性",
            "需求總長(mm)", "需求件數", "總重(kg)",
            "建議採購量", "單位", "來源編碼",
        ])
        self.summary_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.summary_table.setAlternatingRowColors(True)
        self.summary_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        summary_lay.addWidget(self.summary_table)
        splitter.addWidget(summary_group)

        # 下半: 下料方案
        cutting_group = QGroupBox("下料計算（現場裁切方案）")
        cutting_lay = QVBoxLayout(cutting_group)
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(9)
        self.cutting_table.setHorizontalHeaderLabels([
            "材料", "原料 #", "切割段", "需求長(mm)",
            "含損耗(mm)", "累計(mm)", "餘料(mm)", "使用率", "用於",
        ])
        self.cutting_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self.cutting_table.setAlternatingRowColors(True)
        self.cutting_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        cutting_lay.addWidget(self.cutting_table)
        splitter.addWidget(cutting_group)

        splitter.setSizes([350, 350])
        layout.addWidget(splitter)

    # ═══════════════════════════════════════
    #  外部呼叫
    # ═══════════════════════════════════════

    def set_results_ready(self, ready: bool):
        """主視窗分析完成後呼叫，啟用按鈕"""
        self.btn_generate.setEnabled(ready)

    def generate(self, results: List[AnalysisResult]):
        """從分析結果產生材料合計 + 下料方案"""
        valid = [r for r in results if not r.error]
        if not valid:
            QMessageBox.warning(self, "無資料", "沒有有效的分析結果")
            return

        # 1. 聚合
        self._summary = aggregate(valid)

        # 2. 下料
        self._cutting_plans = []
        for ln in self._summary.get_linear_lines():
            plan = optimize_from_summary(ln)
            if plan and plan.total_pieces > 0:
                self._cutting_plans.append(plan)

        # 3. 顯示
        self._display_summary()
        self._display_cutting()

        self.btn_export.setEnabled(True)
        self.lbl_status.setText(
            f"合計 {len(self._summary.lines)} 種材料 | "
            f"總重 {self._summary.total_weight:.2f} kg | "
            f"下料方案 {len(self._cutting_plans)} 種"
        )

    # ═══════════════════════════════════════
    #  顯示邏輯
    # ═══════════════════════════════════════

    def _display_summary(self):
        tbl = self.summary_table
        tbl.setRowCount(0)
        if not self._summary:
            return

        CATEGORY_COLORS = {
            "管路類": QColor("#E3F2FD"),
            "鋼板類": QColor("#FFF3E0"),
            "鋼材類": QColor("#E8F5E9"),
            "螺栓類": QColor("#F3E5F5"),
        }

        for ln in self._summary.lines:
            row = tbl.rowCount()
            tbl.insertRow(row)

            bg = CATEGORY_COLORS.get(ln.category, QColor("white"))

            def _set(col, val, align=Qt.AlignmentFlag.AlignLeft):
                item = QTableWidgetItem(str(val))
                item.setBackground(bg)
                item.setTextAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                tbl.setItem(row, col, item)

            _set(0, ln.name)
            _set(1, ln.spec)
            _set(2, ln.material)
            _set(3, ln.category)

            if ln.aggregate_type == "linear":
                _set(4, f"{ln.total_length_mm:.0f}", Qt.AlignmentFlag.AlignRight)
                _set(5, str(ln.piece_count), Qt.AlignmentFlag.AlignRight)
            else:
                _set(4, "-", Qt.AlignmentFlag.AlignCenter)
                _set(5, str(ln.total_qty), Qt.AlignmentFlag.AlignRight)

            _set(6, f"{ln.total_weight:.2f}", Qt.AlignmentFlag.AlignRight)
            _set(7, str(ln.purchase_qty), Qt.AlignmentFlag.AlignRight)
            _set(8, ln.purchase_unit)

            sources = ", ".join(ln.source_fullstrings[:5])
            if len(ln.source_fullstrings) > 5:
                sources += f" ...+{len(ln.source_fullstrings) - 5}"
            _set(9, sources)

    def _display_cutting(self):
        tbl = self.cutting_table
        tbl.setRowCount(0)
        if not self._cutting_plans:
            return

        HEADER_COLOR = QColor("#D6DCE4")
        GOOD_COLOR = QColor("#C6EFCE")    # 餘料可用
        WARN_COLOR = QColor("#FFEB9C")    # 短料
        BAD_COLOR = QColor("#FFC7CE")     # 廢料

        for plan in self._cutting_plans:
            # 材料標題行
            row = tbl.rowCount()
            tbl.insertRow(row)
            title = f"{plan.name}  {plan.spec}  ({plan.material}) — " \
                    f"需求 {plan.total_pieces} 段, 原料 {plan.total_bars} 根, " \
                    f"平均使用率 {plan.avg_utilization:.1f}%"
            title_item = QTableWidgetItem(title)
            title_item.setFont(QFont("Microsoft JhengHei UI", 10, QFont.Weight.Bold))
            title_item.setBackground(QColor("#4472C4"))
            title_item.setForeground(QColor("white"))
            tbl.setItem(row, 0, title_item)
            # 填滿該行背景
            for c in range(1, 9):
                filler = QTableWidgetItem("")
                filler.setBackground(QColor("#4472C4"))
                tbl.setItem(row, c, filler)
            tbl.setSpan(row, 0, 1, 9)

            # 每根原料
            for bar_idx, bar in enumerate(plan.bars):
                cumulative = 0.0

                for piece_idx, piece in enumerate(bar.pieces):
                    cumulative += piece.cut_length
                    row = tbl.rowCount()
                    tbl.insertRow(row)

                    if piece_idx == 0:
                        tbl.setItem(row, 0, QTableWidgetItem(""))  # 材料欄空白
                        tbl.setItem(row, 1, QTableWidgetItem(f"#{bar_idx + 1}"))
                    else:
                        tbl.setItem(row, 0, QTableWidgetItem(""))
                        tbl.setItem(row, 1, QTableWidgetItem(""))

                    tbl.setItem(row, 2, QTableWidgetItem(f"段 {piece_idx + 1}"))

                    demand_item = QTableWidgetItem(f"{piece.demand_length:.0f}")
                    demand_item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    tbl.setItem(row, 3, demand_item)

                    cut_item = QTableWidgetItem(f"{piece.cut_length:.0f}")
                    cut_item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    tbl.setItem(row, 4, cut_item)

                    cum_item = QTableWidgetItem(f"{cumulative:.0f}")
                    cum_item.setTextAlignment(
                        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                    )
                    tbl.setItem(row, 5, cum_item)

                    # 來源編碼
                    source_item = QTableWidgetItem(piece.source)
                    source_item.setForeground(QColor("#666"))
                    tbl.setItem(row, 8, source_item)

                # 餘料行
                row = tbl.rowCount()
                tbl.insertRow(row)
                remnant = bar.remnant

                if remnant < 100:
                    bg = BAD_COLOR
                    note = "廢料"
                elif remnant < 300:
                    bg = WARN_COLOR
                    note = "短料"
                else:
                    bg = GOOD_COLOR
                    note = ""

                for c in range(9):
                    filler = QTableWidgetItem("")
                    filler.setBackground(bg)
                    tbl.setItem(row, c, filler)

                tbl.item(row, 1).setText("─")
                tbl.item(row, 2).setText("餘料")

                rem_item = tbl.item(row, 6)
                rem_item.setText(f"{remnant:.0f}")
                rem_item.setTextAlignment(
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
                )

                util_item = tbl.item(row, 7)
                util_item.setText(f"{bar.utilization:.1f}%")
                if note:
                    tbl.item(row, 2).setText(f"餘料 ({note})")

    # ═══════════════════════════════════════
    #  匯出
    # ═══════════════════════════════════════

    def _on_export(self):
        if not self._summary:
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "匯出材料合計 + 下料表", "material_cutting.xlsx",
            "Excel (*.xlsx)"
        )
        if not filepath:
            return

        try:
            from export.summary_export import export_summary_and_cutting
            export_summary_and_cutting(
                self._summary, filepath, self._cutting_plans
            )
            QMessageBox.information(
                self, "匯出成功", f"已匯出至:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(self, "匯出錯誤", str(e))
