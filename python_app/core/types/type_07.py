"""
Type 07 計算器 - 滑動彎頭支撐
格式: 07-{line_size}-{H}{M42_letter}
  例: 07-2B-20J
- 第二段: Supported Line Size A
- 第三段: H(數字×100mm) + M42代碼(字母, 應為J)

PDF 限制: 2000 < H < 3500, M42 僅允許 J
Note 1: alloy/stainless → material is resolved through hardware material policy

構件:
  1. Pipe B (dummy): L+100mm, material by resolver
  2. Pipe C (支撐柱): H - 100 - plate_F厚 - M42板厚, material by resolver
  3. Plate E (底板)
  4. Plate F (滑動板)
  5. M42 底板 (用 Pipe C 尺寸查表)
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..m42 import perform_action_by_letter
from ..material_identity import canonical_material_id
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.type07_table import get_type07_data
from data.m42_table import get_m42_data

_MIN_H = 2000
_MAX_H = 3500
_ALLOWED_M42_LETTERS = {"J"}


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


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

    # 第二段: line size
    part2 = get_part(fullstring, 2)
    line_size = int(get_lookup_value(part2))

    # 查表
    data = get_type07_data(line_size)
    if not data:
        result.error = f"Type 07: Line size {part2} ({line_size}\") 不在查表範圍"
        return result

    # 第三段: H + M42 letter
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h = int(part3[:-1]) * 100

    # H 範圍檢查
    if h < _MIN_H or h > _MAX_H:
        result.warnings.append(
            f"H={h}mm 超出 Type 07 適用範圍 ({_MIN_H}~{_MAX_H}mm)"
        )

    # M42 字母限制
    if letter.upper() not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 07 允許範圍 (僅 J)"
        )

    pipe_b_size, pipe_b_sch = data["pipe_b"]
    pipe_c_size, pipe_c_sch = data["pipe_c"]
    plate_e = data["plate_e"]  # (w, h, t)
    plate_f = data["plate_f"]  # (w, h, t)
    L = data["L"]

    # 取 M42 板厚 (用 pipe C 尺寸查)
    pipe_c_val = int(get_lookup_value(pipe_c_size))
    m42_data = get_m42_data(pipe_c_val)
    m42_plate_thickness = m42_data["plate_thickness"]

    upper_material = _material(HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides)
    support_material = _material(HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides)
    plate_material = _material(HardwareKind.SUPPORT_PLATE, service=service, overrides=material_overrides)

    # 1. Pipe B (dummy): L + 100
    pipe_b_length = L + 100
    add_pipe_entry(result, pipe_b_size, pipe_b_sch, pipe_b_length, upper_material)

    # 2. Pipe C (支撐柱): H - 100 - plate_F厚 - M42板厚
    pipe_c_length = h - 100 - plate_f[2] - m42_plate_thickness
    add_pipe_entry(result, pipe_c_size, pipe_c_sch, pipe_c_length, support_material)

    # 3. Plate E (底板)
    add_plate_entry(result, plate_e[0], plate_e[1], plate_e[2], "Plate_E", material=plate_material)

    # 4. Plate F (滑動板)
    add_plate_entry(result, plate_f[0], plate_f[1], plate_f[2], "Plate_F", material=plate_material)

    # 5. M42 底板 (用 Pipe C 尺寸查)
    m42_start = len(result.entries)
    perform_action_by_letter(result, letter, pipe_c_val)
    _attach_existing_material_identity(result, m42_start)

    return result
