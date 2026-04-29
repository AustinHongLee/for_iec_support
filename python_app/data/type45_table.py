"""
Type 45 查表資料 — 資料來源: configs/type_45.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type45_table.py
  Type 45 查表資料 — 曲面設備直接夾持支撐 (D-54, D-55)
  無 Trunnion, 有 Lug Plate, 僅 8"~14" 管徑
  H 公式: H = P - √(R² - Q²) - 60 - t
  
  ⚠️ Detail Y/Z 反轉:
    Detail Y = Vessel 端 → M-35/36 (Type-D/E)
    Detail Z = 管線端 → M-34 (Type-C)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_45.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

TYPE45_BRACE_H_MIN = _DATA["TYPE45_BRACE_H_MIN"]

# TYPE45_BRACE
TYPE45_BRACE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE45_BRACE"].items()
}

# TYPE45_MEMBER
TYPE45_MEMBER = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE45_MEMBER"].items()
}

# TYPE45_PIPE_Q
TYPE45_PIPE_Q = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE45_PIPE_Q"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type45_q(line_size: float) -> int | None:
    return TYPE45_PIPE_Q.get(int(line_size))

def get_type45_member(member_code: str) -> dict | None:
    return TYPE45_MEMBER.get(member_code)

def get_type45_brace(fig: str) -> dict | None:
    return TYPE45_BRACE.get(fig)

