"""
Type 80 查表資料 — 資料來源: configs/type_80.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type80_table.py
  Type 80 — Pipe Shoe detail (D-95 / D-96)
  
  D-95 covers pipe size 3/4"~24".
  D-96 covers pipe size 26"~42" and refers missing dimensions to D-80B.
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_80.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE80_BIG_TABLE
TYPE80_BIG_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE80_BIG_TABLE"].items()
}

# TYPE80_SMALL_TABLE
TYPE80_SMALL_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE80_SMALL_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type80_small_row(pipe_size: float) -> dict | None:
    return TYPE80_SMALL_TABLE.get(float(pipe_size))

def get_type80_big_row(pipe_size: float) -> dict | None:
    return TYPE80_BIG_TABLE.get(float(pipe_size))

