"""
Type 79 查表資料 — 資料來源: configs/type_79.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type79_table.py
  Type 79 U-band support dimensional table (D-94).
  
  Source status:
  - `79.pdf` is vector-outline based; text extraction returns no usable text.
  - 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
    visual inspection.
  
  The drawing calls out `U-BAND SEE M-55`. Type 79 now uses `data.m55_table` for
  the component-level lookup; this file remains as the original D-94 transcription
  reference for regression checks.
"""
import json as _json, os as _os
from .component_size_utils import normalize_fractional_size
from copy import deepcopy

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_79.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

STEEL_DENSITY_KG_PER_MM3 = _DATA["STEEL_DENSITY_KG_PER_MM3"]

# TYPE79_TABLE
TYPE79_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE79_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def estimate_type79_uband_weight_kg(row: dict) -> float:
    return round(row["B"] * row["E"] * row["T"] * STEEL_DENSITY_KG_PER_MM3, 2)

def get_type79_data(line_size) -> dict | None:
    row = TYPE79_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = estimate_type79_uband_weight_kg(item)
    item["weight_status"] = "estimated_from_B_E_T_blank_until_M55_exists"
    return item

def list_type79_sizes() -> list[str]:
    return list(TYPE79_TABLE.keys())

