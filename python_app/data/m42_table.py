"""
M42 底板查詢表 - 對應 VBA 中的 M_42_Table 工作表
"""

# M42/M42A/M43 底板表: pipe_size -> {各欄位}
# 對照 PDF M-43 Rev.1 (HP6-DSD-A4-500-001, page 3 of 3) 欄位:
#   B=plate_a, C=plate_bc, D=plate_d_bc_bolt, E=plate_d,
#   F=plate_d_bolt, G=plate_e, H=bolt_hole_dia, J=exp_bolt_spec,
#   K=plate_thickness
M42_TABLE = {
    1:  {"steel": "L50x50x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    2:  {"steel": "L65x65x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    3:  {"steel": "L65x65x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    4:  {"steel": "L75x75x9",     "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    5:  {"steel": "L100x100x10",  "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    6:  {"steel": "L100x100x10",  "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": '5/8"', "mach_bolt": '5/8" X 40', "plate_thickness": 9},
    8:  {"steel": "C125x65x6",    "plate_a": 330, "plate_bc": 380, "plate_d_bc_bolt": 300, "plate_d": 490, "plate_d_bolt": 410, "plate_e": 380, "bolt_hole_dia": 22, "exp_bolt_spec": '3/4"', "mach_bolt": '3/4" X 60', "plate_thickness": 16},
    10: {"steel": "C150x75x9",    "plate_a": 330, "plate_bc": 380, "plate_d_bc_bolt": 300, "plate_d": 490, "plate_d_bolt": 410, "plate_e": 380, "bolt_hole_dia": 22, "exp_bolt_spec": '3/4"', "mach_bolt": '3/4" X 60', "plate_thickness": 16},
    12: {"steel": "H150x150x7",   "plate_a": 380, "plate_bc": 500, "plate_d_bc_bolt": 410, "plate_d": 560, "plate_d_bolt": 470, "plate_e": 430, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
    14: {"steel": "-",             "plate_a": 440, "plate_bc": 580, "plate_d_bc_bolt": 490, "plate_d": 580, "plate_d_bolt": 490, "plate_e": 580, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
    16: {"steel": "-",             "plate_a": 490, "plate_bc": 630, "plate_d_bc_bolt": 540, "plate_d": 630, "plate_d_bolt": 540, "plate_e": 630, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
    18: {"steel": "-",             "plate_a": 540, "plate_bc": 680, "plate_d_bc_bolt": 590, "plate_d": 680, "plate_d_bolt": 590, "plate_e": 680, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
    24: {"steel": "-",             "plate_a": 690, "plate_bc": 830, "plate_d_bc_bolt": 740, "plate_d": 830, "plate_d_bolt": 740, "plate_e": 830, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
    28: {"steel": "-",             "plate_a": 790, "plate_bc": 930, "plate_d_bc_bolt": 840, "plate_d": 930, "plate_d_bolt": 840, "plate_e": 930, "bolt_hole_dia": 26, "exp_bolt_spec": '7/8"', "mach_bolt": '7/8" X 60', "plate_thickness": 16},
}

# 反向查表: 以型鋼名稱查 M42 資料 (VBA 中 column B 查表路徑)
# 統一將 "x" 和 "*" 視為相同分隔符
M42_BY_STEEL = {}
for _k, _v in M42_TABLE.items():
    _steel_key = _v["steel"].replace("x", "*")
    if _steel_key not in M42_BY_STEEL:
        M42_BY_STEEL[_steel_key] = _v
# 補充 H250x250x9 (VBA 中 pipe 12 有兩筆, VLOOKUP 只取第一筆, 但反向查表需要)
M42_BY_STEEL["H250*250*9"] = M42_TABLE[12]
# 補充 H150*150*10 — Type_27 圖面 MEMBER "M" 使用 H150×150×10, M42 表原本只有 H150*150*7
M42_BY_STEEL["H150*150*10"] = M42_TABLE[12]

_M42_NUMERIC_KEYS = sorted(M42_TABLE.keys())

_M42_STEEL_CODE_ROWS = {
    "L50": 1,
    "L65": 1,
    "L75": 4,
    "L100": 4,
    "L150": 12,
    "C125": 8,
    "C150": 10,
    "H150": 12,
    "H250": 12,
}

_M42_STEEL_FALLBACKS = {
    "L": [(50, 1, "L50"), (65, 1, "L65"), (75, 4, "L75"), (100, 4, "L100"), (150, 12, "L150")],
    "C": [(125, 8, "C125"), (150, 10, "C150")],
    "H": [(150, 12, "H150"), (250, 12, "H250")],
}

# M47 管夾尺寸: pipe_size -> (W, L)
M47_DIMENSIONS = {
    0.75: (50, 83), 1: (50, 105), 1.5: (50, 152), 2: (50, 190),
    2.5: (50, 229), 3: (50, 279), 4: (50, 359), 5: (50, 444),
    6: (50, 529), 8: (80, 688), 10: (80, 858), 12: (80, 1017),
    14: (80, 1117), 16: (80, 1277), 18: (80, 1436), 20: (90, 1596),
    24: (90, 1915), 26: (90, 2074), 28: (90, 2234), 30: (90, 2393),
    32: (90, 2553), 34: (110, 2712), 36: (110, 2872), 40: (110, 3191),
    42: (110, 3350),
}


def get_m42_data(pipe_size) -> dict:
    """
    查詢 M42 底板資料
    支援數字 pipe_size 或含 * 的型鋼字串
    """
    s = str(pipe_size)
    if "*" in s or "x" in s:
        return get_m42_data_by_steel(s)
    size_int = int(float(pipe_size))
    if size_int not in M42_TABLE:
        raise ValueError(f"管徑 {pipe_size} 不在 M42 查詢表中")
    return M42_TABLE[size_int]


def get_m42_data_by_steel(steel_name: str) -> dict:
    """以型鋼名稱查詢 M42 底板資料"""
    key = steel_name.replace("x", "*")
    if key not in M42_BY_STEEL:
        raise ValueError(f"型鋼 {steel_name} 不在 M42 查詢表中")
    return M42_BY_STEEL[key]


def _resolve_m42_numeric_key(pipe_size) -> tuple[int, str | None]:
    size = float(pipe_size)
    if size in M42_TABLE:
        return int(size), None

    # M-43 lists range rows for 1"~3" and 4"~6"; fractional sizes inside
    # these ranges use the same row group and should not be treated as errors.
    if 1 <= size <= 3:
        return 1, None
    if 4 <= size <= 6:
        return 4, None

    candidates = [key for key in _M42_NUMERIC_KEYS if key >= size]
    if candidates:
        fallback = candidates[0]
        return fallback, (
            f"M42: 管徑 {pipe_size}\" 未列於 M-43 表，"
            f"改用 {fallback}\" row 計算，需人工確認"
        )

    fallback = _M42_NUMERIC_KEYS[-1]
    return fallback, (
        f"M42: 管徑 {pipe_size}\" 超出 M-43 表，"
        f"暫用最大 {fallback}\" row 計算，需人工確認"
    )


def _steel_code(steel_name: str) -> str | None:
    normalized = steel_name.upper().replace("X", "*")
    prefix = normalized[0] if normalized else ""
    digits = []
    for char in normalized[1:]:
        if char.isdigit():
            digits.append(char)
            continue
        break
    if not digits or prefix not in _M42_STEEL_FALLBACKS:
        return None
    return f"{prefix}{int(''.join(digits))}"


def _resolve_m42_steel_key(steel_name: str) -> tuple[int, str | None]:
    key = steel_name.replace("x", "*")
    if key in M42_BY_STEEL:
        row = M42_BY_STEEL[key]
        for table_key, table_row in M42_TABLE.items():
            if table_row is row:
                return table_key, None

    code = _steel_code(steel_name)
    if not code:
        raise ValueError(f"型鋼 {steel_name} 不在 M42 查詢表中")

    if code in _M42_STEEL_CODE_ROWS:
        return _M42_STEEL_CODE_ROWS[code], None

    prefix = code[0]
    size = int(code[1:])
    candidates = _M42_STEEL_FALLBACKS[prefix]
    larger = [item for item in candidates if item[0] >= size]
    if larger:
        _, row_key, fallback_code = larger[0]
        return row_key, (
            f"M42: 型鋼 {steel_name} 未列於 M-43 表，"
            f"改用 {fallback_code} row 計算，需人工確認"
        )

    _, row_key, fallback_code = candidates[-1]
    return row_key, (
        f"M42: 型鋼 {steel_name} 超出 M-43 表，"
        f"暫用最大 {fallback_code} row 計算，需人工確認"
    )


def resolve_m42_data(pipe_size) -> tuple[dict, str | None]:
    """
    M42 engineering resolver.

    Returns (row, warning). It keeps strict table rows in get_m42_data(), but
    lets calculator flows continue for documented fallback cases:
    - 0.5"/0.75" -> 1" row, with warning.
    - Missing pipe sizes such as 20"/22" -> next listed row, with warning.
    - Missing shape steel sizes -> next same-family listed steel row, with warning.
    """
    s = str(pipe_size)
    if "*" in s or "x" in s:
        row_key, warning = _resolve_m42_steel_key(s)
    else:
        row_key, warning = _resolve_m42_numeric_key(pipe_size)
    return M42_TABLE[row_key], warning


def get_m47_dimensions(pipe_size: float) -> tuple:
    """查詢 M47 管夾尺寸 (W, L)"""
    if pipe_size not in M47_DIMENSIONS:
        raise ValueError(f"管徑 {pipe_size} 不在 M47 查詢表中")
    return M47_DIMENSIONS[pipe_size]
