"""
M42 底板程序 - 對應 VBA: X_M42底板程序
根據字母代碼執行對應的鋼板/螺栓/角鋼操作
"""
from .models import AnalysisResult
from .plate import add_plate_entry
from .bolt import add_bolt_entry
from .steel import add_steel_section_entry
from data.m42_table import get_m42_data
from .parser import get_lookup_value


def add_m42_plate(result: AnalysisResult, plate_type: str, pipe_size):
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
        bolt_switch=require_drilling,
        bolt_x=bolt_x, bolt_y=bolt_y,
        bolt_hole=bolt_hole, bolt_size=bolt_size
    )


def perform_action_by_letter(result: AnalysisResult, letter: str, pipe_size):
    """
    根據字母代碼決定新增哪些鋼板/螺栓/角鋼
    對應 VBA: PerformActionByLetter
    """
    actions = {
        "A": lambda: add_m42_plate(result, "a", pipe_size),
        "B": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_m42_plate(result, "d", pipe_size),
            add_bolt_entry(result, pipe_size, 4)),
        "C": lambda: add_m42_plate(result, "a", pipe_size),
        "D": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_m42_plate(result, "e", pipe_size)),
        "E": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_m42_plate(result, "d", pipe_size),
            add_bolt_entry(result, pipe_size, 4),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2)),
        "F": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2)),
        "G": lambda: (
            add_m42_plate(result, "b", pipe_size),
            add_bolt_entry(result, pipe_size, 4)),
        "H": lambda: add_m42_plate(result, "a", pipe_size),
        "J": lambda: (
            add_m42_plate(result, "b", pipe_size),
            add_bolt_entry(result, pipe_size, 4)),
        "K": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2)),
        "L": lambda: (
            add_m42_plate(result, "c", pipe_size),
            add_bolt_entry(result, pipe_size, 4)),
        "M": lambda: add_m42_plate(result, "a", pipe_size),
        "N": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2)),
        "P": lambda: (
            add_m42_plate(result, "c", pipe_size),
            add_bolt_entry(result, pipe_size, 4)),
        "R": lambda: add_m42_plate(result, "a", pipe_size),
        "S": lambda: (
            add_m42_plate(result, "a", pipe_size),
            add_m42_plate(result, "e", pipe_size),
            add_steel_section_entry(result, "Angle", "40*40*5", 150, 2)),
        # TYPE-T: 直接接 FDN (by civil), 不產生底板材料
        "T": lambda: None,
    }

    action = actions.get(letter.upper())
    if action:
        action()
