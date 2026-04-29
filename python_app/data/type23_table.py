"""
Type 23 查表資料 — 資料來源: configs/type_23.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type23_table.py
  Type 23 資料表 - 頂掛式懸臂支撐 (Top-mounted Cantilever Support)
  從上方既有結構懸掛的支架
  
  H_MAX 上限 (mm):
    L50=500, L65=1500
    L75/L100/C100/C150/H100/H150=2000
  
  FIG_L_MAP (mm):
    A=300, B=500, C=自訂
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_23.json")

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

