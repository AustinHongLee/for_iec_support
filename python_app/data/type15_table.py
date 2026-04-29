"""
Type 15 查表資料 — 資料來源: configs/type_15.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type15_table.py
  Type 15 查表 - 結構鋼立柱 + Stopper 限位支撐 (落在 existing steel 上)
  Heavy duty structural sliding support, steel-structure mounted
  
  與 Type 14 差異: 無 anchor bolt，底部直接落在既有鋼構上
    - Base Plate = D×D×F (無鑽孔)，Type 14 = C×C×F (有鑽孔)
    - 無 EXP.BOLT
    - P 值 (wing plate 寬度) 不同
  
  主表 (7 entries):
    A    D    F   K    M    P    Q    B   MEMBER "N"
    2"  190   9  70  160   95  150   80  C100X50X5
    3"  260  12  70  160  130  160  110  C100X50X5
    4"  260  12  85  185  120  170  135  C125X65X6
    6"  380  16  95  210  180  190  190  C150X75X9
    8"  380  16 110  260  150  210  240  C200X90X8
    10" 450  16 250  260  180  220  295  C200X90X8
    12" 500  19 250  260  190  240  345  C200X90X8
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_15.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE15_LH_LIMITS
TYPE15_LH_LIMITS = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE15_LH_LIMITS"].items()
}

# TYPE15_TABLE
TYPE15_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE15_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type15_data(line_size: int) -> dict | None:
    """依 line size (inch) 查主表，回傳 dict 或 None"""
    return TYPE15_TABLE.get(line_size)

def get_type15_h_max(line_size: int, l_val: int) -> int | None:
    """依 pipe size 和 L 值查 H 上限，回傳 H_MAX 或 None"""
    limits = TYPE15_LH_LIMITS.get(line_size)
    if not limits:
        return None
    for l_max, h_max in limits:
        if l_val <= l_max:
            return h_max
    return None

