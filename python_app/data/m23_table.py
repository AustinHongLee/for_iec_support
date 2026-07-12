"""
M-23 Welded Eye Rod 資料表
來源: M-23 圖紙

說明:
- WERR = 右牙 welded eye rod
- WERL = 左牙 welded eye rod
- 圖面 LENGTH 為變動值, 表格定義幾何與推薦配合 bolt dia
"""

from .component_size_utils import normalize_fractional_size, steel_round_bar_weight_per_m_kg


_EYE_END_WEIGHT = {
    '3/8"': 0.08,
    '1/2"': 0.10,
    '5/8"': 0.15,
    '3/4"': 0.23,
    '7/8"': 0.30,
    '1"': 0.40,
    '1 1/4"': 0.60,
    '1 1/2"': 0.85,
    '1 3/4"': 1.20,
    '2"': 1.60,
    '2 1/4"': 2.10,
    '2 1/2"': 2.70,
}

M23_TABLE = {
    '3/8"': {
        "type_rh": "WERR-3/8",
        "type_lh": "WERL-3/8",
        "rod_size_a": '3/8"',
        "recommended_bolt_dia_b": '1/2"',
        "thread_length_d": 64,
        "eye_od_c": 22,
        "load_650f_kg": 270,
        "load_750f_kg": 240,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('3/8"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['3/8"'],
    },
    '1/2"': {
        "type_rh": "WERR-1/2",
        "type_lh": "WERL-1/2",
        "rod_size_a": '1/2"',
        "recommended_bolt_dia_b": '5/8"',
        "thread_length_d": 64,
        "eye_od_c": 22,
        "load_650f_kg": 510,
        "load_750f_kg": 460,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1/2"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['1/2"'],
    },
    '5/8"': {
        "type_rh": "WERR-5/8",
        "type_lh": "WERL-5/8",
        "rod_size_a": '5/8"',
        "recommended_bolt_dia_b": '3/4"',
        "thread_length_d": 64,
        "eye_od_c": 22,
        "load_650f_kg": 820,
        "load_750f_kg": 730,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('5/8"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['5/8"'],
    },
    '3/4"': {
        "type_rh": "WERR-3/4",
        "type_lh": "WERL-3/4",
        "rod_size_a": '3/4"',
        "recommended_bolt_dia_b": '7/8"',
        "thread_length_d": 76,
        "eye_od_c": 32,
        "load_650f_kg": 1230,
        "load_750f_kg": 1100,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('3/4"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['3/4"'],
    },
    '7/8"': {
        "type_rh": "WERR-7/8",
        "type_lh": "WERL-7/8",
        "rod_size_a": '7/8"',
        "recommended_bolt_dia_b": '1"',
        "thread_length_d": 89,
        "eye_od_c": 32,
        "load_650f_kg": 1710,
        "load_750f_kg": 1520,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('7/8"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['7/8"'],
    },
    '1"': {
        "type_rh": "WERR-1",
        "type_lh": "WERL-1",
        "rod_size_a": '1"',
        "recommended_bolt_dia_b": '1 1/8"',
        "thread_length_d": 102,
        "eye_od_c": 32,
        "load_650f_kg": 2250,
        "load_750f_kg": 2000,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['1"'],
    },
    '1 1/4"': {
        "type_rh": "WERR-1 1/4",
        "type_lh": "WERL-1 1/4",
        "rod_size_a": '1 1/4"',
        "recommended_bolt_dia_b": '1 3/8"',
        "thread_length_d": 127,
        "eye_od_c": 45,
        "load_650f_kg": 3630,
        "load_750f_kg": 3240,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 1/4"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['1 1/4"'],
    },
    '1 1/2"': {
        "type_rh": "WERR-1 1/2",
        "type_lh": "WERL-1 1/2",
        "rod_size_a": '1 1/2"',
        "recommended_bolt_dia_b": '1 5/8"',
        "thread_length_d": 152,
        "eye_od_c": 45,
        "load_650f_kg": 5280,
        "load_750f_kg": 4700,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 1/2"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['1 1/2"'],
    },
    '1 3/4"': {
        "type_rh": "WERR-1 3/4",
        "type_lh": "WERL-1 3/4",
        "rod_size_a": '1 3/4"',
        "recommended_bolt_dia_b": '2"',
        "thread_length_d": 178,
        "eye_od_c": 65,
        "load_650f_kg": 7120,
        "load_750f_kg": 6350,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 3/4"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['1 3/4"'],
    },
    '2"': {
        "type_rh": "WERR-2",
        "type_lh": "WERL-2",
        "rod_size_a": '2"',
        "recommended_bolt_dia_b": '2 1/4"',
        "thread_length_d": 203,
        "eye_od_c": 65,
        "load_650f_kg": 9390,
        "load_750f_kg": 8370,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['2"'],
    },
    '2 1/4"': {
        "type_rh": "WERR-2 1/4",
        "type_lh": "WERL-2 1/4",
        "rod_size_a": '2 1/4"',
        "recommended_bolt_dia_b": '2 1/2"',
        "thread_length_d": 229,
        "eye_od_c": 76,
        "load_650f_kg": 12430,
        "load_750f_kg": 11000,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2 1/4"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['2 1/4"'],
    },
    '2 1/2"': {
        "type_rh": "WERR-2 1/2",
        "type_lh": "WERL-2 1/2",
        "rod_size_a": '2 1/2"',
        "recommended_bolt_dia_b": '2 3/4"',
        "thread_length_d": 254,
        "eye_od_c": 76,
        "load_650f_kg": 15200,
        "load_750f_kg": 13560,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2 1/2"'),
        "eye_end_weight_kg": _EYE_END_WEIGHT['2 1/2"'],
    },
}


def get_m23_by_dia(dia: str) -> dict | None:
    """依 rod 直徑查 M-23 規格。"""
    return M23_TABLE.get(normalize_fractional_size(dia))


def build_m23_item(dia: str, length_mm: int, left_hand: bool = False) -> dict | None:
    """建立含指定長度的 welded eye rod item。"""
    row = get_m23_by_dia(dia)
    if not row:
        return None
    item = dict(row)
    base_designation = row["type_lh"] if left_hand else row["type_rh"]
    item["length_mm"] = length_mm
    item["designation_base"] = base_designation
    item["designation"] = f"{base_designation}-{length_mm}"
    item["left_hand"] = left_hand
    item["unit_weight_kg"] = round(item["weight_per_m_kg"] * (length_mm / 1000.0) + item["eye_end_weight_kg"], 2)
    return item


def estimate_m23_weight(dia: str, length_mm: int) -> float:
    item = build_m23_item(dia, length_mm)
    return item["unit_weight_kg"] if item else 0.0
