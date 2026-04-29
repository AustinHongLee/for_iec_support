"""
中文化可信度 / evidence 契約。

這層刻意不改既有 BOM 結構，只替 `AnalysisResult` 補上可審核標記：

- `meta`: 整體可信度、信心、是否需審核
- `evidence`: 欄位級來源
"""
from __future__ import annotations

from typing import Any


TRUTH_EXACT = "精確"
TRUTH_DERIVED = "推導"
TRUTH_ESTIMATED = "估算"
TRUTH_UNKNOWN = "未知"

TRUTH_CODE = {
    TRUTH_EXACT: "EXACT",
    TRUTH_DERIVED: "DERIVED",
    TRUTH_ESTIMATED: "ESTIMATED",
    TRUTH_UNKNOWN: "UNKNOWN",
}

BASIS_LABELS = {
    "standard_table": "標準表",
    "reviewed_table": "已審核表",
    "rule": "明確規則",
    "formula": "明確公式",
    "pdf_text": "PDF 文字層",
    "pdf_visual": "PDF 視覺判讀",
    "visual_transcription": "視覺轉錄",
    "visual_measurement": "視覺量測",
    "geometry_estimate": "幾何估算",
    "assumption": "工程假設",
    "missing_table": "缺表補值",
    "unknown": "未知",
}

SOURCE_LABELS = {
    "standard_table": "標準資料表",
    "reviewed_table": "已審核資料表",
    "pdf_text": "PDF 文字層",
    "pdf_visual": "PDF 視覺判讀",
    "rule": "程式規則",
    "formula": "公式推導",
    "catalog": "目錄資料",
    "missing_component_table": "缺少 component table",
    "unknown": "未知來源",
}

ESTIMATE_BASES = {
    "pdf_visual",
    "visual_transcription",
    "visual_measurement",
    "geometry_estimate",
    "assumption",
    "missing_table",
}

DERIVED_BASES = {"rule", "formula", "standard_table", "reviewed_table", "pdf_text"}
EXACT_BASES = {"standard_table", "reviewed_table", "pdf_text"}


def make_evidence(
    field: str,
    value: Any,
    basis: str,
    *,
    source: str | None = None,
    page: int | None = None,
    note_ref: str = "",
    confidence: float = 0.0,
    note: str = "",
) -> dict:
    """建立一筆欄位級 evidence，欄位保留 machine code + 中文 label。"""
    source = source or basis
    return {
        "field": field,
        "value": value,
        "basis": basis,
        "basis_label": BASIS_LABELS.get(basis, basis),
        "source": source,
        "source_label": SOURCE_LABELS.get(source, source),
        "page": page,
        "note_ref": note_ref,
        "confidence": round(float(confidence), 2),
        "note": note,
    }


def classify_truth(evidence_list: list[dict]) -> str:
    """依 evidence basis 保守分級，回傳中文 truth level。"""
    if not evidence_list:
        return TRUTH_UNKNOWN

    bases = {item.get("basis", "unknown") for item in evidence_list}
    if any(base in ESTIMATE_BASES for base in bases):
        return TRUTH_ESTIMATED
    if bases and bases.issubset(EXACT_BASES):
        return TRUTH_EXACT
    if bases and bases.issubset(DERIVED_BASES):
        return TRUTH_DERIVED
    return TRUTH_UNKNOWN


def confidence_from_evidence(evidence_list: list[dict]) -> float:
    """用最低信心作整體信心，避免平均值掩蓋弱點。"""
    confidences = [
        float(item.get("confidence", 0.0))
        for item in evidence_list
        if item.get("confidence") is not None
    ]
    if not confidences:
        return 0.0
    return round(min(confidences), 2)


def need_escalation(meta: dict, invariant_errors: list[str] | None = None) -> bool:
    invariant_errors = invariant_errors or []
    if meta.get("truth_level") in {TRUTH_ESTIMATED, TRUTH_UNKNOWN}:
        return True
    if float(meta.get("confidence", 0.0)) < 0.75:
        return True
    return bool(invariant_errors)


def build_meta(
    *,
    type_id: str,
    evidence: list[dict],
    invariant_errors: list[str] | None = None,
    review_reasons: list[str] | None = None,
) -> dict:
    invariant_errors = invariant_errors or []
    review_reasons = review_reasons or []
    truth_level = classify_truth(evidence)
    confidence = confidence_from_evidence(evidence)
    sources = sorted({item.get("source", "unknown") for item in evidence}) or ["unknown"]
    meta = {
        "type_id": str(type_id),
        "truth_level": truth_level,
        "truth_level_code": TRUTH_CODE[truth_level],
        "confidence": confidence,
        "sources": sources,
        "source_labels": [SOURCE_LABELS.get(source, source) for source in sources],
        "requires_review": False,
        "review_reasons": review_reasons[:],
        "invariant_errors": invariant_errors[:],
    }
    meta["requires_review"] = need_escalation(meta, invariant_errors)
    if meta["requires_review"] and not meta["review_reasons"]:
        meta["review_reasons"].append("可信度分級或信心門檻需要審核")
    return meta


def default_unknown_meta(type_id: str = "") -> dict:
    return build_meta(
        type_id=type_id,
        evidence=[],
        review_reasons=["尚未補齊中文化 evidence 契約；預設需審核"],
    )


def apply_truth_contract(
    result,
    *,
    type_id: str,
    evidence: list[dict] | None = None,
    invariant_errors: list[str] | None = None,
    review_reasons: list[str] | None = None,
):
    """把 evidence/meta 寫回 AnalysisResult，回傳同一個 result 以利鏈式使用。"""
    if evidence is not None:
        result.evidence = evidence
    if not getattr(result, "evidence", None):
        result.evidence = []
    result.meta = build_meta(
        type_id=type_id,
        evidence=result.evidence,
        invariant_errors=invariant_errors or [],
        review_reasons=review_reasons or [],
    )
    return result


def validate_named_invariants(values: dict, rules: dict[str, callable]) -> list[str]:
    """簡易語意 invariant runner；回傳失敗規則名稱。"""
    errors: list[str] = []
    for name, rule in rules.items():
        try:
            if not rule(values):
                errors.append(name)
        except Exception:
            errors.append(f"{name}:rule_exception")
    return errors
