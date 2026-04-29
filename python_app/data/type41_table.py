"""
Type 41 查表資料 — 資料來源: configs/type_41.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type41_table.py
  Type 41 查表資料 — 牆面錨定支撐 (Wall-Mounted Anchor Support, D-49)
  固定規格表, 9 種支撐型號 (41-1 ~ 41-9)
  FIG-A (41-1~41-4): 單懸臂, FIG-B (41-5~41-9): 含斜撐
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_41.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE41_TABLE
TYPE41_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE41_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type41_data(support_no: str) -> dict | None:
    """依支撐型號查詢, 如 '41-1' 或 '1'"""
    if not support_no.startswith("41-"):
        support_no = f"41-{support_no}"
    return TYPE41_TABLE.get(support_no)

