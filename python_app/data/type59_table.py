"""
Type 59 查表資料 — 資料來源: configs/type_59.json
Bridge module (auto-generated 2026-04-29): interface 不變，底層讀 JSON。
原始資料備份: data/_pre_json_backup/type59_table.py
  Type 59 — Lug Plate Support for Shoe / Bare Pipe
  圖號: D-70
  管徑: 2-1/2" & smaller, 3"~8", 10"~14"
  FIG-A: insulated pipe (配 D-63 shoe, NOT FURNISHED)
  FIG-B: bare pipe (配 D-68 U-bolt)
  
  尺寸表依管徑分 3 組
  TABLE A 材料符號: CS=NONE, AS=(A), SS=(S), A516-60=(R)
"""
import json as _json, os as _os

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_59.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

# TYPE59_DIMS
TYPE59_DIMS = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE59_DIMS"].items()
}

# TYPE59_MATERIAL_MAP
TYPE59_MATERIAL_MAP = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["TYPE59_MATERIAL_MAP"].items()
}


# ── 原始查詢函式（interface 不變）────────────────────────
def _size_to_float(size_str: str) -> float:
    """將管徑字串轉為浮點數"""
    s = size_str.replace("B", "").strip()
    if "/" in s:
        parts = s.split("-")
        if len(parts) == 2:
            whole = int(parts[0])
            num, den = parts[1].split("/")
            return whole + int(num) / int(den)
        else:
            num, den = parts[0].split("/")
            return int(num) / int(den)
    return float(s)

def get_type59_group(pipe_size_str: str) -> str:
    """依管徑取得尺寸群組"""
    ps = _size_to_float(pipe_size_str)
    if ps <= 2.5:
        return "small"
    elif ps <= 8:
        return "medium"
    elif ps <= 14:
        return "large"
    else:
        return ""

def get_type59_dims(pipe_size_str: str) -> dict | None:
    """依管徑取得 lug plate 尺寸"""
    group = get_type59_group(pipe_size_str)
    if group:
        return TYPE59_DIMS[group]
    return None

def get_type59_material(symbol: str) -> dict | None:
    """依材料符號取得材料"""
    return TYPE59_MATERIAL_MAP.get(symbol)


if __name__ == "__main__":
    print("Type 59 dimension groups:")
    for grp, dims in TYPE59_DIMS.items():
        print(f"  {grp}: A={dims['A']}, B={dims['B']}, C={dims['C']}, D={dims['D']}, T={dims['T']}")
    print("\nMaterial map:")
    for sym, mat in TYPE59_MATERIAL_MAP.items():
        print(f"  '{sym}' → {mat['material']}")

