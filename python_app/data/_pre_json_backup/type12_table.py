"""
Type 12 查表 - 焊接式雙板夾持 Dummy Pipe 支撐
Rigid welded dummy pipe support with plate reinforcement

PDF 表格 (9 entries):
  A(line_size)  B(support_pipe)  C     P(plate)
  2"            1 1/2" SCH.80    70    150×75×9
  3"            2"     SCH.40    80    150×75×9
  4"            3"     SCH.40    110   150×75×9
  6"            4"     SCH.40    140   150×75×9
  8"            6"     SCH.40    190   250×75×12
  10"           8"     SCH.40    240   250×105×12
  12"           8"     SCH.40    240   350×105×12
  14"           10"    SCH.40    290   350×105×12
  16"           10"    SCH.40    290   350×105×12
"""

TYPE12_TABLE = {
    2:  {"pipe_size_b": 1.5, "pipe_sch": "SCH.80", "C": 70,  "plate_len": 150, "plate_wid": 75,  "plate_t": 9},
    3:  {"pipe_size_b": 2,   "pipe_sch": "SCH.40", "C": 80,  "plate_len": 150, "plate_wid": 75,  "plate_t": 9},
    4:  {"pipe_size_b": 3,   "pipe_sch": "SCH.40", "C": 110, "plate_len": 150, "plate_wid": 75,  "plate_t": 9},
    6:  {"pipe_size_b": 4,   "pipe_sch": "SCH.40", "C": 140, "plate_len": 150, "plate_wid": 75,  "plate_t": 9},
    8:  {"pipe_size_b": 6,   "pipe_sch": "SCH.40", "C": 190, "plate_len": 250, "plate_wid": 75,  "plate_t": 12},
    10: {"pipe_size_b": 8,   "pipe_sch": "SCH.40", "C": 240, "plate_len": 250, "plate_wid": 105, "plate_t": 12},
    12: {"pipe_size_b": 8,   "pipe_sch": "SCH.40", "C": 240, "plate_len": 350, "plate_wid": 105, "plate_t": 12},
    14: {"pipe_size_b": 10,  "pipe_sch": "SCH.40", "C": 290, "plate_len": 350, "plate_wid": 105, "plate_t": 12},
    16: {"pipe_size_b": 10,  "pipe_sch": "SCH.40", "C": 290, "plate_len": 350, "plate_wid": 105, "plate_t": 12},
}


def get_type12_data(line_size: int) -> dict | None:
    """依 line size (inch) 查表，回傳 dict 或 None"""
    return TYPE12_TABLE.get(line_size)
