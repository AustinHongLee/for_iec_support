"""
PDF 匯出模組 (使用 reportlab)
"""
from typing import List
from core.models import AnalysisResult


def export_to_pdf(results: List[AnalysisResult], filepath: str):
    """匯出分析結果至 PDF"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4),
                           leftMargin=10*mm, rightMargin=10*mm)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("IEC Support Weight Analysis", styles['Title']))
    elements.append(Spacer(1, 10*mm))

    headers = ["描述", "項次", "品名", "規格", "長度", "材質",
               "數量", "單重", "總重", "單位", "屬性"]

    for result in results:
        if result.error:
            elements.append(Paragraph(
                f"<b>{result.fullstring}</b>: <font color='red'>{result.error}</font>",
                styles['Normal']))
            elements.append(Spacer(1, 5*mm))
            continue

        data = [headers]
        for entry in result.entries:
            data.append([
                result.fullstring if entry.item_no == 1 else "",
                str(entry.item_no), entry.name, entry.spec,
                str(entry.length), entry.material,
                str(entry.quantity), f"{entry.unit_weight:.2f}",
                f"{entry.weight_output:.2f}", entry.unit, entry.category,
            ])

        table = Table(data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(0.95, 0.95, 0.95)]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 5*mm))

    doc.build(elements)
