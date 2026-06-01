"""Renderers and rules for leader-facing support classification sheets."""

from core.parser import get_lookup_value, get_part
from core.project_aggregation import ProjectAnalysisResult

from .headers import LEADER_DETAIL_HEADERS, LEADER_GROUP_DETAIL_HEADERS, LEADER_STAT_HEADERS
from .models import LeaderHitDetail, LeaderStatRow
from .styles import (
    NUMFMT,
    add_bar_chart,
    apply_report_table,
    apply_status_fill,
    set_print_layout,
    _set_widths,
    _setup_sheet,
    _styles,
    _write_headers,
)


def _leader_stat_template() -> list[LeaderStatRow]:
    return [
        LeaderStatRow("U-Bolt / Band", 'U-Bolt & Band <= 6" 熱浸鍍鋅', "組", "uband_hdg_le6", '明細含 U-Bolt/Band，管徑 <= 6"，材質非 SUS304'),
        LeaderStatRow("U-Bolt / Band", 'U-Bolt & Band >= 8" 熱浸鍍鋅', "組", "uband_hdg_ge8", '明細含 U-Bolt/Band，管徑 >= 8"，材質非 SUS304'),
        LeaderStatRow("U-Bolt / Band", 'U-Bolt & Band <= 6" (SUS304)', "組", "uband_304_le6", '明細含 U-Bolt/Band，管徑 <= 6"，材質含 304'),
        LeaderStatRow("U-Bolt / Band", 'U-Bolt & Band >= 8" (SUS304)', "組", "uband_304_ge8", '明細含 U-Bolt/Band，管徑 >= 8"，材質含 304'),
        LeaderStatRow("Pipe Shoe", 'PIPE SHOE <= 4" 熱浸鍍鋅', "組", "shoe_hdg_le4", 'Type 52/53/54/55/66/67/80/85，管徑 <= 4"，整組不含 SUS304'),
        LeaderStatRow("Pipe Shoe", 'PIPE SHOE 5"~10" 熱浸鍍鋅', "組", "shoe_hdg_5_10", 'Type 52/53/54/55/66/67/80/85，管徑 5"~10"，整組不含 SUS304'),
        LeaderStatRow("Pipe Shoe", 'PIPE SHOE 12"~24" 熱浸鍍鋅', "組", "shoe_hdg_12_24", 'Type 52/53/54/55/66/67/80/85，管徑 12"~24"，整組不含 SUS304'),
        LeaderStatRow("Pipe Shoe", 'PIPE SHOE >= 26" 熱浸鍍鋅', "組", "shoe_hdg_ge26", 'Type 52/53/54/55/66/67/80/85，管徑 >= 26"，整組不含 SUS304'),
        LeaderStatRow("Cold Support", "保冷支撐座（長春帶料）", "組", "cold_support", "Type 代碼尾碼為 C 的保冷支撐"),
        LeaderStatRow("Pipe Shoe SUS304", 'PIPE SHOE <= 4" (SUS304)', "組", "shoe_304_le4", 'Type 52/53/54/55/66/67/80/85，管徑 <= 4"，整組任一明細材質含 304'),
        LeaderStatRow("Pipe Shoe SUS304", 'PIPE SHOE 5"~10" (SUS304)', "組", "shoe_304_5_10", 'Type 52/53/54/55/66/67/80/85，管徑 5"~10"，整組任一明細材質含 304'),
        LeaderStatRow("Pipe Shoe SUS304", 'PIPE SHOE 12"~24" (SUS304)', "組", "shoe_304_12_24", 'Type 52/53/54/55/66/67/80/85，管徑 12"~24"，整組任一明細材質含 304'),
        LeaderStatRow("CS Support", "CS 管支撐製裝 <= 15 kg/組", "組", "cs_support_le15", "整組不含 SUS304，單組總重 <= 15 kg，按支撐組數統計"),
        LeaderStatRow("CS Support", "CS 管支撐製裝 > 15 kg/組", "KG", "cs_support_gt15", "整組不含 SUS304，單組總重 > 15 kg，按總重量統計"),
        LeaderStatRow("SUS304 Support", "SUS304 管支撐製裝 <= 15 kg/組", "組", "ss_support_le15", "整組含 SUS304，單組總重 <= 15 kg，按支撐組數統計"),
        LeaderStatRow("SUS304 Support", "SUS304 管支撐製裝 > 15 kg/組", "KG", "ss_support_gt15", "整組含 SUS304，單組總重 > 15 kg，按總重量統計"),
    ]


def _parse_designation_type(designation: str) -> str:
    return (get_part(designation, 1) or "").strip()


