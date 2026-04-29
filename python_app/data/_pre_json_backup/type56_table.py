"""
Type 56 查表資料 — 結構式管線檔止 (D-67, D-67A)
自成一體的結構鋼檔止, 不引用 D-80/D-81
Designation: 56-{size}B

四種結構:
  3/4"~2-1/2": 標準平板 PL 100×100×6
  3"~4": 小型框架 FAB FROM 6t PLATE
  5"~14": H 型鋼切割框架
  16"~24": 厚板製造框架 FAB FROM 12t PLATE
  26"~42": 大型結構框架 + 120° 鞍座 + D-91 Pad
"""

# D-67 (3/4"~24")
TYPE56_TABLE_1 = {
    0.75: {"A": None, "B": None, "C": None,                          "D": None, "E": None, "R": None},
    1:    {"A": None, "B": None, "C": None,                          "D": None, "E": None, "R": None},
    1.5:  {"A": None, "B": None, "C": None,                          "D": None, "E": None, "R": None},
    2:    {"A": None, "B": None, "C": None,                          "D": None, "E": None, "R": None},
    2.5:  {"A": None, "B": None, "C": None,                          "D": None, "E": None, "R": None},
    3:    {"A": 75,  "B": 100, "C": "FAB FROM 6t PLATE",             "D": 75,  "E": 6,    "R": 45},
    4:    {"A": 75,  "B": 100, "C": "FAB FROM 6t PLATE",             "D": 75,  "E": 6,    "R": 57},
    5:    {"A": 100, "B": 100, "C": "CUT FROM H200*100*5.5*8",       "D": 100, "E": None, "R": 70},
    6:    {"A": 150, "B": 150, "C": "CUT FROM H194*150*6*9",         "D": 100, "E": None, "R": 84},
    8:    {"A": 150, "B": 150, "C": "CUT FROM H194*150*6*9",         "D": 100, "E": None, "R": 110},
    10:   {"A": 200, "B": 200, "C": "CUT FROM H200*200*8*12",        "D": 200, "E": None, "R": 137},
    12:   {"A": 200, "B": 200, "C": "CUT FROM H200*200*8*12",        "D": 200, "E": None, "R": 162},
    14:   {"A": 200, "B": 200, "C": "CUT FROM H200*200*8*12",        "D": 200, "E": None, "R": 178},
    16:   {"A": 300, "B": 250, "C": "FAB FROM 12t PLATE",            "D": 300, "E": 12,   "R": 203},
    18:   {"A": 300, "B": 250, "C": "FAB FROM 12t PLATE",            "D": 300, "E": 12,   "R": 229},
    20:   {"A": 300, "B": 250, "C": "FAB FROM 12t PLATE",            "D": 300, "E": 12,   "R": 254},
    24:   {"A": 350, "B": 250, "C": "FAB FROM 12t PLATE",            "D": 350, "E": 12,   "R": 305},
}

# D-67A (26"~42")
TYPE56_TABLE_2 = {
    26: {"A": 350, "B": 250, "C": 250, "D": 350, "E": 12, "R": 330},
    28: {"A": 350, "B": 250, "C": 250, "D": 350, "E": 12, "R": 356},
    30: {"A": 350, "B": 250, "C": 250, "D": 350, "E": 12, "R": 381},
    32: {"A": 450, "B": 300, "C": 350, "D": 400, "E": 12, "R": 406},
    36: {"A": 450, "B": 300, "C": 350, "D": 400, "E": 12, "R": 457},
    40: {"A": 450, "B": 300, "C": 350, "D": 400, "E": 12, "R": 508},
    42: {"A": 450, "B": 300, "C": 350, "D": 400, "E": 12, "R": 533},
}


def get_type56_data(line_size: float) -> dict | None:
    """依管徑查尺寸"""
    size = line_size if isinstance(line_size, (int, float)) else float(line_size)
    result = TYPE56_TABLE_1.get(size)
    if result is None:
        result = TYPE56_TABLE_2.get(int(size))
    return result
