"""
Type 管理器面板
提供所有 Type / M 系列掛件的總覽、PDF 預覽、中文說明及運算邏輯
支援 Markdown 文件渲染 (docs/types/*.md)
"""
import json
import os
import re
import sys

import markdown
import fitz  # PyMuPDF

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QScrollArea,
    QFrame, QGroupBox, QTextBrowser, QPushButton,
    QLineEdit, QHeaderView, QComboBox, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle, QSlider,
)
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QFont, QPixmap, QColor, QIcon, QPainter, QPen, QBrush, QImage


# ─── 型錄載入 ────────────────────────────────────
_CATALOG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "configs", "type_catalog.json"
)
_APP_DIR = os.path.dirname(os.path.dirname(__file__))
_PDF_DIR = os.path.join(_APP_DIR, "assets", "Type")
_ICON_DIR = os.path.join(_APP_DIR, "assets", "Type_icon")
_PREVIEW_DIR = os.path.join(_APP_DIR, "assets", "previews")
_DOCS_DIR = os.path.join(_APP_DIR, "docs", "types")

# 狀態對應的中文與顏色
STATUS_MAP = {
    "documented":  ("已分析", "#4CAF50"),
    "cataloged":   ("已建檔", "#2196F3"),
    "placeholder": ("預留",   "#9E9E9E"),
}

# 分類對應
CATEGORY_ZH = {
    "support":        "支撐型式 (Type)",
    "support_cold":   "低溫支撐 (Cold Service)",
    "component":      "掛件 / 零組件 (M-Series)",
    "component_cold": "低溫專用零件 (N-Series)",
    "special":        "特殊圖面 / 通用說明",
}

CATEGORY_ORDER = [
    "support", "support_cold",
    "component", "component_cold",
    "special",
]


def load_catalog() -> list[dict]:
    """載入型錄 JSON"""
    if not os.path.exists(_CATALOG_PATH):
        return []
    with open(_CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("types", [])


# ─── Markdown → HTML 渲染 ─────────────────────────
_MD_CSS = """\
<style>
body {
    font-family: 'Microsoft JhengHei UI', 'Segoe UI', sans-serif;
    font-size: 10.5pt;
    color: #222222;
    line-height: 1.7;
    margin: 4px 8px; padding: 0;
}
h1 { font-size: 15pt; color: #0D47A1; border-bottom: 2px solid #1976D2;
     padding-bottom: 6px; margin-top: 12px; margin-bottom: 8px; }
h2 { font-size: 12.5pt; color: #1565C0; border-bottom: 1px solid #BBDEFB;
     padding-bottom: 4px; margin-top: 20px; margin-bottom: 8px; }
h3 { font-size: 11pt; color: #333333; margin-top: 14px; margin-bottom: 6px; }
table { border-collapse: collapse; width: 100%; margin: 10px 0; }
th { background-color: #E3F2FD; color: #0D47A1; font-weight: bold; font-size: 10pt;
     border: 1px solid #90CAF9; padding: 7px 12px; text-align: left; }
td { border: 1px solid #BBDEFB; padding: 6px 12px; font-size: 10pt;
     background-color: #FFFFFF; color: #333333; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 10pt;
       background-color: #FFF3E0; color: #BF360C; }
pre  { font-family: Consolas, 'Courier New', monospace; font-size: 9.5pt;
       background-color: #FAFAFA; color: #212121; padding: 14px 18px;
       border: 1px solid #E0E0E0; line-height: 1.5; white-space: pre; }
blockquote { border-left: 4px solid #42A5F5; background-color: #E3F2FD;
             padding: 10px 16px; margin: 10px 0; color: #1A237E; }
hr { border: none; border-top: 1px solid #E0E0E0; margin: 16px 0; }
ul, ol { margin: 6px 0; padding-left: 24px; }
li { margin-bottom: 3px; }
strong { color: #1B5E20; }
em { color: #4A148C; }
p { margin: 6px 0; }
</style>
"""

_md_converter = markdown.Markdown(
    extensions=["tables", "fenced_code", "nl2br"],
    output_format="html",
)


def _render_markdown(md_text: str) -> str:
    """將 Markdown 文字轉為帶樣式的 HTML"""
    _md_converter.reset()
    body_html = _md_converter.convert(md_text)
    return f"<html><head>{_MD_CSS}</head><body>{body_html}</body></html>"


def _load_doc_file(doc_filename: str) -> str | None:
    """從 docs/types/ 載入 .md 檔案，回傳原始 Markdown 或 None"""
    if not doc_filename:
        return None
    path = os.path.join(_DOCS_DIR, doc_filename)
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _type_sort_key(type_id: str) -> tuple:
    """排序用: 先取前綴文字, 再取數字, 最後取後綴
    例: '01' -> ('', 1, ''), '01T' -> ('', 1, 'T'),
        'M-22' -> ('M-', 22, ''), 'N-01' -> ('N-', 1, '')
    """
    m = re.match(r'^([A-Za-z\-]*)(\d+)(.*)', type_id)
    if m:
        return (m.group(1), int(m.group(2)), m.group(3))
    return (type_id, 0, "")


# ─── 狀態 Badge 繪製 Delegate ────────────────────
class StatusBadgeDelegate(QStyledItemDelegate):
    """在狀態欄繪製圓角色塊 badge"""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        # 先畫背景 (選中 / hover / alternating)
        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QStyle.Style
        style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

        text = index.data(Qt.ItemDataRole.DisplayRole) or ""
        color_str = index.data(Qt.ItemDataRole.UserRole + 1) or "#999"
        if not text:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # badge 背景
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(text) + 16
        th = fm.height() + 4
        badge_rect = QRect(
            option.rect.center().x() - tw // 2,
            option.rect.center().y() - th // 2,
            tw, th,
        )
        bg_color = QColor(color_str)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(badge_rect, 3, 3)

        # badge 文字
        painter.setPen(QPen(QColor("white")))
        painter.setFont(QFont("Microsoft JhengHei UI", 8, QFont.Weight.Bold))
        painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, text)
        painter.restore()

    def sizeHint(self, option, index):
        hint = super().sizeHint(option, index)
        return QSize(max(hint.width(), 72), max(hint.height(), 26))


