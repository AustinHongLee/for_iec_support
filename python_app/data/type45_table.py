"""
Type 45 查表資料 — 曲面設備直接夾持支撐 (D-54, D-55)
無 Trunnion, 有 Lug Plate, 僅 8"~14" 管徑
H 公式: H = P - √(R² - Q²) - 60 - t

⚠️ Detail Y/Z 反轉:
  Detail Y = Vessel 端 → M-35/36 (Type-D/E)
  Detail Z = 管線端 → M-34 (Type-C)
"""

# 管徑 → Q (mm) — 與 Type 44 相同
TYPE45_PIPE_Q = {
    8:  113,
    10: 140,
    12: 165,
    14: 181,
}

# 斜撐資料 (H > 1140 時才安裝)
TYPE45_BRACE = {
    "A": {"vertical": 400, "horizontal": 758, "length": 1008},  # θ=30°
    "B": {"vertical": 693, "horizontal": 758, "length": 1150},  # θ=45°
}
TYPE45_BRACE_H_MIN = 1140  # H > 此值才安裝斜撐

# Member 尺寸 (D-55)
TYPE45_MEMBER = {
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


def get_type45_q(line_size: float) -> int | None:
    return TYPE45_PIPE_Q.get(int(line_size))


def get_type45_member(member_code: str) -> dict | None:
    return TYPE45_MEMBER.get(member_code)


def get_type45_brace(fig: str) -> dict | None:
    return TYPE45_BRACE.get(fig)
