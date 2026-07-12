"""
M37 Lug Plate 查詢表 - 對應 PDF M-37 (LUG PLATE TYPE-F)
主鍵: LGP-F-x, 用 member 尺寸反查

欄位 (mm):
  A=底板寬, B=底板高, C=上緣寬, D=上緣偏移,
  E=加勁板高, F=加勁板間距, G=螺栓水平距, H=螺栓垂直距,
  J=孔徑, K=螺栓規格, T=板厚
"""

M37_TABLE = {
    "LGP-F-1": {"member": "L50*50*6",   "A": 150, "B": 200, "C": 50,  "D": 30, "E": 30, "F": 60,  "G": None, "H": None, "J": 19, "K": "5/8\"x40", "T": 9},
    "LGP-F-2": {"member": "L65*65*6",   "A": 160, "B": 220, "C": 65,  "D": 35, "E": 30, "F": 70,  "G": None, "H": None, "J": 22, "K": "3/4\"x50", "T": 9},
    "LGP-F-3": {"member": "L75*75*9",   "A": 160, "B": 220, "C": 75,  "D": 40, "E": 30, "F": 70,  "G": None, "H": None, "J": 22, "K": "3/4\"x50", "T": 9},
    "LGP-F-4": {"member": "C100*50*5",  "A": 170, "B": 230, "C": 100, "D": 50, "E": 30, "F": 80,  "G": None, "H": None, "J": 22, "K": "3/4\"x50", "T": 10},
    "LGP-F-5": {"member": "C125*65*6",  "A": 170, "B": 230, "C": 125, "D": None, "E": 30, "F": 80, "G": 35, "H": 55, "J": 22, "K": "3/4\"x50", "T": 10},
    "LGP-F-6": {"member": "C150*75*9",  "A": 190, "B": 260, "C": 150, "D": None, "E": 30, "F": 100, "G": 40, "H": 70, "J": 22, "K": "3/4\"x50", "T": 12},
    "LGP-F-7": {"member": "C180*75*7",  "A": 210, "B": 280, "C": 180, "D": None, "E": 35, "F": 110, "G": 45, "H": 90, "J": 22, "K": "3/4\"x50", "T": 12},
    "LGP-F-8": {"member": "C200*80*7.5","A": 220, "B": 300, "C": 200, "D": None, "E": 35, "F": 120, "G": 50, "H": 100, "J": 22, "K": "3/4\"x50", "T": 12},
    "LGP-F-9": {"member": "C250*90*9",  "A": 250, "B": 340, "C": 250, "D": None, "E": 40, "F": 140, "G": 60, "H": 130, "J": 25, "K": "7/8\"x50", "T": 16},
}

# 反向查表: member -> M37 資料
M37_BY_MEMBER = {}
for _k, _v in M37_TABLE.items():
    _member_key = _v["member"]
    M37_BY_MEMBER[_member_key] = {**_v, "lgp_type": _k}


def get_m37_data(member: str) -> dict | None:
    """
    用 member 尺寸查 M37 Lug Plate 資料
    member: 如 "L50*50*6", "C150*75*9"
    回傳含 lgp_type 的完整 dict, 查無回傳 None
    """
    key = member.replace("x", "*").replace("X", "*")
    # 去掉可能的前綴 L/C/H
    if key.startswith(("L", "C", "H")) and key[1].isdigit():
        pass  # 已經是純尺寸含前綴
    return M37_BY_MEMBER.get(key)


def get_m37_by_type(lgp_type: str) -> dict | None:
    """
    用 LGP-F-x 代碼直接查
    """
    return M37_TABLE.get(lgp_type)
