"""
Type 15 查表 - 結構鋼立柱 + Stopper 限位支撐 (落在 existing steel 上)
Heavy duty structural sliding support, steel-structure mounted

與 Type 14 差異: 無 anchor bolt，底部直接落在既有鋼構上
  - Base Plate = D×D×F (無鑽孔)，Type 14 = C×C×F (有鑽孔)
  - 無 EXP.BOLT
  - P 值 (wing plate 寬度) 不同

主表 (7 entries):
  A    D    F   K    M    P    Q    B   MEMBER "N"
  2"  190   9  70  160   95  150   80  C100X50X5
  3"  260  12  70  160  130  160  110  C100X50X5
  4"  260  12  85  185  120  170  135  C125X65X6
  6"  380  16  95  210  180  190  190  C150X75X9
  8"  380  16 110  260  150  210  240  C200X90X8
  10" 450  16 250  260  180  220  295  C200X90X8
  12" 500  19 250  260  190  240  345  C200X90X8
"""

TYPE15_TABLE = {
    2:  {"D": 190, "F": 9,  "K": 70,  "M": 160, "P": 95,  "Q": 150, "B": 80,  "member": "C100X50X5",  "pipe_sch": "SCH.40"},
    3:  {"D": 260, "F": 12, "K": 70,  "M": 160, "P": 130, "Q": 160, "B": 110, "member": "C100X50X5",  "pipe_sch": "SCH.40"},
    4:  {"D": 260, "F": 12, "K": 85,  "M": 185, "P": 120, "Q": 170, "B": 135, "member": "C125X65X6",  "pipe_sch": "SCH.40"},
    6:  {"D": 380, "F": 16, "K": 95,  "M": 210, "P": 180, "Q": 190, "B": 190, "member": "C150X75X9",  "pipe_sch": "SCH.40"},
    8:  {"D": 380, "F": 16, "K": 110, "M": 260, "P": 150, "Q": 210, "B": 240, "member": "C200X90X8",  "pipe_sch": "SCH.40"},
    10: {"D": 450, "F": 16, "K": 250, "M": 260, "P": 180, "Q": 220, "B": 295, "member": "C200X90X8",  "pipe_sch": "SCH.40"},
    12: {"D": 500, "F": 19, "K": 250, "M": 260, "P": 190, "Q": 240, "B": 345, "member": "C200X90X8",  "pipe_sch": "STD.WT"},
}

# L/H 上限表: pipe_size -> [(L_max, H_max), ...]
TYPE15_LH_LIMITS = {
    2:  [(500, 1000), (1000, 500)],
    3:  [(500, 2000), (1000, 1000)],
    4:  [(500, 3000), (1000, 1500)],
    6:  [(500, 4000), (1000, 3500)],
    8:  [(500, 5000), (1000, 4500)],
    10: [(1000, 5000)],
    12: [(1000, 5000)],
}


def get_type15_data(line_size: int) -> dict | None:
    """依 line size (inch) 查主表，回傳 dict 或 None"""
    return TYPE15_TABLE.get(line_size)


def get_type15_h_max(line_size: int, l_val: int) -> int | None:
    """依 pipe size 和 L 值查 H 上限，回傳 H_MAX 或 None"""
    limits = TYPE15_LH_LIMITS.get(line_size)
    if not limits:
        return None
    for l_max, h_max in limits:
        if l_val <= l_max:
            return h_max
    return None
