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
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    ServiceClass,
    resolve_hardware_material,
)
from data.type07_table import get_type07_data
from data.m42_table import get_m42_data

_MIN_H = 2000
_MAX_H = 3500
_ALLOWED_M42_LETTERS = {"J"}


def _service_from_overrides(overrides: dict | None) -> ServiceClass:
    value = (overrides or {}).get("service") or (overrides or {}).get("service_class")
    if isinstance(value, ServiceClass):
        return value
    if value:
        return ServiceClass(str(value).strip().lower().replace("-", "_"))
    return ServiceClass.AMBIENT


def _material_overrides_from_dict(
    overrides: dict | None,
    *,
    legacy_kinds: set[HardwareKind],
) -> HardwareMaterialOverrides | None:
    if not overrides:
        return None
    existing = overrides.get("hardware_material_overrides")
    if isinstance(existing, HardwareMaterialOverrides):
        return existing

    per_kind = {}
    for key, material in (overrides.get("hardware_material_by_kind") or {}).items():
        kind = key if isinstance(key, HardwareKind) else HardwareKind(str(key).strip().lower())
        per_kind[kind] = material

    legacy_material = overrides.get("material") or overrides.get("upper_material")
    if legacy_material:
        for kind in legacy_kinds:
            per_kind.setdefault(kind, legacy_material)

    all_hardware = overrides.get("hardware_material")
    if not per_kind and not all_hardware:
        return None
    return HardwareMaterialOverrides(per_kind=per_kind, all_hardware=all_hardware)


def _material(
    kind: HardwareKind,
    *,
    service: ServiceClass,
    overrides: HardwareMaterialOverrides | None,
) -> str:
    return resolve_hardware_material(kind, service=service, overrides=overrides).name


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    service = _service_from_overrides(overrides)
    material_overrides = _material_overrides_from_dict(
        overrides,
        legacy_kinds={HardwareKind.UPPER_BRACKET},
    )

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

    upper_material = _material(HardwareKind.UPPER_BRACKET, service=service, overrides=material_overrides)
    support_material = _material(HardwareKind.STRUCTURAL_STRUT, service=service, overrides=material_overrides)
    plate_material = _material(HardwareKind.GUSSET_PLATE, service=service, overrides=material_overrides)

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
    perform_action_by_letter(result, letter, pipe_c_val)

    return result
