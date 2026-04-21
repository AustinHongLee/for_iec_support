"""
Type 76 large-pipe pad support data (D-91).

The drawing has no dimensional table; it states the support applies to pipe
sizes 26"~42", with a 120-degree pad cut from the main pipe or fabricated from
carbon-steel plate, 12t minimum, 400mm long.
"""
from __future__ import annotations

import math

from .component_size_utils import STEEL_DENSITY_KG_PER_MM3, normalize_fractional_size, size_to_float
from .pipe_table import PIPE_OD


TYPE76_SUPPORTED_SIZES = ['26"', '28"', '30"', '32"', '34"', '36"', '40"', '42"']
TYPE76_PAD_ANGLE_DEG = 120
TYPE76_PAD_LENGTH_MM = 400
TYPE76_MIN_THICKNESS_MM = 12


def get_type76_data(line_size) -> dict | None:
    key = normalize_fractional_size(line_size)
    size = size_to_float(key)
    if key not in TYPE76_SUPPORTED_SIZES or size not in PIPE_OD:
        return None
    od = PIPE_OD[size]
    arc_length = math.pi * od * (TYPE76_PAD_ANGLE_DEG / 360)
    unit_weight = round(
        arc_length * TYPE76_PAD_LENGTH_MM * TYPE76_MIN_THICKNESS_MM * STEEL_DENSITY_KG_PER_MM3,
        2,
    )
    return {
        "line_size": key,
        "od_mm": od,
        "pad_angle_deg": TYPE76_PAD_ANGLE_DEG,
        "pad_length_mm": TYPE76_PAD_LENGTH_MM,
        "thickness_mm": TYPE76_MIN_THICKNESS_MM,
        "unit_weight_kg": unit_weight,
        "weight_status": "calculated_from_120deg_arc_400L_12t_min",
        "transcription_status": "ai_visual_transcribed",
    }


def list_type76_sizes() -> list[str]:
    return TYPE76_SUPPORTED_SIZES[:]
