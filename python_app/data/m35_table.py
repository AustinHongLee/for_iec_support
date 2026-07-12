"""
M-35 Lug Plate TYPE-D 資料表 (45° 轉接板)
來源: M-35M (D-35M 圖紙)

用途: Type 39 (FIG-B, θ=45°) 的 DETAIL Z Lug Plate
NOTE 2: Material same as the metal to which it is connected
NOTE 3: If reinforcing pad is added, pad thickness included in A or A+t

欄位說明:
  type:   LGP-D 編號
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

M35_TABLE = {
    "LGP-D-1": {
        "type": "LGP-D-1", "member": "L50*50*6",
        "A": 100, "B": 170, "C": 50, "D": 30, "E": 30, "F": 60,
        "G": None, "H": None, "J": 19, "K": '5/8"', "T": 9,
    },
    "LGP-D-2": {
        "type": "LGP-D-2", "member": "L65*65*6",
        "A": 110, "B": 200, "C": 65, "D": 35, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-D-3": {
        "type": "LGP-D-3", "member": "L75*75*9",
        "A": 115, "B": 220, "C": 75, "D": 40, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-D-4": {
        "type": "LGP-D-4", "member": "C100*50*5",
        "A": 120, "B": 260, "C": 100, "D": 50, "E": 30, "F": 80,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-D-5": {
        "type": "LGP-D-5", "member": "C125*65*6",
        "A": 130, "B": 310, "C": 125, "D": None, "E": 30, "F": 80,
        "G": 35, "H": 55, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-D-6": {
        "type": "LGP-D-6", "member": "C150*75*9",
        "A": 140, "B": 350, "C": 150, "D": None, "E": 30, "F": 100,
        "G": 40, "H": 70, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-D-7": {
        "type": "LGP-D-7", "member": "C180*75*7",
        "A": 150, "B": 405, "C": 180, "D": None, "E": 35, "F": 110,
        "G": 45, "H": 90, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-D-8": {
        "type": "LGP-D-8", "member": "C200*90*8",
        "A": 160, "B": 445, "C": 200, "D": None, "E": 35, "F": 120,
        "G": 50, "H": 100, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-D-9": {
        "type": "LGP-D-9", "member": "C250*90*9",
        "A": 190, "B": 545, "C": 250, "D": None, "E": 40, "F": 140,
        "G": 60, "H": 130, "J": 25, "K": '7/8"', "T": 16,
    },
}

# ── 以 member 代碼快速查找 ──
_MEMBER_TO_LGP = {
    "L50":  "LGP-D-1",
    "L65":  "LGP-D-2",
    "L75":  "LGP-D-3",
    "C100": "LGP-D-4",
    "C125": "LGP-D-5",
    "C150": "LGP-D-6",
    "C180": "LGP-D-7",
    "C200": "LGP-D-8",
    "C250": "LGP-D-9",
}


def get_m35_by_member(member_code: str) -> dict | None:
    """依型鋼代碼 (L75, C125 等) 查 LGP Type-D 規格"""
    lgp_type = _MEMBER_TO_LGP.get(member_code)
    if not lgp_type:
        return None
    return M35_TABLE[lgp_type]


def get_m35_by_lgp_type(lgp_type: str) -> dict | None:
    """依 LGP-D 編號直接查詢"""
    return M35_TABLE.get(lgp_type)
