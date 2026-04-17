"""
Type 11 查表資料 - 彈簧可變載支撐 (Spring Variable Support)
PDF: 11.pdf

lookup key = line_size (A) in inches
  L: dummy pipe spacing (mm), 基於 long radius elbow
  spring_mark: 彈簧標記 (SPR12 / SPR14)
  spring_wire: 彈簧線徑 (mm)
  spring_id: 彈簧內徑 (mm)
  spring_k: 彈簧常數 (kg/mm)
  spring_free_len: 彈簧自由長 (mm)
  spring_max_defl: 最大建議撓度 (mm)
"""

TYPE11_TABLE = {
    2:  {"L": 71,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    3:  {"L": 81,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    4:  {"L": 97,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    6:  {"L": 129, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
    8:  {"L": 162, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
    10: {"L": 195, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
}


def get_type11_data(line_size: int) -> dict | None:
    return TYPE11_TABLE.get(line_size)
