"""
Type 09 查表資料 - 可調式螺桿支撐 (Threaded Adjustable Support)
PDF: 09.pdf

lookup key = line size (A)
  support_pipe: 支撐管規格 (都是 2")
  pipe_sch: pipe schedule
  L: dummy pipe spacing (mm), 基於 long radius elbow
"""

TYPE09_TABLE = {
    2: {"support_pipe": 2, "pipe_sch": "SCH.80", "L": 106},
    3: {"support_pipe": 2, "pipe_sch": "SCH.40", "L": 93},
    4: {"support_pipe": 2, "pipe_sch": "SCH.40", "L": 106},
}


def get_type09_data(line_size: int) -> dict | None:
    return TYPE09_TABLE.get(line_size)