def _parse_designation_pipe_size(designation: str) -> float | None:
    token = (get_part(designation, 2) or "").strip()
    if not token:
        return None
    token = token.split("(")[0].replace('"', "").strip()
    if token.upper().endswith("B"):
        token = token[:-1]
    try:
        return float(get_lookup_value(token))
    except (TypeError, ValueError):
        return None


def _is_304_material(material: str) -> bool:
    return "304" in str(material or "").upper().replace(" ", "")


def _is_ubolt_or_band_entry(name: str) -> bool:
    upper = str(name or "").upper().replace(" ", "")
    return "U-BOLT" in upper or "UBOLT" in upper or "U-BAND" in upper or "UBAND" in upper


def _support_has_304_material(row_result) -> bool:
    return any(_is_304_material(entry.material) for entry in row_result.scaled_result.entries)


def _is_cold_support_type(type_id: str) -> bool:
    return type_id.endswith("C") and type_id[:-1].isdigit()


def _leader_size_bucket(size: float | None, buckets: tuple[tuple[str, float, float], ...]) -> str | None:
    if size is None:
        return None
    for key, lower, upper in buckets:
        if lower <= size <= upper:
            return key
    return None


def _leader_procurement_stats(
    project: ProjectAnalysisResult,
) -> tuple[dict[str, float], dict[str, list[str]], list[LeaderHitDetail]]:
    template = _leader_stat_template()
    template_by_key = {row.key: row for row in template}
    stats = {row.key: 0.0 for row in template}
    sources = {row.key: [] for row in template}
    details: list[LeaderHitDetail] = []
    pipe_shoe_types = {"52", "53", "54", "55", "66", "67", "80", "85"}

    def material_label(is_304: bool) -> str:
        return "SUS304" if is_304 else "HDG/CS"

    def pipe_size_label(size: float | None) -> str:
        return "" if size is None else f'{size:g}"'

    def add_detail(
        *,
        status: str,
        key: str,
        designation: str,
        project_qty: int,
        pipe_size: float | None,
        amount: float,
        unit: str,
        matched_detail: str,
        material_basis: str,
        note: str = "",
    ) -> None:
        stat_row = template_by_key.get(key)
        if stat_row is None:
            return
        details.append(
            LeaderHitDetail(
                stat_key=stat_row.key,
                status=status,
                category=stat_row.item,
                label=stat_row.label,
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                amount=amount,
                unit=unit,
                matched_detail=matched_detail,
                material_basis=material_basis,
                criteria=stat_row.criteria,
                note=note,
            )
        )

    def add_stat(key: str, amount: float, source: str, **detail_kwargs) -> None:
        stats[key] += amount
        if source and source not in sources[key]:
            sources[key].append(source)
        add_detail(status="命中", key=key, amount=amount, **detail_kwargs)

    def add_issue(
        *,
        key: str,
        designation: str,
        project_qty: int,
        pipe_size: float | None,
        matched_detail: str,
        material_basis: str,
        note: str,
    ) -> None:
        add_detail(
            status="需確認",
            key=key,
            designation=designation,
            project_qty=project_qty,
            pipe_size=pipe_size,
            amount=0.0,
            unit="",
            matched_detail=matched_detail,
            material_basis=material_basis,
            note=note,
        )

    def add_unmatched(
        *,
        designation: str,
        project_qty: int,
        pipe_size: float | None,
        row_result,
    ) -> None:
        has_304 = _support_has_304_material(row_result)
        entry_names = "、".join(entry.name for entry in row_result.scaled_result.entries[:5])
        if len(row_result.scaled_result.entries) > 5:
            entry_names += "..."
        details.append(
            LeaderHitDetail(
                stat_key="unmatched",
                status="未納入",
                category="未納入支撐分類統計",
                label="未命中摘要規則",
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                amount=0.0,
                unit="",
                matched_detail=entry_names or "無材料明細",
                material_basis="整組含 SUS304" if has_304 else "整組不含 SUS304",
                criteria="目前摘要統計 U-Bolt/Band、Pipe Shoe、Cold Support、CS/SUS304 管支撐製裝",
                note=(
                    "整組含 SUS304，但未符合目前摘要規則，請確認是否需要新增採購/製裝分類。"
                    if has_304
                    else "未符合目前支撐分類統計規則，請確認是否需要新增採購/製裝分類。"
                ),
            )
        )

    for row_result in project.rows:
        designation = row_result.input_row.designation
        project_qty = row_result.input_row.quantity
        type_id = _parse_designation_type(designation)
        pipe_size = _parse_designation_pipe_size(designation)
        detail_count_before = len(details)

        if row_result.single_result.error:
            add_issue(
                key="cs_support_le15",
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                matched_detail="分析失敗",
                material_basis="",
                note=row_result.single_result.error,
            )
            continue

        for entry in row_result.scaled_result.entries:
            if not _is_ubolt_or_band_entry(entry.name):
                continue
            entry_is_304 = _is_304_material(entry.material)
            material_key = "304" if entry_is_304 else "hdg"
            bucket = _leader_size_bucket(pipe_size, (
                ("le6", 0.0, 6.0),
                ("ge8", 8.0, 999.0),
            ))
            if bucket:
                key = f"uband_{material_key}_{bucket}"
                add_stat(
                    key,
                    entry.quantity,
                    f"{designation} ×{project_qty}: {entry.name} {entry.quantity:g}{entry.unit}",
                    designation=designation,
                    project_qty=project_qty,
                    pipe_size=pipe_size,
                    unit=entry.unit,
                    matched_detail=(
                        f"項次{entry.item_no} {entry.name} {entry.display_spec}"
                        f" ×{entry.quantity:g}"
                    ),
                    material_basis=f"{entry.material} -> {material_label(entry_is_304)}",
                )
            else:
                add_issue(
                    key=f"uband_{material_key}_le6",
                    designation=designation,
                    project_qty=project_qty,
                    pipe_size=pipe_size,
                    matched_detail=f"項次{entry.item_no} {entry.name} {entry.display_spec}",
                    material_basis=f"{entry.material} -> {material_label(entry_is_304)}",
                    note="U-Bolt/Band 命中，但管徑無法落入 <=6 或 >=8 統計區間。",
                )

        if type_id in pipe_shoe_types:
            support_is_304 = _support_has_304_material(row_result)
            material_key = "304" if support_is_304 else "hdg"
            bucket = _leader_size_bucket(pipe_size, (
                ("le4", 0.0, 4.0),
                ("5_10", 5.0, 10.0),
                ("12_24", 12.0, 24.0),
                ("ge26", 26.0, 999.0),
            ))
            if bucket and f"shoe_{material_key}_{bucket}" in stats:
                key = f"shoe_{material_key}_{bucket}"
                add_stat(
                    key,
                    project_qty,
                    f"{designation}: {project_qty}組",
                    designation=designation,
                    project_qty=project_qty,
                    pipe_size=pipe_size,
                    unit="組",
                    matched_detail=f"Type {type_id} Pipe Shoe，{pipe_size_label(pipe_size)}",
                    material_basis=f"整組材質 -> {material_label(support_is_304)}",
                )
            elif bucket:
                add_issue(
                    key="shoe_hdg_ge26",
                    designation=designation,
                    project_qty=project_qty,
                    pipe_size=pipe_size,
                    matched_detail=f"Type {type_id} Pipe Shoe，{pipe_size_label(pipe_size)}",
                    material_basis=f"整組材質 -> {material_label(support_is_304)}",
                    note=f"Pipe Shoe 命中 {bucket} 區間，但摘要表尚無對應統計列。",
                )
            else:
                add_issue(
                    key="shoe_hdg_le4",
                    designation=designation,
                    project_qty=project_qty,
                    pipe_size=pipe_size,
                    matched_detail=f"Type {type_id} Pipe Shoe",
                    material_basis=f"整組材質 -> {material_label(support_is_304)}",
                    note="Pipe Shoe Type 命中，但管徑無法落入統計區間。",
                )

        if _is_cold_support_type(type_id):
            add_stat(
                "cold_support",
                project_qty,
                f"{designation}: {project_qty}組",
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                unit="組",
                matched_detail=f"Type {type_id} 保冷支撐",
                material_basis="Type 代碼尾碼 C",
            )

        support_is_304 = _support_has_304_material(row_result)
        material_prefix = "ss" if support_is_304 else "cs"
        material_basis = "整組含 SUS304" if support_is_304 else "整組不含 SUS304"
        single_weight = row_result.single_result.total_weight
        scaled_weight = row_result.scaled_result.total_weight
        if single_weight <= 15:
            add_stat(
                f"{material_prefix}_support_le15",
                project_qty,
                f"{designation}: {project_qty}組，單組 {single_weight:.2f}kg",
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                unit="組",
                matched_detail=f"單組總重 {single_weight:.2f}kg <= 15kg",
                material_basis=material_basis,
            )
        else:
            add_stat(
                f"{material_prefix}_support_gt15",
                scaled_weight,
                f"{designation}: {scaled_weight:.2f}kg，單組 {single_weight:.2f}kg",
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                unit="KG",
                matched_detail=f"單組總重 {single_weight:.2f}kg > 15kg",
                material_basis=material_basis,
            )

        if len(details) == detail_count_before:
            add_unmatched(
                designation=designation,
                project_qty=project_qty,
                pipe_size=pipe_size,
                row_result=row_result,
            )

    return stats, sources, details


