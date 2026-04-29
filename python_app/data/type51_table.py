"""
Type 51 查表資料 — 管線鞍座承托支撐 (D-62, D-62A)
直接承托型: 管線直接坐在鞍座上, 全焊接, 無 bolt/clamp/lug

三種結構:
  3/4"~3": Flat Bar (H×50×9)
  4"~24": 角鐵 Member "M" 兩側對稱
  26"~42": 槽鋼 + 鞍座 (80° 包覆角, 含 D-91 Reinforcing Pad)
"""

TYPE51_TABLE = {
    0.75: {"member": None,          "H": 25},
    1:    {"member": None,          "H": 30},
    1.5:  {"member": None,          "H": 45},
    2:    {"member": None,          "H": 60},
    2.5:  {"member": None,          "H": 70},
    3:    {"member": None,          "H": 80},
    4:    {"member": "L50*50*6",    "H": 125},
    5:    {"member": "L50*50*6",    "H": 125},
    6:    {"member": "L50*50*6",    "H": 125},
    8:    {"member": "L65*65*6",    "H": 150},
    10:   {"member": "L65*65*6",    "H": 150},
    12:   {"member": "L65*65*6",    "H": 200},
    14:   {"member": "L65*65*6",    "H": 200},
    16:   {"member": "L65*65*6",    "H": 250},
    18:   {"member": "L65*65*6",    "H": 300},
    20:   {"member": "L65*65*6",    "H": 300},
    24:   {"member": "L65*65*6",    "H": 300},
    # D-62A 大管 (26"~42")
    26:   {"member": "C125*65*6",   "H": None},
    28:   {"member": "C125*65*6",   "H": None},
    30:   {"member": "C125*65*6",   "H": None},
    32:   {"member": "C125*65*6",   "H": None},
    36:   {"member": "C150*75*9",   "H": None},
    40:   {"member": "C150*75*9",   "H": None},
    42:   {"member": "C150*75*9",   "H": None},
}


def get_type51_data(line_size: float) -> dict | None:
    """依管徑查 member 和 H"""
    return TYPE51_TABLE.get(line_size)
