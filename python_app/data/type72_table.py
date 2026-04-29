from __future__ import annotations
from copy import deepcopy
"""
Type 72 查表資料 — 資料來源: configs/type_72.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type72_table.py
  Type 72 strap support dimensional table (D-87).
  
  Source status:
  - `72.pdf` is vector-outline based; text extraction returns no usable text.
  - 2026-04-21 Codex rendered the vector PDF and transcribed the visible table by
    AI visual inspection.
  
  The drawing calls out:
  - STRAP FIG.2 SEE M-54
  - 2-phi11 bolt holes for EB-3/8" expansion bolt (M-45)
  
  M-54 is now table-backed in `data.m54_table`; Type 72 keeps this D-87 table for
  format/range validation and drawing documentation.
"""
import json as _json, os as _os
from .component_size_utils import normalize_fractional_size

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_72.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE72_TABLE
TYPE72_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE72_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type72_data(line_size) -> dict | None:
    row = TYPE72_TABLE.get(normalize_fractional_size(line_size))
    return deepcopy(row) if row else None

def list_type72_sizes() -> list[str]:
    return list(TYPE72_TABLE.keys())

