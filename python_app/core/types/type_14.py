"""
Type 14 計算器 - 結構鋼立柱 + 雙板托架 + Stopper 限位支撐
Heavy duty structural sliding support with stopper

格式: 14-{line_size}-{LL}{HH}
  例: 14-2B-1005 → A=2", L=1000mm, H=500mm
- 第二段: Supporting Pipe Size A
- 第三段: 4碼數字，前2碼=L(×100mm)，後2碼=H(×100mm)

無 M42 — 自帶 Base Plate + Anchor Bolt (foundation by civil)

構件 (VBA 對照):
  1. Supporting Pipe A (垂直柱): length = H - 2×F - channelHeight, pipe_sch, material by resolver
     ※ 長度 ≤ 0 時跳過
  2. Channel (MEMBER "N"): length = L, material by resolver
     ※ 10" / 12" 視為 DETAIL "a"，改為 2 支橫向 Channel
  3. Wing Plate: Q × P × F, 4 PC, material by resolver
  4. Stopper Plate: M × K × 6t, 2 PC, material by resolver
  5. Base Plate: C × C × F (有4孔 ØE), material by resolver
  6. Top Plate (B SQ): B × B × F, material by resolver
  7. EXP.BOLT (Anchor Bolt): J size, 4 EA, material by resolver

VBA 對照: A1_Type_Calculator_.bas Sub Type_14 (line 514-659)
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..steel import add_steel_section_entry
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.type14_table import get_type14_data, get_type14_h_max

_STOPPER_T = 6  # mm
_WING_QTY = 4
_STOPPER_QTY = 2


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def _attach_material_identity(result: AnalysisResult, material: MaterialSpec):
    if result.entries:
        result.entries[-1].material_canonical_id = material.canonical_id


def _annotate_last_entry(result: AnalysisResult, remark: str):
    if result.entries:
        result.entries[-1].remark = remark


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE, HardwareKind.ANCHOR_BOLT),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides

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
    support_material = _material(HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides)
    steel_material = _material(HardwareKind.STRUCTURAL_STRUT, service=service, overrides=material_overrides)
    plate_material = _material(HardwareKind.SUPPORT_PLATE, service=service, overrides=material_overrides)
    anchor_material = _material(HardwareKind.ANCHOR_BOLT, service=service, overrides=material_overrides)

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
        add_pipe_entry(result, line_size, pipe_sch, pipe_length, support_material)

    # ── 2. Channel (MEMBER "N") ──
    channel_qty = 2 if int(line_size) >= 10 else 1
    add_steel_section_entry(
        result,
        "Channel",
        channel_dim,
        l_val,
        steel_qty=channel_qty,
        material=steel_material.name,
    )
    _attach_material_identity(result, steel_material)
    if channel_qty == 2:
        _annotate_last_entry(result, 'detail_a_double_channel_for_10in_and_12in')

    # ── 3. Wing Plate: Q × P × F ──
    add_plate_entry(
        result,
        plate_a=data["Q"],
        plate_b=data["P"],
        plate_thickness=F,
        plate_name="Plate_WING",
        material=plate_material,
        plate_qty=_WING_QTY,
    )
    _annotate_last_entry(
        result,
        f'shape=wing_plate; size={data["Q"]}x{data["P"]}x{F}; qty={_WING_QTY}; field_cut=P',
    )

    # ── 4. Stopper Plate: M × K × 6t ──
    add_plate_entry(
        result,
        plate_a=data["M"],
        plate_b=data["K"],
        plate_thickness=_STOPPER_T,
        plate_name="Plate_STOPPER",
        material=plate_material,
        plate_qty=_STOPPER_QTY,
    )
    _annotate_last_entry(
        result,
        f'shape=stopper_plate; size={data["M"]}x{data["K"]}x{_STOPPER_T}; qty={_STOPPER_QTY}; lip=10C',
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
        material=plate_material,
    )

    # ── 6. Top Plate (B SQ): B × B × F ──
    add_plate_entry(
        result,
        plate_a=data["B"],
        plate_b=data["B"],
        plate_thickness=F,
        plate_name="Plate_TOP",
        material=plate_material,
    )

    # ── 7. EXP.BOLT (Anchor Bolt): J size, 4 EA ──
    _add_anchor_bolt_entry(result, data["J"], material=anchor_material)

    return result


def _add_anchor_bolt_entry(result: AnalysisResult, bolt_size: str, *, material: MaterialSpec):
    """Anchor Bolt (EXP.BOLT): 4 EA
    bolt_size: '5/8"', '3/4"', '1"'
    """
    # VBA: unit_weight = 1 kg per bolt
    entry = AnalysisEntry()
    entry.name = "EXP.BOLT"
    entry.spec = bolt_size
    entry.material = material.name
    entry.material_canonical_id = material.canonical_id
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
