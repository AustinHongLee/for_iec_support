"""
Type 43 查表資料 — 資料來源: configs/type_43.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type43_table.py
  Type 43 查表資料 — Trunnion 全約束支撐 (D-51, D-52)
  表 1: Member 基本尺寸 (同 Type 39)
  表 2: S/N 公式係數 (不同 H_MAX — Type 43 用 950/1750, Type 39 用 1450/2000)
  表 3: 管徑 → Trunnion / Q 值
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_43.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE43_FORMULAS
TYPE43_FORMULAS = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE43_FORMULAS"].items()
}

# TYPE43_PIPE
TYPE43_PIPE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE43_PIPE"].items()
}

# TYPE43_TABLE
TYPE43_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE43_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type43_data(member_code: str) -> dict | None:
    return TYPE43_TABLE.get(member_code)

def get_type43_formula(member_code: str, fig: str) -> dict | None:
    m = TYPE43_FORMULAS.get(member_code)
    if m is None:
        return None
    return m.get(fig)

def get_type43_h_max(member_code: str) -> int | None:
    m = TYPE43_FORMULAS.get(member_code)
    return m["H_MAX"] if m else None

def get_type43_pipe(line_size: float) -> dict | None:
    return TYPE43_PIPE.get(int(line_size))

