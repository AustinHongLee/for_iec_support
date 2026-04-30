"""
Type 57 查表資料 — 資料來源: configs/type_57.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type57_table.py
  Type 57 查表資料 - U-Bolt on Existing Steel (D-68)
  lookup key = line size (float, 吋)
  
  FIG-A: SLIDE, FIG-B: FIXED
  構件: U-BOLT (ref M-26) + ROD
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_57.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE57_TABLE
TYPE57_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE57_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type57_data(line_size: float) -> dict | None:
    """依管徑查 Type 57 U-bolt / Rod 規格"""
    return TYPE57_TABLE.get(line_size)

