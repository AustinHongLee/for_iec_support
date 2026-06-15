"""Project input import helpers that do not depend on the GUI layer."""

from __future__ import annotations

import re
from collections.abc import Callable

from .project_aggregation import ProjectInputRow

ProjectXlsxMapping = dict[str, int | None]
ProjectXlsxMappingConfirmer = Callable[
    [str, int, list[str], ProjectXlsxMapping],
    ProjectXlsxMapping,
]

PROJECT_ROW_ALIASES = {
    "drawing_line_number": (
        "Drawing line number", "drawing_line_number", "drawing line", "drawing", "line_group",
        "line group", "line no", "line number", "dwg", "dwg no", "圖名", "圖號",
    ),
    "serial": ("流水號.sort", "流水號", "serial", "serial_no", "seq", "sort", "序號", "編號"),
    "designation": ("型號", "designation", "support_designation", "support_no", "支撐編碼", "編碼", "支撐型號", "model"),
    "quantity": ("數量", "quantity", "qty", "count", "組數", "支數"),
    "unit": ("單位", "unit", "uom"),
    "enabled": ("enabled", "啟用"),
    "overrides": ("overrides_json", "overrides"),
    "description": ("description", "desc", "描述", "中文說明", "說明", "品名"),
    "item_code": ("item_code", "item code", "料號", "code"),
}

PROJECT_XLSX_FIELDS = (
    "designation", "quantity", "drawing_line_number", "serial", "unit", "description", "item_code",
)


def read_project_rows_xlsx(
    filepath: str,
    mapping_confirmer: ProjectXlsxMappingConfirmer | None = None,
) -> list[ProjectInputRow]:
    """Read project rows from xlsx/xlsm without importing PyQt UI classes."""
    from openpyxl import load_workbook

    wb = load_workbook(filepath, read_only=True, data_only=True)
    try:
        layout = detect_project_xlsx_layout(wb)
        if layout is None:
            raise ValueError("找不到可用的 MTO 表頭；請確認 Excel 內有流水號/數量/單位/型號等欄位。")

        ws = layout["worksheet"]
        header_row = layout["header_row"]
        headers = layout["headers"]
        mapping = dict(layout["mapping"])
        if mapping_confirmer is not None:
            mapping = mapping_confirmer(ws.title, header_row, headers, mapping)

        if not has_project_designation_source(mapping):
            raise ValueError("xlsx 匯入至少需要指定「型號」欄，或指定可抽型號的說明/料號備援欄。")
        if mapping.get("quantity") is None:
            raise ValueError("xlsx 匯入至少需要指定「數量」欄。")

        rows: list[ProjectInputRow] = []
        for row_idx, values in enumerate(ws.iter_rows(min_row=header_row + 1, values_only=True), start=header_row + 1):
            designation = project_mapped_value(values, mapping, "designation")
            if not designation:
                designation = (
                    extract_designation_from_text(project_mapped_value(values, mapping, "description"))
                    or extract_designation_from_text(project_mapped_value(values, mapping, "item_code"))
                )
            if not designation:
                continue

            quantity_text = project_mapped_value(values, mapping, "quantity") or "1"
            rows.append(
                ProjectInputRow(
                    designation=designation,
                    quantity=parse_list_quantity(quantity_text, row_idx),
                    enabled=True,
                    drawing_line_number=project_mapped_value(values, mapping, "drawing_line_number"),
                    serial=project_mapped_value(values, mapping, "serial"),
                    unit=normalize_project_unit_value(project_mapped_value(values, mapping, "unit")),
                )
            )
        return rows
    finally:
        wb.close()


def detect_project_xlsx_layout(wb):
    best = None
    for ws in wb.worksheets:
        scan_rows = list(
            ws.iter_rows(
                min_row=1,
                max_row=min(ws.max_row, 30),
                values_only=True,
            )
        )
        for row_offset, row_values in enumerate(scan_rows, start=1):
            headers = ["" if cell is None else str(cell).strip() for cell in row_values]
            if sum(1 for header in headers if header) < 2:
                continue
            sample_rows = scan_rows[row_offset:row_offset + 12]
            mapping, score = infer_project_column_mapping(headers, sample_rows)
            score += project_sheet_name_bonus(ws.title)
            score += 60 if mapping.get("designation") is not None and mapping.get("quantity") is not None else 0
            candidate = {
                "worksheet": ws,
                "header_row": row_offset,
                "headers": headers,
                "mapping": mapping,
                "score": score,
            }
            if best is None or candidate["score"] > best["score"]:
                best = candidate
    return best


def project_sheet_name_bonus(title: str) -> int:
    normalized = re.sub(r"\s+", "", str(title or "").strip().lower())
    if normalized == "supportmto":
        return 30
    bonus = 0
    if "support" in normalized:
        bonus += 8
    if "mto" in normalized:
        bonus += 8
    if "材料" in normalized or "支撐" in normalized:
        bonus += 4
    return bonus


