"""
Type 20 查詢表 - 長孔滑動底座支撐 (Slotted Clamp Base Support)
來源: TYPE-20 圖面表格

格式: 20-{M}-{HH}{Fig}
  例: 20-L50-05A → Member=L50X50X6, H=500mm, Fig.A

Note 1: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
Note 2: STANDARD U-BOLT (NOT FURNISHED)
Note 3: DETAIL SEE D-80 (NOT FURNISHED)

組件 (1 項):
  1. MEMBER "M": Angle 或 Channel，長度 H，A36/SS400
"""

# line_size → Z (mm): slot hole 配置區長度
# (Z 用於長孔設計，不影響重量計算，但記錄供參考)
Z_TABLE = {
    2:  76,
    3:  104,
    4:  130,
    6:  184,
    8:  235,
    10: 286,
    12: 340,
}

# member 代碼 → H_MAX (mm)
# 不同 member 可承受的最大 H 高度
MEMBER_H_MAX = {
    "L50":  1500,
    "L65":  1500,
    "L75":  2000,
    "C100": 3000,
}
