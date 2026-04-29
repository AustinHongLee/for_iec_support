"""
Type 08 查表資料 — 資料來源: configs/type_08.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type08_table.py
  Type 08 查表資料 - 立柱式托板支撐 + 滑動 + Stopper
  PDF: 08.pdf
  
  lookup key = pipe size (A)
    pipe_sch: pipe schedule
    K: stopper 寬 (mm)
    M: stopper 高 (mm)
    B: top plate 邊長 (mm)
    member_n: channel 規格
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_08.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE08_TABLE
TYPE08_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE08_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type08_data(pipe_size: int) -> dict | None:
    return TYPE08_TABLE.get(pipe_size)