# ─── Type Manager Widget ─────────────────────────
class TypeManagerWidget(QWidget):
    """Type 管理器主面板 — 左側樹狀清單 + 右側詳情"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._catalog = load_catalog()
        self._filtered = self._catalog[:]
        self._init_ui()

    # ══════════════════════════════════════════
    #  UI 建構
    # ══════════════════════════════════════════
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 4)
        layout.setSpacing(4)

        # ── 頂部: 搜尋列 + 篩選 ──
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)
        lbl_search = QLabel("搜尋:")
        lbl_search.setFont(QFont("Microsoft JhengHei UI", 9))
        top_bar.addWidget(lbl_search)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("輸入 Type 編號、名稱或關鍵字...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFont(QFont("Microsoft JhengHei UI", 9))
        self.search_input.setFixedHeight(28)
        self.search_input.setStyleSheet(
            "QLineEdit { border: 1px solid #ccc; border-radius: 4px; padding: 2px 8px; }"
            "QLineEdit:focus { border-color: #1976D2; }"
        )
        self.search_input.textChanged.connect(self._on_search)
        top_bar.addWidget(self.search_input)

        lbl_cat = QLabel("分類:")
        lbl_cat.setFont(QFont("Microsoft JhengHei UI", 9))
        top_bar.addWidget(lbl_cat)
        self.filter_combo = QComboBox()
        self.filter_combo.setFont(QFont("Microsoft JhengHei UI", 9))
        self.filter_combo.setFixedHeight(28)
        self.filter_combo.addItem("全部", "")
        for cat_id in CATEGORY_ORDER:
            self.filter_combo.addItem(CATEGORY_ZH.get(cat_id, cat_id), cat_id)
        self.filter_combo.addItem("僅已分析", "__documented__")
        self.filter_combo.currentIndexChanged.connect(self._on_search)
        top_bar.addWidget(self.filter_combo)

        layout.addLayout(top_bar)

        # ── 主體: 左右分割 ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # [左] 樹狀清單
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Type", "名稱", "狀態"])
        self.tree.setIconSize(QSize(28, 28))
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(18)
        self.tree.currentItemChanged.connect(self._on_item_selected)
        self.tree.setFont(QFont("Microsoft JhengHei UI", 9))

        # 欄位寬度: Type 固定, 名稱自適應填滿, 狀態固定
        header = self.tree.header()
        header.setFont(QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold))
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(2, 74)

        # 狀態欄使用 badge delegate
        self._status_delegate = StatusBadgeDelegate(self.tree)
        self.tree.setItemDelegateForColumn(2, self._status_delegate)

        # 樹狀清單風格
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                outline: none;
            }
            QTreeWidget::item {
                padding: 2px 0px;
                min-height: 26px;
            }
            QTreeWidget::item:selected {
                background: #E3F2FD;
                color: #1565C0;
            }
            QTreeWidget::item:hover:!selected {
                background: #F5F5F5;
            }
            QHeaderView::section {
                background: #FAFAFA;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                padding: 4px 8px;
                font-weight: bold;
            }
        """)

        splitter.addWidget(self.tree)

        # [右] 詳情面板
        self.detail_panel = self._build_detail_panel()
        splitter.addWidget(self.detail_panel)

        splitter.setSizes([420, 720])
        splitter.setHandleWidth(3)
        layout.addWidget(splitter)

        # ── 底部統計 ──
        self._build_stat_bar(layout)

        self._populate_tree()

    def _build_stat_bar(self, parent_layout: QVBoxLayout):
        """底部統計列"""
        total = len(self._catalog)
        documented = sum(1 for t in self._catalog if t.get("status") == "documented")
        cataloged = sum(1 for t in self._catalog if t.get("status") == "cataloged")
        placeholder = sum(1 for t in self._catalog if t.get("status") == "placeholder")

        stat_frame = QFrame()
        stat_frame.setFixedHeight(24)
        stat_frame.setStyleSheet(
            "QFrame { background: #FAFAFA; border: 1px solid #E0E0E0; "
            "border-radius: 3px; }"
        )
        stat_layout = QHBoxLayout(stat_frame)
        stat_layout.setContentsMargins(8, 0, 8, 0)
        stat_layout.setSpacing(14)

        pairs = [
            (f"共 {total} 項", "#333"),
            (f"已分析: {documented}", "#4CAF50"),
            (f"已建檔: {cataloged}", "#2196F3"),
            (f"預留: {placeholder}", "#9E9E9E"),
        ]
        for text, color in pairs:
            lbl = QLabel(text)
            lbl.setFont(QFont("Microsoft JhengHei UI", 8))
            lbl.setStyleSheet(f"color: {color}; border: none; background: transparent;")
            stat_layout.addWidget(lbl)

        stat_layout.addStretch()
        self.stat_label = stat_frame
        parent_layout.addWidget(stat_frame)

    def _build_detail_panel(self) -> QWidget:
        """建構右側詳情面板：標題列 + 上下分割（預覽 / 文字）"""
        outer = QWidget()
        outer.setStyleSheet("background: white;")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(16, 10, 16, 6)
        outer_layout.setSpacing(4)

        # ═══════════════════════════════
        #  標題區 (固定在頂部，不捲動)
        # ═══════════════════════════════
        # ── 標題列 ──
        title_row = QHBoxLayout()
        title_row.setSpacing(10)
        self.lbl_type_id = QLabel("")
        self.lbl_type_id.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self.lbl_type_id.setStyleSheet("color: #212121;")
        title_row.addWidget(self.lbl_type_id)
        self.lbl_status_badge = QLabel("")
        self.lbl_status_badge.setFixedHeight(24)
        title_row.addWidget(self.lbl_status_badge)
        title_row.addStretch()
        self.btn_open_pdf = QPushButton("📄 開啟 PDF")
        self.btn_open_pdf.setEnabled(False)
        self.btn_open_pdf.setFont(QFont("Microsoft JhengHei UI", 9))
        self.btn_open_pdf.setFixedHeight(30)
        self.btn_open_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_pdf.setStyleSheet(
            "QPushButton { background: #1976D2; color: white; border: none; "
            "border-radius: 4px; padding: 4px 14px; font-weight: bold; }"
            "QPushButton:hover { background: #1565C0; }"
            "QPushButton:disabled { background: #E0E0E0; color: #999; }"
        )
        self.btn_open_pdf.clicked.connect(self._on_open_pdf)
        title_row.addWidget(self.btn_open_pdf)
        outer_layout.addLayout(title_row)

        # ── 英文名 + 中文名 ──
        self.lbl_name_en = QLabel("")
        self.lbl_name_en.setFont(QFont("Segoe UI", 11))
        self.lbl_name_en.setStyleSheet("color: #424242;")
        outer_layout.addWidget(self.lbl_name_en)

        self.lbl_name_zh = QLabel("")
        self.lbl_name_zh.setFont(QFont("Microsoft JhengHei UI", 11))
        self.lbl_name_zh.setStyleSheet("color: #1565C0; font-weight: bold;")
        outer_layout.addWidget(self.lbl_name_zh)

        # ── 圖號 + 適用範圍 ──
        info_row = QHBoxLayout()
        info_row.setSpacing(20)
        self.lbl_drawing = QLabel("")
        self.lbl_drawing.setFont(QFont("Microsoft JhengHei UI", 9))
        self.lbl_drawing.setStyleSheet("color: #666;")
        info_row.addWidget(self.lbl_drawing)
        info_row.addStretch()
        self.lbl_range = QLabel("")
        self.lbl_range.setFont(QFont("Microsoft JhengHei UI", 9))
        self.lbl_range.setStyleSheet("color: #666;")
        info_row.addWidget(self.lbl_range)
        outer_layout.addLayout(info_row)

        # ── 分隔線 ──
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet("background: #BDBDBD; border: none;")
        outer_layout.addWidget(line)

        # ═══════════════════════════════
        #  上下 Splitter: 預覽 / 內容
        # ═══════════════════════════════
        self._detail_splitter = QSplitter(Qt.Orientation.Vertical)
        self._detail_splitter.setHandleWidth(6)
        self._detail_splitter.setStyleSheet(
            "QSplitter::handle { background: #E0E0E0; }"
        )

        # ───── 上半：PDF 預覽 ─────
        preview_widget = QWidget()
        preview_widget.setStyleSheet("background: white;")
        preview_vbox = QVBoxLayout(preview_widget)
        preview_vbox.setContentsMargins(0, 4, 0, 0)
        preview_vbox.setSpacing(4)

        # 縮放控制列
        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(6)
        zoom_lbl = QLabel("圖面預覽")
        zoom_lbl.setFont(QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold))
        zoom_lbl.setStyleSheet("color: #555;")
        zoom_row.addWidget(zoom_lbl)
        zoom_row.addStretch()

        self.btn_zoom_out = QPushButton("－")
        self.btn_zoom_out.setFixedSize(28, 26)
        self.btn_zoom_out.setStyleSheet(
            "QPushButton { font-size: 14px; font-weight: bold; background: #EEEEEE; "
            "border: 1px solid #CCC; color: #333; }"
            "QPushButton:hover { background: #BDBDBD; }"
        )
        self.lbl_zoom_pct = QLabel("100%")
        self.lbl_zoom_pct.setFont(QFont("Consolas", 9))
        self.lbl_zoom_pct.setStyleSheet("color: #555;")
        self.lbl_zoom_pct.setFixedWidth(46)
        self.lbl_zoom_pct.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_zoom_in = QPushButton("＋")
        self.btn_zoom_in.setFixedSize(28, 26)
        self.btn_zoom_in.setStyleSheet(
            "QPushButton { font-size: 14px; font-weight: bold; background: #EEEEEE; "
            "border: 1px solid #CCC; color: #333; }"
            "QPushButton:hover { background: #BDBDBD; }"
        )
        self.btn_zoom_fit = QPushButton("適合寬度")
        self.btn_zoom_fit.setFixedHeight(26)
        self.btn_zoom_fit.setStyleSheet(
            "QPushButton { font-size: 11px; background: #EEEEEE; "
            "border: 1px solid #CCC; color: #333; padding: 0 8px; }"
            "QPushButton:hover { background: #BDBDBD; }"
        )
        zoom_row.addWidget(self.btn_zoom_out)
        zoom_row.addWidget(self.lbl_zoom_pct)
        zoom_row.addWidget(self.btn_zoom_in)
        zoom_row.addWidget(self.btn_zoom_fit)
        preview_vbox.addLayout(zoom_row)

        # 可捲動的圖片區
        self._preview_scroll = QScrollArea()
        self._preview_scroll.setWidgetResizable(False)
        self._preview_scroll.setStyleSheet(
            "QScrollArea { background: white; border: 1px solid #E0E0E0; }"
            "QScrollBar:vertical { width: 8px; }"
            "QScrollBar:horizontal { height: 8px; }"
        )
        self.lbl_preview = QLabel("選擇一個 Type 以查看詳情")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setMinimumSize(200, 200)
        self.lbl_preview.setStyleSheet(
            "background: white; color: #AAA; font-size: 13px; padding: 20px;"
        )
        self._preview_scroll.setWidget(self.lbl_preview)
        preview_vbox.addWidget(self._preview_scroll)

        self._preview_pixmap = None
        self._zoom_level = 1.0
        self.btn_zoom_in.clicked.connect(lambda: self._zoom_preview(0.15))
        self.btn_zoom_out.clicked.connect(lambda: self._zoom_preview(-0.15))
        self.btn_zoom_fit.clicked.connect(self._zoom_fit)

        self._detail_splitter.addWidget(preview_widget)

        # ───── 下半：文字內容 ─────
        content_widget = QWidget()
        content_widget.setStyleSheet("background: white;")
        content_vbox = QVBoxLayout(content_widget)
        content_vbox.setContentsMargins(0, 6, 0, 0)
        content_vbox.setSpacing(0)

        # Markdown 文件區
        self.md_browser = QTextBrowser()
        self.md_browser.setOpenExternalLinks(False)
        self.md_browser.setFont(QFont("Microsoft JhengHei UI", 10))
        self.md_browser.setStyleSheet(
            "QTextBrowser { border: 1px solid #E0E0E0; "
            "background: white; padding: 10px; }"
        )
        self.md_browser.setVisible(False)
        content_vbox.addWidget(self.md_browser)

        # 傳統欄位區
        self._legacy_scroll = QScrollArea()
        self._legacy_scroll.setWidgetResizable(True)
        self._legacy_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._legacy_scroll.setStyleSheet(
            "QScrollArea { background: white; }"
            "QScrollBar:vertical { width: 8px; }"
        )
        self._legacy_sections = QWidget()
        self._legacy_sections.setStyleSheet("background: white;")
        legacy_layout = QVBoxLayout(self._legacy_sections)
        legacy_layout.setContentsMargins(4, 4, 4, 4)
        legacy_layout.setSpacing(12)

        # ── 簡述 ──
        brief_group = self._make_section_group("簡述")
        brief_lay = QVBoxLayout(brief_group)
        brief_lay.setContentsMargins(12, 28, 12, 10)
        self.lbl_brief = QTextBrowser()
        self.lbl_brief.setMaximumHeight(72)
        self.lbl_brief.setOpenExternalLinks(False)
        self.lbl_brief.setFont(QFont("Microsoft JhengHei UI", 10))
        self.lbl_brief.setStyleSheet(
            "QTextBrowser { border: none; background: transparent; color: #333; }"
        )
        brief_lay.addWidget(self.lbl_brief)
        legacy_layout.addWidget(brief_group)

        # ── 編碼格式 ──
        desig_group = self._make_section_group("編碼格式 (Designation)")
        desig_lay = QVBoxLayout(desig_group)
        desig_lay.setContentsMargins(12, 28, 12, 10)
        self.lbl_designation = QLabel("")
        self.lbl_designation.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        self.lbl_designation.setStyleSheet(
            "color: #BF360C; padding: 6px 10px; "
            "background-color: #FFF3E0; border: 1px solid #FFCCBC;"
        )
        self.lbl_designation.setWordWrap(True)
        desig_lay.addWidget(self.lbl_designation)
        legacy_layout.addWidget(desig_group)

        # ── 完整說明 ──
        desc_group = self._make_section_group("說明")
        desc_lay = QVBoxLayout(desc_group)
        desc_lay.setContentsMargins(12, 28, 12, 10)
        self.txt_description = QTextBrowser()
        self.txt_description.setMinimumHeight(80)
        self.txt_description.setFont(QFont("Microsoft JhengHei UI", 10))
        self.txt_description.setStyleSheet(
            "QTextBrowser { border: none; background: transparent; color: #333; }"
        )
        desc_lay.addWidget(self.txt_description)
        legacy_layout.addWidget(desc_group)

        # ── 運算邏輯 ──
        calc_group = self._make_section_group("運算邏輯")
        calc_lay = QVBoxLayout(calc_group)
        calc_lay.setContentsMargins(12, 28, 12, 10)
        self.txt_calc_logic = QTextBrowser()
        self.txt_calc_logic.setMinimumHeight(60)
        self.txt_calc_logic.setFont(QFont("Consolas", 10))
        self.txt_calc_logic.setStyleSheet(
            "QTextBrowser { border: none; background-color: #FAFAFA; "
            "color: #212121; padding: 8px; }"
        )
        calc_lay.addWidget(self.txt_calc_logic)
        legacy_layout.addWidget(calc_group)

        legacy_layout.addStretch()
        self._legacy_scroll.setWidget(self._legacy_sections)
        content_vbox.addWidget(self._legacy_scroll)

        self._detail_splitter.addWidget(content_widget)

        # 預設比例: 預覽佔 55%, 文字佔 45%
        self._detail_splitter.setStretchFactor(0, 55)
        self._detail_splitter.setStretchFactor(1, 45)

        outer_layout.addWidget(self._detail_splitter, 1)
        return outer

    @staticmethod
    def _make_section_group(title: str) -> QGroupBox:
        """建立統一風格的 section group"""
        group = QGroupBox(title)
        group.setFont(QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold))
        group.setStyleSheet(
            "QGroupBox { border: 1px solid #E8E8E8; border-radius: 6px; "
            "margin-top: 10px; padding-top: 4px; background: #FAFAFA; }"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; "
            "padding: 0 6px; color: #555; }"
        )
        return group

    # ══════════════════════════════════════════
    #  樹狀清單建構
    # ══════════════════════════════════════════
    def _populate_tree(self):
        """根據 _filtered 重新填充樹狀清單"""
        self.tree.clear()
        # 按分類分組
        groups: dict[str, list[dict]] = {}
        for t in self._filtered:
            cat = t.get("category", "special")
            groups.setdefault(cat, []).append(t)

        for cat_id in CATEGORY_ORDER:
            items = groups.get(cat_id, [])
            if not items:
                continue
            # 數字排序: 取出 type_id 中的數字部分
            items.sort(key=lambda t: _type_sort_key(t["type_id"]))
            cat_node = QTreeWidgetItem(self.tree)
            cat_label = CATEGORY_ZH.get(cat_id, cat_id)
            doc_count = sum(1 for t in items if t.get("status") == "documented")
            cat_node.setText(0, f"{cat_label}  ({doc_count}/{len(items)})")
            cat_node.setFont(0, QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold))
            cat_node.setForeground(0, QColor("#424242"))
            cat_node.setExpanded(True)
            cat_node.setFlags(cat_node.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            for t in items:
                child = QTreeWidgetItem(cat_node)
                child.setText(0, t["type_id"])
                # 顯示名稱：優先中文，其次英文
                display_name = (
                    t.get("name_zh") or t.get("name_en") or ""
                )
                child.setText(1, display_name)
                status_zh, status_color = STATUS_MAP.get(
                    t.get("status", "placeholder"), ("未知", "#999")
                )
                child.setText(2, status_zh)
                # 儲存顏色供 StatusBadgeDelegate 使用
                child.setData(2, Qt.ItemDataRole.UserRole + 1, status_color)
                child.setData(0, Qt.ItemDataRole.UserRole, t)

                # 小圖示
                icon = self._get_icon(t["type_id"])
                if icon:
                    child.setIcon(0, icon)

                # 已分析的粗體 + 預留的灰色
                if t.get("status") == "documented":
                    bold_f = QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold)
                    child.setFont(0, bold_f)
                    child.setFont(1, bold_f)
                elif t.get("status") == "placeholder":
                    child.setForeground(1, QColor("#999"))

    # ══════════════════════════════════════════
    #  圖示
    # ══════════════════════════════════════════
    _icon_cache: dict[str, QIcon | None] = {}

    def _get_icon(self, type_id: str) -> QIcon | None:
        """從 assets/Type_icon/ 載入小圖示，格式 {type_id}_Type.png"""
        if type_id in self._icon_cache:
            return self._icon_cache[type_id]
        candidates = [
            os.path.join(_ICON_DIR, f"{type_id}_Type.png"),
            os.path.join(_ICON_DIR, f"{type_id}.png"),
        ]
        for path in candidates:
            if os.path.exists(path):
                icon = QIcon(QPixmap(path))
                self._icon_cache[type_id] = icon
                return icon
        self._icon_cache[type_id] = None
        return None

    # ══════════════════════════════════════════
    #  搜尋 / 篩選
    # ══════════════════════════════════════════
    def _on_search(self):
        keyword = self.search_input.text().strip().lower()
        cat_filter = self.filter_combo.currentData()

        self._filtered = []
        for t in self._catalog:
            # 分類篩選
            if cat_filter == "__documented__":
                if t.get("status") != "documented":
                    continue
            elif cat_filter and t.get("category") != cat_filter:
                continue

            # 關鍵字
            if keyword:
                searchable = " ".join([
                    t.get("type_id", ""),
                    t.get("name_en", ""),
                    t.get("name_zh", ""),
                    t.get("brief", ""),
                    t.get("drawing_no", ""),
                ]).lower()
                if keyword not in searchable:
                    continue

            self._filtered.append(t)

        self._populate_tree()

    # ══════════════════════════════════════════
    #  詳情顯示
    # ══════════════════════════════════════════
    def _on_item_selected(self, current, previous):
        if current is None:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if data is None:
            return
        self._show_detail(data)

    def _show_detail(self, t: dict):
        """填充右側詳情面板"""
        self._current_type = t

        self.lbl_type_id.setText(f'Type {t["type_id"]}')
        name_en = t.get("name_en", "")
        name_zh = t.get("name_zh", "")
        self.lbl_name_en.setText(name_en if name_en else "")
        self.lbl_name_en.setVisible(bool(name_en))
        self.lbl_name_zh.setText(name_zh if name_zh else "")
        self.lbl_name_zh.setVisible(bool(name_zh))

        # 狀態 badge
        status = t.get("status", "planned")
        status_zh, status_color = STATUS_MAP.get(status, ("未知", "#999"))
        self.lbl_status_badge.setText(f"  {status_zh}  ")
        self.lbl_status_badge.setStyleSheet(
            f"background: {status_color}; color: white; border-radius: 4px; "
            f"font-size: 11px; font-weight: bold; padding: 2px 10px;"
        )

        # 圖號 + 範圍
        dno = t.get("drawing_no", "")
        self.lbl_drawing.setText(f"圖號: {dno}" if dno else "")
        rng = t.get("line_size_range", "")
        self.lbl_range.setText(f"適用範圍: {rng}" if rng else "")

        # PDF 按鈕
        pdf_file = t.get("pdf_file", "")
        pdf_path = os.path.join(_PDF_DIR, pdf_file) if pdf_file else ""
        self.btn_open_pdf.setEnabled(bool(pdf_file))
        self.btn_open_pdf.setToolTip(pdf_path if pdf_file else "無 PDF 檔")

        # 圖面預覽
        self._load_preview(t)

        # ── 判斷：有 .md 文件 → 渲染 Markdown；否則 → 傳統欄位 ──
        doc_file = t.get("doc_file", "")
        md_text = _load_doc_file(doc_file)

        if md_text:
            # Markdown 模式
            html = _render_markdown(md_text)
            self.md_browser.setHtml(html)
            self.md_browser.setVisible(True)
            self._legacy_scroll.setVisible(False)
        else:
            # 傳統模式 (fallback)
            self.md_browser.setVisible(False)
            self._legacy_scroll.setVisible(True)

            # 簡述
            brief = t.get("brief", "（無簡述）")
            self.lbl_brief.setHtml(
                f'<p style="font-size:10.5pt; color:#333; line-height:1.6;">{brief}</p>'
            )

            # 編碼格式
            desig = t.get("designation", "")
            self.lbl_designation.setText(desig if desig else "—")

            # 完整說明
            desc = t.get("description", "")
            if desc:
                self.txt_description.setHtml(
                    f'<p style="font-size:10.5pt; color:#333; line-height:1.6;">{desc}</p>'
                )
            else:
                self.txt_description.setHtml(
                    '<p style="color:#999; font-size:10pt;">尚未填寫，可在 type_catalog.json 中更新。</p>'
                )

            # 運算邏輯
            calc = t.get("calc_logic", "")
            if calc:
                html_calc = calc.replace("\n", "<br>")
                self.txt_calc_logic.setHtml(
                    f'<pre style="font-family:Consolas; font-size:10pt; '
                    f'color:#212121; line-height:1.5;">{html_calc}</pre>'
                )
            else:
                self.txt_calc_logic.setHtml(
                    '<p style="color:#999; font-size:10pt;">尚未填寫運算邏輯。</p>'
                )

    def _load_preview(self, t: dict):
        """嘗試載入預覽: PNG 優先 → PDF 渲染 → 提示"""
        type_id = t["type_id"]
        self._preview_pixmap = None

        # 1) 嘗試 PNG/JPG 預覽圖
        candidates = [
            os.path.join(_PREVIEW_DIR, f"{type_id}.png"),
            os.path.join(_PREVIEW_DIR, f"{type_id}.jpg"),
        ]
        pdf_name = t.get("pdf_file", "")
        if pdf_name:
            base = os.path.splitext(pdf_name)[0]
            candidates.append(os.path.join(_PREVIEW_DIR, f"{base}.png"))
            candidates.append(os.path.join(_PREVIEW_DIR, f"{base}.jpg"))
        candidates.append(os.path.join(_ICON_DIR, f"{type_id}.png"))

        for path in candidates:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self._preview_pixmap = pixmap
                    self._zoom_fit()
                    return

        # 2) 嘗試從 PDF 渲染第一頁
        pdf_file = pdf_name or f"{type_id}.pdf"
        pdf_path = os.path.join(_PDF_DIR, pdf_file)
        if os.path.exists(pdf_path):
            try:
                doc = fitz.open(pdf_path)
                page = doc[0]
                mat = fitz.Matrix(2.5, 2.5)
                pix = page.get_pixmap(matrix=mat)
                img = QImage(
                    pix.samples, pix.width, pix.height,
                    pix.stride, QImage.Format.Format_RGB888,
                )
                pixmap = QPixmap.fromImage(img)
                doc.close()
                if not pixmap.isNull():
                    self._preview_pixmap = pixmap
                    self._zoom_fit()
                    return
            except Exception:
                pass

        # 3) 都沒有 → 提示
        self.lbl_preview.clear()
        self.lbl_preview.setMinimumSize(400, 200)
        self.lbl_preview.setText(
            f"尚無 PDF 或預覽圖\n\n"
            f"請將 PDF 放入: assets/Type/\n"
            f"檔名: {pdf_file}"
        )
        self.lbl_preview.setStyleSheet(
            "background: #FAFAFA; color: #AAA; font-size: 12px; padding: 16px;"
        )
        self.lbl_zoom_pct.setText("—")

    def _apply_zoom(self):
        """依目前 _zoom_level 縮放圖片"""
        if not self._preview_pixmap:
            return
        new_w = int(self._preview_pixmap.width() * self._zoom_level)
        scaled = self._preview_pixmap.scaledToWidth(
            max(100, new_w),
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_preview.setPixmap(scaled)
        self.lbl_preview.resize(scaled.size())
        self.lbl_preview.setStyleSheet("background: white;")
        self.lbl_zoom_pct.setText(f"{int(self._zoom_level * 100)}%")

    def _zoom_preview(self, delta: float):
        """放大或縮小"""
        new_level = self._zoom_level + delta
        self._zoom_level = max(0.2, min(3.0, new_level))
        self._apply_zoom()

    def _zoom_fit(self):
        """適合寬度"""
        if not self._preview_pixmap:
            return
        available_w = self._preview_scroll.viewport().width() - 4
        if available_w <= 0:
            available_w = 600
        self._zoom_level = available_w / max(1, self._preview_pixmap.width())
        self._zoom_level = max(0.2, min(3.0, self._zoom_level))
        self._apply_zoom()

    def _on_open_pdf(self):
        """用系統預設程式開啟 PDF"""
        t = getattr(self, "_current_type", None)
        if not t:
            return
        pdf_file = t.get("pdf_file", "")
        if not pdf_file:
            return
        pdf_path = os.path.join(_PDF_DIR, pdf_file)
        if not os.path.exists(pdf_path):
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self, "找不到 PDF",
                f"檔案不存在:\n{pdf_path}\n\n請確認 PDF 檔案已放入「單張-本案有關」資料夾。"
            )
            return

        if sys.platform == "win32":
            os.startfile(pdf_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", pdf_path])
        else:
            subprocess.run(["xdg-open", pdf_path])
