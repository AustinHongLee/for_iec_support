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


def _is_int_token(value: str | None) -> bool:
    return bool(value and value.strip().isdigit())


def _parse_hops_lops(fullstring: str, pipe_size: float) -> tuple[int, int]:
    """Parse optional HOPS/LOPS overrides while keeping legacy D-80A formats."""
    hops_value = 150
    lops_value = _table66_d(pipe_size)

    part3 = get_part(fullstring, 3)
    part4 = get_part(fullstring, 4)
    part5 = get_part(fullstring, 5)

    if _is_int_token(part4) and _is_int_token(part5):
        return int(part4), int(part5)
    if _is_int_token(part3) and _is_int_token(part4):
        return int(part3), int(part4)
    if _is_int_token(part4):
        return hops_value, int(part4)

    return hops_value, lops_value


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


def _pad_plate_thickness(pipe_size: float) -> int:
    """D-80 NOTE 1 reinforcing pad thickness by line size."""
    if pipe_size <= 1.5:
        return 6
    if 2 <= pipe_size <= 14:
        return 9
    if pipe_size >= 16:
        return 12
    return 6


def _pad_plate_length(pipe_size: float) -> int:
    """Pad longitudinal length based on D/E table values plus 25 mm end margins."""
    if pipe_size < 10:
        return _table66_d(pipe_size) + 25 * 2
    return _table66_e(pipe_size) * 2 + 25 * 2 + 250


def _pad_plate_width(pipe_size: float) -> float:
    """120 degree pad developed width: one third of pipe circumference."""
    pipe_details = get_pipe_details(pipe_size, "10S")
    od = pipe_details["od_mm"]
    return od * math.pi / 3


def _support_member_thickness(pipe_size: float) -> float:
    """Thickness of the vertical member inside the shoe detail."""
    c_spec = _table66_c(pipe_size)
    if c_spec == "FB12":
        return 12
    try:
        return float(c_spec.split("*")[-1])
    except (TypeError, ValueError):
        return 0


def _fb3_plate_width(pipe_size: float) -> float:
    """FB_52Type_3 width: A + half 35 mm gap - half inner member thickness."""
    return _table66_a(pipe_size) + 35 / 2 - _support_member_thickness(pipe_size) / 2


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

    if dash_count >= 2:
        material_value = _get_material(fullstring)

    hops_value, lops_value = _parse_hops_lops(fullstring, pipe_size)

    # === Pad 計算 ===
    if pad_symbol != "N/A":
        pipe_thickness_val = _pad_plate_thickness(pipe_size)
        pad_a = _pad_plate_length(pipe_size)
        pad_b = _pad_plate_width(pipe_size)

        add_plate_entry(result, round(pad_a), round(pad_b),
                        pipe_thickness_val, "Pad_52Type")
        if pipe_size < 10:
            length_rule = "D + 25*2"
        else:
            length_rule = "E*2 + 25*2 + 250"
        result.entries[-1].remark = (
            f"120deg pad developed width=OD*pi/3; length_rule={length_rule}; "
            f"thickness by line size={pipe_thickness_val}t"
        )

    # === 楔子 (Angle) ===
    if first in ("52", "53", "54", "55"):
        add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material_value)
        result.entries[-1].remark = "L40x40x5 side guide, CUT IN FIELD, length provisional=150"

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
        add_steel_section_entry(result, "H Beam", c_spec, lops_value + 25 * 2, 1, material_value)

    # === D 鋼板 (>= 10B) ===
    if pipe_size >= 10:
        d_a = hops_value
        d_b = _fb3_plate_width(pipe_size)
        d_t = _table66_b(pipe_size)
        add_plate_entry(result, d_a, d_b, d_t, "FB_52Type_3", plate_qty=4)
        result.entries[-1].remark = (
            "length uses HOPS; width=A+35/2-member_t/2; qty=4; pending precision check"
        )

    return result