def _write_leader_procurement_sheet(ws, project: ProjectAnalysisResult):
    from openpyxl.chart import Reference
    from openpyxl.utils import get_column_letter

    styles = _styles()
    rows = _leader_stat_template()
    stats, _, details = _leader_procurement_stats(project)

    details_by_key: dict[str, list[LeaderHitDetail]] = {stat_row.key: [] for stat_row in rows}
    for detail in details:
        if detail.stat_key in details_by_key:
            details_by_key[detail.stat_key].append(detail)

    def stat_value(stat_row: LeaderStatRow):
        value = stats.get(stat_row.key, 0.0)
        return int(value) if stat_row.unit == "組" else round(value, 2)

    def write_detail_header(row: int) -> None:
        for col, header in enumerate(LEADER_GROUP_DETAIL_HEADERS, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.fill = styles["subheader_fill"]
            cell.font = styles["bold_font"]
            cell.alignment = styles["center"]
            cell.border = styles["border"]

    def write_detail_row(row: int, detail: LeaderHitDetail) -> None:
        values = [
            detail.status,
            detail.designation,
            detail.project_qty,
            "" if detail.pipe_size is None else detail.pipe_size,
            round(detail.amount, 3) if detail.unit == "KG" else int(detail.amount),
            detail.unit,
            detail.matched_detail,
            detail.material_basis,
            detail.note,
        ]
        for col, value in enumerate(values, 1):
            cell = ws.cell(row=row, column=col, value=value)
            cell.border = styles["border"]
            cell.alignment = styles["wrap"]
            if col in (3, 4, 5):
                cell.alignment = styles["right"]
            if col == 1:
                apply_status_fill(cell, detail.status)
                cell.alignment = styles["center"]
        ws.cell(row=row, column=4).number_format = NUMFMT["PIPE_IN"]
        ws.cell(row=row, column=5).number_format = NUMFMT["WEIGHT_KG3"] if detail.unit == "KG" else NUMFMT["QTY_INT"]

    _setup_sheet(ws, "支撐分類統計", "I1")
    ws.cell(
        row=2,
        column=1,
        value=(
            "業主/長官摘要：僅列本批有數量或需確認的支撐分類統計；"
            "每個統計項目下方列出命中型號與判定依據，完整查核請見「支撐統計明細」。"
        ),
    )
    ws.cell(row=2, column=1).font = styles["section_font"]
    ws.merge_cells("A2:I2")

    active_rows = [
        stat_row for stat_row in rows
        if stat_value(stat_row) != 0 or details_by_key.get(stat_row.key)
    ]

    row = 4
    if not active_rows:
        ws.cell(row=row, column=1, value="本批無需列示之支撐分類統計項目")
        ws.cell(row=row, column=1).font = styles["bold_font"]
        ws.cell(row=row, column=1).fill = styles["section_fill"]
        ws.cell(row=row, column=1).border = styles["border"]
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=9)
        row += 1

    for stat_row in active_rows:
        stat_details = details_by_key.get(stat_row.key, [])
        summary_values = [
            stat_row.item,
            stat_row.label,
            stat_row.criteria,
            stat_row.unit,
            stat_value(stat_row),
            len(stat_details),
        ]
        for col, header in enumerate(LEADER_STAT_HEADERS, 1):
            cell = ws.cell(row=row, column=col, value=header)
            cell.fill = styles["header_fill"]
            cell.font = styles["header_font"]
            cell.alignment = styles["center"]
            cell.border = styles["border"]
        ws.merge_cells(start_row=row, start_column=7, end_row=row, end_column=9)
        note_cell = ws.cell(row=row, column=7, value="命中型號依據")
        note_cell.fill = styles["header_fill"]
        note_cell.font = styles["header_font"]
        note_cell.alignment = styles["center"]
        note_cell.border = styles["border"]

        row += 1
        for col in range(1, 10):
            cell = ws.cell(row=row, column=col)
            cell.fill = styles["section_fill"]
            cell.font = styles["bold_font"]
            cell.border = styles["border"]
            cell.alignment = styles["wrap"]
        for col, value in enumerate(summary_values, 1):
            ws.cell(row=row, column=col, value=value)
        ws.merge_cells(start_row=row, start_column=7, end_row=row, end_column=9)
        ws.cell(row=row, column=7, value=f"{len(stat_details)} 筆命中/確認")
        ws.cell(row=row, column=4).alignment = styles["center"]
        ws.cell(row=row, column=5).alignment = styles["right"]
        ws.cell(row=row, column=6).alignment = styles["right"]
        ws.cell(row=row, column=5).number_format = NUMFMT["WEIGHT_KG"] if stat_row.unit == "KG" else NUMFMT["QTY_INT"]

        row += 1
        write_detail_header(row)
        row += 1
        for detail in stat_details:
            write_detail_row(row, detail)
            row += 1
        row += 1

    last_row = max(row - 1, 4)
    if active_rows:
        chart_row = 4
        label_col = 13
        value_col = 14
        ws.cell(row=chart_row, column=label_col, value="統計項目")
        ws.cell(row=chart_row, column=value_col, value="數量")
        ranked = sorted(active_rows, key=lambda stat_row: float(stat_value(stat_row) or 0), reverse=True)[:8]
        for offset, stat_row in enumerate(ranked, start=1):
            ws.cell(row=chart_row + offset, column=label_col, value=stat_row.label)
            ws.cell(row=chart_row + offset, column=value_col, value=stat_value(stat_row))
        add_bar_chart(
            ws,
            Reference(ws, min_col=label_col, min_row=chart_row + 1, max_row=chart_row + len(ranked)),
            Reference(ws, min_col=value_col, min_row=chart_row, max_row=chart_row + len(ranked)),
            "K4",
            "accent",
            "支撐分類 Top",
            horizontal=True,
        )
        for col in (label_col, value_col):
            ws.column_dimensions[get_column_letter(col)].hidden = True
    ws.freeze_panes = "A4"
    _set_widths(ws, [12, 24, 8, 10, 12, 8, 38, 24, 42])
    set_print_layout(ws, title_rows=None, area=f"A1:I{last_row}", footer_title="支撐分類統計")


