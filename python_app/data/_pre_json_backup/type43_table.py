"""
Type 43 查表資料 — Trunnion 全約束支撐 (D-51, D-52)
表 1: Member 基本尺寸 (同 Type 39)
表 2: S/N 公式係數 (不同 H_MAX — Type 43 用 950/1750, Type 39 用 1450/2000)
表 3: 管徑 → Trunnion / Q 值
"""

# 表 1: 基本尺寸 (D-51)
TYPE43_TABLE = {
    "L75": {
        "member_full": "L75*75*9",
        "A": 160, "C": 75, "D": 40, "E": 30, "F": 70,
        "G": None, "J": None,
    },
    "C100": {
        "member_full": "C100*50*5",
        "A": 170, "C": 100, "D": 50, "E": 30, "F": 80,
        "G": None, "J": None,
    },
    "C125": {
        "member_full": "C125*65*6",
        "A": 170, "C": 125, "D": None, "E": 30, "F": 80,
        "G": 35, "J": 55,
    },
    "C150": {
        "member_full": "C150*75*9",
        "A": 190, "C": 150, "D": None, "E": 30, "F": 100,
        "G": 40, "J": 70,
    },
    "C180": {
        "member_full": "C180*75*7",
        "A": 210, "C": 180, "D": None, "E": 35, "F": 110,
        "G": 45, "J": 90,
    },
    "C200": {
        "member_full": "C200*90*8",
        "A": 220, "C": 200, "D": None, "E": 35, "F": 120,
        "G": 50, "J": 100,
    },
}

# 表 2: S/N 公式 (D-52) — 注意 H_MAX 與 Type 39 不同
# S = s_coeff * H + s_offset
# N = n_coeff * H + n_offset
TYPE43_FORMULAS = {
    "L75": {
        "H_MAX": 950,
        "A": {"B": 135, "s_coeff": 0.577, "s_offset": -8,   "n_coeff": 1.155, "n_offset": 92},
        "B": {"B": 115, "s_coeff": 1.0,   "s_offset": -30,  "n_coeff": 1.414, "n_offset": 57},
    },
    "C100": {
        "H_MAX": 950,
        "A": {"B": 145, "s_coeff": 0.577, "s_offset": -7,   "n_coeff": 1.155, "n_offset": 100},
        "B": {"B": 120, "s_coeff": 1.0,   "s_offset": -31,  "n_coeff": 1.414, "n_offset": 55},
    },
    "C125": {
        "H_MAX": 1750,
        "A": {"B": 145, "s_coeff": 0.577, "s_offset": 4,    "n_coeff": 1.155, "n_offset": 114},
        "B": {"B": 130, "s_coeff": 1.0,   "s_offset": -33,  "n_coeff": 1.414, "n_offset": 41},
    },
    "C150": {
        "H_MAX": 1750,
        "A": {"B": 165, "s_coeff": 0.577, "s_offset": 3,    "n_coeff": 1.155, "n_offset": 125},
        "B": {"B": 140, "s_coeff": 1.0,   "s_offset": -36,  "n_coeff": 1.414, "n_offset": 47},
    },
    "C180": {
        "H_MAX": 1750,
        "A": {"B": 185, "s_coeff": 0.577, "s_offset": 7,    "n_coeff": 1.155, "n_offset": 145},
        "B": {"B": 150, "s_coeff": 1.0,   "s_offset": -32,  "n_coeff": 1.414, "n_offset": 60},
    },
    "C200": {
        "H_MAX": 1750,
        "A": {"B": 195, "s_coeff": 0.577, "s_offset": 9,    "n_coeff": 1.155, "n_offset": 155},
        "B": {"B": 160, "s_coeff": 1.0,   "s_offset": -36,  "n_coeff": 1.414, "n_offset": 56},
    },
}

# 表 3: 管徑 → Trunnion / Q (D-52)
TYPE43_PIPE = {
    2:  {"Q": 85,  "trunnion": '1-1/2"'},
    3:  {"Q": 100, "trunnion": '2"'},
    4:  {"Q": 113, "trunnion": '2"'},
    6:  {"Q": 140, "trunnion": '3"'},
    8:  {"Q": 165, "trunnion": '4"'},
    10: {"Q": 195, "trunnion": '6"'},
    12: {"Q": 215, "trunnion": '8"'},
    14: {"Q": 230, "trunnion": '10"'},
    16: {"Q": 255, "trunnion": '10"'},
    18: {"Q": 280, "trunnion": '12"'},
    20: {"Q": 305, "trunnion": '12"'},
    24: {"Q": 355, "trunnion": '14"'},
}


def get_type43_data(member_code: str) -> dict | None:
    return TYPE43_TABLE.get(member_code)


def get_type43_formula(member_code: str, fig: str) -> dict | None:
    m = TYPE43_FORMULAS.get(member_code)
    if m is None:
        return None
    return m.get(fig)


def get_type43_h_max(member_code: str) -> int | None:
    m = TYPE43_FORMULAS.get(member_code)
    return m["H_MAX"] if m else None


def get_type43_pipe(line_size: float) -> dict | None:
    return TYPE43_PIPE.get(int(line_size))
