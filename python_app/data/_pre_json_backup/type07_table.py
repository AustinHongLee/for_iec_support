"""
Type 07 查表資料 - 滑動彎頭支撐
PDF: 07.pdf

lookup key = supported line size (A)
  pipe_b: dummy pipe 規格 (size + schedule)
  pipe_c: 支撐柱規格 (size + schedule)
  plate_e: 底板 (寬×高×厚)
  plate_f: 滑動板 (寬×高×厚)
  L: 基於 long radius elbow 的長度 (mm)
"""

TYPE07_TABLE = {
    2:  {"pipe_b": ("1-1/2", "SCH.80"),  "pipe_c": ("3",  "SCH.40"),  "plate_e": (200, 200, 9),  "plate_f": (200, 200, 9),  "L": 71},
    3:  {"pipe_b": ("2",     "SCH.40"),  "pipe_c": ("4",  "SCH.40"),  "plate_e": (200, 200, 9),  "plate_f": (250, 250, 9),  "L": 93},
    4:  {"pipe_b": ("3",     "SCH.40"),  "pipe_c": ("4",  "SCH.40"),  "plate_e": (200, 200, 9),  "plate_f": (250, 250, 9),  "L": 137},
    6:  {"pipe_b": ("4",     "SCH.40"),  "pipe_c": ("8",  "SCH.40"),  "plate_e": (250, 250, 9),  "plate_f": (300, 300, 12), "L": 186},
    8:  {"pipe_b": ("6",     "SCH.40"),  "pipe_c": ("12", "STD.WT"),  "plate_e": (250, 250, 9),  "plate_f": (400, 400, 16), "L": 271},
    10: {"pipe_b": ("8",     "SCH.40"),  "pipe_c": ("12", "STD.WT"),  "plate_e": (350, 350, 12), "plate_f": (400, 400, 16), "L": 353},
    12: {"pipe_b": ("8",     "SCH.40"),  "pipe_c": ("12", "STD.WT"),  "plate_e": (350, 350, 12), "plate_f": (400, 400, 16), "L": 370},
}


def get_type07_data(line_size: int) -> dict | None:
    return TYPE07_TABLE.get(line_size)
