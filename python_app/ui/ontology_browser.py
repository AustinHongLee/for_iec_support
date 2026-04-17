"""
支撐架構瀏覽器 (Ontology Browser)
從 support_ontology.json 驅動的多層樹狀結構瀏覽 + 選型決策

架構設計支援未來擴充:
  - 多設計公司 (standards) 各自的命名體系
  - 家族關係 + 介面引用鏈
  - 約束矩陣比較
  - 選型決策樹
"""
import json
import os
import re

import markdown

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QLabel, QTextBrowser,
    QFrame, QComboBox, QGroupBox, QPushButton,
    QHeaderView, QScrollArea, QStackedWidget,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap

# ─── 路徑 ────────────────────────────────────
_APP_DIR = os.path.dirname(os.path.dirname(__file__))
_ONTOLOGY_PATH = os.path.join(
    _APP_DIR, "configs", "support_ontology.json"
)
_CATALOG_PATH = os.path.join(
    _APP_DIR, "configs", "type_catalog.json"
)
_DOCS_DIR = os.path.join(_APP_DIR, "docs", "types")
_ICON_DIR = os.path.join(_APP_DIR, "assets", "Type_icon")

# ─── Markdown ─────────────────────────────────
_MD_CSS = """\
<style>
body {
    font-family: 'Microsoft JhengHei UI', 'Segoe UI', sans-serif;
    font-size: 10.5pt; color: #222; line-height: 1.7;
    margin: 4px 8px; padding: 0;
}
h1 { font-size: 15pt; color: #0D47A1;
     border-bottom: 2px solid #1976D2;
     padding-bottom: 6px; margin: 12px 0 8px; }
h2 { font-size: 12.5pt; color: #1565C0;
     border-bottom: 1px solid #BBDEFB;
     padding-bottom: 4px; margin: 20px 0 8px; }
h3 { font-size: 11pt; color: #333;
     margin: 14px 0 6px; }
table { border-collapse: collapse; width: 100%;
        margin: 10px 0; }
th { background: #E3F2FD; color: #0D47A1;
     font-weight: bold; font-size: 10pt;
     border: 1px solid #90CAF9; padding: 7px 12px;
     text-align: left; }
td { border: 1px solid #BBDEFB; padding: 6px 12px;
     font-size: 10pt; background: #FFF; color: #333; }
code { font-family: Consolas, monospace; font-size: 10pt;
       background: #FFF3E0; color: #BF360C; }
pre  { font-family: Consolas, monospace; font-size: 9.5pt;
       background: #FAFAFA; color: #212121;
       padding: 14px 18px; border: 1px solid #E0E0E0;
       line-height: 1.5; white-space: pre; }
blockquote { border-left: 4px solid #42A5F5;
             background: #E3F2FD;
             padding: 10px 16px; margin: 10px 0;
             color: #1A237E; }
strong { color: #1B5E20; }
em { color: #4A148C; }
p { margin: 6px 0; }
.badge { display: inline-block; padding: 2px 8px;
         border-radius: 3px; font-size: 9pt;
         font-weight: bold; color: white; }
.tag { display: inline-block; padding: 1px 6px;
       border-radius: 3px; font-size: 8.5pt;
       background: #E8EAF6; color: #283593;
       margin: 1px 2px; }
</style>
"""

_md_converter = markdown.Markdown(
    extensions=["tables", "fenced_code", "nl2br"],
    output_format="html",
)


def _render_md(md_text):
    _md_converter.reset()
    body = _md_converter.convert(md_text)
    return f"<html><head>{_MD_CSS}</head><body>{body}</body></html>"


