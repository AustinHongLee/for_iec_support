"""
Type 51 查表資料 — 資料來源: configs/type_51.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type51_table.py
  Type 51 查表資料 — 管線鞍座承托支撐 (D-62, D-62A)
  直接承托型: 管線直接坐在鞍座上, 全焊接, 無 bolt/clamp/lug
  
  三種結構:
    3/4"~3": Flat Bar (H×50×9)
    4"~24": 角鐵 Member "M" 兩側對稱
    26"~42": 槽鋼 + 鞍座 (80° 包覆角, 含 D-91 Reinforcing Pad)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_51.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE51_TABLE
TYPE51_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE51_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type51_data(line_size: float) -> dict | None:
    """依管徑查 member 和 H"""
    return TYPE51_TABLE.get(line_size)

