"""
M-21 Turnbuckle 資料表

說明:
- 目前先補 rod-size / load class / unit weight 等 component-level 欄位，
  供後續 hanger 類型正式接用。
"""
from .component_size_utils import normalize_fractional_size


M21_TABLE = {
    '3/8"':   {"designation": 'M-21 3/8"', "rod_size_a": '3/8"', "take_up_mm": 100, "unit_weight_kg": 0.50, "load_650f_kg": 270, "load_750f_kg": 240},
    '1/2"':   {"designation": 'M-21 1/2"', "rod_size_a": '1/2"', "take_up_mm": 100, "unit_weight_kg": 0.70, "load_650f_kg": 510, "load_750f_kg": 460},
    '5/8"':   {"designation": 'M-21 5/8"', "rod_size_a": '5/8"', "take_up_mm": 120, "unit_weight_kg": 0.95, "load_650f_kg": 820, "load_750f_kg": 730},
    '3/4"':   {"designation": 'M-21 3/4"', "rod_size_a": '3/4"', "take_up_mm": 120, "unit_weight_kg": 1.30, "load_650f_kg": 1230, "load_750f_kg": 1100},
    '7/8"':   {"designation": 'M-21 7/8"', "rod_size_a": '7/8"', "take_up_mm": 150, "unit_weight_kg": 1.70, "load_650f_kg": 1710, "load_750f_kg": 1520},
    '1"':     {"designation": 'M-21 1"', "rod_size_a": '1"', "take_up_mm": 150, "unit_weight_kg": 2.20, "load_650f_kg": 2250, "load_750f_kg": 2000},
    '1 1/4"': {"designation": 'M-21 1 1/4"', "rod_size_a": '1 1/4"', "take_up_mm": 180, "unit_weight_kg": 2.90, "load_650f_kg": 3630, "load_750f_kg": 3240},
    '1 1/2"': {"designation": 'M-21 1 1/2"', "rod_size_a": '1 1/2"', "take_up_mm": 180, "unit_weight_kg": 3.70, "load_650f_kg": 5280, "load_750f_kg": 4700},
    '1 3/4"': {"designation": 'M-21 1 3/4"', "rod_size_a": '1 3/4"', "take_up_mm": 220, "unit_weight_kg": 4.80, "load_650f_kg": 7120, "load_750f_kg": 6350},
    '2"':     {"designation": 'M-21 2"', "rod_size_a": '2"', "take_up_mm": 220, "unit_weight_kg": 6.00, "load_650f_kg": 9390, "load_750f_kg": 8370},
    '2 1/4"': {"designation": 'M-21 2 1/4"', "rod_size_a": '2 1/4"', "take_up_mm": 260, "unit_weight_kg": 7.50, "load_650f_kg": 12430, "load_750f_kg": 11000},
    '2 1/2"': {"designation": 'M-21 2 1/2"', "rod_size_a": '2 1/2"', "take_up_mm": 300, "unit_weight_kg": 9.20, "load_650f_kg": 15200, "load_750f_kg": 13560},
}


def get_m21_by_dia(dia) -> dict | None:
    return M21_TABLE.get(normalize_fractional_size(dia))

