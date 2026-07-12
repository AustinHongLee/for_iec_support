"""
M-36 Lug Plate TYPE-E 資料表 (60° 補償轉接板)
來源: M-36M (D-36M 圖紙)

用途: Type 39 (FIG-A, θ=30°) 的 DETAIL Z Lug Plate
板角度 60°, 含 0.577T = tan(30°)×T 幾何補償
NOTE 2: Material same as the metal to which it is connected
NOTE 3: If reinforcing pad is added, pad thickness included in A or A+t

欄位說明: 同 M-35 (TYPE-D)
"""

M36_TABLE = {
    "LGP-E-1": {
        "type": "LGP-E-1", "member": "L50*50*6",
        "A": 125, "B": 130, "C": 50, "D": 30, "E": 30, "F": 60,
        "G": None, "H": None, "J": 19, "K": '5/8"', "T": 9,
    },
    "LGP-E-2": {
        "type": "LGP-E-2", "member": "L65*65*6",
        "A": 135, "B": 155, "C": 65, "D": 35, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-E-3": {
        "type": "LGP-E-3", "member": "L75*75*9",
        "A": 135, "B": 165, "C": 75, "D": 40, "E": 30, "F": 70,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 9,
    },
    "LGP-E-4": {
        "type": "LGP-E-4", "member": "C100*50*5",
        "A": 145, "B": 200, "C": 100, "D": 50, "E": 30, "F": 80,
        "G": None, "H": None, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-E-5": {
        "type": "LGP-E-5", "member": "C125*65*6",
        "A": 145, "B": 230, "C": 125, "D": None, "E": 30, "F": 80,
        "G": 35, "H": 55, "J": 22, "K": '3/4"', "T": 10,
    },
    "LGP-E-6": {
        "type": "LGP-E-6", "member": "C150*75*9",
        "A": 165, "B": 270, "C": 150, "D": None, "E": 30, "F": 100,
        "G": 40, "H": 70, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-E-7": {
        "type": "LGP-E-7", "member": "C180*75*7",
        "A": 185, "B": 315, "C": 180, "D": None, "E": 35, "F": 110,
        "G": 45, "H": 90, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-E-8": {
        "type": "LGP-E-8", "member": "C200*90*8",
        "A": 195, "B": 345, "C": 200, "D": None, "E": 35, "F": 120,
        "G": 50, "H": 100, "J": 22, "K": '3/4"', "T": 12,
    },
    "LGP-E-9": {
        "type": "LGP-E-9", "member": "C250*90*9",
        "A": 220, "B": 415, "C": 250, "D": None, "E": 40, "F": 140,
        "G": 60, "H": 130, "J": 25, "K": '7/8"', "T": 16,
    },
}

# ── 以 member 代碼快速查找 ──
_MEMBER_TO_LGP = {
    "L50":  "LGP-E-1",
    "L65":  "LGP-E-2",
    "L75":  "LGP-E-3",
    "C100": "LGP-E-4",
    "C125": "LGP-E-5",
    "C150": "LGP-E-6",
    "C180": "LGP-E-7",
    "C200": "LGP-E-8",
    "C250": "LGP-E-9",
}


def get_m36_by_member(member_code: str) -> dict | None:
    """依型鋼代碼 (L75, C125 等) 查 LGP Type-E 規格"""
    lgp_type = _MEMBER_TO_LGP.get(member_code)
    if not lgp_type:
        return None
    return M36_TABLE[lgp_type]


def get_m36_by_lgp_type(lgp_type: str) -> dict | None:
    """依 LGP-E 編號直接查詢"""
    return M36_TABLE.get(lgp_type)
