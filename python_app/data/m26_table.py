"""
M-26 U-Bolt 資料表
來源: M-26 圖紙

用途:
- Type 58 等 U-bolt 類支撐
- bare pipe clamp / saddle 類型
"""
from .component_size_utils import normalize_fractional_size

M26_TABLE = {
    '1/4"': {"type": "UB-1/4B", "line_size": '1/4"', "rod_size_a": '1/4"', "B": 18, "C": 24, "D": 36, "E": 39, "load_650f_kg": 220, "load_750f_kg": 220},
    '1/2"': {"type": "UB-1/2B", "line_size": '1/2"', "rod_size_a": '1/4"', "B": 24, "C": 30, "D": 40, "E": 43, "load_650f_kg": 220, "load_750f_kg": 200},
    '3/4"': {"type": "UB-3/4B", "line_size": '3/4"', "rod_size_a": '1/4"', "B": 29, "C": 35, "D": 40, "E": 45, "load_650f_kg": 220, "load_750f_kg": 200},
    '1"': {"type": "UB-1B", "line_size": '1"', "rod_size_a": '1/4"', "B": 35, "C": 41, "D": 40, "E": 49, "load_650f_kg": 220, "load_750f_kg": 200},
    '1 1/4"': {"type": "UB-1 1/4B", "line_size": '1 1/4"', "rod_size_a": '3/8"', "B": 43, "C": 52, "D": 58, "E": 65, "load_650f_kg": 555, "load_750f_kg": 495},
    '1 1/2"': {"type": "UB-1 1/2B", "line_size": '1 1/2"', "rod_size_a": '3/8"', "B": 51, "C": 60, "D": 58, "E": 68, "load_650f_kg": 555, "load_750f_kg": 495},
    '2"': {"type": "UB-2B", "line_size": '2"', "rod_size_a": '3/8"', "B": 62, "C": 71, "D": 58, "E": 74, "load_650f_kg": 555, "load_750f_kg": 495},
    '2 1/2"': {"type": "UB-2 1/2B", "line_size": '2 1/2"', "rod_size_a": '1/2"', "B": 75, "C": 87, "D": 64, "E": 85, "load_650f_kg": 1025, "load_750f_kg": 920},
    '3"': {"type": "UB-3B", "line_size": '3"', "rod_size_a": '1/2"', "B": 91, "C": 103, "D": 64, "E": 93, "load_650f_kg": 1025, "load_750f_kg": 920},
    '3 1/2"': {"type": "UB-3 1/2B", "line_size": '3 1/2"', "rod_size_a": '1/2"', "B": 103, "C": 116, "D": 64, "E": 99, "load_650f_kg": 1025, "load_750f_kg": 920},
    '4"': {"type": "UB-4B", "line_size": '4"', "rod_size_a": '1/2"', "B": 116, "C": 129, "D": 67, "E": 108, "load_650f_kg": 1025, "load_750f_kg": 920},
    '5"': {"type": "UB-5B", "line_size": '5"', "rod_size_a": '1/2"', "B": 143, "C": 156, "D": 67, "E": 122, "load_650f_kg": 1025, "load_750f_kg": 920},
    '6"': {"type": "UB-6B", "line_size": '6"', "rod_size_a": '5/8"', "B": 171, "C": 187, "D": 79, "E": 143, "load_650f_kg": 1645, "load_750f_kg": 1470},
    '8"': {"type": "UB-8B", "line_size": '8"', "rod_size_a": '5/8"', "B": 222, "C": 238, "D": 79, "E": 169, "load_650f_kg": 1645, "load_750f_kg": 1470},
    '10"': {"type": "UB-10B", "line_size": '10"', "rod_size_a": '3/4"', "B": 276, "C": 295, "D": 102, "E": 213, "load_650f_kg": 2460, "load_750f_kg": 2155},
    '12"': {"type": "UB-12B", "line_size": '12"', "rod_size_a": '7/8"', "B": 327, "C": 349, "D": 111, "E": 245, "load_650f_kg": 3425, "load_750f_kg": 3060},
    '14"': {"type": "UB-14B", "line_size": '14"', "rod_size_a": '7/8"', "B": 359, "C": 381, "D": 111, "E": 261, "load_650f_kg": 3425, "load_750f_kg": 3060},
    '16"': {"type": "UB-16B", "line_size": '16"', "rod_size_a": '7/8"', "B": 410, "C": 432, "D": 111, "E": 286, "load_650f_kg": 3425, "load_750f_kg": 3060},
    '18"': {"type": "UB-18B", "line_size": '18"', "rod_size_a": '1"', "B": 460, "C": 486, "D": 117, "E": 316, "load_650f_kg": 4500, "load_750f_kg": 4015},
    '20"': {"type": "UB-20B", "line_size": '20"', "rod_size_a": '1"', "B": 511, "C": 537, "D": 121, "E": 345, "load_650f_kg": 4500, "load_750f_kg": 4015},
    '24"': {"type": "UB-24B", "line_size": '24"', "rod_size_a": '1"', "B": 613, "C": 638, "D": 121, "E": 396, "load_650f_kg": 4500, "load_750f_kg": 4015},
    '30"': {"type": "UB-30B", "line_size": '30"', "rod_size_a": '1"', "B": 765, "C": 791, "D": 121, "E": 472, "load_650f_kg": 4500, "load_750f_kg": 4015},
}


def get_m26_by_line_size(line_size) -> dict | None:
    """依 line size 查 U-bolt 規格。"""
    key = normalize_fractional_size(line_size)
    key = key.replace("-", " ")
    return M26_TABLE.get(key)


def get_m26_by_type(ub_type: str) -> dict | None:
    """依 type 名稱查詢，例如 UB-2B。"""
    for row in M26_TABLE.values():
        if row["type"] == ub_type:
            return row
    return None