def infer_project_column_mapping(headers: list[str], sample_rows: list[tuple]) -> tuple[ProjectXlsxMapping, float]:
    thresholds = {
        "designation": 35,
        "quantity": 35,
        "drawing_line_number": 35,
        "serial": 45,
        "unit": 35,
        "description": 35,
        "item_code": 35,
    }
    scores = []
    for field in PROJECT_XLSX_FIELDS:
        for col_idx, header in enumerate(headers):
            column_values = [
                row[col_idx] if col_idx < len(row) else None
                for row in sample_rows
            ]
            score = project_column_score(field, header, column_values)
            if score >= thresholds[field]:
                scores.append((score, field, col_idx))

    mapping: ProjectXlsxMapping = {field: None for field in PROJECT_XLSX_FIELDS}
    used_cols: set[int] = set()
    total_score = 0.0
    for score, field, col_idx in sorted(scores, reverse=True):
        if mapping[field] is not None or col_idx in used_cols:
            continue
        mapping[field] = col_idx
        used_cols.add(col_idx)
        total_score += score
    return mapping, total_score


def project_column_score(field: str, header, values: list) -> float:
    header_text = str(header or "").strip()
    normalized = normalize_project_header(header_text)
    if not normalized:
        return 0.0

    score = 0.0
    aliases = [normalize_project_header(alias) for alias in PROJECT_ROW_ALIASES.get(field, ())]
    if normalized in aliases:
        score += 100
    elif any(alias and alias in normalized for alias in aliases):
        score += 65

    keyword_scores = {
        "serial": (("流水", "序號", "編號", "serial", "serialno", "seq", "sort", "rowno", "lineno"), 42),
        "drawing_line_number": (
            ("drawinglinenumber", "drawingline", "linegroup", "line_group", "dwg", "圖名", "圖號"), 42
        ),
        "quantity": (("數量", "組數", "qty", "quantity", "count"), 42),
        "unit": (("單位", "unit", "uom"), 42),
        "designation": (("型號", "designation", "model", "supportno", "supportdesignation", "支撐編碼"), 42),
        "description": (("description", "desc", "描述", "說明", "中文說明", "品名"), 42),
        "item_code": (("itemcode", "料號", "code"), 42),
    }
    keywords, keyword_score = keyword_scores.get(field, ((), 0))
    if any(normalize_project_header(keyword) in normalized for keyword in keywords):
        score += keyword_score

    nonempty = [str(value).strip() for value in values if value is not None and str(value).strip()]
    if not nonempty:
        return score

    if field == "designation":
        hit_ratio = sum(1 for value in nonempty if looks_like_designation(value)) / len(nonempty)
        score += hit_ratio * 70
    elif field == "quantity":
        numeric_ratio = sum(1 for value in nonempty if looks_like_list_quantity(value)) / len(nonempty)
        score += numeric_ratio * 45
    elif field == "unit":
        unit_ratio = sum(1 for value in nonempty if looks_like_project_unit(value)) / len(nonempty)
        score += unit_ratio * 70
    elif field == "serial":
        unique_ratio = len(set(nonempty)) / len(nonempty)
        score += min(unique_ratio, 1.0) * 15
    elif field == "drawing_line_number":
        drawing_ratio = sum(1 for value in nonempty if looks_like_drawing_line_number(value)) / len(nonempty)
        score += drawing_ratio * 35
    elif field == "description":
        extracted_ratio = sum(1 for value in nonempty if extract_designation_from_text(value) != value) / len(nonempty)
        score += extracted_ratio * 35
    return score


def project_mapped_value(values, mapping: dict, field: str) -> str:
    col_idx = mapping.get(field)
    if col_idx is None or col_idx >= len(values):
        return ""
    value = values[col_idx]
    return "" if value is None else str(value).strip()


def has_project_designation_source(mapping: dict) -> bool:
    return any(mapping.get(field) is not None for field in ("designation", "description", "item_code"))


def parse_list_quantity(text: str, row_number: int) -> int:
    try:
        numeric = float(str(text).strip().replace(",", ""))
        if not numeric.is_integer():
            raise ValueError
        value = int(numeric)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"第 {row_number} 列組數不是整數: {text!r}") from exc
    if value <= 0:
        raise ValueError(f"第 {row_number} 列組數必須大於 0")
    return value


def looks_like_list_quantity(text: str) -> bool:
    try:
        parse_list_quantity(text, 0)
    except ValueError:
        return False
    return True


def normalize_project_unit_value(text: str) -> str:
    value = str(text or "").strip()
    normalized = value.replace(" ", "").lower()
    if normalized in {"", "ве", "вe", "be"}:
        return "組"
    return value


def looks_like_project_unit(text: str) -> bool:
    return normalize_project_unit_value(text).lower() in {"組", "set", "sets", "kg", "ea", "pc", "m"}


def looks_like_designation(text: str) -> bool:
    return bool(re.fullmatch(r"\d{2}[A-Z]?(?:-[A-Z0-9./()]+)+", str(text or "").strip().upper()))


def looks_like_drawing_line_number(text: str) -> bool:
    value = str(text or "").strip()
    return bool(re.search(r"[A-Z]", value, re.IGNORECASE) and ("--" in value or value.count("-") >= 2))


def normalize_project_header(text) -> str:
    return re.sub(r"[\s._-]+", "", str(text or "").strip().lower())


def extract_designation_from_text(text: str) -> str:
    text = str(text or "").strip()
    if not text:
        return ""
    matches = re.findall(r"\b\d{2}[A-Z]?(?:-[A-Z0-9./()]+)+\b", text.upper())
    return matches[-1] if matches else text
