"""
Type 16 計算器
格式: 16-2B-05
- 第二段: 管徑
- 第三段: 長度 (純數字, *100mm)
"""
import math
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..hardware_material import (
    HardwareKind,
    MaterialSpec,
    parse_hardware_material_context,
    resolve_hardware_material,
)
from data.pipe_table import get_pipe_details


# Type 16: 管徑 -> (支撐管徑, 壁厚, 鋼板尺寸)
TYPE16_MAP = {
    2:  ("1.5", "SCH.80",  70),
    3:  ("2",   "SCH.40",  80),
    4:  ("3",   "SCH.40",  110),
    6:  ("4",   "SCH.40",  140),
    8:  ("6",   "SCH.40",  190),
    10: ("8",   "SCH.40",  240),
    12: ("10",  "SCH.40",  290),
    14: ("12",  "STD.WT",  340),
    16: ("12",  "STD.WT",  340),
    18: ("14",  "STD.WT",  380),
    20: ("14",  "STD.WT",  380),
    24: ("16",  "STD.WT",  430),
}


def _material(
    kind: HardwareKind,
    *,
    service,
    overrides,
) -> MaterialSpec:
    return resolve_hardware_material(kind, service=service, overrides=overrides)


def calculate(fullstring: str, overrides: dict | None = None) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    material_context = parse_hardware_material_context(
        overrides,
        legacy_material_keys=("material", "upper_material"),
        legacy_material_kinds=(HardwareKind.SUPPORT_PIPE,),
    )
    service = material_context.service
    material_overrides = material_context.material_overrides

    # 解析
    part2 = get_part(fullstring, 2)
    pipe_size = int(get_lookup_value(part2))
    third_length = int(get_part(fullstring, 3)) * 100

    if pipe_size not in TYPE16_MAP:
        result.error = f"Type 16: 不支援管徑 {pipe_size}"
        return result

    support_pipe_size, pipe_thickness, plate_size = TYPE16_MAP[pipe_size]
    upper_material = _material(HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides)
    support_material = _material(HardwareKind.SUPPORT_PIPE, service=service, overrides=material_overrides)
    plate_material = _material(HardwareKind.SUPPORT_PLATE, service=service, overrides=material_overrides)

    # 計算管道細節
    pipe_details = get_pipe_details(pipe_size, "10S")

    # 主管長度
    main_pipe_length = round(
        (pipe_size * 1.5 * 25.4) + (pipe_details["od_mm"] / 2) + 100
    )
    add_pipe_entry(result, support_pipe_size, pipe_thickness, main_pipe_length, upper_material)

    # 支管長度
    support_pipe_length = round(
        third_length - (pipe_details["od_mm"] / 2) - 100 + 300
    )
    if support_pipe_length > 0:
        add_pipe_entry(result, support_pipe_size, pipe_thickness, support_pipe_length, support_material)

    # 鋼板
    add_plate_entry(result, plate_size, plate_size, 6, "Plate", material=plate_material)

    return result
