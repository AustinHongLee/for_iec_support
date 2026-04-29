"""
Type 42 查表資料 — Trunnion 曲面設備斜撐支撐 (D-50)
表 1: Member 斜撐尺寸 + G 公式
表 2: 管徑 → Trunnion / E 值
"""

# 表 1: Member 尺寸 + G (斜撐長度) 公式
# G = g_coeff * H + g_offset
TYPE42_MEMBER = {
    "L75": {
        "member_full": "L75*75*9", "C": 75, "D": 75, "H_MAX": 950,
        "A": {"g_coeff": 1.155, "g_offset": 92},   # θ=30°
        "B": {"g_coeff": 1.414, "g_offset": 80},    # θ=45°
    },
    "C100": {
        "member_full": "C100*50*5", "C": 100, "D": 50, "H_MAX": 950,
        "A": {"g_coeff": 1.155, "g_offset": 115},
        "B": {"g_coeff": 1.414, "g_offset": 100},
    },
    "C125": {
        "member_full": "C125*65*6", "C": 125, "D": 65, "H_MAX": 1750,
        "A": {"g_coeff": 1.155, "g_offset": 144},
        "B": {"g_coeff": 1.414, "g_offset": 125},
    },
    "C150": {
        "member_full": "C150*75*9", "C": 150, "D": 75, "H_MAX": 1750,
        "A": {"g_coeff": 1.155, "g_offset": 173},
        "B": {"g_coeff": 1.414, "g_offset": 150},
    },
    "C180": {
        "member_full": "C180*75*7", "C": 180, "D": 75, "H_MAX": 1750,
        "A": {"g_coeff": 1.155, "g_offset": 208},
        "B": {"g_coeff": 1.414, "g_offset": 180},
    },
    "C200": {
        "member_full": "C200*90*8", "C": 200, "D": 90, "H_MAX": 1750,
        "A": {"g_coeff": 1.155, "g_offset": 231},
        "B": {"g_coeff": 1.414, "g_offset": 200},
    },
}

# 表 2: 管徑 → E (偏移) + Trunnion 尺寸
TYPE42_PIPE = {
    2:  {"E": 85,  "trunnion": '1-1/2"'},
    3:  {"E": 100, "trunnion": '2"'},
    4:  {"E": 113, "trunnion": '2"'},
    6:  {"E": 140, "trunnion": '3"'},
    8:  {"E": 165, "trunnion": '4"'},
    10: {"E": 195, "trunnion": '6"'},
    12: {"E": 215, "trunnion": '8"'},
    14: {"E": 230, "trunnion": '10"'},
    16: {"E": 255, "trunnion": '10"'},
    18: {"E": 280, "trunnion": '12"'},
    20: {"E": 305, "trunnion": '12"'},
    24: {"E": 355, "trunnion": '14"'},
}


def get_type42_member(member_code: str) -> dict | None:
    """查 Type 42 member 尺寸與 G 公式"""
    return TYPE42_MEMBER.get(member_code)


def get_type42_pipe(line_size: float) -> dict | None:
    """查 Type 42 管徑 → E + Trunnion"""
    return TYPE42_PIPE.get(int(line_size))
