"""
Type 19 查詢表 - 斜撐式 (Lateral Bracing) 支撐
來源: TYPE-19 圖面表格

格式: 19-{A}B (只有兩段, 無 H/L 段)

組件: MEMBER "M" with "L" LENGTH
  - 1"~6" 使用 L-Angle
  - 8"~12" 使用 CUT FROM H194X150X6X9

Note 1: DIMENSION "L" SHALL BE CUT TO SUIT IN FIELD.
"""

# pipe_size (float) -> {member, L, section_type, dim}
#   member: 型鋼規格標記
#   L: 標準長度 (mm)
#   section_type: "Angle" | "H Beam" (對應 steel_sections.py)
#   dim: 查重量用的 key (對應 steel_sections.py 表)
TYPE19_TABLE = {
    1:    {"member": "L40X40X5",      "L": 600,  "section_type": "Angle",  "dim": "40*40*5"},
    1.5:  {"member": "L40X40X5",      "L": 600,  "section_type": "Angle",  "dim": "40*40*5"},
    2:    {"member": "L50X50X6",      "L": 600,  "section_type": "Angle",  "dim": "50*50*6"},
    3:    {"member": "L50X50X6",      "L": 600,  "section_type": "Angle",  "dim": "50*50*6"},
    4:    {"member": "L75X75X9",      "L": 600,  "section_type": "Angle",  "dim": "75*75*9"},
    6:    {"member": "L75X75X9",      "L": 1200, "section_type": "Angle",  "dim": "75*75*9"},
    8:    {"member": "H194X150X6X9",  "L": 1200, "section_type": "H Beam", "dim": "194*150*6"},
    10:   {"member": "H194X150X6X9",  "L": 1200, "section_type": "H Beam", "dim": "194*150*6"},
    12:   {"member": "H194X150X6X9",  "L": 1200, "section_type": "H Beam", "dim": "194*150*6"},
}


def get_type19_data(pipe_size: float) -> dict | None:
    """查表取得 Type 19 資料, 回傳 dict 或 None"""
    return TYPE19_TABLE.get(pipe_size)
