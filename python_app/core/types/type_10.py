"""
Type 10 計算器 - 可調式 Dummy Pipe 支撐 (Four-Bolt Adjustable Support)
格式: 10-{line_size}-{H}{M42_letter}
  例: 10-6B-05B
- 第二段: Supported Line Size A
- 第三段: H(前2碼×100mm) + M42字母(末字母)

PDF 限制: H≤1500mm

構件:
  1. Main Pipe (dummy): L+100+100, pipe_size_b / pipe_sch, temporary SUS304 basis
  2. Support Pipe (vertical): H-100-100-100, pipe_size_b / pipe_sch, A53Gr.B basis
     ※ Support Pipe 長度 ≤ 0 時跳過
  3. Plate F: plate_w × plate_w × plate_t, 有鑽孔(4×dø), 2 PC
  4. Adjustable Bolt (J bolt): bolt_spec, 4 EA
  5. HEX NUT: 對應bolt規格, 16 EA (每支 J bolt 4 顆)
  6. M42 底板 (用 pipe_size_b 查表)

Note 6 禁用: 溫度≤10°C 或 ≥400°C, 壓力≥70Kg/cm²G
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..m42 import perform_action_by_letter
from ..material_identity import canonical_material_id
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.type10_table import get_type10_data

_MAX_H = 1500
_ALLOWED_M42_LETTERS = {"A", "B", "E", "G"}


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def _fixed_material(kind: HardwareKind, material_name: str, *, service) -> MaterialSpec:
    return resolve_hardware_material(
        kind,
        service=service,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


def _attach_existing_material_identity(result: AnalysisResult, start_index: int):
    for entry in result.entries[start_index:]:
        canonical_id = canonical_material_id(entry.material)
        if canonical_id:
            entry.material_canonical_id = canonical_id


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides

    # 第二段: line size A
    part2 = get_part(fullstring, 2)
    line_size = get_lookup_value(part2)

    # 查表
    data = get_type10_data(line_size)
    if not data:
        result.error = (
            f"Type 10: Line size {part2} ({line_size}\") 不在查表範圍 "
            f"(1.5\"/2\"/2.5\"/3\"/4\"~20\"/28\"/32\"/36\"/44\")"
        )
        return result

    # 第三段: H + letter
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h_val = int(part3[:-1]) * 100

    # Current designation cannot distinguish elbow vs inserted pipe variants.
    # Keep the common D-10 basis here and leave variant modeling as a future extension.
    upper_material = _fixed_material(HardwareKind.SUPPORT_PIPE, "SUS304", service=service)
    support_material = _fixed_material(HardwareKind.SUPPORT_PIPE, "A53Gr.B", service=service)
    plate_material = _material(HardwareKind.SUPPORT_PLATE, service=service, overrides=material_overrides)
    bolt_material = _material(HardwareKind.ANCHOR_BOLT, service=service, overrides=material_overrides)
    nut_material = _material(HardwareKind.HEAVY_HEX_NUT, service=service, overrides=material_overrides)

    pipe_size_b = data["pipe_size_b"]
    pipe_sch = data["pipe_sch"]
    l_val = data["L"]
    plate_t = data["plate_t"]
    plate_w = data["plate_w"]
    bolt_spec = data["bolt_spec"]
    w_val = data["W"]
    d_phi = data["d_phi"]

    # ── warnings ──
    if h_val > _MAX_H:
        result.warnings.append(f"H={h_val}mm 超過建議上限 {_MAX_H}mm（照算）")
    if letter.upper() not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 10 允許範圍 {sorted(_ALLOWED_M42_LETTERS)}（照算）"
        )

    # ── 1. Main Pipe (dummy, 水平) ──
    main_pipe_length = l_val + 100 + 100
    add_pipe_entry(result, pipe_size_b, pipe_sch, main_pipe_length, upper_material)

    # ── 2. Support Pipe (垂直柱) ──
    support_pipe_length = h_val - 100 - 100 - 100
    if support_pipe_length > 0:
        add_pipe_entry(result, pipe_size_b, pipe_sch, support_pipe_length, support_material)

    # ── 3. Plate F (有鑽孔, 4×dø) ──
    # bolt_spec 例如 "M16*180L"，取 bolt 直徑部分作為 bolt_size
    bolt_dia = bolt_spec.split("*")[0]  # "M16"
    add_plate_entry(
        result,
        plate_a=plate_w,
        plate_b=plate_w,
        plate_thickness=plate_t,
        plate_name="Plate_F",
        bolt_switch=True,
        bolt_x=w_val,
        bolt_y=w_val,
        bolt_hole=d_phi,
        bolt_size=bolt_dia,
        material=plate_material,
        plate_qty=2,
    )

    # ── 4. Adjustable Bolt (J bolt), 4 EA ──
    _add_adj_bolt_entry(result, bolt_spec, material=bolt_material)

    # ── 5. HEX NUT, 16 EA ──
    _add_hex_nut_entry(result, bolt_dia, material=nut_material)

    # ── 6. M42 底板 (用 pipe_size_b 查表) ──
    m42_start = len(result.entries)
    perform_action_by_letter(result, letter, pipe_size_b)
    _attach_existing_material_identity(result, m42_start)

    return result


def _add_adj_bolt_entry(result: AnalysisResult, bolt_spec: str, *, material: MaterialSpec):
    """Adjustable Bolt (J bolt): 4 EA
    bolt_spec 格式: "M12*160L", "M16*180L", "M20*180L"
    """
    # 估算重量: M12~0.8kg, M16~1.5kg, M20~2.5kg
    weight_map = {"M12": 0.8, "M16": 1.5, "M20": 2.5}
    bolt_dia = bolt_spec.split("*")[0]
    unit_w = weight_map.get(bolt_dia, 1.5)

    entry = AnalysisEntry()
    entry.name = "ADJ.BOLT"
    entry.spec = bolt_spec
    entry.material = material.name
    entry.material_canonical_id = material.canonical_id
    entry.quantity = 4
    entry.unit_weight = unit_w
    entry.total_weight = round(unit_w * 4, 2)
    entry.unit = "EA"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 4
    entry.weight_output = round(unit_w * 4, 2)
    entry.weight_per_unit = unit_w
    entry.category = "螺栓類"
    result.add_entry(entry)


def _add_hex_nut_entry(result: AnalysisResult, bolt_dia: str, *, material: MaterialSpec):
    """HEX NUT: 16 EA (每支 J bolt 配 4 顆)
    bolt_dia: "M12", "M16", "M20"
    """
    nut_weight_map = {"M12": 0.15, "M16": 0.3, "M20": 0.5}
    unit_w = nut_weight_map.get(bolt_dia, 0.3)

    entry = AnalysisEntry()
    entry.name = "HEX NUT"
    entry.spec = bolt_dia
    entry.material = material.name
    entry.material_canonical_id = material.canonical_id
    entry.quantity = 16
    entry.unit_weight = unit_w
    entry.total_weight = round(unit_w * 16, 2)
    entry.unit = "EA"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 16
    entry.weight_output = round(unit_w * 16, 2)
    entry.weight_per_unit = unit_w
    entry.category = "螺栓類"
    result.add_entry(entry)
