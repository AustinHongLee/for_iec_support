"""
M-24 Forged Steel Clevis 資料表

說明:
- 目前先補 rod-size / pin dia / unit weight 等 component-level 欄位，
  供後續 hanger 類型正式接用。
"""
from .component_size_utils import normalize_fractional_size


M24_TABLE = {
    '3/8"':   {"designation": 'M-24 3/8"', "rod_size_a": '3/8"', "pin_dia_b": '1/2"', "unit_weight_kg": 0.25, "load_650f_kg": 270, "load_750f_kg": 240},
    '1/2"':   {"designation": 'M-24 1/2"', "rod_size_a": '1/2"', "pin_dia_b": '5/8"', "unit_weight_kg": 0.35, "load_650f_kg": 510, "load_750f_kg": 460},
    '5/8"':   {"designation": 'M-24 5/8"', "rod_size_a": '5/8"', "pin_dia_b": '3/4"', "unit_weight_kg": 0.50, "load_650f_kg": 820, "load_750f_kg": 730},
    '3/4"':   {"designation": 'M-24 3/4"', "rod_size_a": '3/4"', "pin_dia_b": '7/8"', "unit_weight_kg": 0.70, "load_650f_kg": 1230, "load_750f_kg": 1100},
    '7/8"':   {"designation": 'M-24 7/8"', "rod_size_a": '7/8"', "pin_dia_b": '1"', "unit_weight_kg": 0.95, "load_650f_kg": 1710, "load_750f_kg": 1520},
    '1"':     {"designation": 'M-24 1"', "rod_size_a": '1"', "pin_dia_b": '1 1/8"', "unit_weight_kg": 1.25, "load_650f_kg": 2250, "load_750f_kg": 2000},
    '1 1/4"': {"designation": 'M-24 1 1/4"', "rod_size_a": '1 1/4"', "pin_dia_b": '1 3/8"', "unit_weight_kg": 1.65, "load_650f_kg": 3630, "load_750f_kg": 3240},
    '1 1/2"': {"designation": 'M-24 1 1/2"', "rod_size_a": '1 1/2"', "pin_dia_b": '1 5/8"', "unit_weight_kg": 2.10, "load_650f_kg": 5280, "load_750f_kg": 4700},
    '1 3/4"': {"designation": 'M-24 1 3/4"', "rod_size_a": '1 3/4"', "pin_dia_b": '2"', "unit_weight_kg": 2.70, "load_650f_kg": 7120, "load_750f_kg": 6350},
    '2"':     {"designation": 'M-24 2"', "rod_size_a": '2"', "pin_dia_b": '2 1/4"', "unit_weight_kg": 3.40, "load_650f_kg": 9390, "load_750f_kg": 8370},
    '2 1/4"': {"designation": 'M-24 2 1/4"', "rod_size_a": '2 1/4"', "pin_dia_b": '2 1/2"', "unit_weight_kg": 4.20, "load_650f_kg": 12430, "load_750f_kg": 11000},
    '2 1/2"': {"designation": 'M-24 2 1/2"', "rod_size_a": '2 1/2"', "pin_dia_b": '2 3/4"', "unit_weight_kg": 5.10, "load_650f_kg": 15200, "load_750f_kg": 13560},
}


def get_m24_by_dia(dia) -> dict | None:
    return M24_TABLE.get(normalize_fractional_size(dia))

