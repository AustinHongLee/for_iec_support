"""
Type 23 資料表 - 頂掛式懸臂支撐 (Top-mounted Cantilever Support)
從上方既有結構懸掛的支架

H_MAX 上限 (mm):
  L50=500, L65=1500
  L75/L100/C100/C150/H100/H150=2000

FIG_L_MAP (mm):
  A=300, B=500, C=自訂
"""

MEMBER_H_MAX: dict[str, int] = {
    "L50":  500,
    "L65":  1500,
    "L75":  2000,
    "L100": 2000,
    "C100": 2000,
    "C150": 2000,
    "H100": 2000,
    "H150": 2000,
}

FIG_L_MAP: dict[str, int | None] = {
    "A": 300,
    "B": 500,
    "C": None,  # 由第四段指定
}
