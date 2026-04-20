"""
Type 59 — Lug Plate Support for Shoe / Bare Pipe
圖號: D-70
管徑: 2-1/2" & smaller, 3"~8", 10"~14"
FIG-A: insulated pipe (配 D-63 shoe, NOT FURNISHED)
FIG-B: bare pipe (配 D-68 U-bolt)

尺寸表依管徑分 3 組
TABLE A 材料符號: CS=NONE, AS=(A), SS=(S), A516-60=(R)
"""

# 三組尺寸 (A, B, C, D, T) mm
TYPE59_DIMS = {
    "small":  {"A": 80,  "B": 55,  "C": 15, "D": None, "T": 9},   # 2-1/2" & smaller
    "medium": {"A": 150, "B": 100, "C": 50, "D": None, "T": 12},  # 3"~8"
    "large":  {"A": 150, "B": 130, "C": 50, "D": 120,  "T": 12},  # 10"~14"
}

# 材料符號對應
TYPE59_MATERIAL_MAP = {
    "":    {"material": "A283 Gr.C", "desc": "Carbon Steel"},
    "(A)": {"material": "A387-22",   "desc": "Alloy Steel"},
    "(S)": {"material": "A240-304",  "desc": "Stainless Steel"},
    "(R)": {"material": "A516-60",   "desc": "Carbon Steel (A516-60)"},
}


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
