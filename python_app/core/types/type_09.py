"""
Type 09 計算器 - 可調式螺桿支撐 (Threaded Adjustable Support)
格式: 09-{line_size}-{H}{M42_letter}
  例: 09-2B-05B
- 第二段: Supported Line Size A
- 第三段: H(前2碼×100mm) + M42字母(末字母)

PDF 限制: H≤1500mm, M42僅允許 B/H

構件 (VBA 對照):
  1. Main Pipe (dummy): L+100, 同管 2" SCH查表, upper_material (SUS304)
  2. Support Pipe: H-100, 同管 2" SCH查表, A53Gr.B (黑鐵)
     ※ Support Pipe 長度 ≤ 0 時跳過
  3. M42 底板 (用 support pipe size = 2" 查表)
  4. Machine Bolt: 1-5/8"×150L, A307Gr.B, 1 SET, 20kg
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..m42 import perform_action_by_letter
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    MaterialSpec,
    resolve_hardware_material,
)
from data.type09_table import get_type09_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_SUPPORT_PIPE_MATERIAL = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
_THREADED_ROD_MATERIAL = _material_spec(HardwareKind.THREADED_ROD, "A307Gr.B(HDG)")
_HEX_NUT_MATERIAL = _material_spec(HardwareKind.HEAVY_HEX_NUT, "A307Gr.B(HDG)")


_MAX_H = 1500
_ALLOWED_M42_LETTERS = {"B", "H"}


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # 第二段: line size
    part2 = get_part(fullstring, 2)
    line_size = int(get_lookup_value(part2))

    # 查表
    data = get_type09_data(line_size)
    if not data:
        result.error = f"Type 09: Line size {part2} ({line_size}\") 不在查表範圍 (2\"/3\"/4\")"
        return result

    # 第三段: H + letter
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h_val = int(part3[:-1]) * 100

    # 取得上層材質
    from ..calculator import get_analysis_setting
    upper_material = overrides.get("upper_material") or get_analysis_setting("upper_material") or "SUS304"
    upper_material_spec = _material_spec(HardwareKind.SUPPORT_PIPE, upper_material)

    support_pipe = data["support_pipe"]  # 都是 2"
    pipe_sch = data["pipe_sch"]
    l_val = data["L"]

    # ── warnings ──
    if h_val > _MAX_H:
        result.warnings.append(f"H={h_val}mm 超過建議上限 {_MAX_H}mm（照算）")
    if letter not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 09 允許範圍 {sorted(_ALLOWED_M42_LETTERS)}（照算）"
        )
    if letter == "B":
        result.warnings.append("M42 Type-B: H 應從最低鋪面高程起算 (NOTE 6)")

    # ── 1. Main Pipe (dummy) ──
    main_pipe_length = l_val + 100
    add_pipe_entry(result, support_pipe, pipe_sch, main_pipe_length, upper_material_spec)

    # ── 2. Support Pipe ──
    support_pipe_length = h_val - 100
    if support_pipe_length > 0:
        add_pipe_entry(result, support_pipe, pipe_sch, support_pipe_length, _SUPPORT_PIPE_MATERIAL)

    # ── 3. M42 底板 (用 support pipe size = 2") ──
    perform_action_by_letter(result, letter, support_pipe)

    # ── 4. M.B. (全牙螺桿) ──
    _add_threaded_rod_entry(result, _THREADED_ROD_MATERIAL)

    # ── 5. Hex Nut (六角螺帽) ×2 ──
    _add_hex_nut_entry(result, _HEX_NUT_MATERIAL)

    return result


def _add_threaded_rod_entry(result: AnalysisResult, material: MaterialSpec):
    """全牙螺桿: 1-5/8"×150L (FULL THREADED), A307Gr.B(HDG), 1 EA, ~1.6kg"""
    entry = AnalysisEntry()
    entry.name = "M.B.(FULL THREADED)"
    entry.spec = '1-5/8"*150L'
    entry.material = material.name
    entry.material_canonical_id = material.canonical_id
    entry.quantity = 1
    entry.unit_weight = 1.6
    entry.total_weight = 1.6
    entry.unit = "EA"
    entry.factor = 1
    entry.length = 150
    entry.length_subtotal = 0
    entry.qty_subtotal = 1
    entry.weight_output = 1.6
    entry.weight_per_unit = 1.6
    entry.category = "螺栓類"
    result.add_entry(entry)


def _add_hex_nut_entry(result: AnalysisResult, material: MaterialSpec):
    """六角螺帽: 1-5/8", A307Gr.B(HDG), 2 EA, ~0.4kg/顆"""
    entry = AnalysisEntry()
    entry.name = "HEX NUT"
    entry.spec = '1-5/8"'
    entry.material = material.name
    entry.material_canonical_id = material.canonical_id
    entry.quantity = 2
    entry.unit_weight = 0.4
    entry.total_weight = 0.8
    entry.unit = "EA"
    entry.factor = 1
    entry.length = 0
    entry.length_subtotal = 0
    entry.qty_subtotal = 2
    entry.weight_output = 0.8
    entry.weight_per_unit = 0.4
    entry.category = "螺栓類"
    result.add_entry(entry)
