"""
Type 15 計算器 - 結構鋼立柱 + Stopper 限位支撐 (落在 existing steel 上)
Heavy duty structural sliding support, steel-structure mounted

格式: 15-{line_size}-{LL}{HH}
  例: 15-2B-1005 → A=2", L=1000mm, H=500mm
- 第二段: Supporting Pipe Size A
- 第三段: 4碼數字，前2碼=L(×100mm)，後2碼=H(×100mm)

與 TYPE-14 差異:
  TYPE-14 = ground mounted (foundation + anchor bolt)
  TYPE-15 = steel structure mounted (existing steel, 無 anchor bolt)
  - Base Plate = D×D×F (無鑽孔)
  - 無 EXP.BOLT
  - P 值不同

構件 (VBA 對照):
  1. Supporting Pipe A (垂直柱): H - 2×F - channelHeight, pipe_sch, SUS304
     ※ 長度 ≤ 0 時跳過
  2. Channel (MEMBER "N"): length = L, A36/SS400
  3. Wing Plate: Q × P × F, A36/SS400
  4. Stopper Plate: M × K × 6t, A36/SS400
  5. Base Plate: D × D × F (無鑽孔), A36/SS400
  6. Top Plate (B SQ): B × B × F, A36/SS400

VBA 對照: A1_Type_Calculator_.bas Sub Type_15 (line 660-785)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..steel import add_steel_section_entry
from ..component_rules import DEFAULT_UPPER_MATERIAL, resolve_material
from data.type15_table import get_type15_data, get_type15_h_max

_STOPPER_T = 6  # mm


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # ── 第二段: pipe size A ──
    part2 = get_part(fullstring, 2)
    line_size = get_lookup_value(part2)

    # 查表
    data = get_type15_data(int(line_size))
    if not data:
        result.error = (
            f"Type 15: Pipe size {part2} ({line_size}\") 不在查表範圍 "
            f"(2\"/3\"/4\"/6\"/8\"/10\"/12\")"
        )
        return result

    # ── 第三段: LL + HH (4 碼) ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) != 4 or not part3.isdigit():
        result.error = f"Type 15: 第三段 '{part3}' 格式不正確，需為4碼數字 (LLHH)"
        return result

    l_val = int(part3[:2]) * 100   # L (mm)
    h_val = int(part3[2:]) * 100   # H (mm)

    F = data["F"]
    member_spec = data["member"]                         # e.g. "C100X50X5"
    channel_height = int(member_spec[1:4])               # "C100..." → 100
    channel_dim = member_spec[1:].replace("X", "*")      # "100*50*5"
    pipe_material = resolve_material(overrides=overrides, default=DEFAULT_UPPER_MATERIAL)

    # ── warnings: L/H 上限 ──
    h_max = get_type15_h_max(int(line_size), l_val)
    if h_max is not None and h_val > h_max:
        result.warnings.append(
            f"H={h_val}mm 超過 L={l_val}mm 時的建議上限 {h_max}mm（照算）"
        )

    # ── 1. Supporting Pipe A (垂直柱) ──
    pipe_length = h_val - 2 * F - channel_height
    if pipe_length > 0:
        add_pipe_entry(result, line_size, data["pipe_sch"], pipe_length, pipe_material)

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

    # ── 5. Base Plate: D × D × F (無鑽孔, 落在 existing steel) ──
    add_plate_entry(
        result,
        plate_a=data["D"],
        plate_b=data["D"],
        plate_thickness=F,
        plate_name="Plate_BASE",
    )

    # ── 6. Top Plate (B SQ): B × B × F ──
    add_plate_entry(
        result,
        plate_a=data["B"],
        plate_b=data["B"],
        plate_thickness=F,
        plate_name="Plate_TOP",
    )

    return result
