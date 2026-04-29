"""
Type 22 查表資料 — 資料來源: configs/type_22.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type22_table.py
  Type 22 查詢表 - 落地式懸臂 U-bolt 支撐 (Ground Cantilever Support)
  來源: TYPE-22 圖面表格
  
  格式: 22-{M}-{HH}{Fig}{M42}         (Fig = A/B)
        22-{M}-{HH}C{M42}-{LL}        (Fig = C, LL=L/100)
    例: 22-L50-05AL     → L50, H=500, Fig.A, M42=L
        22-L50-05CL-07  → L50, H=500, Fig.C, M42=L, L=700
  
  Note 1: U-BOLT (D-68) NOT FURNISHED
  Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
  Note 3: H counted from lowest point of paving if no foundation.
  Note 4: USE WITH M-42, TYPE L & P ONLY.
  
  構件:
    1. MEMBER "M" (H段): 垂直, 長度 H
    2. MEMBER "M" (L段): 水平, 長度 L (300/500/自定)
    3. M42 下部構件 (letter L or P only)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_22.json")

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


# ALLOWED_M42_LETTERS (set)
ALLOWED_M42_LETTERS = set(_DATA["ALLOWED_M42_LETTERS"])
