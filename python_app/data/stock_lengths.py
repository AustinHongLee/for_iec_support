"""
標準原料長度與下料參數

管材 / 角鋼 / 型鋼標準進貨長度為 6M。
下料時需考慮鋸口損耗、原料頭尾切除、量測容差等。
"""

# ── 標準原料長度 (mm) ──
STOCK_LENGTH_PIPE = 6000       # 管材
STOCK_LENGTH_STEEL = 6000      # 角鋼 / 型鋼 (L, H, C)

# ── 原料頭尾切除 (mm) ──
# 6M 原料兩端可能有毛邊、壓痕、鏽蝕，需各切掉一段
STOCK_END_TRIM = 25            # 每端 25mm → 有效長度 = stock - 2*25

# ── 每刀損耗 (mm) ──
KERF_WIDTH = 3                 # 鋸口 (鋸床 ~3mm, 砂輪 ~3-4mm, 火焰 ~5mm)

# ── 量測容差 (mm) ──
# 每段需求長度額外加上的安全餘量
LENGTH_TOLERANCE = 2

# ── 最小可用餘料 (mm) ──
# 切完剩餘長度 < 此值者視為廢料，不再使用
MIN_USABLE_REMNANT = 100

# ── 鋼板標準板材尺寸 (mm) ──
# 4' × 8' = 1219 × 2438
PLATE_STANDARD_SIZES = [
    (1219, 2438),   # 4' × 8'
    (1524, 3048),   # 5' × 10'
]


def get_effective_stock_length(stock_type: str = "pipe") -> float:
    """取得有效原料長度 (扣除頭尾切除量)"""
    if stock_type == "pipe":
        return STOCK_LENGTH_PIPE - 2 * STOCK_END_TRIM
    elif stock_type == "steel":
        return STOCK_LENGTH_STEEL - 2 * STOCK_END_TRIM
    return 6000 - 2 * STOCK_END_TRIM


def get_cut_piece_length(demand_length: float) -> float:
    """計算每段實際佔用長度 (需求 + kerf + tolerance)

    注意: 最後一段不需要 kerf，但 FFD 演算法在排列時
    統一加 kerf 更簡單且保守。
    """
    return demand_length + KERF_WIDTH + LENGTH_TOLERANCE
