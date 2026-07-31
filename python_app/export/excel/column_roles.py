"""欄位用途分級（B1 地基模組）。

單一真值表：定義匯出 Excel 每個欄位「給誰看、主明細視圖是否預設顯示」。
本模組**只提供定義**，不改變任何既有 sheet 的輸出行為；B2/B3/B4 才依此調整呈現。

role 角色：
    "manager"  長官  —— 要結論（型號、品名、總數量、總重）
    "procure"  採購  —— 要採購／數量資訊
    "engineer" 工程  —— 要規格、材質、尺寸、切割等工程細節
    "trace"    稽核追溯 —— 內部追溯欄；保留在檔案，但主明細視圖預設隱藏

default_visible：該欄在「主明細視圖」是否預設顯示。
    追溯欄一律 False（資料留在檔案，只是收起），其餘預設 True。

依方案書 §0 鐵則：本檔屬呈現／設定層，**不碰計算真值**。
"""

from __future__ import annotations

# role: "manager" / "procure" / "engineer" / "trace"
# default_visible: 是否在主明細視圖預設顯示
COLUMN_ROLE: dict[str, dict] = {
    # —— manager 長官：結論欄 ——
    "型號":        {"role": "manager",  "default_visible": True},
    "品名":        {"role": "manager",  "default_visible": True},
    "數量":        {"role": "manager",  "default_visible": True},
    "總數量":      {"role": "manager",  "default_visible": True},
    "總重(kg)":    {"role": "manager",  "default_visible": True},
    "總重合計":    {"role": "manager",  "default_visible": True},
    "合約名稱":    {"role": "manager",  "default_visible": True},
    "合約總量":    {"role": "manager",  "default_visible": True},
    "本列計入":    {"role": "manager",  "default_visible": True},

    # —— procure 採購：採購量／需求量 ——
    "建議採購量":      {"role": "procure", "default_visible": True},
    "需求總長(mm)":    {"role": "procure", "default_visible": True},
    "需求件數/數量":   {"role": "procure", "default_visible": True},
    "原料長度(mm)":    {"role": "procure", "default_visible": True},
    "來源編碼":        {"role": "procure", "default_visible": True},
    "計價單位":        {"role": "procure", "default_visible": True},
    "專案組數":        {"role": "procure", "default_visible": True},

    # —— engineer 工程：規格／材質／尺寸／切割等 ——
    "規格":        {"role": "engineer", "default_visible": True},
    "尺寸/規格":   {"role": "engineer", "default_visible": True},
    "材質":        {"role": "engineer", "default_visible": True},
    "密度(g/cm³)": {"role": "engineer", "default_visible": True},
    "密度狀態":    {"role": "engineer", "default_visible": True},
    "加工狀態":    {"role": "engineer", "default_visible": True},
    "材料描述欄":  {"role": "engineer", "default_visible": True},
    "長度":        {"role": "engineer", "default_visible": True},
    "寬度":        {"role": "engineer", "default_visible": True},
    "長度(mm)":    {"role": "engineer", "default_visible": True},
    "寬度(mm)":    {"role": "engineer", "default_visible": True},
    "管徑(吋)":    {"role": "engineer", "default_visible": True},
    "型號類別":    {"role": "engineer", "default_visible": True},
    "單位":        {"role": "engineer", "default_visible": True},
    "計入單位":    {"role": "engineer", "default_visible": True},
    "計入數量":    {"role": "engineer", "default_visible": True},
    "單件數量":    {"role": "engineer", "default_visible": True},
    "組數":        {"role": "engineer", "default_visible": True},
    "每米重":      {"role": "engineer", "default_visible": True},
    "單重":        {"role": "engineer", "default_visible": True},
    "單組重(kg)":  {"role": "engineer", "default_visible": True},
    "單組重量(kg)": {"role": "engineer", "default_visible": True},
    "單件重(kg)":  {"role": "engineer", "default_visible": True},
    "單組小計(kg)": {"role": "engineer", "default_visible": True},
    "總重小計":    {"role": "engineer", "default_visible": True},
    "係數":        {"role": "engineer", "default_visible": True},
    "長度小計":    {"role": "engineer", "default_visible": True},
    "數量小計":    {"role": "engineer", "default_visible": True},
    "屬性":        {"role": "engineer", "default_visible": True},
    "狀態":        {"role": "engineer", "default_visible": True},
    "類別":        {"role": "engineer", "default_visible": True},
    "統計項目":    {"role": "engineer", "default_visible": True},
    "統計條件":    {"role": "engineer", "default_visible": True},
    "命中/確認筆數": {"role": "engineer", "default_visible": True},
    "命中明細":    {"role": "engineer", "default_visible": True},
    "材質判定":    {"role": "engineer", "default_visible": True},
    "備註":        {"role": "engineer", "default_visible": True},
    "支撐單組總重(kg)": {"role": "engineer", "default_visible": True},
    "分類門檻 / 原因": {"role": "engineer", "default_visible": True},
    "本列請款計算": {"role": "engineer", "default_visible": True},
    "命中材料 / 零件": {"role": "engineer", "default_visible": True},
    "狀態 / 備註": {"role": "engineer", "default_visible": True},
    # 切割表（工程／現場用）
    "材料":        {"role": "engineer", "default_visible": True},
    "原料 #":      {"role": "engineer", "default_visible": True},
    "切割段":      {"role": "engineer", "default_visible": True},
    "需求長(mm)":  {"role": "engineer", "default_visible": True},
    "含損耗(mm)":  {"role": "engineer", "default_visible": True},
    "累計(mm)":    {"role": "engineer", "default_visible": True},
    "餘料(mm)":    {"role": "engineer", "default_visible": True},
    "使用率":      {"role": "engineer", "default_visible": True},
    "用於":        {"role": "engineer", "default_visible": True},

    # —— trace 稽核追溯：保留在檔案，主視圖預設隱藏 ——
    "項次":        {"role": "trace", "default_visible": False},
    "重量計算式":  {"role": "trace", "default_visible": False},
    "計算說明":    {"role": "trace", "default_visible": False},
    "物件類別":    {"role": "trace", "default_visible": False},
    "製造方式":    {"role": "trace", "default_visible": False},
    "列型":        {"role": "trace", "default_visible": False},
    "來源圖號":    {"role": "trace", "default_visible": False},
    "流水號":      {"role": "trace", "default_visible": False},
    "輸入數量":    {"role": "trace", "default_visible": False},
    "輸入單位":    {"role": "trace", "default_visible": False},
    "零件ID":      {"role": "trace", "default_visible": False},
    "庫存ID":      {"role": "trace", "default_visible": False},
    "來源圖面":    {"role": "trace", "default_visible": False},
}

