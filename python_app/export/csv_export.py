"""
CSV 匯出模組
"""
import csv
from typing import List
from core.models import AnalysisResult

HEADERS = [
    "材料描述欄", "項次", "品名", "尺寸/規格", "長度", "寬度",
    "材質", "數量", "每米重", "單重", "總重小計", "單位",
    "係數", "長度小計", "數量小計", "總重合計", "屬性", "備註"
]


def export_to_csv(results: List[AnalysisResult], filepath: str):
    """匯出分析結果至 CSV"""
    with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(HEADERS)

        for result in results:
            if result.error:
                writer.writerow([result.fullstring, "Error", result.error])
                continue

            for entry in result.entries:
                writer.writerow([
                    result.fullstring if entry.item_no == 1 else "",
                    entry.item_no, entry.name, entry.spec,
                    entry.length, entry.width if entry.width else "",
                    entry.material, entry.quantity,
                    entry.weight_per_unit if entry.weight_per_unit else "",
                    entry.unit_weight, entry.total_weight, entry.unit,
                    entry.factor,
                    entry.length_subtotal if entry.length_subtotal else "",
                    entry.qty_subtotal if entry.qty_subtotal else "",
                    entry.weight_output, entry.category,
                    entry.remark if entry.remark else "",
                ])
