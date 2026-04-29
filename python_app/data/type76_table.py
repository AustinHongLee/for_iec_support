from __future__ import annotations
import math
from .component_size_utils import STEEL_DENSITY_KG_PER_MM3, normalize_fractional_size, size_to_float
from .pipe_table import PIPE_OD as _PIPE_OD_src
"""
Type 76 查表資料 — 資料來源: configs/type_76.json
Bridge module (auto-fixed 2026-04-29): interface 不變，底層讀 JSON。
"""
import json as _json, os as _os
from .component_size_utils import normalize_fractional_size

_HERE = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
_JSON_PATH = _os.path.join(_HERE, "configs", "type_76.json")

with open(_JSON_PATH, encoding="utf-8") as _f:
    _DATA = _json.load(_f)

STEEL_DENSITY_KG_PER_MM3 = _DATA["STEEL_DENSITY_KG_PER_MM3"]
TYPE76_MIN_THICKNESS_MM = _DATA["TYPE76_MIN_THICKNESS_MM"]
TYPE76_PAD_ANGLE_DEG = _DATA["TYPE76_PAD_ANGLE_DEG"]
TYPE76_PAD_LENGTH_MM = _DATA["TYPE76_PAD_LENGTH_MM"]

# PIPE_OD (dict)
PIPE_OD = {
    (int(k) if isinstance(k, str) and k.lstrip("-").isdigit() else k): v
    for k, v in _DATA["PIPE_OD"].items()
}

# TYPE76_SUPPORTED_SIZES (list)
TYPE76_SUPPORTED_SIZES = _DATA["TYPE76_SUPPORTED_SIZES"]


# ── 原始查詢函式（interface 不變）────────────────────────

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

