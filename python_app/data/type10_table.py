"""
Type 10 查表資料 - 可調式 Dummy Pipe 支撐 (Four-Bolt Adjustable Support)
PDF: 10.pdf

lookup key = line_size (A) in inches
  pipe_size_b: supporting pipe size (inches, float)
  pipe_sch: pipe schedule
  L: dummy pipe spacing (mm), 基於 long radius elbow
  plate_t: Plate F 厚度 (mm)
  plate_w: Plate F 邊長 (mm) — 正方形
  bolt_spec: Adjustable Bolt 規格 (J × L1)
  W: bolt 孔距 (mm)
  d_phi: bolt 孔徑 (mm)
"""

TYPE10_TABLE = {
    1.5:  {"pipe_size_b": 1.5, "pipe_sch": "SCH.80",  "L": 81,   "plate_t": 9,  "plate_w": 170, "bolt_spec": "M12*160L", "W": 100, "d_phi": 15},
    2:    {"pipe_size_b": 1.5, "pipe_sch": "SCH.80",  "L": 71,   "plate_t": 9,  "plate_w": 170, "bolt_spec": "M12*160L", "W": 100, "d_phi": 15},
    2.5:  {"pipe_size_b": 2,   "pipe_sch": "SCH.40",  "L": 91,   "plate_t": 9,  "plate_w": 200, "bolt_spec": "M12*160L", "W": 130, "d_phi": 15},
    3:    {"pipe_size_b": 2,   "pipe_sch": "SCH.40",  "L": 93,   "plate_t": 9,  "plate_w": 200, "bolt_spec": "M12*160L", "W": 130, "d_phi": 15},
    4:    {"pipe_size_b": 3,   "pipe_sch": "SCH.40",  "L": 138,  "plate_t": 12, "plate_w": 230, "bolt_spec": "M16*180L", "W": 160, "d_phi": 19},
    5:    {"pipe_size_b": 4,   "pipe_sch": "SCH.40",  "L": 178,  "plate_t": 12, "plate_w": 260, "bolt_spec": "M16*180L", "W": 190, "d_phi": 19},
    6:    {"pipe_size_b": 4,   "pipe_sch": "SCH.40",  "L": 186,  "plate_t": 12, "plate_w": 260, "bolt_spec": "M16*180L", "W": 190, "d_phi": 19},
    8:    {"pipe_size_b": 6,   "pipe_sch": "SCH.40",  "L": 272,  "plate_t": 12, "plate_w": 330, "bolt_spec": "M16*180L", "W": 260, "d_phi": 19},
    10:   {"pipe_size_b": 6,   "pipe_sch": "SCH.40",  "L": 291,  "plate_t": 12, "plate_w": 330, "bolt_spec": "M16*180L", "W": 260, "d_phi": 19},
    12:   {"pipe_size_b": 8,   "pipe_sch": "SCH.40",  "L": 370,  "plate_t": 16, "plate_w": 400, "bolt_spec": "M16*180L", "W": 330, "d_phi": 19},
    14:   {"pipe_size_b": 8,   "pipe_sch": "SCH.40",  "L": 407,  "plate_t": 16, "plate_w": 400, "bolt_spec": "M16*180L", "W": 330, "d_phi": 19},
    16:   {"pipe_size_b": 8,   "pipe_sch": "SCH.40",  "L": 434,  "plate_t": 16, "plate_w": 400, "bolt_spec": "M16*180L", "W": 330, "d_phi": 19},
    18:   {"pipe_size_b": 10,  "pipe_sch": "SCH.40",  "L": 515,  "plate_t": 16, "plate_w": 440, "bolt_spec": "M16*180L", "W": 370, "d_phi": 19},
    20:   {"pipe_size_b": 10,  "pipe_sch": "SCH.40",  "L": 542,  "plate_t": 16, "plate_w": 440, "bolt_spec": "M16*180L", "W": 370, "d_phi": 19},
    28:   {"pipe_size_b": 18,  "pipe_sch": "STD.WT",  "L": 835,  "plate_t": 19, "plate_w": 520, "bolt_spec": "M20*180L", "W": 450, "d_phi": 23},
    32:   {"pipe_size_b": 18,  "pipe_sch": "STD.WT",  "L": 886,  "plate_t": 19, "plate_w": 520, "bolt_spec": "M20*180L", "W": 450, "d_phi": 23},
    36:   {"pipe_size_b": 24,  "pipe_sch": "STD.WT",  "L": 1098, "plate_t": 19, "plate_w": 670, "bolt_spec": "M20*180L", "W": 600, "d_phi": 23},
    44:   {"pipe_size_b": 24,  "pipe_sch": "STD.WT",  "L": 1200, "plate_t": 19, "plate_w": 670, "bolt_spec": "M20*180L", "W": 600, "d_phi": 23},
}


def get_type10_data(line_size: float) -> dict | None:
    return TYPE10_TABLE.get(line_size)
