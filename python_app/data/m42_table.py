"""
M42 底板查詢表 - 對應 VBA 中的 M_42_Table 工作表
"""

# M42/M43 底板表: pipe_size -> {各欄位}
# 對照 PDF M-43 (STM-05.01 page 3 of 3) 欄位:
#   B=plate_a, C=plate_bc, D=plate_d_bc_bolt, E=plate_d,
#   F=plate_d_bolt, G=plate_e, H=bolt_hole_dia, J=exp_bolt_spec,
#   MACH.BOLT=mach_bolt, K=plate_thickness
M42_TABLE = {
    1:  {"steel": "L50x50x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    2:  {"steel": "L65x65x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    3:  {"steel": "L65x65x6",     "plate_a": 150, "plate_bc": 180, "plate_d_bc_bolt": 110, "plate_d": 290, "plate_d_bolt": 220, "plate_e": 200, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    4:  {"steel": "L75x75x9",     "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    5:  {"steel": "L100x100x10",  "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    6:  {"steel": "L100x100x10",  "plate_a": 230, "plate_bc": 260, "plate_d_bc_bolt": 190, "plate_d": 370, "plate_d_bolt": 300, "plate_e": 280, "bolt_hole_dia": 19, "exp_bolt_spec": "M16", "mach_bolt": "M16 X 40", "plate_thickness": 9},
    8:  {"steel": "C125x65x6",    "plate_a": 330, "plate_bc": 380, "plate_d_bc_bolt": 300, "plate_d": 490, "plate_d_bolt": 410, "plate_e": 380, "bolt_hole_dia": 22, "exp_bolt_spec": "M20", "mach_bolt": "M20 X 60", "plate_thickness": 16},
    10: {"steel": "C150x75x9",    "plate_a": 330, "plate_bc": 380, "plate_d_bc_bolt": 300, "plate_d": 490, "plate_d_bolt": 410, "plate_e": 380, "bolt_hole_dia": 22, "exp_bolt_spec": "M20", "mach_bolt": "M20 X 60", "plate_thickness": 16},
    12: {"steel": "H150x150x7",   "plate_a": 380, "plate_bc": 500, "plate_d_bc_bolt": 410, "plate_d": 560, "plate_d_bolt": 470, "plate_e": 430, "bolt_hole_dia": 26, "exp_bolt_spec": "M24", "mach_bolt": "M24 X 60", "plate_thickness": 16},
    18: {"steel": "-",             "plate_a": 540, "plate_bc": 680, "plate_d_bc_bolt": 590, "plate_d": 680, "plate_d_bolt": 590, "plate_e": 680, "bolt_hole_dia": 26, "exp_bolt_spec": "M24", "mach_bolt": "M24 X 60", "plate_thickness": 16},
    24: {"steel": "-",             "plate_a": 690, "plate_bc": 830, "plate_d_bc_bolt": 740, "plate_d": 830, "plate_d_bolt": 740, "plate_e": 830, "bolt_hole_dia": 26, "exp_bolt_spec": "M24", "mach_bolt": "M24 X 60", "plate_thickness": 16},
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


def get_m47_dimensions(pipe_size: float) -> tuple:
    """查詢 M47 管夾尺寸 (W, L)"""
    if pipe_size not in M47_DIMENSIONS:
        raise ValueError(f"管徑 {pipe_size} 不在 M47 查詢表中")
    return M47_DIMENSIONS[pipe_size]
