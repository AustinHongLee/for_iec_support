"""
M-34 Lug Plate TYPE-C 資料表
來源: D-35M (M-34 圖紙)

用途: Type 36 等固定型支撐的 Lug Plate 規格查詢
NOTE 2: Material same as the metal to which it is connected
NOTE 3: If reinforcing pad is added, pad thickness included in A or A+t

欄位說明:
  type:   LGP-C 編號
  member: 對應型鋼規格
  A:      板寬 (mm)
  B:      板高 (mm)
  C:      型鋼尺寸基準 (mm)
  D:      孔距 (mm), None 表示無
  E:      邊距 (mm)
  F:      中心距 (mm)
  G:      偏移 (mm), None 表示無
  H:      高度偏移 (mm), None 表示無
  J:      孔徑 ØJ (mm)
  K:      bolt 規格
  T:      板厚 (mm)
"""

# key = member 代碼 (與 steel_sections 的 code 對應)
# 注意: C100 有兩種 (LGP-C-4 / LGP-C-5), 以 member 字串區分
M34_TABLE = {
    "LGP-C-1": {
        "type": "LGP-C-1", "member": "L50*50*6",
        "A": 150, "B": 100, "C": 50, "D": 30, "E": 30, "F": 60,
        "G": None, "H": None, "J": 19, "K": '5/8"', "T": 9,
    },
    "LGP-C-2": {
        "type": "LGP-C-2", "member": "L65*65*6",
        "A": 160, "B": 130, "C": 65, "D": 35, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-C-3": {
        "type": "LGP-C-3", "member": "L75*75*9",
        "A": 160, "B": 140, "C": 75, "D": 40, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-C-4": {
        "type": "LGP-C-4", "member": "C100*50*5",
        "A": 170, "B": 160, "C": 100, "D": 50, "E": 30, "F": 80,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-C-5": {
        "type": "LGP-C-5", "member": "C100*50*5",
        "A": 170, "B": 160, "C": 100, "D": None, "E": 30, "F": 80,
        "G": 25, "H": 50, "J": 19, "K": '5/8"', "T": 10,
    },
    "LGP-C-6": {
        "type": "LGP-C-6", "member": "C125*65*6",
        "A": 170, "B": 180, "C": 125, "D": None, "E": 30, "F": 80,
        "G": 35, "H": 55, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-C-7": {
        "type": "LGP-C-7", "member": "C150*75*9",
        "A": 190, "B": 220, "C": 150, "D": None, "E": 30, "F": 100,
        "G": 40, "H": 70, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-C-8": {
        "type": "LGP-C-8", "member": "C180*75*7",
        "A": 210, "B": 260, "C": 180, "D": None, "E": 35, "F": 110,
        "G": 45, "H": 90, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-C-9": {
        "type": "LGP-C-9", "member": "C200*90*8",
        "A": 220, "B": 300, "C": 200, "D": None, "E": 35, "F": 120,
        "G": 50, "H": 100, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-C-10": {
        "type": "LGP-C-10", "member": "C250*90*9",
        "A": 250, "B": 350, "C": 250, "D": None, "E": 40, "F": 140,
        "G": 60, "H": 130, "J": 25, "K": '7/8"', "T": 16,
    },
}

# ── 以 member 代碼 (L50, C125 等) 快速查找 ──────────────
# 注意: C100 有兩型 (LGP-C-4 有 D 值, LGP-C-5 有 G/H 值)
#       預設回傳 LGP-C-4 (標準型), 需要 LGP-C-5 時用 get_m34_by_lgp_type
_MEMBER_TO_LGP = {
    "L50":  "LGP-C-1",
    "L65":  "LGP-C-2",
    "L75":  "LGP-C-3",
    "C100": "LGP-C-4",
    "C125": "LGP-C-6",
    "C150": "LGP-C-7",
    "C180": "LGP-C-8",
    "C200": "LGP-C-9",
    "C250": "LGP-C-10",
}


def get_m34_by_member(member_code: str) -> dict | None:
    """
    依型鋼代碼 (L50, C125 等) 查 Lug Plate 規格
    C100 預設回傳 LGP-C-4
    """
    lgp_type = _MEMBER_TO_LGP.get(member_code)
    if not lgp_type:
        return None
    return M34_TABLE[lgp_type]


def get_m34_by_lgp_type(lgp_type: str) -> dict | None:
    """依 LGP-C 編號直接查詢"""
    return M34_TABLE.get(lgp_type)
