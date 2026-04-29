"""
Type 80 calculator — Pipe Shoe (D-95 / D-96)

Formats:
- 80-2B(P)-A(A)-130-500    # D-95, 3/4"~24"
- 80-30B-A(A)-130-500      # D-96, 26"~42"
"""
import math

from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value, extract_parts, parse_pipe_size
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from data.pipe_table import get_pipe_details
from data.type80_table import get_type80_small_row, get_type80_big_row


_MATERIAL_MAP = {
    "": "A36/SS400",
    "(A)": "AS",
    "(S)": "SUS304",
}


def _parse_size_and_pad(fullstring: str) -> tuple[str, bool]:
    part2 = get_part(fullstring, 2) or ""
    if "(" in part2:
        before, paren = extract_parts(part2)
        return parse_pipe_size(before), paren.upper() == "(P)"
    return parse_pipe_size(part2), False


def _parse_table_tokens(fullstring: str) -> tuple[str, str]:
    part3 = get_part(fullstring, 3) or ""
    if "(" in part3:
        before, paren = extract_parts(part3)
        return (before or "").upper(), paren.upper()
    return part3.upper(), ""


def _parse_hops_lops(fullstring: str, default_lops: int) -> tuple[int, int]:
    part4 = get_part(fullstring, 4)
    part5 = get_part(fullstring, 5)
    hops = int(part4) if part4 and part4.isdigit() else 150
    lops = int(part5) if part5 and part5.isdigit() else default_lops
    return hops, lops


def _pad_width(pipe_size: float) -> float:
    pipe_details = get_pipe_details(pipe_size, "10S")
    return pipe_details["od_mm"] * math.pi / 3


def _pad_thickness(pipe_size: float) -> int:
    if pipe_size <= 1.5:
        return 6
    if pipe_size <= 14:
        return 9
    return 12


def _pad_length(pipe_size: float) -> int:
    if pipe_size < 10:
        return 150 + 25 * 2
    return 50 * 2 + 25 * 2 + 250


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    size_str, pad_required = _parse_size_and_pad(fullstring)
    pipe_size = get_lookup_value(size_str)
    table_a_symbol, material_symbol = _parse_table_tokens(fullstring)
    material = _MATERIAL_MAP.get(material_symbol, "A36/SS400")

    if pipe_size <= 24:
        row = get_type80_small_row(pipe_size)
        if row is None:
            result.error = f"Type 80 D-95 查表失敗: 管徑 {size_str}\" 不在 3/4\"~24\" 範圍"
            return result
        _, default_member_length = row["member_c"]
        default_lops = 500 if default_member_length == "12" else row["A"]
        hops, lops = _parse_hops_lops(fullstring, default_lops)

        if pad_required:
            add_plate_entry(
                result,
                _pad_length(pipe_size),
                round(_pad_width(pipe_size), 1),
                _pad_thickness(pipe_size),
                "REINFORCING_PAD",
                material,
            )
            result.entries[-1].remark = "Type 80 (P): 120deg reinforcing pad required"

        member_type, member_spec = row["member_c"]
        if member_type == "H Beam":
            add_steel_section_entry(result, "H Beam", member_spec, lops, 1, material)
            result.entries[-1].remark = (
                f'Member C, CUT FROM H{member_spec.replace("*", "X")}, '
                f"A/B={row['A']}/{row['B']}, HOPS={hops}, LOPS={lops}"
            )
        else:
            add_plate_entry(result, lops, row["B"], 12, "MEMBER_C_FAB_PLATE", material)
            result.entries[-1].remark = (
                f"Member C, FAB. FROM 12t PLATE, A/B={row['A']}/{row['B']}, "
                f"HOPS={hops}, LOPS={lops}"
            )

        if row["D"] is not None:
            result.warnings.append(
                f'Type 80 D-95 shows 12t STIFF.PL for {size_str}" pipe; '
                "stiffener cutting geometry is not fully modeled"
            )

        return result

    row = get_type80_big_row(pipe_size)
    if row is None:
        result.error = f"Type 80 D-96 查表失敗: 管徑 {size_str}\" 不在 26\"~42\" 範圍"
        return result

    type_key = "b" if table_a_symbol == "B" else "a"
    default_lops = row["L"]
    hops, lops = _parse_hops_lops(fullstring, default_lops)
    foot_width = row["foot_b"] if type_key == "b" else row["foot_a"]
    side_height = row["e_b"] if type_key == "b" else row["e_a"]
    saddle_height = row["a_b"] if type_key == "b" else row["a_a"]

    add_plate_entry(result, lops, side_height, 16, "SADDLE_SIDE_PLATE", material, plate_qty=2)
    result.entries[-1].remark = f"D-96 NO.1 side plate x2, type={table_a_symbol or 'A'}, h={row['h_' + type_key]}"

    add_plate_entry(result, lops, foot_width, 16, "SADDLE_FOOT_PLATE", material)
    result.entries[-1].remark = "D-96 NO.2 foot plate"

    add_plate_entry(result, lops, row["b"], 16, "SADDLE_ARC_PLATE", material)
    result.entries[-1].remark = "D-96 NO.3 saddle arc plate, 16t"

    add_plate_entry(result, saddle_height, side_height, 12, "STIFFENER_PLATE", material, plate_qty=4)
    result.entries[-1].remark = "D-96 NO.4 stiffener plate x4, 12t"

    add_plate_entry(result, 400, round(_pad_width(pipe_size), 1), 12, "REINFORCING_PAD", material)
    result.entries[-1].remark = "D-96 NO.5 optional 12t reinforcing pad; included for D-96 baseline"

    add_steel_section_entry(result, "Angle", "100*100*10", lops, 2, material)
    result.entries[-1].remark = "D-96 NO.6 stop angle x2; length uses LOPS pending cutting detail"

    result.warnings.append(
        "Type 80 D-96 NO.7 has PLATE 6 THK x6, but cutting dimensions are not shown in provided D-96 image; not included"
    )
    result.warnings.append(f"Type 80 D-96 HOPS={hops}, LOPS={lops}, material symbol={material_symbol or 'NONE'}")

    return result
