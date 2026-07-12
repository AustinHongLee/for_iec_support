"""Project-level status strip for the analysis workspace."""

from __future__ import annotations

from collections.abc import Iterable

from PyQt6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QLabel, QSizePolicy

from ui.theme import TOKENS


class ProjectHeader(QFrame):
    """Keep project-wide inputs and future workflow status in one visible strip."""

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
        layout.setSpacing(TOKENS["space"]["summary_gap"])

        layout.addWidget(self._caption("清單"))
        self.project_name_label = QLabel("未命名清單")
        self.project_name_label.setObjectName("projectName")
        layout.addWidget(self.project_name_label, 1)

        layout.addWidget(self._caption("全域上段管材質"))
        self.material_combo = QComboBox()
        self.material_combo.addItems(list(materials))
        self.material_combo.setEditable(True)
        self.material_combo.setCurrentText(current_material)
        layout.addWidget(self.material_combo)

        layout.addWidget(self._caption("模式"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["概算", "精算"])
        self.mode_combo.setEnabled(False)
        self.mode_combo.setToolTip("概算／精算模式將於後續模組啟用")
        layout.addWidget(self.mode_combo)

        self.completion_label = QLabel("完成度：待接入")
        self.completion_label.setEnabled(False)
        self.completion_label.setToolTip("材質確認完成度將於後續模組啟用")
        layout.addWidget(self.completion_label)

        self.version_label = QLabel("資料版本：待接入")
        self.version_label.setEnabled(False)
        self.version_label.setToolTip("資料版本提示將於後續模組啟用")
        layout.addWidget(self.version_label)

        self.setStyleSheet(self._stylesheet())

    @staticmethod
    def _caption(text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("projectHeaderCaption")
        return label

    def set_project_name(self, name: str | None) -> None:
        self.project_name_label.setText((name or "").strip() or "未命名清單")

    def set_material_completion(self, confirmed: int, total: int) -> None:
        self.completion_label.setText(f"材質確認：{confirmed}/{total}")
        self.completion_label.setEnabled(True)
        self.completion_label.setToolTip("啟用項目中已確認上段管材質的筆數")

    def enable_mode_selector(self) -> None:
        self.mode_combo.setEnabled(True)
        self.mode_combo.setToolTip("概算會標示假設值；精算遇未定值時預設禁止匯出")

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
            QFrame#projectHeader QLabel:disabled {{
                color: {color['text_disabled']};
            }}
        """
