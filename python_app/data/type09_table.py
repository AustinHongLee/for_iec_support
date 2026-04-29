"""
Type 09 查表資料 — 資料來源: configs/type_09.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type09_table.py
  Type 09 查表資料 - 可調式螺桿支撐 (Threaded Adjustable Support)
  PDF: 09.pdf
  
  lookup key = line size (A)
    support_pipe: 支撐管規格 (都是 2")
    pipe_sch: pipe schedule
    L: dummy pipe spacing (mm), 基於 long radius elbow
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_09.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE09_TABLE
TYPE09_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE09_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type09_data(line_size: int) -> dict | None:
    return TYPE09_TABLE.get(line_size)

