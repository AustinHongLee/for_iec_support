"""
M / N component 共用尺寸正規化工具。
"""
from __future__ import annotations

import math


SIZE_DISPLAY_MAP = {
    0.25: '1/4"',
    0.375: '3/8"',
    0.5: '1/2"',
    0.625: '5/8"',
    0.75: '3/4"',
    0.875: '7/8"',
    1.0: '1"',
    1.125: '1 1/8"',
    1.25: '1 1/4"',
    1.375: '1 3/8"',
    1.5: '1 1/2"',
    1.625: '1 5/8"',
    1.75: '1 3/4"',
    1.875: '1 7/8"',
    2.0: '2"',
    2.25: '2 1/4"',
    2.5: '2 1/2"',
    2.75: '2 3/4"',
    3.0: '3"',
    3.5: '3 1/2"',
    4.0: '4"',
    5.0: '5"',
    6.0: '6"',
    7.0: '7"',
    8.0: '8"',
    9.0: '9"',
    10.0: '10"',
    11.0: '11"',
    12.0: '12"',
    14.0: '14"',
    16.0: '16"',
    18.0: '18"',
    20.0: '20"',
    22.0: '22"',
    24.0: '24"',
    26.0: '26"',
    28.0: '28"',
    30.0: '30"',
    32.0: '32"',
    34.0: '34"',
    36.0: '36"',
    40.0: '40"',
    42.0: '42"',
}

STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def _parse_size_value(value) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("B", "").replace("'", "").replace('"', "").replace("-", " ").strip()

    if "/" in text:
        whole_and_num, den = text.split("/", 1)
        den_val = float(den.strip())
        parts = whole_and_num.strip().split()
        if len(parts) == 2:
            return float(parts[0]) + float(parts[1]) / den_val
        return float(parts[0]) / den_val

    try:
        return float(text)
    except ValueError:
        return None


def normalize_fractional_size(value) -> str:
    """
    將 0.5 / 1-1/2 / 1 1/2" / 2B 等格式統一成 table key.
    """
    parsed = _parse_size_value(value)
    if parsed is None:
        return str(value).strip()
    rounded = round(parsed, 4)
    if rounded in SIZE_DISPLAY_MAP:
        return SIZE_DISPLAY_MAP[rounded]
    if rounded.is_integer():
        return f'{int(rounded)}"'
    return f'{rounded:g}"'



def size_to_float(value) -> float | None:
    return _parse_size_value(value)


def steel_round_bar_weight_per_m_kg(dia) -> float:
    """圓鋼單位重 (kg/m)。"""
    dia_in = size_to_float(dia)
    if dia_in is None:
        return 0.0
    dia_mm = dia_in * 25.4
    area_mm2 = math.pi * dia_mm ** 2 / 4
    return round(area_mm2 * 1_000 * STEEL_DENSITY_KG_PER_MM3, 2)


def estimate_round_bar_weight_kg(dia, length_mm: int) -> float:
    """圓鋼指定長度重量 (kg)。"""
    return round(steel_round_bar_weight_per_m_kg(dia) * (length_mm / 1000.0), 2)
