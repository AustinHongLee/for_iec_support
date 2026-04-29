"""
Type 46 查表資料 — 資料來源: configs/type_46.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type46_table.py
  Type 46/47 共用查表資料 — 曲面設備直接支撐含 D-80 接口 (D-56, D-57/D-58)
  Type 46: 無 Lug Plate (D-56), H = P - √(R² - Q²)
  Type 47: 有 Lug Plate (D-57/D-58), H = P - √(R² - Q²) - 60 - t
  
  管徑 2"~14", Q 值比 Type 44/45 大 ~100mm (D-80 接口偏移)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_46.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

TYPE46_BRACE_H_MIN = _DATA["TYPE46_BRACE_H_MIN"]
TYPE47_BRACE_H_MIN = _DATA["TYPE47_BRACE_H_MIN"]

# TYPE46_47_PIPE_Q
TYPE46_47_PIPE_Q = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE46_47_PIPE_Q"].items()
}

# TYPE46_BRACE
TYPE46_BRACE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE46_BRACE"].items()
}

# TYPE46_MEMBER
TYPE46_MEMBER = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE46_MEMBER"].items()
}

# TYPE47_BRACE
TYPE47_BRACE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE47_BRACE"].items()
}

# TYPE47_MEMBER
TYPE47_MEMBER = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE47_MEMBER"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type46_47_q(line_size: float) -> int | None:
    return TYPE46_47_PIPE_Q.get(int(line_size))

