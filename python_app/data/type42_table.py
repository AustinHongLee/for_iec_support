"""
Type 42 查表資料 — 資料來源: configs/type_42.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type42_table.py
  Type 42 查表資料 — Trunnion 曲面設備斜撐支撐 (D-50)
  表 1: Member 斜撐尺寸 + G 公式
  表 2: 管徑 → Trunnion / E 值
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_42.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE42_MEMBER
TYPE42_MEMBER = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE42_MEMBER"].items()
}

# TYPE42_PIPE
TYPE42_PIPE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE42_PIPE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type42_member(member_code: str) -> dict | None:
    """查 Type 42 member 尺寸與 G 公式"""
    return TYPE42_MEMBER.get(member_code)

def get_type42_pipe(line_size: float) -> dict | None:
    """查 Type 42 管徑 → E + Trunnion"""
    return TYPE42_PIPE.get(int(line_size))

