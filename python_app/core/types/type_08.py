"""
Type 08 計算器 - 立柱式托板支撐 + 滑動 + Stopper
格式: 08-{pipe_size}-{LH}{M42_letter}
  例: 08-2B-1005G
- 第二段: Supporting Pipe Size A
- 第三段: L(前2碼×100mm) + H(中2碼×100mm) + M42字母(末字母)

PDF 限制: H≤1500mm, L≤1000mm, M42僅允許 G/J

構件 (VBA 對照):
  1. Pipe A (支撐柱): H - 6(top plate厚) - channel高/2 - M42板厚, 黑鐵
  2. Channel N: 長度 = L
  3. M42 底板 (用 pipe size 查表)
  4. Plate(STOPPER): K × M × 6mm
  5. Plate(TOP): B × B × 6mm
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..steel import add_steel_section_entry
from ..m42 import perform_action_by_letter
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type08_table import get_type08_data
from data.m42_table import get_m42_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_STRUCTURAL_MATERIAL = _material_spec(HardwareKind.STRUCTURAL_STRUT, "A36/SS400")
_SUPPORT_PLATE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PLATE, "A36/SS400")


_MAX_H = 1500
_MAX_L = 1000
_ALLOWED_M42_LETTERS = {"G", "J"}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: pipe size
    part2 = get_part(fullstring, 2)
    pipe_size = int(get_lookup_value(part2))

    # 查表
    data = get_type08_data(pipe_size)
    if not data:
        result.error = f"Type 08: Pipe size {part2} ({pipe_size}\") 不在查表範圍"
        return result

    # 第三段: L(前2) + H(中2) + letter(末字母)
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    l_val = int(part3[:2]) * 100
    h_val = int(part3[2:4]) * 100

    # H / L 範圍檢查
    if h_val > _MAX_H:
        result.warnings.append(f"H={h_val}mm 超出 Type 08 適用範圍 (≤ {_MAX_H}mm)")
    if l_val > _MAX_L:
        result.warnings.append(f"L={l_val}mm 超出 Type 08 適用範圍 (≤ {_MAX_L}mm)")

    # M42 字母限制
    if letter.upper() not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 08 允許範圍 (僅 G/J)"
        )

    pipe_sch = data["pipe_sch"]
    member_n = data["member_n"]  # e.g. "C100*50*5"
    k = data["K"]
    m = data["M"]
    b = data["B"]

    # channel 高度 (C100*50*5 -> 100)
    channel_height = int(member_n.split("*")[0][1:])  # 去掉 C 取數字

    # M42 板厚
    m42_data = get_m42_data(pipe_size)
    m42_plate_thickness = m42_data["plate_thickness"]

    # 1. Pipe A (支撐柱): H - 6(top plate厚) - channel高/2 - M42板厚
    top_plate_t = 6
    pipe_length = h_val - top_plate_t - channel_height / 2 - m42_plate_thickness
    add_pipe_entry(result, str(pipe_size), pipe_sch, pipe_length, _SUPPORT_PIPE_MATERIAL)

    # 2. Channel N: 長度 = L
    channel_dim = member_n[1:]  # C100*50*5 -> 100*50*5
    add_steel_section_entry(
        result, "Channel", channel_dim, l_val,
        material=_STRUCTURAL_MATERIAL,
    )

    # 3. M42 底板 (用 pipe size 查表)
    perform_action_by_letter(result, letter, pipe_size)

    # 4. Plate(STOPPER): K × M × 6mm
    add_plate_entry(result, k, m, 6, "Plate_STOPPER", material=_SUPPORT_PLATE_MATERIAL)

    # 5. Plate(TOP): B × B × 6mm
    add_plate_entry(result, b, b, 6, "Plate_TOP", material=_SUPPORT_PLATE_MATERIAL)

    return result
