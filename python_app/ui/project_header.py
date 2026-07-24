"""Project-level status strip for the analysis workspace."""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QSizePolicy

from ui.theme import TOKENS


class ProjectHeader(QFrame):
    """Keep project-wide inputs and workflow status in one visible strip.

    Layout is grouped so intent is obvious at a glance:
      [清單名]  |  設定：全域材質 · 模式  |  狀態：材質確認 · 資料版本
    The left/middle groups are things the user sets; the right group is
    passive read-only status that populates after analysis.
    """

    def __init__(
        self,
        materials: Iterable[str],
        current_material: str = "SUS304",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("projectHeader")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            TOKENS["space"]["summary_x"],
            TOKENS["space"]["summary_y"],
            TOKENS["space"]["summary_x"],
            TOKENS["space"]["summary_y"],
        )
        layout.setSpacing(TOKENS["space"]["metric_gap"])

        # ── 清單名稱 ──
        layout.addWidget(self._caption("清單"))
        self.project_name_label = QLabel("未命名清單")
        self.project_name_label.setObjectName("projectName")
        layout.addWidget(self.project_name_label)

        layout.addSpacing(TOKENS["space"]["summary_gap"])
        layout.addWidget(self._separator())
        layout.addSpacing(TOKENS["space"]["summary_gap"])

        # ── 設定群組（使用者操作）──
        layout.addWidget(self._caption("全域上段管材質"))
        self.material_combo = QComboBox()
        self.material_combo.addItems(list(materials))
        self.material_combo.setEditable(True)
        self.material_combo.setCurrentText(current_material)
        layout.addWidget(self.material_combo)

        layout.addSpacing(TOKENS["space"]["summary_gap"])

        layout.addWidget(self._caption("模式"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["概算", "精算"])
        self.mode_combo.setEnabled(False)
        self.mode_combo.setToolTip("概算／精算模式將於後續模組啟用")
        layout.addWidget(self.mode_combo)

        layout.addStretch(1)

        layout.addWidget(self._separator())
        layout.addSpacing(TOKENS["space"]["summary_gap"])

        # ── 狀態群組（分析後回填的唯讀資訊）──
        self.completion_label = QLabel("材質確認：待分析")
        self.completion_label.setObjectName("projectHeaderStatus")
        self.completion_label.setEnabled(False)
        self.completion_label.setToolTip(
            "分析後顯示：使用全域上段管材質的啟用項目中，材質已確認的筆數"
        )
        layout.addWidget(self.completion_label)

        self.version_label = QLabel("資料版本：待分析")
        self.version_label.setObjectName("projectHeaderStatus")
        self.version_label.setEnabled(False)
        self.version_label.setToolTip(
            "分析後顯示：本次分析實際使用的 Type 計算資料版本"
        )
        layout.addWidget(self.version_label)

        self.setStyleSheet(self._stylesheet())

    @staticmethod
    def _caption(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("projectHeaderCaption")
        return label

    @staticmethod
    def _separator() -> QFrame:
        line = QFrame()
        line.setObjectName("projectHeaderSep")
        line.setFixedSize(1, 18)
        line.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        return line

    def set_project_name(self, name: str | None) -> None:
        self.project_name_label.setText((name or "").strip() or "未命名清單")

    def set_material_completion(self, confirmed: int, total: int) -> None:
        if total:
            text = f"材質確認：{confirmed}/{total}"
            tooltip = "使用全域上段管材質之啟用項目，其材質已確認的筆數"
        else:
            text = "材質確認：不適用"
            tooltip = "目前清單沒有使用全域上段管材質的 Type"
        self.completion_label.setText(text)
        self.completion_label.setEnabled(True)
        self.completion_label.setToolTip(tooltip)

    def enable_mode_selector(self) -> None:
        self.mode_combo.setEnabled(True)
        self.mode_combo.setToolTip("概算會標示假設值；精算遇未定值時預設禁止匯出")

    def set_data_versions(self, versions: list[str]) -> None:
        values = [value for value in dict.fromkeys(versions) if value]
        self.version_label.setText(
            "資料版本：" + (" / ".join(values) if values else "無版本資訊")
        )
        self.version_label.setEnabled(True)
        self.version_label.setToolTip("本次分析實際使用的 Type config 版本")

    def reset_data_versions(self) -> None:
        self.version_label.setText("資料版本：待分析")
        self.version_label.setEnabled(False)

    @staticmethod
    def _stylesheet() -> str:
        color = TOKENS["color"]
        font = TOKENS["font"]
        radius = TOKENS["radius"]
        return f"""
            QFrame#projectHeader {{
                background: {color['summary_bg']};
                border: 1px solid {color['summary_border']};
                border-radius: {radius['md']}px;
            }}
            QFrame#projectHeader QLabel {{
                border: none;
                color: {color['text']};
                font-size: {font['control']}px;
            }}
            QFrame#projectHeader QLabel#projectHeaderCaption {{
                color: {color['metric_label']};
            }}
            QFrame#projectHeader QLabel#projectName {{
                color: {color['primary_dark']};
                font-weight: bold;
            }}
            QFrame#projectHeader QLabel#projectHeaderStatus {{
                color: {color['metric_label']};
            }}
            QFrame#projectHeader QLabel:disabled {{
                color: {color['text_disabled']};
            }}
            QFrame#projectHeader QFrame#projectHeaderSep {{
                background: {color['summary_border']};
                border: none;
            }}
        """