# 未在 COLUMN_ROLE 明確定義的欄位，預設視為此角色且可見（§B1 停損條件）。
DEFAULT_ROLE = "engineer"
DEFAULT_VISIBLE = True

VALID_ROLES = ("manager", "procure", "engineer", "trace")


def role_of(header: str) -> str:
    """回傳欄位角色；未定義者回 DEFAULT_ROLE。"""
    return COLUMN_ROLE.get(header, {}).get("role", DEFAULT_ROLE)


def is_visible(header: str) -> bool:
    """回傳欄位在主明細視圖是否預設顯示；未定義者預設可見。"""
    return COLUMN_ROLE.get(header, {}).get("default_visible", DEFAULT_VISIBLE)


def visible_columns(headers: list[str]) -> list[str]:
    """從一組 headers 取出「主明細視圖預設顯示」的欄（保持原順序）。"""
    return [h for h in headers if is_visible(h)]


def trace_columns(headers: list[str]) -> list[str]:
    """從一組 headers 取出「稽核追溯」欄（B2 會把這些預設隱藏）。"""
    return [h for h in headers if role_of(h) == "trace"]


def columns_by_role(headers: list[str], role: str) -> list[str]:
    """從一組 headers 取出指定角色的欄（保持原順序）。"""
    return [h for h in headers if role_of(h) == role]


def apply_default_visibility(ws, headers: list[str], *, outline_level: int = 1) -> None:
    """依欄位用途設定 Excel 預設顯示狀態；只隱藏欄，不刪欄或改值。"""
    from openpyxl.utils import get_column_letter

    for index, header in enumerate(headers, 1):
        if is_visible(header):
            continue
        dimension = ws.column_dimensions[get_column_letter(index)]
        dimension.hidden = True
        dimension.outline_level = outline_level

    ws.sheet_view.showOutlineSymbols = True
    ws.sheet_properties.outlinePr.summaryRight = False
