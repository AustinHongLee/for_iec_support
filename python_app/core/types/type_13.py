"""
Type 13 計算器 - Clamp 式雙板夾持 Dummy Pipe 支撐
Clamped (non-welded) dummy pipe support with plate reinforcement

格式: 13-{line_size}-{H}{M42_letter}
  例: 13-6B-05B  → A=6", H=500, M42=B

- 第二段: Supported Line Size A
- 第三段: H(前2碼×100mm) + M42字母(末字母)

與 TYPE-12 差異:
  TYPE-12 = 焊接 (welded)
  TYPE-13 = 管夾 (clamped, 不焊主管)
  - 多 Pipe Clamp TYPE-A (M-4) + Non-Asbestos Sheet (M-47)
  - 無材料尾碼 (板材固定為碳鋼)
  - 幾何尺寸表完全相同

PDF 限制: H≤1500mm, MAX LINE TEMP 750°F
Note 1: 通常用於合金鋼 / 不鏽鋼管線 (不允許焊接主管)
Note 6: M42 底座類型 A,B,E,G 時，H 從地坪最低點起算

構件:
  1. Pipe Clamp TYPE-A (M-4): 1 SET，夾持主管
  2. Non-Asbestos Sheet (M-47): 1 PC，管 ↔ clamp 之間隔熱防磨
  3. Supporting Pipe B (垂直柱): H-100, pipe_size_b / pipe_sch, A53Gr.B
     ※ 長度 ≤ 0 時跳過
  4. Plate P (側板): plate_len × plate_wid × plate_t, A36/SS400
  5. Cover Plate (蓋板): 75×75×6t, A36/SS400
  6. M42 底板 (用 pipe_size_b 查表)

VBA 對照: VBA 未實作 Type 13 (僅有註解佔位)
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..m42 import perform_action_by_letter
from ..component_rules import component_or_estimated_clamp_weight
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type13_table import get_type13_data
from data.m47_table import build_m47_item
from data.m4_table import build_m4_item


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_CLAMP_MATERIAL = _material_spec(HardwareKind.CLAMP_BODY, "A36/SS400")
_M47_MATERIAL = _material_spec(HardwareKind.COLD_SHOE_INSULATION_CLAMP, "M-47")
_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


_MAX_H = 1500
_COVER_PLATE_SIZE = 75   # mm, square
_COVER_PLATE_T = 6       # mm

# Note 6: 這些 M42 底座類型，H 從地坪最低點起算
_PAVING_LETTERS = {"A", "B", "E", "G"}


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # ── 第二段: line size A ──
    part2 = get_part(fullstring, 2)
    line_size = get_lookup_value(part2)

    # 查表
    data = get_type13_data(int(line_size))
    if not data:
        result.error = (
            f"Type 13: Line size {part2} ({line_size}\") 不在查表範圍 "
            f"(2\"/3\"/4\"/6\"/8\"/10\"/12\"/14\"/16\")"
        )
        return result

    # ── 第三段: H + M42 letter (無材料尾碼) ──
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h_val = int(part3[:-1]) * 100

    pipe_size_b = data["pipe_size_b"]
    pipe_sch = data["pipe_sch"]
    plate_len = data["plate_len"]
    plate_wid = data["plate_wid"]
    plate_t = data["plate_t"]

    # ── warnings ──
    if h_val > _MAX_H:
        result.warnings.append(f"H={h_val}mm 超過建議上限 {_MAX_H}mm（照算）")
    if letter in _PAVING_LETTERS:
        result.warnings.append(
            f"M42 底座類型 {letter} — H 應從地坪最低點 (lowest point of paving) 起算 (NOTE 6)"
        )

    # ── 1. Pipe Clamp TYPE-A (M-4) ──
    _add_pipe_clamp_entry(result, line_size)

    # ── 2. Non-Asbestos Sheet (M-47) ──
    _add_non_asbestos_sheet_entry(result, line_size)

    # ── 3. Supporting Pipe B (垂直柱) ──
    support_pipe_length = h_val - 100
    if support_pipe_length > 0:
        add_pipe_entry(result, pipe_size_b, pipe_sch, support_pipe_length, _SUPPORT_PIPE_MATERIAL)

    # ── 4. Plate P (側板, 碳鋼) ──
    add_plate_entry(
        result,
        plate_a=plate_len,
        plate_b=plate_wid,
        plate_thickness=plate_t,
        plate_name="Plate_P",
        material=_SUPPORT_PLATE_MATERIAL,
        plate_role="generic_plate",
    )

    # ── 5. Cover Plate (蓋板, 75×75×6t, 碳鋼) ──
    add_plate_entry(
        result,
        plate_a=_COVER_PLATE_SIZE,
        plate_b=_COVER_PLATE_SIZE,
        plate_thickness=_COVER_PLATE_T,
        plate_name="COVER_PL",
        material=_SUPPORT_PLATE_MATERIAL,
        plate_role="cover_plate",
    )

    # ── 6. M42 底板 (用 pipe_size_b 查表) ──
    perform_action_by_letter(result, letter, pipe_size_b)

    return result


def _add_pipe_clamp_entry(result: AnalysisResult, line_size: float):
    """Pipe Clamp TYPE-A (SEE M-4): 1 SET
    由 M-4 component table 取得重量與 designation
    """
    clamp_item = build_m4_item(line_size)
    unit_w = component_or_estimated_clamp_weight(clamp_item, line_size, component_id="M-4")
    spec = clamp_item["designation"] if clamp_item else f'TYPE-A {int(line_size)}"'

    entry = AnalysisEntry()
    entry.name = "PIPE CLAMP"
    entry.spec = spec
    entry.material = _CLAMP_MATERIAL.name
    entry.material_canonical_id = _CLAMP_MATERIAL.canonical_id
    entry.quantity = 1
    entry.unit_weight = unit_w
    entry.total_weight = unit_w
    entry.unit = "SET"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 1
    entry.weight_output = unit_w
    entry.weight_per_unit = unit_w
    entry.category = "管路類"
    if clamp_item:
        entry.remark = f'SEE M-4, rod {clamp_item["rod_size_a"]}; weight estimated'
        if not clamp_item.get("weight_ready"):
            result.warnings.append("M-4 clamp 無 source unit-weight 欄，PIPE CLAMP 重量使用集中估算規則")
    else:
        entry.remark = "M-4 lookup failed; weight estimated by core.component_rules"
        result.warnings.append("M-4 table lookup failed，PIPE CLAMP 重量使用集中估算規則")
    result.add_entry(entry)


def _add_non_asbestos_sheet_entry(result: AnalysisResult, line_size: float):
    """Non-Asbestos Sheet (SEE M-47): 1 PC
    由 M-47 component table 取得尺寸與重量
    """
    gasket_item = build_m47_item(line_size)
    if gasket_item:
        w = gasket_item["width_mm"]
        l = gasket_item["length_mm"]
        thickness = gasket_item["thickness_mm"]
        weight = gasket_item["unit_weight_kg"]
    else:
        w, l, thickness, weight = 50, 150, 3, 0.03

    entry = AnalysisEntry()
    entry.name = "NON-ASBESTOS"
    entry.spec = f"{w}×{l}×{thickness:g}t"
    entry.material = _M47_MATERIAL.name
    entry.material_canonical_id = _M47_MATERIAL.canonical_id
    entry.quantity = 1
    entry.unit_weight = weight
    entry.total_weight = weight
    entry.unit = "PC"
    entry.factor = 1
    entry.length = l
    entry.width = w
    entry.length_subtotal = 0
    entry.qty_subtotal = 1
    entry.weight_output = weight
    entry.weight_per_unit = weight
    entry.category = "管路類"
    if gasket_item:
        entry.remark = gasket_item["thickness_source"]
    result.add_entry(entry)
