"""
Type 21 查詢表 - 側掛式懸臂 U-bolt 支撐 (Cantilever Clamp Support)
來源: TYPE-21 圖面表格

格式: 21-{M}-{HH}{Fig}        (Fig = A/B)
      21-{M}-{HH}{Fig}-{LL}   (Fig = C, LL=L/100)
  例: 21-L50-05A     → Member=L50X50X6, H=500, L=300 (Fig.A)
      21-L50-05B     → Member=L50X50X6, H=500, L=500 (Fig.B)
      21-L50-05C-07  → Member=L50X50X6, H=500, L=700 (Fig.C)

Note 1: U-BOLT (D-68) NOT FURNISHED
Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.

構件 (2 項):
  1. MEMBER "M" (H): 垂直段, 長度 H
  2. MEMBER "M" (L): 水平段, 長度 L (300/500/自定)
"""

# member 代碼 → H_MAX (mm)
MEMBER_H_MAX = {
    "L50":  1000,
    "L65":  1500,
    "L75":  2000,
}

# Fig → 固定 L 值 (mm), None 表示需從第四段取得
FIG_L_MAP = {
    "A": 300,
    "B": 500,
    "C": None,   # from 4th segment
}
