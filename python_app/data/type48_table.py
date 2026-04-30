"""
Type 48 查表資料 — 資料來源: configs/type_48.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type48_table.py
  Type 48 查表資料 — Drain Hub 偏移底座支撐 (D-59)
  極簡支撐: 1 塊 plate + 焊接, 100mm 偏移
  管徑 1/2"~6", plate 固定 150×100, 厚度 6 或 9mm
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_48.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE48_MATERIAL_SYMBOL
TYPE48_MATERIAL_SYMBOL = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE48_MATERIAL_SYMBOL"].items()
}

# TYPE48_TABLE
TYPE48_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE48_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type48_data(line_size: float) -> dict | None:
    """依管徑查 plate 規格"""
    return TYPE48_TABLE.get(line_size)

