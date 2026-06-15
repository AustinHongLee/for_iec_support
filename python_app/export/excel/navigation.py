"""Shared workbook navigation metadata for Excel report sheets."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkbookNavItem:
    sheet: str
    purpose: str
    print_note: str
    audience: str


def workbook_navigation(total_bars: int | None = None) -> list[WorkbookNavItem]:
    """Return the canonical sheet navigation order for project workbooks."""
    cutting_note = "依原料分頁查看" if total_bars is None else f"依 {total_bars:,} 根原料分頁查看"
    return [
        WorkbookNavItem("長官-摘要", "主管/業主快速看量；只放重點數字與查閱路徑。", "A4 直式，第一頁優先列印", "主管"),
        WorkbookNavItem("專案摘要", "工程內部總覽；專案用了哪些 Type、總體重量、是否有錯誤或需確認項。", "A4 直式", "工程"),
        WorkbookNavItem("重量明細表", "工程審查用明細；每列含 Type、單件數量、組數、總重與計算式。", "欄位多，建議橫式或用篩選", "工程"),
        WorkbookNavItem("計算標準與假設", "引用標準、資料狀態圖例、各 Type 計算可信度彙整。", "A4 直式", "工程"),
        WorkbookNavItem("長官-支撐分類", "採購/施工合約項目彙總，例如 Pipe Shoe、U-Bolt、CS 支撐。", "A4 直式摘要", "主管"),
        WorkbookNavItem("查核-支撐明細", "分類規則命中與需確認原因的逐筆追蹤。", "欄位多，建議橫式", "工程"),
        WorkbookNavItem("重量分析", "傳統重量分析明細，保留零件ID、庫存ID與備註。", "欄位多，建議橫式", "工程"),
        WorkbookNavItem("材料合計", "採購 BOM 聚合清單，以此頁總重與採購量為準。", "A4 直式或橫式皆可", "採購"),
        WorkbookNavItem("下料明細", "每根原料的切割段、餘料與使用率。", cutting_note, "製造"),
        WorkbookNavItem("下料圖示", "下料配置視覺化，用於初步規劃與溝通。", "通常不列印全頁", "製造"),
    ]
