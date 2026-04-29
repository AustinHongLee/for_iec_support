"""
M42 底板程序 - 對應 VBA: X_M42底板程序
根據字母代碼執行對應的鋼板/螺栓/角鋼操作
"""
from .models import AnalysisResult
from .hardware_material import MaterialSpec
from .material_identity import canonical_material_id
from .plate import add_plate_entry
from .bolt import add_bolt_entry
from .steel import add_steel_section_entry
from data.m42_table import get_m42_data
from .parser import get_lookup_value


_DEFAULT_M42_PLATE_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.m42.default_plate_material",
    requires_review=True,
)
_DEFAULT_M42_BOLT_MATERIAL = MaterialSpec(
    name="SUS304",
    canonical_id=canonical_material_id("SUS304") or "UNRESOLVED_SUS304",
    source="core.m42.default_bolt_material",
    requires_review=True,
)
_DEFAULT_M42_STEEL_MATERIAL = MaterialSpec(
    name="A36/SS400",
    canonical_id=canonical_material_id("A36/SS400") or "UNRESOLVED_A36_SS400",
    source="core.m42.default_steel_material",
    requires_review=True,
)
_DEFAULT_M42_SS304_PLATE_MATERIAL = MaterialSpec(
    name="SUS304",
    canonical_id=canonical_material_id("SUS304") or "UNRESOLVED_SUS304",
    source="core.m42.m42a_ss304_plate_material",
    requires_review=False,
)


def add_m42_plate(
    result: AnalysisResult,
    plate_type: str,
    pipe_size,
    material: str | MaterialSpec | None = None,
):
    """
    依據板型代碼 (a/b/c/d/e) 新增 M42 鋼板
    對應 VBA: AddPlateEntry
    pipe_size 可以是數字(管徑)或含"*"的型鋼字串
    """
    s = str(pipe_size)
    if "*" in s or "x" in s:
        m42 = get_m42_data(s)
    else:
        size_val = get_lookup_value(pipe_size)
        m42 = get_m42_data(size_val)

    require_drilling = plate_type in ("b", "c", "d")

    # 依據板型決定查表欄位 (對照 PDF M-43 表格)
    plate_size_map = {
        "a": "plate_a",      # B 欄: B×B
        "b": "plate_bc",     # C 欄: C×C
        "c": "plate_bc",     # C 欄: C×C
        "d": "plate_d",      # E 欄: E×E
        "e": "plate_e",      # G 欄: G×G
    }

    plate_size = m42[plate_size_map.get(plate_type, "plate_a")]
    plate_thickness = m42["plate_thickness"]
    plate_name = f"Plate_{plate_type}" + ("_有鑽孔" if require_drilling else "_無鑽孔")

    bolt_x = bolt_y = bolt_hole = 0
    bolt_size = ""
    if require_drilling:
        if plate_type in ("b", "c"):
            bolt_x = bolt_y = m42["plate_d_bc_bolt"]
        else:
            bolt_x = bolt_y = m42["plate_d_bolt"]
        bolt_hole = m42["bolt_hole_dia"]
        bolt_size = m42["exp_bolt_spec"]

    add_plate_entry(
        result, plate_size, plate_size, plate_thickness, plate_name,
        material=material or _DEFAULT_M42_PLATE_MATERIAL,
        bolt_switch=require_drilling,
        bolt_x=bolt_x, bolt_y=bolt_y,
        bolt_hole=bolt_hole, bolt_size=bolt_size,
        plate_role="base_plate",   # M42 底板
    )


def perform_action_by_letter(
    result: AnalysisResult,
    letter: str,
    pipe_size,
    *,
    plate_material: str | MaterialSpec | None = None,
    bolt_material: str | MaterialSpec | None = None,
    steel_material: str | MaterialSpec | None = None,
):
    """
    根據字母代碼決定新增哪些鋼板/螺栓/角鋼
    對應 VBA: PerformActionByLetter
    """
    plate_material = plate_material or _DEFAULT_M42_PLATE_MATERIAL
    bolt_material = bolt_material or _DEFAULT_M42_BOLT_MATERIAL
    steel_material = steel_material or _DEFAULT_M42_STEEL_MATERIAL
    ss304_plate_material = _DEFAULT_M42_SS304_PLATE_MATERIAL
    actions = {
        "A": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "B": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "C": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "D": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "e", pipe_size, plate_material)),
        "E": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "F": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "G": lambda: (
            add_m42_plate(result, "b", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "H": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "J": lambda: (
            add_m42_plate(result, "b", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "K": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "L": lambda: (
            add_m42_plate(result, "c", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "M": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "N": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "P": lambda: (
            add_m42_plate(result, "c", pipe_size, plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "R": lambda: add_m42_plate(result, "a", pipe_size, plate_material),
        "S": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "e", pipe_size, plate_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "T": lambda: add_m42_plate(result, "a", pipe_size, ss304_plate_material),
        "U": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, ss304_plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "V": lambda: (
            add_m42_plate(result, "a", pipe_size, plate_material),
            add_m42_plate(result, "d", pipe_size, ss304_plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2, material=steel_material)),
        "W": lambda: (
            add_m42_plate(result, "b", pipe_size, ss304_plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "X": lambda: (
            add_m42_plate(result, "c", pipe_size, ss304_plate_material),
            add_bolt_entry(result, pipe_size, 4, material=bolt_material)),
        "Y": lambda: add_m42_plate(result, "a", pipe_size, ss304_plate_material),
    }

    action = actions.get(letter.upper())
    if action:
        action()
    else:
        result.warnings.append(f"M-42 型式 '{letter}' 未定義，未新增底板組件")
