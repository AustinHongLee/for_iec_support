from __future__ import annotations
from copy import deepcopy
"""
Type 77 查表資料 — 資料來源: configs/type_77.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type77_table.py
  Type 77 saddle support dimensional table (D-92).
  
  Source status:
  - `77.pdf` is vector-outline based; text extraction returns no usable text.
  - 2026-04-21 Codex rendered the PDF and transcribed the visible table by AI
    visual inspection.
"""
import json as _json, os as _os
from .component_size_utils import normalize_fractional_size

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_77.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

STEEL_DENSITY_KG_PER_MM3 = _DATA["STEEL_DENSITY_KG_PER_MM3"]

# TYPE77_TABLE
TYPE77_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE77_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def estimate_type77_saddle_weight_kg(row: dict) -> float:
    # Conservative bounding rectangle estimate for the side-plate envelope plus bottom strip.
    side_plate_area = row["C"] * row["H"]
    bottom_strip_area = row["A"] * row["B"]
    return round((side_plate_area + bottom_strip_area) * row["T"] * STEEL_DENSITY_KG_PER_MM3, 2)

def get_type77_data(line_size) -> dict | None:
    row = TYPE77_TABLE.get(normalize_fractional_size(line_size))
    if not row:
        return None
    item = deepcopy(row)
    item["unit_weight_kg"] = estimate_type77_saddle_weight_kg(item)
    item["weight_status"] = "estimated_from_saddle_bounding_geometry"
    return item

def list_type77_sizes() -> list[str]:
    return list(TYPE77_TABLE.keys())

