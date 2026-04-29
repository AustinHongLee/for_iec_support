"""
Type 60 查表資料 — 資料來源: configs/type_60.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type60_table.py
  Type 60 — Large Bore Shoe Side Support
  圖號: D-71
  管徑: 16"~42"
  FIG-A: insulated pipe (配 D-80/80B shoe, NOT FURNISHED)
  FIG-B: bare pipe
  
  完整 support number → 尺寸列 (A, B, C, D, E, F, T) mm
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_60.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE60_TABLE
TYPE60_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE60_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type60_data(support_no: str) -> dict | None:
    """以完整 support number 查詢 Type 60 尺寸"""
    return TYPE60_TABLE.get(support_no)


if __name__ == "__main__":
    print(f"Type 60 table: {len(TYPE60_TABLE)} entries")
    for k, v in sorted(TYPE60_TABLE.items()):
        f_str = f"F={v['F']}" if v['F'] else "F=—"
        print(f"  {k:>12} → A={v['A']}, B={v['B']}, T={v['T']}, {f_str}")

