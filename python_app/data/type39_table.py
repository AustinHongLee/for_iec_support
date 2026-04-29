"""
Type 39 查表資料 — 資料來源: configs/type_39.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type39_table.py
  Type 39 查表資料 — Vessel 斜撐支撐 (D-45)
  lookup key = member 代碼 (L75, C100, C125, C150, C180, C200)
  
  表 1: 基本尺寸 (Lug / 接點)
  表 2: θ=30° (FIG-A) 的 B, S公式, N公式
  表 3: θ=45° (FIG-B) 的 B, S公式, N公式
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_39.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE39_FORMULAS
TYPE39_FORMULAS = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE39_FORMULAS"].items()
}

# TYPE39_TABLE
TYPE39_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE39_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type39_data(member_code: str) -> dict | None:
    """查 Type 39 基本尺寸表"""
    return TYPE39_TABLE.get(member_code)

def get_type39_formula(member_code: str, fig: str) -> dict | None:
    """查 Type 39 S/N 公式係數, fig = 'A' 或 'B'"""
    m = TYPE39_FORMULAS.get(member_code)
    if m is None:
        return None
    return m.get(fig)

