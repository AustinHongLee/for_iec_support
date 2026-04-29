"""
Type 14 查表資料 — 資料來源: configs/type_14.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type14_table.py
  Type 14 查表 - 結構鋼立柱 + 雙板托架 + Stopper 限位支撐
  Heavy duty structural sliding support with stopper
  
  Designation: 14-{pipe_size}-{LL}{HH}
    LL = L (×100mm, 2 digits)
    HH = H (×100mm, 2 digits)
    例: 14-2B-1005 → A=2", L=1000, H=500
  
  主表 (7 entries):
    A     C    D    E   F   K    M    P    Q    J     B    MEMBER "N"
    2"   190  110  19   9  70  160   65  150  5/8"  80   C100X50X5
    3"   260  190  19  12  70  160   85  160  5/8"  110  C100X50X5
    4"   260  190  19  12  85  185   73  170  5/8"  135  C125X65X6
    6"   380  300  22  16  95  210  105  190  3/4"  190  C150X75X9
    8"   380  300  22  16 110  260   80  210  3/4"  240  C200X90X8
    10"  450  360  28  16 250  260   88  220    1"  295  C200X90X8
    12"  500  410  28  19 250  260   88  240    1"  345  C200X90X8
  
  第二頁 L/H 上限表:
    Pipe_size  pipe_sch  L_MAX  H_MAX
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_14.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE14_LH_LIMITS
TYPE14_LH_LIMITS = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE14_LH_LIMITS"].items()
}

# TYPE14_TABLE
TYPE14_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE14_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type14_data(line_size: int) -> dict | None:
    """依 line size (inch) 查主表，回傳 dict 或 None"""
    return TYPE14_TABLE.get(line_size)

def get_type14_h_max(line_size: int, l_val: int) -> int | None:
    """依 pipe size 和 L 值查 H 上限，回傳 H_MAX 或 None (無匹配)"""
    limits = TYPE14_LH_LIMITS.get(line_size)
    if not limits:
        return None
    for l_max, h_max in limits:
        if l_val <= l_max:
            return h_max
    return None

