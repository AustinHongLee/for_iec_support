"""UI design tokens and global QSS builder."""

from __future__ import annotations


TOKENS = {
    "color": {
        "app_bg": "#F5F6FA",
        "surface": "#FFFFFF",
        "surface_soft": "#F0F2F5",
        "surface_hover": "#E2E8F0",
        "surface_pressed": "#D0DAEA",
        "surface_disabled": "#EAEAEA",
        "tab_bg": "#E8ECF1",
        "tab_hover": "#DDE3EC",
        "tab_selected": "#FFFFFF",
        "ink": "#222",
        "text": "#333",
        "text_muted": "#555",
        "text_disabled": "#AAA",
        "primary": "#1565C0",
        "primary_dark": "#0D47A1",
        "primary_weak": "#BBDEFB",
        "border": "#C8CDD5",
        "border_control": "#C0C8D4",
        "border_soft": "#D0D5DC",
        "button_border": "#B8C0CC",
        "button_border_hover": "#8898B0",
        "button_border_disabled": "#D0D0D0",
        "list_divider": "#EEF0F3",
        "list_hover": "#E8F0F8",
        "table_border": "#C0C8D4",
        "table_grid": "#E4E8EE",
        "table_alt": "#F8FAFB",
        "table_header": "#EEF2F8",
        "table_header_text": "#2C3E60",
        "table_header_border": "#D2D8E2",
        "summary_bg": "#F8FBFE",
        "summary_border": "#D6E2EF",
        "metric_label": "#607080",
        "metric_weight": "#0D47A1",
        "metric_ok": "#1B5E20",
        "metric_muted": "#546E7A",
        "metric_support": "#263238",
        "scroll_handle": "#C0CBD8",
        "splitter": "#D0D5DC",
    },
    "font": {
        "control": 12,
        "table": 12,
        "metric_label": 11,
        "metric_value": 18,
        "metric_primary": 20,
    },
    "space": {
        "tab_y": 7,
        "tab_x": 18,
        "button_y": 5,
        "button_x": 12,
        "input_y": 4,
        "input_x": 8,
        "list_item_y": 3,
        "list_item_x": 6,
        "header_y": 5,
        "header_x": 8,
        "summary_y": 8,
        "summary_x": 12,
        "summary_gap": 16,
        "metric_gap": 6,
    },
    "radius": {
        "xs": 2,
        "sm": 4,
        "md": 6,
        "scroll": 5,
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

    return f"""
        QMainWindow, QDialog {{
            background-color: {color["app_bg"]};
        }}
        QTabWidget::pane {{
            border: 1px solid {color["border"]};
            background: {color["surface"]};
            border-radius: 0 {_px(radius["sm"])} {_px(radius["sm"])} {_px(radius["sm"])};
        }}
        QTabBar::tab {{
            padding: {_px(space["tab_y"])} {_px(space["tab_x"])};
            background: {color["tab_bg"]};
            color: {color["text_muted"]};
            border: 1px solid {color["border"]};
            border-bottom: none;
            border-radius: {_px(radius["sm"])} {_px(radius["sm"])} 0 0;
            font-size: {_px(font["control"])};
            margin-right: 2px;
        }}
        QTabBar::tab:selected {{
            background: {color["tab_selected"]};
            color: {color["primary"]};
            font-weight: bold;
            border-bottom: 2px solid {color["tab_selected"]};
        }}
        QTabBar::tab:hover:!selected {{
            background: {color["tab_hover"]};
        }}
        QGroupBox {{
            font-weight: bold;
            font-size: {_px(font["control"])};
            color: {color["text"]};
            border: 1px solid {color["border"]};
            border-radius: {_px(radius["md"])};
            margin-top: 18px;
            padding: 12px 8px 8px 8px;
            background: {color["surface"]};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: {color["primary"]};
            font-size: {_px(font["control"])};
        }}
        QPushButton {{
            padding: {_px(space["button_y"])} {_px(space["button_x"])};
            border: 1px solid {color["button_border"]};
            border-radius: {_px(radius["sm"])};
            background-color: {color["surface_soft"]};
            color: {color["text"]};
            font-size: {_px(font["control"])};
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: {color["surface_hover"]};
            border-color: {color["button_border_hover"]};
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
            font-size: {_px(font["control"])};
        }}
        QLineEdit:focus, QComboBox:focus {{
            border-color: {color["primary"]};
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
        }}
        QListWidget::item:selected {{
            background: {color["primary_weak"]};
            color: {color["primary_dark"]};
            border-radius: {_px(radius["xs"])};
        }}
        QListWidget::item:hover:!selected {{
            background: {color["list_hover"]};
        }}
        QTableWidget {{
            border: 1px solid {color["table_border"]};
            border-radius: {_px(radius["sm"])};
            gridline-color: {color["table_grid"]};
            background: {color["surface"]};
            alternate-background-color: {color["table_alt"]};
            selection-background-color: {color["primary_weak"]};
            font-size: {_px(font["table"])};
        }}
        QHeaderView::section {{
            background-color: {color["table_header"]};
            color: {color["table_header_text"]};
            font-weight: bold;
            font-size: {_px(font["table"])};
            border: none;
            border-right: 1px solid {color["table_header_border"]};
            border-bottom: 1px solid {color["primary_weak"]};
            padding: {_px(space["header_y"])} {_px(space["header_x"])};
        }}
        QScrollBar:vertical {{
            width: 10px;
            background: {color["surface_soft"]};
        }}
        QScrollBar::handle:vertical {{
            background: {color["scroll_handle"]};
            border-radius: {_px(radius["scroll"])};
            min-height: 20px;
        }}
        QStatusBar {{
            color: #666;
            font-size: {_px(font["control"])};
            background: {color["surface_soft"]};
            border-top: 1px solid {color["border_soft"]};
        }}
        QSplitter::handle {{
            background: {color["splitter"]};
            width: 2px;
        }}
    """
