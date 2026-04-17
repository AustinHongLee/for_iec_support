"""
Type 52 計算器 (也用於 Type 53, 54, 55, 66, 67, 85)
格式: 52-2B(P)-A(A)-130-500
"""
import math
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts, count_char, clean_pipe_size
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from data.pipe_table import get_pipe_details


def _get_pipe_size(fullstring: str) -> str:
    part2 = get_part(fullstring, 2)
    if "(" in part2:
        before, _ = extract_parts(part2)
        return before
    return part2


def _get_pad_symbol(fullstring: str) -> str:
    part2 = get_part(fullstring, 2)
    if "(" in part2:
        _, paren = extract_parts(part2)
        return paren
    return "N/A"


def _get_material(fullstring: str) -> str:
    part3 = get_part(fullstring, 3)
    if not part3 or part3.strip() == "":
        return "A36/SS400"
    if "(" in part3:
        _, paren = extract_parts(part3)
        material_map = {"(A)": "AS", "(S)": "SUS304"}
        return material_map.get(paren, "A36/SS400")
    return "A36/SS400"


def _get_insulation(fullstring: str) -> int:
    part3 = get_part(fullstring, 3)
    if not part3 or part3.strip() == "":
        return 75
    if "(" in part3:
        before, _ = extract_parts(part3)
        val = before
    else:
        val = part3
    insulation_map = {"A": 80, "B": 130, "C": 180}
    return insulation_map.get(val, 75)


def _table66_a(pipe_size: float) -> int:
    if 0.5 <= pipe_size <= 8: return 100
    if 10 <= pipe_size <= 14: return 130
    if 16 <= pipe_size <= 20: return 250
    if 22 <= pipe_size <= 40: return 300
    return 100


def _table66_b(pipe_size: float) -> int:
    if 0.5 <= pipe_size <= 8: return 0
    if 10 <= pipe_size <= 14: return 9
    if 16 <= pipe_size <= 40: return 12
    return 0


def _table66_c(pipe_size: float) -> str:
    ps = clean_pipe_size(pipe_size)
    if 0.5 <= ps <= 8: return "200*100*5.5"
    if 10 <= ps <= 14: return "200*200*8"
    if 16 <= ps <= 40: return "FB12"
    return "200*100*5.5"


def _table66_d(pipe_size) -> int:
    ps = clean_pipe_size(pipe_size)
    if 0.5 <= ps <= 2.5: return 150
    if 3 <= ps <= 8: return 250
    if 10 <= ps <= 40: return 250
    return 150


def _table66_e(pipe_size: float) -> int:
    if 1.5 <= pipe_size < 2: return 0
    if 2 <= pipe_size <= 40: return 50
    return 0


def _table66_hopes_plate(pipe_size: float) -> float:
    hopes_map = {
        10: 68.25, 12: 76.2, 14: 88.9, 16: 101.6,
        18: 114.3, 20: 127.0,
    }
    if pipe_size in hopes_map:
        return hopes_map[pipe_size]
    if 22 <= pipe_size <= 40:
        return 152.4
    return 0


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    first = get_part(fullstring, 1)
    dash_count = count_char(fullstring, "-")

    # 預設值
    hops_value = 150
    pipe_size_str = _get_pipe_size(fullstring)
    pipe_size = get_lookup_value(pipe_size_str.replace("B", ""))
    pad_symbol = _get_pad_symbol(fullstring)
    material_value = "A36/SS400"
    lops_value = _table66_d(pipe_size)

    if dash_count >= 2:
        material_value = _get_material(fullstring)

    if dash_count >= 4:
        h_val = get_part(fullstring, 4)
        l_val = get_part(fullstring, 5)
        if h_val and h_val.strip():
            hops_value = int(h_val)
        if l_val and l_val.strip():
            lops_value = int(l_val)

    # === Pad 計算 ===
    if pad_symbol != "N/A":
        pipe_thickness_val = 6
        if pipe_size >= 2 and pipe_size <= 14:
            pipe_thickness_val = 9
        elif pipe_size >= 15 and pipe_size <= 24:
            pipe_thickness_val = 12

        pipe_details = get_pipe_details(pipe_size, "10S")
        od = pipe_details["od_mm"]

        if pipe_size < 10:
            pad_a = (od / 2 + pipe_thickness_val * 2) * math.pi
            pad_b = _table66_e(pipe_size) * 2 + lops_value
        else:
            pad_a = (od / 2 + pipe_thickness_val * 2) * math.pi
            pad_b = _table66_e(pipe_size) * (2 + lops_value) + 25 * 2

        add_plate_entry(result, round(pad_a), round(pad_b),
                       pipe_thickness_val, "Pad_52Type")

    # === 楔子 (Angle) ===
    if first in ("52", "53", "54", "55"):
        add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material_value)

    # === C 型鋼 / FB ===
    c_spec = _table66_c(pipe_size)
    if c_spec == "FB12":
        # FB 板 1
        fb_a = _table66_a(pipe_size) + 35 * 2
        fb_b = lops_value + 25 * 2
        add_plate_entry(result, fb_a, fb_b, 12, "FB_52Type_1")
        # FB 板 2
        add_plate_entry(result, 100, fb_b, 12, "FB_52Type_2")
    else:
        add_steel_section_entry(result, "H Beam", c_spec, lops_value, 1, material_value)

    # === D 鋼板 (>= 10B) ===
    if pipe_size >= 10:
        hp = _table66_hopes_plate(pipe_size)
        d_a = hp + 100
        d_b = lops_value + 25 * 2
        d_t = _table66_b(pipe_size)
        add_plate_entry(result, d_a, d_b, d_t, "FB_52Type_3")

    return result
