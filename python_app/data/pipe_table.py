"""
管道查詢表 - 對應 VBA 中的 Pipe_Table 工作表
包含管徑(inch)、外徑(mm)、各 Schedule 壁厚(mm)
"""

# 管道外徑 (Nominal Pipe Size -> OD in mm)
PIPE_OD = {
    0.5: 21.3, 0.75: 26.7, 1: 33.4, 1.5: 48.3, 2: 60.3, 2.5: 73.0,
    3: 88.9, 4: 114.3, 5: 141.3, 6: 168.3, 8: 219.1, 10: 273.0,
    12: 323.8, 14: 355.6, 16: 406.4, 18: 457.2, 20: 508.0,
    22: 558.8, 24: 609.6, 26: 660.4, 28: 711.2, 30: 762.0,
    32: 812.8, 34: 863.6, 36: 914.4, 40: 1016.0, 42: 1066.8,
}

# 壁厚表 (Pipe Size -> {Schedule: thickness_mm})
# 10S, 40S, 80S, STD.WT 等
PIPE_THICKNESS = {
    0.5:  {"10S": 1.24, "40S": 2.77, "80S": 3.73, "STD.WT": 2.77},
    0.75: {"10S": 1.65, "40S": 2.87, "80S": 3.91, "STD.WT": 2.87},
    1:    {"10S": 1.65, "40S": 3.38, "80S": 4.55, "STD.WT": 3.38},
    1.5:  {"10S": 2.11, "40S": 3.68, "80S": 5.08, "STD.WT": 3.68},
    2:    {"10S": 2.11, "40S": 3.91, "80S": 5.54, "STD.WT": 3.91},
    2.5:  {"10S": 2.11, "40S": 5.16, "80S": 7.01, "STD.WT": 5.16},
    3:    {"10S": 2.11, "40S": 5.49, "80S": 7.62, "STD.WT": 5.49},
    4:    {"10S": 2.11, "40S": 6.02, "80S": 8.56, "STD.WT": 6.02},
    5:    {"10S": 2.77, "40S": 6.55, "80S": 9.53, "STD.WT": 6.55},
    6:    {"10S": 2.77, "40S": 7.11, "80S": 10.97, "STD.WT": 7.11},
    8:    {"10S": 2.77, "40S": 8.18, "80S": 12.70, "STD.WT": 8.18},
    10:   {"10S": 3.40, "40S": 9.27, "80S": 15.09, "STD.WT": 9.27},
    12:   {"10S": 3.96, "40S": 10.31, "80S": 17.48, "STD.WT": 9.53},
    14:   {"10S": 3.96, "40S": 11.13, "80S": 19.05, "STD.WT": 9.53},
    16:   {"10S": 3.96, "40S": 12.70, "80S": 21.44, "STD.WT": 9.53},
    18:   {"10S": 3.96, "40S": 14.27, "80S": 23.83, "STD.WT": 9.53},
    20:   {"10S": 3.96, "40S": 15.09, "80S": 26.19, "STD.WT": 9.53},
    24:   {"10S": 3.96, "40S": 17.48, "80S": 30.96, "STD.WT": 9.53},
    26:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    28:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    30:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    32:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    34:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    36:   {"10S": 3.96, "40S": 12.70, "STD.WT": 9.53},
    40:   {"10S": 3.96, "STD.WT": 9.53},
    42:   {"10S": 3.96, "STD.WT": 9.53},
}


def get_pipe_od(pipe_size: float) -> float:
    """取得管道外徑 (mm)"""
    if pipe_size not in PIPE_OD:
        raise ValueError(f"管徑 {pipe_size} 不在查詢表中")
    return PIPE_OD[pipe_size]


def get_pipe_thickness(pipe_size: float, schedule: str) -> float:
    """取得管道壁厚 (mm)，schedule 如 '10S', '40S', '80S', 'STD.WT'"""
    if pipe_size not in PIPE_THICKNESS:
        raise ValueError(f"管徑 {pipe_size} 不在查詢表中")
    sch_map = PIPE_THICKNESS[pipe_size]
    if schedule not in sch_map:
        raise ValueError(f"管徑 {pipe_size} 無 Schedule {schedule}")
    return sch_map[schedule]


def calculate_pipe_weight(od_mm: float, thickness_mm: float) -> float:
    """計算管道每米重量 (kg/m)"""
    import math
    return round((od_mm - thickness_mm) * math.pi / 1000 * thickness_mm * 7.85, 2)


def get_pipe_details(pipe_size: float, schedule: str) -> dict:
    """
    取得管道完整資訊
    回傳 {"od_mm": float, "thickness_mm": float, "weight_per_m": float}
    """
    od = get_pipe_od(pipe_size)
    thk = get_pipe_thickness(pipe_size, schedule)
    wt = calculate_pipe_weight(od, thk)
    return {"od_mm": od, "thickness_mm": thk, "weight_per_m": wt}
