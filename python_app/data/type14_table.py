"""
Type 14 查表 - 結構鋼立柱 + 雙板托架 + Stopper 限位支撐
Heavy duty structural sliding support with stopper

Designation: 14-{pipe_size}-{LL}{HH}
  LL = L (×100mm, 2 digits)
  HH = H (×100mm, 2 digits)
  例: 14-2B-1005 → A=2", L=1000, H=500

主表 (7 entries):
  A     C    D    E   F   K    M    P    Q    J     B    MEMBER "N"
  2"   190  110  19   9  70  160   65  150  5/8"  80   C100X50X5
  3"   260  190  19  12  70  160   85  160  5/8"  110  C100X50X5
  4"   260  190  19  12  85  185   73  170  5/8"  135  C125X65X6
  6"   380  300  22  16  95  210  105  190  3/4"  190  C150X75X9
  8"   380  300  22  16 110  260   80  210  3/4"  240  C200X90X8
  10"  450  360  28  16 250  260   88  220    1"  295  C200X90X8
  12"  500  410  28  19 250  260   88  240    1"  345  C200X90X8

第二頁 L/H 上限表:
  Pipe_size  pipe_sch  L_MAX  H_MAX
"""

TYPE14_TABLE = {
    2:  {"C": 190, "D": 110, "E": 19, "F": 9,  "K": 70,  "M": 160, "P": 65,  "Q": 150, "J": '5/8"', "B": 80,  "member": "C100X50X5",  "pipe_sch": "SCH.40"},
    3:  {"C": 260, "D": 190, "E": 19, "F": 12, "K": 70,  "M": 160, "P": 85,  "Q": 160, "J": '5/8"', "B": 110, "member": "C100X50X5",  "pipe_sch": "SCH.40"},
    4:  {"C": 260, "D": 190, "E": 19, "F": 12, "K": 85,  "M": 185, "P": 73,  "Q": 170, "J": '5/8"', "B": 135, "member": "C125X65X6",  "pipe_sch": "SCH.40"},
    6:  {"C": 380, "D": 300, "E": 22, "F": 16, "K": 95,  "M": 210, "P": 105, "Q": 190, "J": '3/4"', "B": 190, "member": "C150X75X9",  "pipe_sch": "SCH.40"},
    8:  {"C": 380, "D": 300, "E": 22, "F": 16, "K": 110, "M": 260, "P": 80,  "Q": 210, "J": '3/4"', "B": 240, "member": "C200X90X8",  "pipe_sch": "SCH.40"},
    10: {"C": 450, "D": 360, "E": 28, "F": 16, "K": 250, "M": 260, "P": 88,  "Q": 220, "J": '1"',   "B": 295, "member": "C200X90X8",  "pipe_sch": "SCH.40"},
    12: {"C": 500, "D": 410, "E": 28, "F": 19, "K": 250, "M": 260, "P": 88,  "Q": 240, "J": '1"',   "B": 345, "member": "C200X90X8",  "pipe_sch": "STD.WT"},
}

# L/H 上限表: pipe_size -> [(L_max, H_max), ...]
TYPE14_LH_LIMITS = {
    2:  [(500, 1000), (1000, 500)],
    3:  [(500, 2000), (1000, 1000)],
    4:  [(500, 3000), (1000, 1500)],
    6:  [(500, 4000), (1000, 3500)],
    8:  [(500, 5000), (1000, 4500)],
    10: [(1000, 5000)],
    12: [(1000, 5000)],
}


def get_type14_data(line_size: int) -> dict | None:
    """依 line size (inch) 查主表，回傳 dict 或 None"""
    return TYPE14_TABLE.get(line_size)


def get_type14_h_max(line_size: int, l_val: int) -> int | None:
    """依 pipe size 和 L 值查 H 上限，回傳 H_MAX 或 None (無匹配)"""
    limits = TYPE14_LH_LIMITS.get(line_size)
    if not limits:
        return None
    for l_max, h_max in limits:
        if l_val <= l_max:
            return h_max
    return None
