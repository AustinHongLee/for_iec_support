"""
Type 22 查詢表 - 落地式懸臂 U-bolt 支撐 (Ground Cantilever Support)
來源: TYPE-22 圖面表格

格式: 22-{M}-{HH}{Fig}{M42}         (Fig = A/B)
      22-{M}-{HH}C{M42}-{LL}        (Fig = C, LL=L/100)
  例: 22-L50-05AL     → L50, H=500, Fig.A, M42=L
      22-L50-05CL-07  → L50, H=500, Fig.C, M42=L, L=700

Note 1: U-BOLT (D-68) NOT FURNISHED
Note 2: DIMENSION "H" SHALL BE CUT TO SUIT IN FIELD.
Note 3: H counted from lowest point of paving if no foundation.
Note 4: USE WITH M-42, TYPE L & P ONLY.

構件:
  1. MEMBER "M" (H段): 垂直, 長度 H
  2. MEMBER "M" (L段): 水平, 長度 L (300/500/自定)
  3. M42 下部構件 (letter L or P only)
"""

# member 代碼 → H_MAX (mm) — 比 Type 21 更保守
MEMBER_H_MAX = {
    "L50":  1000,
    "L65":  1000,
    "L75":  1500,
}

# Fig → 固定 L 值 (mm), None 表示需從下一段取得
FIG_L_MAP = {
    "A": 300,
    "B": 500,
    "C": None,   # from next segment
}

# 允許的 M42 下部構件字母
ALLOWED_M42_LETTERS = {"L", "P"}
