"""
M-22 Machine Threaded Rod 資料表
來源: M-22 圖紙

用途:
- Type 64 的 machine threaded rod
- 其他 rod hanger 類型的吊桿規格查詢

說明:
- MTR  = 兩端皆右牙
- MTRL = 一端右牙、一端左牙
- 圖面中的 L 為變動長度, 表格只定義直徑 / 螺紋長 / 推薦載重
"""

from .component_size_utils import normalize_fractional_size, steel_round_bar_weight_per_m_kg

M22_TABLE = {
    '3/8"': {
        "type_rh": "MTR-3/8",
        "type_lh": "MTRL-3/8",
        "dia": '3/8"',
        "thread_length_c": 152,
        "load_650f_kg": 270,
        "load_750f_kg": 240,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('3/8"'),
    },
    '1/2"': {
        "type_rh": "MTR-1/2",
        "type_lh": "MTRL-1/2",
        "dia": '1/2"',
        "thread_length_c": 152,
        "load_650f_kg": 510,
        "load_750f_kg": 460,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1/2"'),
    },
    '5/8"': {
        "type_rh": "MTR-5/8",
        "type_lh": "MTRL-5/8",
        "dia": '5/8"',
        "thread_length_c": 152,
        "load_650f_kg": 820,
        "load_750f_kg": 730,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('5/8"'),
    },
    '3/4"': {
        "type_rh": "MTR-3/4",
        "type_lh": "MTRL-3/4",
        "dia": '3/4"',
        "thread_length_c": 152,
        "load_650f_kg": 1230,
        "load_750f_kg": 1100,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('3/4"'),
    },
    '7/8"': {
        "type_rh": "MTR-7/8",
        "type_lh": "MTRL-7/8",
        "dia": '7/8"',
        "thread_length_c": 152,
        "load_650f_kg": 1710,
        "load_750f_kg": 1520,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('7/8"'),
    },
    '1"': {
        "type_rh": "MTR-1",
        "type_lh": "MTRL-1",
        "dia": '1"',
        "thread_length_c": 152,
        "load_650f_kg": 2250,
        "load_750f_kg": 2000,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1"'),
    },
    '1 1/4"': {
        "type_rh": "MTR-1 1/4",
        "type_lh": "MTRL-1 1/4",
        "dia": '1 1/4"',
        "thread_length_c": 152,
        "load_650f_kg": 3630,
        "load_750f_kg": 3240,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 1/4"'),
    },
    '1 1/2"': {
        "type_rh": "MTR-1 1/2",
        "type_lh": "MTRL-1 1/2",
        "dia": '1 1/2"',
        "thread_length_c": 152,
        "load_650f_kg": 5280,
        "load_750f_kg": 4700,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 1/2"'),
    },
    '1 3/4"': {
        "type_rh": "MTR-1 3/4",
        "type_lh": "MTRL-1 3/4",
        "dia": '1 3/4"',
        "thread_length_c": 178,
        "load_650f_kg": 7120,
        "load_750f_kg": 6350,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('1 3/4"'),
    },
    '2"': {
        "type_rh": "MTR-2",
        "type_lh": "MTRL-2",
        "dia": '2"',
        "thread_length_c": 203,
        "load_650f_kg": 9390,
        "load_750f_kg": 8370,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2"'),
    },
    '2 1/4"': {
        "type_rh": "MTR-2 1/4",
        "type_lh": "MTRL-2 1/4",
        "dia": '2 1/4"',
        "thread_length_c": 229,
        "load_650f_kg": 12430,
        "load_750f_kg": 11000,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2 1/4"'),
    },
    '2 1/2"': {
        "type_rh": "MTR-2 1/2",
        "type_lh": "MTRL-2 1/2",
        "dia": '2 1/2"',
        "thread_length_c": 254,
        "load_650f_kg": 15200,
        "load_750f_kg": 13560,
        "weight_per_m_kg": steel_round_bar_weight_per_m_kg('2 1/2"'),
    },
}


def get_m22_by_dia(dia: str) -> dict | None:
    """依 rod 直徑查詢 M-22 規格。"""
    return M22_TABLE.get(normalize_fractional_size(dia))


def build_m22_item(dia: str, length_mm: int, left_hand: bool = False) -> dict | None:
    """
    建立含指定長度的 M-22 item.
    left_hand=True 時回傳 MTRL 型號, 否則回傳 MTR 型號。
    """
    row = get_m22_by_dia(dia)
    if not row:
        return None
    item = dict(row)
    base_designation = row["type_lh"] if left_hand else row["type_rh"]
    item["length_mm"] = length_mm
    item["designation_base"] = base_designation
    item["designation"] = f"{base_designation}-{length_mm}"
    item["left_hand"] = left_hand
    item["unit_weight_kg"] = round(item["weight_per_m_kg"] * (length_mm / 1000.0), 2)
    return item


def estimate_m22_weight(dia: str, length_mm: int) -> float:
    item = build_m22_item(dia, length_mm)
    return item["unit_weight_kg"] if item else 0.0
