"""Renderer for the material summary/procurement sheet."""

from core.material_summary import MaterialSummary

from .headers import SUMMARY_HEADERS
from .styles import (
    NUMFMT,
    add_color_scale,
    apply_report_table,
    set_print_layout,
    write_grand_total_band,
    _setup_sheet,
)


def _write_material_summary_sheet(ws, summary: MaterialSummary):
    _setup_sheet(
        ws,
        "材料合計與採購清單",
        "M1",
        subtitle=f"採購/製造清單    材料 {len(summary.lines)} 項    全案總重 {summary.total_weight:,.2f} kg",
        audience="採購 / 製造",
    )

    row = 4
    for ln in summary.lines:
        length_value = round(ln.total_length_mm, 1) if ln.aggregate_type == "linear" else ""
        qty_value = ln.piece_count if ln.aggregate_type == "linear" else ln.total_qty
        stock_length = round(ln.stock_length, 0) if ln.stock_length else ""
        sources = ", ".join(ln.source_fullstrings[:8])
        if len(ln.source_fullstrings) > 8:
            sources += f" ...+{len(ln.source_fullstrings) - 8}"
        values = [
            ln.name,
            ln.spec,
            ln.material,
            ln.category,
            ln.item_class,
            ln.manufacturing_type,
            length_value,
            qty_value,
            round(ln.total_weight, 2),
            stock_length,
            ln.purchase_qty,
            ln.purchase_unit,
            sources,
        ]
        for col, value in enumerate(values, 1):
            ws.cell(row=row, column=col, value=value)
        row += 1

    last_row = max(row - 1, 3)
    apply_report_table(
        ws,
        3,
        SUMMARY_HEADERS,
        4,
        last_row,
        col_formats={
            7: NUMFMT["LEN_MM1"],
            8: NUMFMT["QTY_INT"],
            9: NUMFMT["WEIGHT_KG"],
            10: NUMFMT["LEN_MM"],
            11: NUMFMT["QTY_INT"],
        },
        widths=[16, 22, 16, 10, 14, 14, 14, 12, 12, 12, 12, 8, 46],
    )
    if last_row >= 4:
        add_color_scale(ws, f"I4:I{last_row}", "weight")

    total_row = row
    write_grand_total_band(
        ws,
        total_row,
        len(SUMMARY_HEADERS),
        "合計總重",
        9,
        round(summary.total_weight, 2),
        fmt=NUMFMT["WEIGHT_KG"],
        label_col=8,
    )
    set_print_layout(ws, title_rows="3:3", area=f"A1:M{total_row}", footer_title="材料合計")
