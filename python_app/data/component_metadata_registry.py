"""
Metadata-only component table helpers.

用途:
- 為尚未完成尺寸/重量轉錄的 component 建立穩定入口
- 讓 catalog / registry / review handoff 有可引用的單一來源

注意:
- `table_kind == "metadata_only"` 不代表已可用於精算或 BOM lookup
- 這類 table 主要服務低風險批次整理，不應被誤用為數值真相
"""
from __future__ import annotations


def build_metadata_component(
    component_id: str,
    name_en: str,
    category: str,
    pdf_file: str,
    summary: str,
    *,
    line_size_range: str = "pending PDF transcription",
    designation: str = "pending PDF transcription",
    transcription_status: str = "pending_vector_pdf_review",
    notes: list[str] | None = None,
) -> dict:
    return {
        "component_id": component_id,
        "name_en": name_en,
        "category": category,
        "pdf_file": pdf_file,
        "table_kind": "metadata_only",
        "lookup_ready": False,
        "transcription_status": transcription_status,
        "summary": summary,
        "designation": designation,
        "line_size_range": line_size_range,
        "notes": list(notes or []),
    }


def clone_metadata_component(row: dict) -> dict:
    cloned = dict(row)
    cloned["notes"] = list(row.get("notes", []))
    return cloned
