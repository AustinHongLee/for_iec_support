"""
Type 13 查表資料 — 資料來源: configs/type_13.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type13_table.py
  Type 13 查表 - Clamp 式雙板夾持 Dummy Pipe 支撐
  Clamped (non-welded) dummy pipe support with plate reinforcement
  
  表格與 Type 12 完全相同:
    A(line_size)  B(support_pipe)  C     P(plate)
    2"            1 1/2" SCH.80    70    150×75×9
    3"            2"     SCH.40    80    150×75×9
    4"            3"     SCH.40    110   150×75×9
    6"            4"     SCH.40    140   150×75×9
    8"            6"     SCH.40    190   250×75×12
    10"           8"     SCH.40    240   250×105×12
    12"           8"     SCH.40    240   350×105×12
    14"           10"    SCH.40    290   350×105×12
    16"           10"    SCH.40    290   350×105×12
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_13.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE12_TABLE
TYPE12_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE12_TABLE"].items()
}

# TYPE13_TABLE
TYPE13_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE13_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type13_data(line_size: int) -> dict | None:
    """依 line size (inch) 查表，回傳 dict 或 None"""
    return TYPE13_TABLE.get(line_size)

