"""
Type 10 查表資料 — 資料來源: configs/type_10.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type10_table.py
  Type 10 查表資料 - 可調式 Dummy Pipe 支撐 (Four-Bolt Adjustable Support)
  PDF: 10.pdf
  
  lookup key = line_size (A) in inches
    pipe_size_b: supporting pipe size (inches, float)
    pipe_sch: pipe schedule
    L: dummy pipe spacing (mm), 基於 long radius elbow
    plate_t: Plate F 厚度 (mm)
    plate_w: Plate F 邊長 (mm) — 正方形
    bolt_spec: Adjustable Bolt 規格 (J × L1)
    W: bolt 孔距 (mm)
    d_phi: bolt 孔徑 (mm)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_10.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE10_TABLE
TYPE10_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE10_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type10_data(line_size: float) -> dict | None:
    return TYPE10_TABLE.get(line_size)

