"""
Type 13 查表 - Clamp 式雙板夾持 Dummy Pipe 支撐
Clamped (non-welded) dummy pipe support with plate reinforcement

表格與 Type 12 完全相同:
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
from data.type12_table import TYPE12_TABLE

# Type 13 幾何與 Type 12 完全一致，直接重用
TYPE13_TABLE = TYPE12_TABLE


def get_type13_data(line_size: int) -> dict | None:
    """依 line size (inch) 查表，回傳 dict 或 None"""
    return TYPE13_TABLE.get(line_size)
