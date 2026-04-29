"""
Type 58 查表資料 — 資料來源: configs/type_58.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type58_table.py
  Type 58 — U-Bolt Plate Saddle on Steel Plate / Shape Steel
  圖號: D-69
  管徑: 1/4"~30"
  FIG-A: 鋼板放在平板上
  FIG-B: 鋼板放在型鋼上 (多 X 尺寸)
  
  欄位: rod_size, hole_d(mm), hole_pitch(mm), plate_l(mm), plate_b(mm), plate_t(mm), x(mm)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_58.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE58_TABLE
TYPE58_TABLE = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE58_TABLE"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def get_type58_data(pipe_size_str: str) -> dict | None:
    """查詢 Type 58 尺寸資料"""
    return TYPE58_TABLE.get(pipe_size_str)


if __name__ == "__main__":
    print(f"Type 58 table: {len(TYPE58_TABLE)} entries")
    for k, v in TYPE58_TABLE.items():
        print(f"  {k:>6}\" → rod={v['rod_size']}, plate={v['plate_l']}×{v['plate_b']}×{v['plate_t']}")

