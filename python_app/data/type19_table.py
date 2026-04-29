"""
Type 19 查表資料 — 資料來源: configs/type_19.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type19_table.py
  Type 19 查詢表 - 斜撐式 (Lateral Bracing) 支撐
  來源: TYPE-19 圖面表格
  
  格式: 19-{A}B (只有兩段, 無 H/L 段)
  
  組件: MEMBER "M" with "L" LENGTH
    - 1"~6" 使用 L-Angle
    - 8"~12" 使用 CUT FROM H194X150X6X9
  
  Note 1: DIMENSION "L" SHALL BE CUT TO SUIT IN FIELD.
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_19.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE19_TABLE
TYPE19_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE19_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type19_data(pipe_size: float) -> dict | None:
    """查表取得 Type 19 資料, 回傳 dict 或 None"""
    return TYPE19_TABLE.get(pipe_size)

