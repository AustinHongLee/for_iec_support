"""
Type 11 查表資料 — 資料來源: configs/type_11.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type11_table.py
  Type 11 查表資料 - 彈簧可變載支撐 (Spring Variable Support)
  PDF: 11.pdf
  
  lookup key = line_size (A) in inches
    L: dummy pipe spacing (mm), 基於 long radius elbow
    spring_mark: 彈簧標記 (SPR12 / SPR14)
    spring_wire: 彈簧線徑 (mm)
    spring_id: 彈簧內徑 (mm)
    spring_k: 彈簧常數 (kg/mm)
    spring_free_len: 彈簧自由長 (mm)
    spring_max_defl: 最大建議撓度 (mm)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_11.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE11_HARDWARE_TABLE
TYPE11_HARDWARE_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE11_HARDWARE_TABLE"].items()
}

# TYPE11_SPRING_TABLE
TYPE11_SPRING_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE11_SPRING_TABLE"].items()
}

# TYPE11_TABLE
TYPE11_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE11_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type11_data(line_size: int) -> dict | None:
    row = TYPE11_TABLE.get(line_size)
    return dict(row) if row else None

def get_type11_hardware_item(item_id: str) -> dict | None:
    row = TYPE11_HARDWARE_TABLE.get(item_id)
    return dict(row) if row else None

def build_type11_spring_item(spring_mark: str) -> dict | None:
    row = TYPE11_SPRING_TABLE.get(spring_mark)
    if not row:
        return None
    item = dict(row)
    item["spring_mark"] = spring_mark
    item["spec"] = f'{spring_mark} ({item["wire_mm"]}W×{item["id_mm"]}ID)'
    return item

