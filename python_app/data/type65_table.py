from .component_size_utils import normalize_fractional_size
"""
Type 65 查表資料 — 資料來源: configs/type_65.json
Bridge module (auto-fixed 2026-04-29): interface 不變，底層讀 JSON。
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_65.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE65_TABLE: 外層 key = 字串管徑 ("2","3"...)，內層 member_by_l key = int mm
def _rebuild_type65_table(raw):
    out = {}
    for pipe_key, row in raw.items():
        row2 = dict(row)
        if "member_by_l" in row2:
            row2["member_by_l"] = {int(k): v for k, v in row2["member_by_l"].items()}
        out[pipe_key] = row2
    return out
TYPE65_TABLE = _rebuild_type65_table(_DATA["TYPE65_TABLE"])

# L_BUCKETS (list)
L_BUCKETS = _DATA["L_BUCKETS"]


# ── 原始查詢函式（interface 不變）────────────────────────

def get_type65_data(line_size: str) -> dict | None:
    """依管徑查 Type 65 資料"""
    key = normalize_fractional_size(line_size).replace('"', "")
    return TYPE65_TABLE.get(key)



def snap_l_bucket(l_mm: int) -> int | None:
    """將 L 值向上取至最近 bucket，超出 2500 回傳 None"""
    for b in L_BUCKETS:
        if l_mm <= b:
            return b
    return None


if __name__ == "__main__":
    print(f"Type 65 table: {len(TYPE65_TABLE)} entries")
    for k, v in TYPE65_TABLE.items():
        print(f"  D={k:>5}\" → rod={v['rod_size']}, members={list(v['member_by_l'].values())}")