# ─── 資料載入 ─────────────────────────────────
def _load_ontology():
    if not os.path.exists(_ONTOLOGY_PATH):
        return {}
    with open(_ONTOLOGY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_catalog():
    if not os.path.exists(_CATALOG_PATH):
        return {}
    with open(_CATALOG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 建立 type_id → entry 的快速查表
    return {t["type_id"]: t for t in data.get("types", [])}


# ─── Widget ───────────────────────────────────
class OntologyBrowserWidget(QWidget):
    """支撐架構瀏覽器 — 左側 ontology 樹 + 右側詳情"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ontology = _load_ontology()
        self._catalog = _load_catalog()
        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 4)
        root.setSpacing(4)

        # ── 頂部: 設計標準切換 ──
        top = QHBoxLayout()
        top.setSpacing(8)

        lbl = QLabel("設計標準:")
        lbl.setFont(QFont("Microsoft JhengHei UI", 9))
        top.addWidget(lbl)

        self.std_combo = QComboBox()
        self.std_combo.setFont(
            QFont("Microsoft JhengHei UI", 9)
        )
        self.std_combo.setFixedHeight(28)
        self._populate_standards()
        self.std_combo.currentIndexChanged.connect(
            self._on_standard_changed
        )
        top.addWidget(self.std_combo)
        top.addStretch()

        # 統計
        self.lbl_stats = QLabel()
        self.lbl_stats.setFont(
            QFont("Microsoft JhengHei UI", 8)
        )
        self.lbl_stats.setStyleSheet("color: #666;")
        top.addWidget(self.lbl_stats)
        root.addLayout(top)

        # ── 主體: 左右 splitter ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # [左] 樹
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["架構", "說明"])
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)
        self.tree.setIndentation(22)
        self.tree.setFont(QFont("Microsoft JhengHei UI", 9))
        self.tree.currentItemChanged.connect(
            self._on_tree_selected
        )

        hdr = self.tree.header()
        hdr.setFont(
            QFont("Microsoft JhengHei UI", 9, QFont.Weight.Bold)
        )
        hdr.setStretchLastSection(True)
        hdr.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Fixed
        )
        self.tree.setColumnWidth(0, 240)

        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ddd;
                border-radius: 4px; outline: none;
            }
            QTreeWidget::item {
                padding: 3px 0; min-height: 28px;
            }
            QTreeWidget::item:selected {
                background: #E3F2FD; color: #1565C0;
            }
            QTreeWidget::item:hover:!selected {
                background: #F5F5F5;
            }
            QHeaderView::section {
                background: #FAFAFA; border: none;
                border-bottom: 2px solid #E0E0E0;
                padding: 4px 8px; font-weight: bold;
            }
        """)
        splitter.addWidget(self.tree)

        # [右] 詳情
        self.detail_browser = QTextBrowser()
        self.detail_browser.setOpenExternalLinks(False)
        self.detail_browser.setFont(
            QFont("Microsoft JhengHei UI", 10)
        )
        self.detail_browser.setStyleSheet(
            "QTextBrowser { border: 1px solid #E0E0E0; "
            "background: white; padding: 10px; }"
        )
        splitter.addWidget(self.detail_browser)

        splitter.setSizes([360, 680])
        splitter.setHandleWidth(3)
        root.addWidget(splitter, 1)

        # 填充
        self._build_tree()
        self._update_stats()
        self._show_overview()

    # ══════════════════════════════════════════
    #  設計標準
    # ══════════════════════════════════════════
    def _populate_standards(self):
        standards = self._ontology.get("standards", [])
        # 永遠有預設的 IEC
        self.std_combo.addItem(
            "IEC (International Engineering)", "iec"
        )
        for std in standards:
            self.std_combo.addItem(
                std.get("label", std["id"]),
                std["id"],
            )

    def _on_standard_changed(self, idx):
        self._build_tree()
        self._update_stats()
        self._show_overview()

    # ══════════════════════════════════════════
    #  樹狀結構
    # ══════════════════════════════════════════
    def _build_tree(self):
        self.tree.clear()
        ont = self._ontology
        sub_groups = ont.get("sub_groups", [])
        families = ont.get("families", {})
        status_defs = ont.get("status_definitions", {})

        # 排序
        sub_groups_sorted = sorted(
            sub_groups, key=lambda g: g.get("sort", 99)
        )

        for sg in sub_groups_sorted:
            sg_node = self._make_group_node(sg)
            self.tree.addTopLevelItem(sg_node)

            type_ids = sg.get("types", [])
            type_ids_sorted = sorted(
                type_ids,
                key=lambda t: self._type_sort(t),
            )

            for tid in type_ids_sorted:
                cat_entry = self._catalog.get(tid, {})
                self._make_type_node(
                    sg_node, tid, cat_entry,
                    status_defs,
                )

            # 預設展開 beam_shoe / interface
            expand_ids = ont.get(
                "display_config", {}
            ).get(
                "sub_group_style", {}
            ).get("expanded_by_default", [])
            if sg["id"] in expand_ids:
                sg_node.setExpanded(True)

        # 家族節點 (頂層)
        if families:
            fam_root = QTreeWidgetItem(self.tree)
            fam_root.setText(0, "🔗 家族關係")
            fam_root.setFont(
                0,
                QFont("Microsoft JhengHei UI", 10,
                      QFont.Weight.Bold),
            )
            fam_root.setForeground(0, QColor("#6A1B9A"))
            fam_root.setFlags(
                fam_root.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
            )
            fam_root.setExpanded(True)

            for fam_id, fam in families.items():
                fam_node = QTreeWidgetItem(fam_root)
                fam_node.setText(
                    0, fam.get("label_zh", fam_id)
                )
                fam_node.setText(
                    1, fam.get("label_en", "")
                )
                fam_node.setFont(
                    0,
                    QFont("Microsoft JhengHei UI", 9,
                          QFont.Weight.Bold),
                )
                fam_node.setForeground(0, QColor("#7B1FA2"))
                fam_node.setData(
                    0, Qt.ItemDataRole.UserRole,
                    {"_kind": "family", "_id": fam_id},
                )

        # 未分類
        all_assigned = set()
        for sg in sub_groups:
            all_assigned.update(sg.get("types", []))

        support_types = [
            tid for tid, e in self._catalog.items()
            if e.get("category") == "support"
            and tid not in all_assigned
            and e.get("status") != "placeholder"
        ]
        if support_types:
            uc_node = QTreeWidgetItem(self.tree)
            uc_node.setText(
                0, "📦 其他 / 未分類"
            )
            uc_node.setFont(
                0,
                QFont("Microsoft JhengHei UI", 9,
                      QFont.Weight.Bold),
            )
            uc_node.setForeground(0, QColor("#757575"))
            uc_node.setFlags(
                uc_node.flags()
                & ~Qt.ItemFlag.ItemIsSelectable
            )
            for tid in sorted(
                support_types,
                key=lambda t: self._type_sort(t),
            ):
                self._make_type_node(
                    uc_node, tid,
                    self._catalog.get(tid, {}),
                    status_defs,
                )

    def _make_group_node(self, sg):
        node = QTreeWidgetItem()
        icon = sg.get("icon", "")
        label = sg.get("label_zh", sg["id"])
        count = len(sg.get("types", []))

        # 計算已分析數
        doc_count = sum(
            1 for tid in sg.get("types", [])
            if self._catalog.get(tid, {}).get("status")
            == "documented"
        )

        node.setText(
            0, f"{icon} {label}  ({doc_count}/{count})"
        )
        node.setText(1, sg.get("label_en", ""))
        node.setFont(
            0,
            QFont("Microsoft JhengHei UI", 9,
                  QFont.Weight.Bold),
        )
        node.setForeground(0, QColor("#37474F"))
        node.setExpanded(False)
        node.setFlags(
            node.flags() & ~Qt.ItemFlag.ItemIsSelectable
        )
        node.setData(
            0, Qt.ItemDataRole.UserRole,
            {"_kind": "group", "_id": sg["id"]},
        )
        return node

    def _make_type_node(self, parent, tid, entry,
                        status_defs):
        child = QTreeWidgetItem(parent)
        child.setText(0, f"TYPE-{tid}")

        name = (
            entry.get("name_zh")
            or entry.get("name_en")
            or ""
        )
        status = entry.get("status", "placeholder")
        sdef = status_defs.get(status, {})
        color = sdef.get("color", "#999")

        child.setText(1, name)
        child.setData(
            0, Qt.ItemDataRole.UserRole,
            {"_kind": "type", "_id": tid},
        )

        # 粗體 / 灰色
        if status == "documented":
            f = QFont("Microsoft JhengHei UI", 9,
                      QFont.Weight.Bold)
            child.setFont(0, f)
            child.setFont(1, f)
            child.setForeground(0, QColor("#1B5E20"))
        elif status == "placeholder":
            child.setForeground(0, QColor("#BDBDBD"))
            child.setForeground(1, QColor("#BDBDBD"))
        else:
            child.setForeground(0, QColor("#1565C0"))

        # icon
        icon = self._get_icon(tid)
        if icon:
            child.setIcon(0, icon)

    # ══════════════════════════════════════════
    #  詳情顯示
    # ══════════════════════════════════════════
    def _on_tree_selected(self, current, prev):
        if current is None:
            return
        data = current.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return

        kind = data.get("_kind")
        if kind == "type":
            self._show_type_detail(data["_id"])
        elif kind == "family":
            self._show_family_detail(data["_id"])

    def _show_overview(self):
        ont = self._ontology
        groups = ont.get("sub_groups", [])
        families = ont.get("families", {})

        lines = [
            "# 支撐架構總覽",
            "",
            f"**設計標準**: "
            f"{self.std_combo.currentText()}",
            "",
            f"**分組數**: {len(groups)}　"
            f"**家族數**: {len(families)}　"
            f"**已分析**: "
            f"{sum(1 for e in self._catalog.values() if e.get('status')=='documented')}",
            "",
            "---",
            "",
            "## 功能分組",
            "",
            "| # | 分組 | 類型數 | 已分析 |",
            "|---|------|--------|--------|",
        ]
        for sg in sorted(
            groups, key=lambda g: g.get("sort", 99)
        ):
            icon = sg.get("icon", "")
            label = sg.get("label_zh", "")
            tids = sg.get("types", [])
            doc = sum(
                1 for tid in tids
                if self._catalog.get(tid, {}).get("status")
                == "documented"
            )
            lines.append(
                f"| {sg.get('sort','')} "
                f"| {icon} {label} "
                f"| {len(tids)} | {doc} |"
            )

        if families:
            lines += [
                "", "---", "",
                "## 家族關係", "",
            ]
            for fid, fam in families.items():
                members = fam.get("members", [])
                interfaces = fam.get("interfaces", [])
                lines.append(
                    f"### {fam.get('label_zh', fid)}"
                )
                lines.append(
                    f"{fam.get('description', '')}"
                )
                lines.append(
                    f"- **成員**: "
                    f"{', '.join('TYPE-'+m for m in members)}"
                )
                if interfaces:
                    lines.append(
                        f"- **介面層**: "
                        f"{', '.join('TYPE-'+i for i in interfaces)}"
                    )
                lines.append("")

        std = self.std_combo.currentData()
        lines += [
            "", "---", "",
            "## 設計標準擴充",
            "",
            "> 此系統支援多家設計公司的命名體系。",
            "> 每家公司可定義自己的 type 對應、"
            "命名慣例、常數單位差異。",
            "",
            "目前使用: **IEC (International Engineering)**",
        ]

        html = _render_md("\n".join(lines))
        self.detail_browser.setHtml(html)

    def _show_type_detail(self, tid):
        entry = self._catalog.get(tid, {})
        ont = self._ontology
        tags = ont.get("type_tags", {}).get(tid, [])
        tag_defs = ont.get("tag_definitions", {})
        status_defs = ont.get("status_definitions", {})

        status = entry.get("status", "placeholder")
        sdef = status_defs.get(status, {})
        badge_color = sdef.get("color", "#999")
        badge_text = sdef.get("label_zh", status)

        # 找所屬 sub_group
        group_label = "未分類"
        for sg in ont.get("sub_groups", []):
            if tid in sg.get("types", []):
                group_label = (
                    f"{sg.get('icon','')} "
                    f"{sg.get('label_zh', sg['id'])}"
                )
                break

        # 找所屬 family
        family_info = []
        for fid, fam in ont.get("families", {}).items():
            if tid in fam.get("members", []):
                family_info.append(
                    f"**{fam.get('label_zh', fid)}** (成員)"
                )
                # 約束矩陣
                cm = fam.get("constraint_matrix")
                if cm:
                    for row in cm.get("rows", []):
                        if row[0] == tid:
                            family_info.append(
                                f"- 軸向: {row[1]}"
                                f"　側向: {row[2]}"
                                f"　向上: {row[3]}"
                                f"　隔離: "
                                f"{'✅' if row[4] else '❌'}"
                            )
                            family_info.append(
                                f"- 本質: **{row[5]}**"
                            )
                            break
                # 引用鏈
                refs = fam.get("detail_refs", {})
                for dwg, info in refs.items():
                    if tid in info.get("used_by", []):
                        family_info.append(
                            f"- 引用 **{dwg}** "
                            f"(TYPE-{info['type_id']}): "
                            f"{info['role']}"
                        )
            elif tid in fam.get("interfaces", []):
                family_info.append(
                    f"**{fam.get('label_zh', fid)}**"
                    f" (介面層)"
                )
                # 被誰引用
                refs = fam.get("detail_refs", {})
                for dwg, info in refs.items():
                    if info.get("type_id") == tid:
                        users = ", ".join(
                            f"TYPE-{u}"
                            for u in info.get("used_by", [])
                        )
                        family_info.append(
                            f"- 提供 **{dwg}** → "
                            f"被 {users} 引用"
                        )

        lines = [
            f"# TYPE-{tid}",
            "",
            f'<span class="badge" '
            f'style="background:{badge_color}">'
            f'{badge_text}</span>',
            "",
            f"**中文**: "
            f"{entry.get('name_zh', '—')}",
            f"**英文**: "
            f"{entry.get('name_en', '—')}",
            f"**圖號**: "
            f"{entry.get('drawing_no', '—')}",
            f"**範圍**: "
            f"{entry.get('line_size_range', '—')}",
            f"**分組**: {group_label}",
            "",
        ]

        if family_info:
            lines += ["## 家族關係", ""] + family_info + [""]

        if tags:
            tag_html = " ".join(
                f'`{t}`' for t in tags
            )
            lines += [
                "## 語意標籤", "", tag_html, "",
            ]

        # .md 文件預覽 (前 30 行)
        doc_file = entry.get("doc_file", "")
        if doc_file:
            doc_path = os.path.join(_DOCS_DIR, doc_file)
            if os.path.isfile(doc_path):
                with open(doc_path, "r",
                          encoding="utf-8") as f:
                    md_content = f.read()
                lines += [
                    "---", "",
                    "## 分析文件", "",
                    md_content,
                ]

        html = _render_md("\n".join(lines))
        self.detail_browser.setHtml(html)

    def _show_family_detail(self, fam_id):
        ont = self._ontology
        fam = ont.get("families", {}).get(fam_id, {})
        if not fam:
            return

        lines = [
            f"# {fam.get('label_zh', fam_id)}",
            f"*{fam.get('label_en', '')}*",
            "",
            fam.get("description", ""),
            "",
        ]

        # 架構圖
        arch = fam.get("architecture", {})
        if arch:
            lines += ["## 架構", ""]
            for layer in arch.get("layers", []):
                lines.append(f"- {layer}")
            lines.append("")

            diagram = arch.get("diagram", [])
            if diagram:
                lines.append("```")
                for d in diagram:
                    lines.append(d)
                lines.append("```")
                lines.append("")

        # 約束矩陣
        cm = fam.get("constraint_matrix")
        if cm:
            cols = cm["columns"]
            header_map = {
                "type_id": "Type",
                "axial": "軸向",
                "lateral": "側向",
                "vertical_up": "向上",
                "isolation": "隔離",
                "essence_zh": "本質",
            }
            headers = [
                header_map.get(c, c) for c in cols
            ]
            lines += [
                "## 約束矩陣", "",
                "| " + " | ".join(headers) + " |",
                "|" + "|".join(
                    "---" for _ in headers
                ) + "|",
            ]
            for row in cm["rows"]:
                cells = []
                for i, val in enumerate(row):
                    if isinstance(val, bool):
                        cells.append(
                            "✅" if val else "❌"
                        )
                    elif cols[i] == "type_id":
                        cells.append(f"TYPE-{val}")
                    else:
                        cells.append(str(val))
                lines.append(
                    "| " + " | ".join(cells) + " |"
                )
            lines.append("")

        # 引用鏈
        refs = fam.get("detail_refs", {})
        if refs:
            lines += ["## 引用鏈", ""]
            for dwg, info in refs.items():
                users = ", ".join(
                    f"TYPE-{u}"
                    for u in info.get("used_by", [])
                )
                lines.append(
                    f"- **{dwg}** → TYPE-{info['type_id']}"
                    f" ({info['role']}) → 被 {users} 引用"
                )
            lines.append("")

        # 選型決策
        rules = ont.get("selector_rules", {})
        for rule_id, rule in rules.items():
            if rule.get("family_id") == fam_id:
                lines += [
                    "## 選型決策",
                    "",
                    f"**{rule.get('title_zh', '')}**",
                    "",
                    rule.get("description", ""),
                    "",
                ]
                for dr in rule.get("decision_tree", []):
                    cond = dr.get("condition", {})
                    cond_str = ", ".join(
                        f"{k}={v}" for k, v in cond.items()
                    )
                    lines.append(
                        f"- `{cond_str}` → "
                        f"**TYPE-{dr['result']}** — "
                        f"{dr.get('reason_zh', '')}"
                    )
                fb = rule.get("fallback")
                if fb:
                    lines.append(
                        f"- *預設* → "
                        f"**TYPE-{fb['result']}** — "
                        f"{fb.get('reason_zh', '')}"
                    )
                lines.append("")

        html = _render_md("\n".join(lines))
        self.detail_browser.setHtml(html)

    # ══════════════════════════════════════════
    #  統計
    # ══════════════════════════════════════════
    def _update_stats(self):
        total = len(self._catalog)
        documented = sum(
            1 for e in self._catalog.values()
            if e.get("status") == "documented"
        )
        groups = len(
            self._ontology.get("sub_groups", [])
        )
        families = len(
            self._ontology.get("families", {})
        )
        self.lbl_stats.setText(
            f"分組: {groups}　"
            f"家族: {families}　"
            f"已分析: {documented}/{total}"
        )

    # ══════════════════════════════════════════
    #  工具
    # ══════════════════════════════════════════
    _icon_cache: dict[str, QIcon | None] = {}

    def _get_icon(self, type_id):
        if type_id in self._icon_cache:
            return self._icon_cache[type_id]
        for fn in [
            f"{type_id}_Type.png",
            f"{type_id}.png",
        ]:
            path = os.path.join(_ICON_DIR, fn)
            if os.path.exists(path):
                icon = QIcon(QPixmap(path))
                self._icon_cache[type_id] = icon
                return icon
        self._icon_cache[type_id] = None
        return None

    @staticmethod
    def _type_sort(tid):
        m = re.match(r'^([A-Za-z\-]*)(\d+)(.*)', tid)
        if m:
            return (m.group(1), int(m.group(2)),
                    m.group(3))
        return (tid, 0, "")