def _write_leader_detail_sheet(ws, project: ProjectAnalysisResult):
    styles = _styles()
    _, _, details = _leader_procurement_stats(project)

    _setup_sheet(ws, "支撐統計明細（製表者查核）", "L1")
    ws.cell(
        row=2,
        column=1,
        value=(
            "本表逐筆列出支撐分類統計的命中、需確認與未納入來源；"
            "圖例：命中=綠、需確認=紅、未納入=橘。"
        ),
    )
    ws.cell(row=2, column=1).font = styles["section_font"]
    ws.merge_cells("A2:L2")

    row = 4
    if not details:
        ws.cell(row=row, column=1, value="無命中資料")
        ws.cell(row=row, column=1).border = styles["border"]
        row += 1
    else:
        for detail in details:
            values = [
                detail.status,
                detail.category,
                detail.label,
                detail.designation,
                detail.project_qty,
                "" if detail.pipe_size is None else detail.pipe_size,
                round(detail.amount, 3) if detail.unit == "KG" else int(detail.amount),
                detail.unit,
                detail.matched_detail,
                detail.material_basis,
                detail.criteria,
                detail.note,
            ]
            for col, value in enumerate(values, 1):
                cell = ws.cell(row=row, column=col, value=value)
                cell.border = styles["border"]
                cell.alignment = styles["wrap"]
                if col in (5, 6, 7):
                    cell.alignment = styles["right"]
                if col == 1:
                    apply_status_fill(cell, detail.status)
                    cell.alignment = styles["center"]
            ws.cell(row=row, column=6).number_format = NUMFMT["PIPE_IN"]
            ws.cell(row=row, column=7).number_format = NUMFMT["WEIGHT_KG3"] if detail.unit == "KG" else NUMFMT["QTY_INT"]
            row += 1

    last_row = max(row - 1, 3)
    apply_report_table(
        ws,
        3,
        LEADER_DETAIL_HEADERS,
        4,
        last_row,
        col_formats={
            5: NUMFMT["QTY_INT"],
            6: NUMFMT["PIPE_IN"],
            7: NUMFMT["WEIGHT_KG3"],
        },
        widths=[10, 16, 34, 22, 8, 10, 12, 8, 36, 22, 52, 42],
    )
    for data_row in range(4, last_row + 1):
        apply_status_fill(ws.cell(row=data_row, column=1), ws.cell(row=data_row, column=1).value)
    set_print_layout(ws, title_rows="3:3", area=f"A1:L{last_row}", footer_title="支撐統計明細")
