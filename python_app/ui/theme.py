"""UI design tokens and global QSS builder."""

from __future__ import annotations


TOKENS = {
    "color": {
        "app_bg": "#EEF1F5",
        "surface": "#FFFFFF",
        "surface_soft": "#F4F6F9",
        "surface_hover": "#E9EEF5",
        "surface_pressed": "#DCE4EF",
        "surface_disabled": "#F0F1F3",
        "tab_bg": "transparent",
        "tab_hover": "#E7EDF6",
        "tab_selected": "transparent",
        "ink": "#1A2332",
        "text": "#2A3342",
        "text_muted": "#5B6878",
        "text_disabled": "#A6AEBB",
        "primary": "#175CD3",
        "primary_dark": "#1249A8",
        "primary_weak": "#D6E4FB",
        "border": "#DEE3EB",
        "border_control": "#CBD3DE",
        "border_soft": "#E7EBF1",
        "button_border": "#CDD5E0",
        "button_border_hover": "#175CD3",
        "button_border_disabled": "#E0E3E8",
        "list_divider": "#EFF2F6",
        "list_hover": "#F0F5FC",
        "table_border": "#DEE3EB",
        "table_grid": "#EDF0F5",
        "table_alt": "#F8FAFC",
        "table_header": "#F3F6FA",
        "table_header_text": "#46536A",
        "table_header_border": "#DCE2EA",
        "summary_bg": "#F7FAFE",
        "summary_border": "#DBE6F5",
        "metric_label": "#64748B",
        "metric_weight": "#1249A8",
        "metric_ok": "#15803D",
        "metric_muted": "#64748B",
        "metric_support": "#1A2332",
        "status_info": "#64748B",
        "status_busy": "#175CD3",
        "status_ok": "#15803D",
        "status_warn": "#C2570A",
        "status_high": "#C2410C",
        "status_error": "#DC2626",
        "scroll_handle": "#C3CCD9",
        "splitter": "#E2E7EE",
        "section_title": "#46536A",
    },
    "font": {
        "family": '"Segoe UI", "Microsoft JhengHei UI", "Noto Sans CJK TC", "PingFang TC", sans-serif',
        "control": 12,
        "table": 12,
        "metric_label": 11,
        "metric_value": 18,
        "metric_primary": 20,
    },
    "space": {
        "tab_y": 8,
        "tab_x": 16,
        "button_y": 5,
        "button_x": 12,
        "input_y": 4,
        "input_x": 8,
        "list_item_y": 3,
        "list_item_x": 6,
        "header_y": 6,
        "header_x": 9,
        "summary_y": 10,
        "summary_x": 14,
        "summary_gap": 18,
        "metric_gap": 6,
    },
    "radius": {
        "xs": 3,
        "sm": 6,
        "md": 8,
        "scroll": 4,
    },
}


def _px(value: int | float) -> str:
    return f"{value}px"


