"""
Type 11 計算器 - 彈簧可變載支撐 (Spring Variable Support)
格式: 11-{line_size}-{H}{M42_letter}
  例: 11-2B-06G
- 第二段: Supported Line Size A
- 第三段: H(前2碼×100mm) + M42字母(末字母)

PDF 限制: M42僅允許 G/J

構件 (VBA 對照 + 修正):
  1. Upper Pipe (dummy): 1.5" SCH.80, L+100, upper_material
  2. Support Pipe (vertical): 2" SCH.40, H-100-(300-9)=H-391, A53Gr.B
     ※ 長度 ≤ 0 時跳過
  3. M42 底板 (用 support pipe size = 2" 查表)
  4. M.B. (全牙螺桿): 1-5/8"×300L, 1 EA
  5. HEX NUT (重型六角螺帽): 1-5/8", 2 EA
  6. Washer: 92×9t×50, 2 EA
  7. Spring: SPR12 或 SPR14, 2 EA, ASTM A229
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..m42 import perform_action_by_letter
from ..bolt import add_custom_entry
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type11_table import get_type11_data, get_type11_hardware_item, build_type11_spring_item


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


def _type11_item_material(item: dict):
    material_name = item["material"]
    item_name = item["name"]
    if item_name == "M.B.(FULL THREADED)":
        kind = HardwareKind.THREADED_ROD
    elif item_name == "HEAVY HEX NUT":
        kind = HardwareKind.HEAVY_HEX_NUT
    elif item_name == "WASHER":
        kind = HardwareKind.SUPPORT_PLATE
    elif item_name == "SPRING":
        kind = HardwareKind.SPRING_CAN
    else:
        kind = HardwareKind.SUPPORT_PLATE
    return _material_spec(kind, material_name)


_UPPER_PIPE_SIZE = 1.5
_UPPER_PIPE_SCH = "SCH.80"
_SUPPORT_PIPE_SIZE = 2
_SUPPORT_PIPE_SCH = "SCH.40"
_MB_LENGTH = 300  # 全牙螺桿長度(mm)
_PLATE_T = 9      # base plate 厚度(mm)
_ALLOWED_M42_LETTERS = {"G", "J"}


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # 第二段: line size A
    part2 = get_part(fullstring, 2)
    line_size = int(get_lookup_value(part2))

    # 查表
    data = get_type11_data(line_size)
    if not data:
        result.error = f"Type 11: Line size {part2} ({line_size}\") 不在查表範圍 (2\"/3\"/4\"/6\"/8\"/10\")"
        return result

    # 第三段: H + letter
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h_val = int(part3[:-1]) * 100

    # 取得上層材質
    from ..calculator import get_analysis_setting
    upper_material = overrides.get("upper_material") or get_analysis_setting("upper_material") or "SUS304"
    upper_material_spec = _material_spec(HardwareKind.SUPPORT_PIPE, upper_material)

    l_val = data["L"]

    # ── warnings ──
    if letter not in _ALLOWED_M42_LETTERS:
        result.warnings.append(
            f"M42 字母 '{letter}' 不在 Type 11 允許範圍 {sorted(_ALLOWED_M42_LETTERS)}（照算）"
        )
    if letter == "G":
        result.warnings.append("M42 Type-G: H 應從最低鋪面高程起算 (NOTE 7)")

    # ── 1. Upper Pipe (dummy, 1.5" SCH.80) ──
    main_pipe_length = l_val + 100
    add_pipe_entry(result, _UPPER_PIPE_SIZE, _UPPER_PIPE_SCH, main_pipe_length, upper_material_spec)

    # ── 2. Support Pipe (vertical, 2" SCH.40) ──
    # VBA: H*100 - 100 - (MB_LENGTH - plate_t)
    support_pipe_length = h_val - 100 - (_MB_LENGTH - _PLATE_T)
    if support_pipe_length > 0:
        support_material = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
        add_pipe_entry(result, _SUPPORT_PIPE_SIZE, _SUPPORT_PIPE_SCH, support_pipe_length, support_material)

    # ── 3. M42 底板 (用 support pipe size = 2") ──
    perform_action_by_letter(result, letter, _SUPPORT_PIPE_SIZE)

    # ── 4. M.B. (全牙螺桿) 1-5/8"×300L ──
    _add_threaded_rod_entry(result)

    # ── 5. HEX NUT (重型六角螺帽) ×2 ──
    _add_hex_nut_entry(result)

    # ── 6. Washer ×2 ──
    _add_washer_entry(result)

    # ── 7. Spring ×2 ──
    _add_spring_entry(result, data)

    return result


def _add_threaded_rod_entry(result: AnalysisResult):
    """全牙螺桿: 1-5/8"×300L (FULL THREADED), A307Gr.B(HDG), 1 EA"""
    _add_type11_item(result, get_type11_hardware_item("threaded_rod"))


def _add_hex_nut_entry(result: AnalysisResult):
    """重型六角螺帽: 1-5/8", A307Gr.B(HDG), 2 EA"""
    _add_type11_item(result, get_type11_hardware_item("hex_nut"))


def _add_washer_entry(result: AnalysisResult):
    """Wrought Steel Washer: 92×9t×50, 2 EA, ~1kg/ea"""
    _add_type11_item(result, get_type11_hardware_item("washer"))


def _add_spring_entry(result: AnalysisResult, data: dict):
    """Spring: SPR12/SPR14, ASTM A229, 2 EA, ~1kg/ea"""
    _add_type11_item(result, build_type11_spring_item(data["spring_mark"]))


def _add_type11_item(result: AnalysisResult, item: dict | None):
    if not item:
        result.warnings.append("Type 11 hardware table lookup failed; item skipped")
        return
    add_custom_entry(
        result,
        item["name"],
        item["spec"],
        _type11_item_material(item),
        item["quantity"],
        item["unit_weight_kg"],
        item["unit"],
        remark=item.get("remark", ""),
        category=item.get("category", "螺栓類"),
    )
    entry = result.entries[-1]
    entry.length = item.get("length_mm", 0)
    entry.weight_per_unit = item["unit_weight_kg"]
