from core.project_aggregation import ProjectInputRow, analyze_project_rows
from export.project_export_preview import (
    build_project_export_preview,
    format_project_export_preview,
)


def test_project_export_preview_summarizes_workbook_before_save():
    project = analyze_project_rows(
        [
            ProjectInputRow("51-1.1/2B", 10, drawing_line_number="DL-001", serial="S-001"),
            ProjectInputRow("57-1/2B-A", 2, drawing_line_number="DL-002", serial="S-002"),
        ]
    )

    preview = build_project_export_preview(
        project,
        export_label="Excel (.xlsx)",
        include_workbook_sheets=True,
    )
    message = format_project_export_preview(preview)

    assert preview.row_count == 2
    assert preview.support_count == 12
    assert preview.type_count == 2
    assert preview.success_count == 2
    assert preview.error_count == 0
    assert preview.review_required_count >= 1
    assert "估算" in preview.confidence_summary
    assert preview.material_line_count > 0
    assert preview.total_weight > 0
    assert preview.sheet_names == (
        "長官-摘要",
        "專案摘要",
        "重量明細表",
        "單組重量明細",
        "計算標準與假設",
        "長官-支撐分類",
        "查核-支撐明細",
        "重量分析",
        "材料合計",
        "下料明細",
        "下料圖示",
    )
    assert "即將匯出：Excel (.xlsx)" in message
    assert "Type 2 種" in message
    assert "資料信心" in message
    assert "需複核" in message
    assert "Workbook 分頁" in message
    assert "材料合計" in message


def test_project_export_preview_flags_attention_for_errors():
    project = analyze_project_rows([ProjectInputRow("99-1B", 5)])

    preview = build_project_export_preview(
        project,
        export_label="CSV (.csv)",
        include_workbook_sheets=False,
    )
    message = format_project_export_preview(preview)

    assert preview.needs_attention
    assert preview.error_count == 1
    assert preview.review_required_count == 1
    assert preview.success_count == 0
    assert preview.sheet_names == ()
    assert "需複核 1" in message
    assert "錯誤 1" in message
