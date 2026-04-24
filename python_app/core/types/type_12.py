"""
Type 12 計算器 - 焊接式雙板夾持 Dummy Pipe 支撐
Rigid welded dummy pipe support with plate reinforcement

格式: 12-{line_size}-{H}{M42_letter}         (碳鋼板)
      12-{line_size}-{H}{M42_letter}(A)      (合金鋼板)
      12-{line_size}-{H}{M42_letter}(S)      (不鏽鋼板)
  例: 12-6B-05B       → A=6", H=500, M42=B, plate=Carbon Steel
      12-6B-05B(A)    → 同上, plate=Alloy Steel
      12-6B-05B(S)    → 同上, plate=Stainless Steel

- 第二段: Supported Line Size A
- 第三段: H(前2碼×100mm) + M42字母(末字母) + 可選材料尾碼(A)/(S)

PDF 限制: H≤1500mm

Note 4 - 板材材料符號:
  CARBON STEEL  → 無尾碼
  ALLOY STEEL   → (A)
  STAINLESS STEEL → (S)

Note 5 - M42 底座類型 A,B,E,G 時，H 從地坪最低點起算

構件:
  1. Supporting Pipe B (垂直柱): H-100, pipe_size_b / pipe_sch, A53Gr.B
     ※ 長度 ≤ 0 時跳過
  2. Plate P (側板): plate_len × plate_wid × plate_t, 材料依尾碼
  3. Cover Plate (蓋板): 75×75×6t, 材料依尾碼
  4. M42 底板 (用 pipe_size_b 查表)

VBA 對照: VBA 未實作 Type 12 (僅有註解佔位)
"""
from ..models import AnalysisResult, AnalysisEntry
from ..parser import get_part, get_lookup_value, extract_parts
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..m42 import perform_action_by_letter
from ..hardware_material import (
    HardwareKind,
    HardwareMaterialOverrides,
    resolve_hardware_material,
)
from data.type12_table import get_type12_data


def _material_spec(kind: HardwareKind, material_name: str):
    return resolve_hardware_material(
        kind,
        overrides=HardwareMaterialOverrides(per_kind={kind: material_name}),
    )


_MAX_H = 1500
_COVER_PLATE_SIZE = 75   # mm, square
_COVER_PLATE_T = 6       # mm

# Note 5: 這些 M42 底座類型，H 從地坪最低點起算
_PAVING_LETTERS = {"A", "B", "E", "G"}

# Note 4: 板材材料對照
_PLATE_MATERIAL_MAP = {
    "":    "A36/SS400",
    "(A)": "ALLOY STEEL",
    "(S)": "SUS304",
}


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    # ── 第二段: line size A ──
    part2 = get_part(fullstring, 2)
    line_size = get_lookup_value(part2)

    # 查表
    data = get_type12_data(int(line_size))
    if not data:
        result.error = (
            f"Type 12: Line size {part2} ({line_size}\") 不在查表範圍 "
            f"(2\"/3\"/4\"/6\"/8\"/10\"/12\"/14\"/16\")"
        )
        return result

    # ── 第三段: H + M42 letter + 可選材料尾碼 ──
    part3 = get_part(fullstring, 3)
    base, suffix = extract_parts(part3)   # "05B(A)" → ("05B", "(A)")
    letter = base[-1]
    h_val = int(base[:-1]) * 100

    # 板材材料
    plate_material = _PLATE_MATERIAL_MAP.get(suffix, "A36/SS400")

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
            f"M42 底座類型 {letter} — H 應從地坪最低點 (lowest point of paving) 起算 (NOTE 5)"
        )

    # ── 1. Supporting Pipe B (垂直柱) ──
    support_pipe_length = h_val - 100
    if support_pipe_length > 0:
        support_pipe_material = _material_spec(HardwareKind.SUPPORT_PIPE, "A53Gr.B")
        add_pipe_entry(
            result, pipe_size_b, pipe_sch, support_pipe_length,
            support_pipe_material,
        )

    # ── 2. Plate P (側板) ──
    plate_material_spec = _material_spec(HardwareKind.SUPPORT_PLATE, plate_material)
    add_plate_entry(
        result,
        plate_a=plate_len,
        plate_b=plate_wid,
        plate_thickness=plate_t,
        plate_name="Plate_P",
        material=plate_material_spec,
    )

    # ── 3. Cover Plate (蓋板, 75×75×6t) ──
    add_plate_entry(
        result,
        plate_a=_COVER_PLATE_SIZE,
        plate_b=_COVER_PLATE_SIZE,
        plate_thickness=_COVER_PLATE_T,
        plate_name="COVER_PL",
        material=plate_material_spec,
    )

    # ── 4. M42 底板 (用 pipe_size_b 查表) ──
    perform_action_by_letter(result, letter, pipe_size_b)

    return result
