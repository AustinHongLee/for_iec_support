"""
Type 08 查表資料 - 立柱式托板支撐 + 滑動 + Stopper
PDF: 08.pdf

lookup key = pipe size (A)
  pipe_sch: pipe schedule
  K: stopper 寬 (mm)
  M: stopper 高 (mm)
  B: top plate 邊長 (mm)
  member_n: channel 規格
"""

TYPE08_TABLE = {
    2: {"pipe_sch": "SCH.40", "K": 70,  "M": 160, "B": 80,  "member_n": "C100*50*5"},
    3: {"pipe_sch": "SCH.40", "K": 70,  "M": 160, "B": 110, "member_n": "C100*50*5"},
    4: {"pipe_sch": "SCH.40", "K": 85,  "M": 185, "B": 135, "member_n": "C125*65*6"},
}


def get_type08_data(pipe_size: int) -> dict | None:
    return TYPE08_TABLE.get(pipe_size)
