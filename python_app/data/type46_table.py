"""
Type 46/47 共用查表資料 — 曲面設備直接支撐含 D-80 接口 (D-56, D-57/D-58)
Type 46: 無 Lug Plate (D-56), H = P - √(R² - Q²)
Type 47: 有 Lug Plate (D-57/D-58), H = P - √(R² - Q²) - 60 - t

管徑 2"~14", Q 值比 Type 44/45 大 ~100mm (D-80 接口偏移)
"""

# 管徑 → Q (mm) — Type 46 & 47 共用
TYPE46_47_PIPE_Q = {
    2:  133,
    3:  148,
    4:  160,
    6:  187,
    8:  213,
    10: 240,
    12: 265,
    14: 281,
}

# Type 46 斜撐 (同 Type 44: H > 1200)
TYPE46_BRACE = {
    "A": {"vertical": 450, "horizontal": 780, "length": 1016},
    "B": {"vertical": 780, "horizontal": 780, "length": 1203},
}
TYPE46_BRACE_H_MIN = 1200

# Type 47 斜撐 (同 Type 45: H > 1140)
TYPE47_BRACE = {
    "A": {"vertical": 400, "horizontal": 758, "length": 1008},
    "B": {"vertical": 669, "horizontal": 758, "length": 1150},
}
TYPE47_BRACE_H_MIN = 1140

# Type 46 Member (極簡: 僅 C 值)
TYPE46_MEMBER = {
    "C100": {"member_full": "C100*50*5", "C": 50},
    "C125": {"member_full": "C125*65*6", "C": 65},
    "C150": {"member_full": "C150*75*9", "C": 75},
}

# Type 47 Member (同 Type 45)
TYPE47_MEMBER = {
    "C100": {
        "member_full": "C100*50*5",
        "A": 170, "B": 50, "C": 100, "D": None, "E": 30, "F": 80,
        "G": None, "J": 22, "K": '3/4"x50',
    },
    "C125": {
        "member_full": "C125*65*6",
        "A": 170, "B": None, "C": 125, "D": 55, "E": 30, "F": 80,
        "G": 35, "J": 22, "K": '3/4"x50',
    },
    "C150": {
        "member_full": "C150*75*9",
        "A": 190, "B": None, "C": 150, "D": 70, "E": 30, "F": 100,
        "G": 40, "J": 22, "K": '3/4"x50',
    },
}


def get_type46_47_q(line_size: float) -> int | None:
    return TYPE46_47_PIPE_Q.get(int(line_size))
