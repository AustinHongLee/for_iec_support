"""
Type 20 查表資料 — 資料來源: configs/type_20.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type20_table.py
  Type 20 查詢表 - 長孔滑動底座支撐 (Slotted Clamp Base Support)
  來源: TYPE-20 圖面表格
  
  格式: 20-{M}-{HH}{Fig}
    例: 20-L50-05A → Member=L50X50X6, H=500mm, Fig.A
  
  Note 1: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
  Note 2: STANDARD U-BOLT (NOT FURNISHED)
  Note 3: DETAIL SEE D-80 (NOT FURNISHED)
  
  組件 (1 項):
    1. MEMBER "M": Angle 或 Channel，長度 H，A36/SS400
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_20.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# MEMBER_H_MAX
MEMBER_H_MAX = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["MEMBER_H_MAX"].items()
}

# Z_TABLE
Z_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["Z_TABLE"].items()
}

