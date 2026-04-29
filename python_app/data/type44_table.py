"""
Type 44 查表資料 — 資料來源: configs/type_44.json
Bridge module (auto-fixed 2026-04-29): interface 不變，底層讀 JSON。
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_44.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

TYPE44_BRACE_H_MIN = _DATA["TYPE44_BRACE_H_MIN"]

# TYPE44_BRACE (dict)
TYPE44_BRACE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE44_BRACE"].items()
}

# TYPE44_PIPE_Q (dict)
TYPE44_PIPE_Q = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE44_PIPE_Q"].items()
}

# TYPE44_MEMBERS (list)
TYPE44_MEMBERS = _DATA["TYPE44_MEMBERS"]


# ── 原始查詢函式（interface 不變）────────────────────────

def get_type44_q(line_size: float) -> int | None:
    """查 Q 值 (管徑偏移)"""
    return TYPE44_PIPE_Q.get(int(line_size))



def get_type44_brace(fig: str) -> dict | None:
    """查斜撐資料, fig = 'A' (30°) 或 'B' (45°)"""
    return TYPE44_BRACE.get(fig)

