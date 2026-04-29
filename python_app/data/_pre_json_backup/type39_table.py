"""
Type 39 查表資料 — Vessel 斜撐支撐 (D-45)
lookup key = member 代碼 (L75, C100, C125, C150, C180, C200)

表 1: 基本尺寸 (Lug / 接點)
表 2: θ=30° (FIG-A) 的 B, S公式, N公式
表 3: θ=45° (FIG-B) 的 B, S公式, N公式
"""

# 表 1: 基本尺寸
# key = member 短代碼
TYPE39_TABLE = {
    "L75": {
        "member_full": "L75*75*9",
        "A": 160, "C": 75, "D": 40, "E": 30, "F": 70,
        "G": None, "J": None, "H_MAX": 1450,
    },
    "C100": {
        "member_full": "C100*50*5",
        "A": 170, "C": 100, "D": 50, "E": 30, "F": 80,
        "G": None, "J": None, "H_MAX": 1450,
    },
    "C125": {
        "member_full": "C125*65*6",
        "A": 170, "C": 125, "D": None, "E": 30, "F": 80,
        "G": 35, "J": 55, "H_MAX": 1450,
    },
    "C150": {
        "member_full": "C150*75*9",
        "A": 190, "C": 150, "D": None, "E": 30, "F": 100,
        "G": 40, "J": 70, "H_MAX": 2000,
    },
    "C180": {
        "member_full": "C180*75*7",
        "A": 210, "C": 180, "D": None, "E": 35, "F": 110,
        "G": 45, "J": 90, "H_MAX": 2000,
    },
    "C200": {
        "member_full": "C200*90*8",
        "A": 220, "C": 200, "D": None, "E": 35, "F": 120,
        "G": 50, "J": 100, "H_MAX": 2000,
    },
}

# 表 2 & 3: S 和 N 公式係數
# S = s_coeff * H + s_offset
# N = n_coeff * H + n_offset
TYPE39_FORMULAS = {
    "L75": {
        "A": {"B": 135, "s_coeff": 0.577, "s_offset": -8,   "n_coeff": 1.155, "n_offset": 92},
        "B": {"B": 115, "s_coeff": 1.0,   "s_offset": -30,  "n_coeff": 1.414, "n_offset": 57},
    },
    "C100": {
        "A": {"B": 145, "s_coeff": 0.577, "s_offset": -7,   "n_coeff": 1.155, "n_offset": 100},
        "B": {"B": 120, "s_coeff": 1.0,   "s_offset": -31,  "n_coeff": 1.414, "n_offset": 55},
    },
    "C125": {
        "A": {"B": 145, "s_coeff": 0.577, "s_offset": 4,    "n_coeff": 1.155, "n_offset": 114},
        "B": {"B": 130, "s_coeff": 1.0,   "s_offset": -33,  "n_coeff": 1.414, "n_offset": 41},
    },
    "C150": {
        "A": {"B": 165, "s_coeff": 0.577, "s_offset": 3,    "n_coeff": 1.155, "n_offset": 125},
        "B": {"B": 140, "s_coeff": 1.0,   "s_offset": -36,  "n_coeff": 1.414, "n_offset": 47},
    },
    "C180": {
        "A": {"B": 185, "s_coeff": 0.577, "s_offset": 7,    "n_coeff": 1.155, "n_offset": 145},
        "B": {"B": 150, "s_coeff": 1.0,   "s_offset": -32,  "n_coeff": 1.414, "n_offset": 60},
    },
    "C200": {
        "A": {"B": 195, "s_coeff": 0.577, "s_offset": 9,    "n_coeff": 1.155, "n_offset": 155},
        "B": {"B": 160, "s_coeff": 1.0,   "s_offset": -36,  "n_coeff": 1.414, "n_offset": 56},
    },
}


def get_type39_data(member_code: str) -> dict | None:
    """查 Type 39 基本尺寸表"""
    return TYPE39_TABLE.get(member_code)


def get_type39_formula(member_code: str, fig: str) -> dict | None:
    """查 Type 39 S/N 公式係數, fig = 'A' 或 'B'"""
    m = TYPE39_FORMULAS.get(member_code)
    if m is None:
        return None
    return m.get(fig)
