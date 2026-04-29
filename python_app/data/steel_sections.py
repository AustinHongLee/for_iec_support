"""
鋼材查詢表 - 對應 VBA 中的 Angle/Channel/HBeam Weight Table
key = 尺寸字串, value = 每米重量 (kg/m)
"""

# 角鋼 (Angle) - "寬*寬*厚" -> kg/m
ANGLE_WEIGHT = {
    "40*40*5": 2.96,
    "50*50*6": 4.43,
    "65*65*6": 5.91,
    "75*75*9": 9.96,
    "80*80*8": 9.66,
    "90*90*9": 12.2,
    "100*100*10": 15.0,
    "110*110*10": 16.6,
    "120*120*11": 19.9,
    "130*130*12": 23.6,
    "140*140*13": 27.5,
    "150*150*14": 31.8,
    "160*160*15": 36.3,
    "180*180*16": 43.6,
}

# 槽鋼 (Channel) - "寬*翼*厚" -> kg/m
CHANNEL_WEIGHT = {
    "100*50*5": 9.36,
    "125*65*6": 13.4,
    "150*75*9": 23.8,
    "180*75*7": 21.0,
    "200*80*7.5": 24.6,
    "200*90*8": 27.2,
    "250*90*8": 32.0,
    "300*100*8.5": 37.3,
    "350*100*9": 41.4,
    "400*150*10": 56.1,
    "450*150*11": 62.0,
    "500*200*12": 76.0,
}

# H型鋼 (H Beam) - "高*寬*腹板厚" -> kg/m
HBEAM_WEIGHT = {
    "100*100*6": 17.2,
    "125*125*6.5": 23.8,
    "150*150*7": 31.5,
    "150*150*10": 37.3,
    "194*150*6": 30.6,
    "200*100*5.5": 21.3,
    "200*200*8": 49.9,
    "250*125*6": 29.6,
    "250*250*9": 72.4,
    "300*150*6.5": 37.3,
    "350*175*7": 49.6,
    "400*200*8": 66.0,
    "450*200*9": 76.0,
    "500*250*10": 89.6,
    "550*300*11": 106.0,
    "600*300*12": 120.0,
}

# 型鋼代號 -> (完整尺寸, 類型) 對照表
SECTION_CODE_MAP = {
    # Angle
    "L50":  ("L50*50*6", "Angle"),
    "L65":  ("L65*65*6", "Angle"),
    "L75":  ("L75*75*9", "Angle"),
    "L80":  ("L80*80*8", "Angle"),
    "L90":  ("L90*90*9", "Angle"),
    "L100": ("L100*100*10", "Angle"),
    "L110": ("L110*110*10", "Angle"),
    "L120": ("L120*120*11", "Angle"),
    "L130": ("L130*130*12", "Angle"),
    "L140": ("L140*140*13", "Angle"),
    "L150": ("L150*150*14", "Angle"),
    "L160": ("L160*160*15", "Angle"),
    "L180": ("L180*180*16", "Angle"),
    # Channel
    "C100": ("C100*50*5", "Channel"),
    "C125": ("C125*65*6", "Channel"),
    "C150": ("C150*75*9", "Channel"),
    "C180": ("C180*75*7", "Channel"),
    "C200": ("C200*80*7.5", "Channel"),
    "C250": ("C250*90*8", "Channel"),
    "C300": ("C300*100*8.5", "Channel"),
    "C350": ("C350*100*9", "Channel"),
    "C400": ("C400*150*10", "Channel"),
    "C450": ("C450*150*11", "Channel"),
    "C500": ("C500*200*12", "Channel"),
    # H Beam
    "H100": ("H100*100*6", "H Beam"),
    "H125": ("H125*125*6.5", "H Beam"),
    "H150": ("H150*150*10", "H Beam"),  # 預設用 10mm, Type_37 用 7mm
    "H250": ("H250*125*6", "H Beam"),
    "H300": ("H300*150*6.5", "H Beam"),
    "H350": ("H350*175*7", "H Beam"),
    "H400": ("H400*200*8", "H Beam"),
    "H450": ("H450*200*9", "H Beam"),
    "H500": ("H500*250*10", "H Beam"),
    "H550": ("H550*300*11", "H Beam"),
    "H600": ("H600*300*12", "H Beam"),
}


def get_section_details(code: str, type_first: str = "") -> dict:
    """
    依代號取得型鋼資訊
    回傳 {"size": str, "type": str} 或 None
    """
    if code not in SECTION_CODE_MAP:
        return None
    size, stype = SECTION_CODE_MAP[code]
    # H150 特殊處理: Type_37 用 7mm
    if code == "H150" and type_first:
        size = "H150*150*7"
    return {"size": size, "type": stype}


def get_section_weight(section_type: str, dim: str) -> float:
    """取得型鋼每米重量 (kg/m)"""
    table = {
        "Angle": ANGLE_WEIGHT,
        "Channel": CHANNEL_WEIGHT,
        "H Beam": HBEAM_WEIGHT,
    }
    if section_type not in table:
        raise ValueError(f"未知型鋼類型: {section_type}")
    wt_table = table[section_type]
    if dim not in wt_table:
        raise ValueError(f"{section_type} 尺寸 {dim} 不在查詢表中")
    return wt_table[dim]
