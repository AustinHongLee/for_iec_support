"""
M-25 Weldless Eye Nut 資料表
來源: M-25 圖紙

說明:
- WENR = 右牙 weldless eye nut
- WENL = 左牙 weldless eye nut
"""
from .component_size_utils import normalize_fractional_size

M25_TABLE = {
    '3/8"': {
        "type_rh": "WENR-3/8",
        "type_lh": "WENL-3/8",
        "rod_size_a": '3/8"',
        "B": 38, "C": 30, "D": 13, "E": 51, "F": 35, "G": 18,
        "load_650f_kg": 270,
        "load_750f_kg": 240,
        "unit_weight_kg": 0.08,
    },
    '1/2"': {
        "type_rh": "WENR-1/2",
        "type_lh": "WENL-1/2",
        "rod_size_a": '1/2"',
        "B": 38, "C": 30, "D": 13, "E": 51, "F": 35, "G": 18,
        "load_650f_kg": 510,
        "load_750f_kg": 460,
        "unit_weight_kg": 0.15,
    },
    '5/8"': {
        "type_rh": "WENR-5/8",
        "type_lh": "WENL-5/8",
        "rod_size_a": '5/8"',
        "B": 38, "C": 30, "D": 13, "E": 51, "F": 35, "G": 18,
        "load_650f_kg": 820,
        "load_750f_kg": 730,
        "unit_weight_kg": 0.22,
    },
    '3/4"': {
        "type_rh": "WENR-3/4",
        "type_lh": "WENL-3/4",
        "rod_size_a": '3/4"',
        "B": 38, "C": 30, "D": 13, "E": 51, "F": 35, "G": 18,
        "load_650f_kg": 1230,
        "load_750f_kg": 1100,
        "unit_weight_kg": 0.35,
    },
    '7/8"': {
        "type_rh": "WENR-7/8",
        "type_lh": "WENL-7/8",
        "rod_size_a": '7/8"',
        "B": 51, "C": 43, "D": 19, "E": 67, "F": 49, "G": 25,
        "load_650f_kg": 1710,
        "load_750f_kg": 1520,
        "unit_weight_kg": 0.50,
    },
    '1"': {
        "type_rh": "WENR-1",
        "type_lh": "WENL-1",
        "rod_size_a": '1"',
        "B": 51, "C": 43, "D": 19, "E": 67, "F": 49, "G": 25,
        "load_650f_kg": 2250,
        "load_750f_kg": 2000,
        "unit_weight_kg": 0.70,
    },
    '1 1/4"': {
        "type_rh": "WENR-1 1/4",
        "type_lh": "WENL-1 1/4",
        "rod_size_a": '1 1/4"',
        "B": 64, "C": 46, "D": 25, "E": 86, "F": 60, "G": 32,
        "load_650f_kg": 3630,
        "load_750f_kg": 3240,
        "unit_weight_kg": 1.10,
    },
    '1 1/2"': {
        "type_rh": "WENR-1 1/2",
        "type_lh": "WENL-1 1/2",
        "rod_size_a": '1 1/2"',
        "B": 64, "C": 46, "D": 25, "E": 86, "F": 60, "G": 32,
        "load_650f_kg": 5280,
        "load_750f_kg": 4700,
        "unit_weight_kg": 1.45,
    },
    '1 3/4"': {
        "type_rh": "WENR-1 3/4",
        "type_lh": "WENL-1 3/4",
        "rod_size_a": '1 3/4"',
        "B": 102, "C": 102, "D": 38, "E": 159, "F": 102, "G": 57,
        "load_650f_kg": 7120,
        "load_750f_kg": 6350,
        "unit_weight_kg": 2.10,
    },
    '2"': {
        "type_rh": "WENR-2",
        "type_lh": "WENL-2",
        "rod_size_a": '2"',
        "B": 102, "C": 102, "D": 38, "E": 159, "F": 102, "G": 57,
        "load_650f_kg": 9390,
        "load_750f_kg": 8370,
        "unit_weight_kg": 2.60,
    },
    '2 1/4"': {
        "type_rh": "WENR-2 1/4",
        "type_lh": "WENL-2 1/4",
        "rod_size_a": '2 1/4"',
        "B": 102, "C": 102, "D": 38, "E": 159, "F": 102, "G": 57,
        "load_650f_kg": 12430,
        "load_750f_kg": 11000,
        "unit_weight_kg": 3.20,
    },
    '2 1/2"': {
        "type_rh": "WENR-2 1/2",
        "type_lh": "WENL-2 1/2",
        "rod_size_a": '2 1/2"',
        "B": 102, "C": 102, "D": 38, "E": 159, "F": 102, "G": 57,
        "load_650f_kg": 15200,
        "load_750f_kg": 13560,
        "unit_weight_kg": 3.90,
    },
}


def get_m25_by_dia(dia: str) -> dict | None:
    """依 rod 直徑查 M-25 規格。"""
    return M25_TABLE.get(normalize_fractional_size(dia))


def build_m25_item(dia: str, left_hand: bool = False) -> dict | None:
    """建立 weldless eye nut item。"""
    row = get_m25_by_dia(dia)
    if not row:
        return None
    item = dict(row)
    item["designation"] = row["type_lh"] if left_hand else row["type_rh"]
    item["left_hand"] = left_hand
    return item
