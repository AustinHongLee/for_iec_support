"""
Type 44 查表資料 — 曲面設備直接斜撐支撐 (D-53)
無 Trunnion、無 Lug Plate、僅 8"~14" 管徑
H 公式: H = P - √(R² - Q²)
"""

# 管徑 → Q (mm)
TYPE44_PIPE_Q = {
    8:  113,
    10: 140,
    12: 165,
    14: 181,
}

# 斜撐資料 (H >= 1200 時才安裝)
TYPE44_BRACE = {
    "A": {"vertical": 450, "horizontal": 780, "length": 1016},  # θ=30°
    "B": {"vertical": 780, "horizontal": 780, "length": 1203},  # θ=45°
}
TYPE44_BRACE_H_MIN = 1200  # H >= 此值才安裝斜撐

# Member 選型: C100/C125/C150 (3 種)
TYPE44_MEMBERS = ["C100", "C125", "C150"]


def get_type44_q(line_size: float) -> int | None:
    """查 Q 值 (管徑偏移)"""
    return TYPE44_PIPE_Q.get(int(line_size))


def get_type44_brace(fig: str) -> dict | None:
    """查斜撐資料, fig = 'A' (30°) 或 'B' (45°)"""
    return TYPE44_BRACE.get(fig)
