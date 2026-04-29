"""
Type 48 查表資料 — Drain Hub 偏移底座支撐 (D-59)
極簡支撐: 1 塊 plate + 焊接, 100mm 偏移
管徑 1/2"~6", plate 固定 150×100, 厚度 6 或 9mm
"""

TYPE48_TABLE = {
    0.5:  {"plate_size": "150*100*6", "plate_a": 150, "plate_b": 100, "plate_t": 6},
    0.75: {"plate_size": "150*100*6", "plate_a": 150, "plate_b": 100, "plate_t": 6},
    1:    {"plate_size": "150*100*6", "plate_a": 150, "plate_b": 100, "plate_t": 6},
    1.5:  {"plate_size": "150*100*6", "plate_a": 150, "plate_b": 100, "plate_t": 6},
    2:    {"plate_size": "150*100*6", "plate_a": 150, "plate_b": 100, "plate_t": 6},
    3:    {"plate_size": "150*100*9", "plate_a": 150, "plate_b": 100, "plate_t": 9},
    4:    {"plate_size": "150*100*9", "plate_a": 150, "plate_b": 100, "plate_t": 9},
    6:    {"plate_size": "150*100*9", "plate_a": 150, "plate_b": 100, "plate_t": 9},
}

# 材質符號 (TABLE "B")
TYPE48_MATERIAL_SYMBOL = {
    "CS": "",      # Carbon Steel → NONE
    "AS": "(A)",   # Alloy Steel
    "SS": "(B)",   # Stainless Steel — 注意是 (B) 不是 (S)
}


def get_type48_data(line_size: float) -> dict | None:
    """依管徑查 plate 規格"""
    return TYPE48_TABLE.get(line_size)
