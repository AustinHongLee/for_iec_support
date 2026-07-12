"""
M-45 Expansion Bolt (膨脹螺栓) 資料表
來源: M-45 圖紙 (m_45.md)

用途: Type 41 牆面錨定支撐的 Expansion Bolt 規格查詢
NOTE: R.C. strength 210 kg/cm², safety factor = 5
"""

M45_TABLE = {
    "EB-1/4": {
        "type": "EB-1/4", "dia": '1/4"', "L": 76,
        "thread_length": 19, "drill_size": 'Ø1/4" × 32L',
        "tensile_kg": 693, "shear_kg": 892,
    },
    "EB-3/8": {
        "type": "EB-3/8", "dia": '3/8"', "L": 89,
        "thread_length": 32, "drill_size": 'Ø3/8" × 38L',
        "tensile_kg": 1602, "shear_kg": 1905,
    },
    "EB-1/2": {
        "type": "EB-1/2", "dia": '1/2"', "L": 114,
        "thread_length": 35, "drill_size": 'Ø1/2" × 57L',
        "tensile_kg": 2312, "shear_kg": 3300,
    },
    "EB-5/8": {
        "type": "EB-5/8", "dia": '5/8"', "L": 127,
        "thread_length": 38, "drill_size": 'Ø5/8" × 70L',
        "tensile_kg": 3083, "shear_kg": 4503,
    },
    "EB-3/4": {
        "type": "EB-3/4", "dia": '3/4"', "L": 152,
        "thread_length": 38, "drill_size": 'Ø3/4" × 83L',
        "tensile_kg": 4417, "shear_kg": 6322,
    },
    "EB-7/8": {
        "type": "EB-7/8", "dia": '7/8"', "L": 178,
        "thread_length": 57, "drill_size": 'Ø7/8" × 95L',
        "tensile_kg": 5629, "shear_kg": 8400,
    },
}


def get_m45_by_dia(dia: str) -> dict | None:
    """依螺栓直徑查詢, dia 如 '1/2"' 或 '3/4"'"""
    key = f"EB-{dia.rstrip(chr(34))}"  # 去掉可能多餘的引號
    if not key.endswith('"'):
        key += '"'
    # 嘗試直接 key
    for k, v in M45_TABLE.items():
        if v["dia"] == dia or k == f"EB-{dia}" or k == f'EB-{dia.strip(chr(34))}':
            return v
    return None


def get_m45_by_type(eb_type: str) -> dict | None:
    """依 EB 型號查詢, 如 'EB-1/2'"""
    return M45_TABLE.get(eb_type)
