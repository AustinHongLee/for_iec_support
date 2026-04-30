"""
Type 56 查表資料 — 資料來源: configs/type_56.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type56_table.py
  Type 56 查表資料 — 結構式管線檔止 (D-67, D-67A)
  自成一體的結構鋼檔止, 不引用 D-80/D-81
  Designation: 56-{size}B
  
  四種結構:
    3/4"~2-1/2": 標準平板 PL 100×100×6
    3"~4": 小型框架 FAB FROM 6t PLATE
    5"~14": H 型鋼切割框架
    16"~24": 厚板製造框架 FAB FROM 12t PLATE
    26"~42": 大型結構框架 + 120° 鞍座 + D-91 Pad
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_56.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE56_TABLE_1
TYPE56_TABLE_1 = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE56_TABLE_1"].items()
}

# TYPE56_TABLE_2
TYPE56_TABLE_2 = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit()
     else float(k) if isinstance(k, str) and k.lstrip("-").replace(".", "", 1).isdigit()
     else k): v
    for k, v in _DATA["TYPE56_TABLE_2"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type56_data(line_size: float) -> dict | None:
    """依管徑查尺寸"""
    size = line_size if isinstance(line_size, (int, float)) else float(line_size)
    result = TYPE56_TABLE_1.get(size)
    if result is None:
        result = TYPE56_TABLE_2.get(int(size))
    return result

