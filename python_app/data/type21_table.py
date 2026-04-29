"""
Type 21 查表資料 — 資料來源: configs/type_21.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type21_table.py
  Type 21 查詢表 - 側掛式懸臂 U-bolt 支撐 (Cantilever Clamp Support)
  來源: TYPE-21 圖面表格
  
  格式: 21-{M}-{HH}{Fig}        (Fig = A/B)
        21-{M}-{HH}{Fig}-{LL}   (Fig = C, LL=L/100)
    例: 21-L50-05A     → Member=L50X50X6, H=500, L=300 (Fig.A)
        21-L50-05B     → Member=L50X50X6, H=500, L=500 (Fig.B)
        21-L50-05C-07  → Member=L50X50X6, H=500, L=700 (Fig.C)
  
  Note 1: U-BOLT (D-68) NOT FURNISHED
  Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
  
  構件 (2 項):
    1. MEMBER "M" (H): 垂直段, 長度 H
    2. MEMBER "M" (L): 水平段, 長度 L (300/500/自定)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_21.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# FIG_L_MAP
FIG_L_MAP = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["FIG_L_MAP"].items()
}

# MEMBER_H_MAX
MEMBER_H_MAX = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["MEMBER_H_MAX"].items()
}

