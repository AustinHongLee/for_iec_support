"""
Type 07 查表資料 — 資料來源: configs/type_07.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type07_table.py
  Type 07 查表資料 - 滑動彎頭支撐
  PDF: 07.pdf
  
  lookup key = supported line size (A)
    pipe_b: dummy pipe 規格 (size + schedule)
    pipe_c: 支撐柱規格 (size + schedule)
    plate_e: 底板 (寬×高×厚)
    plate_f: 滑動板 (寬×高×厚)
    L: 基於 long radius elbow 的長度 (mm)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_07.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE07_TABLE
TYPE07_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE07_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type07_data(line_size: int) -> dict | None:
    return TYPE07_TABLE.get(line_size)