def build_stylesheet(t: dict = TOKENS) -> str:
    """Return the current global application stylesheet from design tokens."""
    color = t["color"]
    font = t["font"]
    space = t["space"]
    radius = t["radius"]
    family = font.get(
        "family",
        '"Segoe UI", "Microsoft JhengHei UI", "Noto Sans CJK TC", sans-serif',
    )
    section_title = color.get("section_title", color["table_header_text"])

    return f"""
        QWidget {{
            font-family: {family};
        }}
        QMainWindow, QDialog {{
            background-color: {color["app_bg"]};
        }}
        QToolTip {{
            background-color: #24303F;
            color: #F5F7FA;
            border: none;
            border-radius: {_px(radius["sm"])};
            padding: 6px 10px;
            font-size: {_px(font["control"])};
        }}
        QTabWidget::pane {{
            border: none;
            border-top: 1px solid {color["border"]};
            background: transparent;
        }}
        QTabBar::tab {{
            padding: {_px(space["tab_y"])} {_px(space["tab_x"])};
            background: {color["tab_bg"]};
            color: {color["text_muted"]};
            border: none;
            border-bottom: 2px solid transparent;
            font-size: {_px(font["control"])};
            font-weight: 600;
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {color["tab_selected"]};
            color: {color["primary"]};
            border-bottom: 2px solid {color["primary"]};
        }}
        QTabBar::tab:hover:!selected {{
            background: {color["tab_hover"]};
            color: {color["ink"]};
            border-top-left-radius: {_px(radius["sm"])};
            border-top-right-radius: {_px(radius["sm"])};
        }}
        QGroupBox {{
            font-weight: 600;
            font-size: {_px(font["control"])};
            color: {color["text"]};
            border: 1px solid {color["border"]};
            border-radius: {_px(radius["md"])};
            margin-top: 20px;
            padding: 14px 10px 10px 10px;
            background: {color["surface"]};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 6px;
            color: {section_title};
            font-size: {_px(font["control"])};
            font-weight: 600;
        }}
        QPushButton {{
            padding: {_px(space["button_y"])} {_px(space["button_x"])};
            border: 1px solid {color["button_border"]};
            border-radius: {_px(radius["sm"])};
            background-color: {color["surface"]};
            color: {color["text"]};
            font-size: {_px(font["control"])};
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {color["list_hover"]};
            border-color: {color["button_border_hover"]};
            color: {color["primary_dark"]};
        }}
        QPushButton:pressed {{
            background-color: {color["surface_pressed"]};
        }}
        QPushButton:disabled {{
            color: {color["text_disabled"]};
            background-color: {color["surface_disabled"]};
            border-color: {color["button_border_disabled"]};
        }}
        QLineEdit, QComboBox {{
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            padding: {_px(space["input_y"])} {_px(space["input_x"])};
            background: {color["surface"]};
            color: {color["ink"]};
            selection-background-color: {color["primary_weak"]};
            selection-color: {color["ink"]};
            font-size: {_px(font["control"])};
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {color["primary"]};
        }}
        QLineEdit:disabled, QComboBox:disabled {{
            background: {color["surface_disabled"]};
            color: {color["text_disabled"]};
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            background: {color["surface"]};
            selection-background-color: {color["primary_weak"]};
            selection-color: {color["primary_dark"]};
            outline: none;
            padding: 4px;
        }}
        QTextEdit, QPlainTextEdit {{
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            background: {color["surface"]};
            selection-background-color: {color["primary_weak"]};
            selection-color: {color["ink"]};
        }}
        QListWidget {{
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            background: {color["surface"]};
            outline: none;
        }}
        QListWidget::item {{
            padding: {_px(space["list_item_y"])} {_px(space["list_item_x"])};
            border-bottom: 1px solid {color["list_divider"]};
            color: {color["text"]};
        }}
        QListWidget::item:selected {{
            background: {color["primary_weak"]};
            color: {color["primary_dark"]};
            border-radius: {_px(radius["xs"])};
        }}
        QListWidget::item:hover:!selected {{
            background: {color["list_hover"]};
        }}
        QTableWidget, QTableView {{
            border: 1px solid {color["table_border"]};
            border-radius: {_px(radius["sm"])};
            gridline-color: {color["table_grid"]};
            background: {color["surface"]};
            alternate-background-color: {color["table_alt"]};
            selection-background-color: {color["primary_weak"]};
            selection-color: {color["ink"]};
            font-size: {_px(font["table"])};
        }}
        QTableWidget::item, QTableView::item {{
            padding: 3px 6px;
        }}
        QHeaderView::section {{
            background-color: {color["table_header"]};
            color: {color["table_header_text"]};
            font-weight: 600;
            font-size: {_px(font["table"])};
            border: none;
            border-right: 1px solid {color["table_header_border"]};
            border-bottom: 2px solid {color["table_header_border"]};
            padding: {_px(space["header_y"])} {_px(space["header_x"])};
        }}
        QHeaderView::section:vertical {{
            color: {color["text_muted"]};
            font-weight: 400;
            border-bottom: 1px solid {color["table_grid"]};
        }}
        QScrollBar:vertical {{
            width: 10px;
            background: transparent;
            margin: 2px;
        }}
        QScrollBar:horizontal {{
            height: 10px;
            background: transparent;
            margin: 2px;
        }}
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
            background: {color["scroll_handle"]};
            border-radius: {_px(radius["scroll"])};
            min-height: 24px;
            min-width: 24px;
        }}
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
            background: #A9B5C6;
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{
            height: 0px;
            width: 0px;
        }}
        QScrollBar::add-page, QScrollBar::sub-page {{
            background: transparent;
        }}
        QMenu {{
            background: {color["surface"]};
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            padding: 4px;
        }}
        QMenu::item {{
            padding: 6px 24px 6px 12px;
            border-radius: {_px(radius["xs"])};
            color: {color["text"]};
        }}
        QMenu::item:selected {{
            background: {color["list_hover"]};
            color: {color["primary_dark"]};
        }}
        QMenu::separator {{
            height: 1px;
            background: {color["list_divider"]};
            margin: 4px 6px;
        }}
        QCheckBox, QRadioButton {{
            spacing: 6px;
            color: {color["text"]};
        }}
        QProgressBar {{
            border: 1px solid {color["border_control"]};
            border-radius: {_px(radius["sm"])};
            background: {color["surface_soft"]};
            text-align: center;
            color: {color["text"]};
        }}
        QProgressBar::chunk {{
            background: {color["primary"]};
            border-radius: {_px(radius["xs"])};
        }}
        QStatusBar {{
            color: {color["text_muted"]};
            font-size: {_px(font["control"])};
            background: {color["surface"]};
            border-top: 1px solid {color["border_soft"]};
        }}
        QSplitter::handle {{
            background: {color["splitter"]};
            width: 2px;
        }}
        QSplitter::handle:hover {{
            background: {color["primary_weak"]};
        }}
    """
