"""
Type 14 計算器 - 結構鋼立柱 + 雙板托架 + Stopper 限位支撐
Heavy duty structural sliding support with stopper

格式: 14-{line_size}-{LL}{HH}
  例: 14-2B-1005 → A=2", L=1000mm, H=500mm
- 第二段: Supporting Pipe Size A
- 第三段: 4碼數字，前2碼=L(×100mm)，後2碼=H(×100mm)

無 M42 — 自帶 Base Plate + Anchor Bolt (foundation by civil)

構件 (VBA 對照):
  1. Supporting Pipe A (垂直柱): length = H - 2×F - channelHeight, pipe_sch, SUS304
     ※ 長度 ≤ 0 時跳過
  2. Channel (MEMBER "N"): length = L, A36/SS400
  3. Wing Plate: Q × P × F, A36/SS400
  4. Stopper Plate: M × K × 6t, A36/SS400
  5. Base Plate: C × C × F (有4孔 ØE), A36/SS400
  6. Top Plate (B SQ): B × B × F, A36/SS400
  7. EXP.BOLT (Anchor Bolt): J size, 4 EA, SUS304

VBA 對照: A1_Type_Calculator_.bas Sub Type_14 (line 514-659)
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..steel import add_steel_section_entry
from data.type14_table import get_type14_data, get_type14_h_max

_STOPPER_T = 6  # mm


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # ── 第二段: pipe size A ──
    part2 = get_part(fullstring, 2)
    line_size = get_lookup_value(part2)

    # 查表
    data = get_type14_data(int(line_size))
    if not data:
        result.error = (
            f"Type 14: Pipe size {part2} ({line_size}\") 不在查表範圍 "
            f"(2\"/3\"/4\"/6\"/8\"/10\"/12\")"
        )
        return result

    # ── 第三段: LL + HH (4 碼) ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) != 4 or not part3.isdigit():
        result.error = f"Type 14: 第三段 '{part3}' 格式不正確，需為4碼數字 (LLHH)"
        return result

    l_val = int(part3[:2]) * 100   # L (mm)
    h_val = int(part3[2:]) * 100   # H (mm)

    pipe_sch = data["pipe_sch"]
    F = data["F"]
    member_spec = data["member"]                         # e.g. "C100X50X5"
    channel_height = int(member_spec[1:4])               # "C100..." → 100
    channel_dim = member_spec[1:].replace("X", "*")      # "100*50*5"

    # ── warnings: L/H 上限 ──
    h_max = get_type14_h_max(int(line_size), l_val)
    if h_max is not None and h_val > h_max:
        result.warnings.append(
            f"H={h_val}mm 超過 L={l_val}mm 時的建議上限 {h_max}mm（照算）"
        )

    # ── 1. Supporting Pipe A (垂直柱) ──
    # VBA: Main_Pipe_Length = H - F(top) - channelHeight - F(base)
    pipe_length = h_val - 2 * F - channel_height
    if pipe_length > 0:
        add_pipe_entry(result, line_size, pipe_sch, pipe_length, "SUS304")

    # ── 2. Channel (MEMBER "N") ──
    add_steel_section_entry(result, "Channel", channel_dim, l_val)

    # ── 3. Wing Plate: Q × P × F ──
    add_plate_entry(
        result,
        plate_a=data["Q"],
        plate_b=data["P"],
        plate_thickness=F,
        plate_name="Plate_WING",
    )

    # ── 4. Stopper Plate: M × K × 6t ──
    add_plate_entry(
        result,
        plate_a=data["M"],
        plate_b=data["K"],
        plate_thickness=_STOPPER_T,
        plate_name="Plate_STOPPER",
    )

    # ── 5. Base Plate: C × C × F (有4孔 ØE) ──
    add_plate_entry(
        result,
        plate_a=data["C"],
        plate_b=data["C"],
        plate_thickness=F,
        plate_name="Plate_BASE",
        bolt_switch=True,
        bolt_x=data["D"],
        bolt_y=data["D"],
        bolt_hole=data["E"],
        bolt_size=data["J"],
    )

    # ── 6. Top Plate (B SQ): B × B × F ──
    add_plate_entry(
        result,
        plate_a=data["B"],
        plate_b=data["B"],
        plate_thickness=F,
        plate_name="Plate_TOP",
    )

    # ── 7. EXP.BOLT (Anchor Bolt): J size, 4 EA ──
    _add_anchor_bolt_entry(result, data["J"])

    return result


def _add_anchor_bolt_entry(result: AnalysisResult, bolt_size: str):
    """Anchor Bolt (EXP.BOLT): 4 EA
    bolt_size: '5/8"', '3/4"', '1"'
    """
    # VBA: unit_weight = 1 kg per bolt
    entry = AnalysisEntry()
    entry.name = "EXP.BOLT"
    entry.spec = bolt_size
    entry.material = "SUS304"
    entry.quantity = 4
    entry.unit_weight = 1
    entry.total_weight = 4
    entry.unit = "SET"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 4
    entry.weight_output = 4
    entry.weight_per_unit = 1
    entry.category = "螺栓類"
    result.add_entry(entry)
