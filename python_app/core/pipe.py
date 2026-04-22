"""
管道計算模組 - 對應 VBA: B_管道計算相關函數
"""
from .models import AnalysisEntry, AnalysisResult
from .hardware_material import MaterialSpec
from data.pipe_table import get_pipe_details


def normalize_schedule(thickness_str: str) -> str:
    """
    將 VBA 的 Schedule 表示法統一為查表用格式
    "SCH.40" -> "40S", "SCH.80" -> "80S", "STD.WT" -> "STD.WT", "STD" -> "STD.WT"
    """
    s = thickness_str.strip()
    if s == "STD":
        return "STD.WT"
    if s == "STD.WT":
        return s
    if s.startswith("SCH."):
        return s.replace("SCH.", "") + "S"
    return s


def _material_name_and_identity(material: str | MaterialSpec) -> tuple[str, str | None]:
    if isinstance(material, MaterialSpec):
        return material.name, material.canonical_id
    return str(material), None


def add_pipe_entry(result: AnalysisResult, pipe_size, pipe_thickness: str,
                   pipe_length: float, material: str | MaterialSpec):
    """
    新增管道項目到結果
    對應 VBA: AddPipeEntry
    """
    material_name, canonical_id = _material_name_and_identity(material)

    # 清理 pipe_size
    size_str = str(pipe_size).replace("'", "").replace("B", "")
    from .parser import get_lookup_value
    size_val = get_lookup_value(size_str)

    schedule = normalize_schedule(pipe_thickness)
    details = get_pipe_details(size_val, schedule)

    entry = AnalysisEntry()
    entry.name = "Pipe"
    entry.spec = f'{size_str}"*{pipe_thickness}'
    entry.length = pipe_length
    entry.material = material_name
    if canonical_id:
        entry.material_canonical_id = canonical_id
    entry.quantity = 1
    entry.weight_per_unit = details["weight_per_m"]
    entry.unit_weight = round(pipe_length / 1000 * details["weight_per_m"], 2)
    entry.total_weight = entry.unit_weight * entry.quantity
    entry.unit = "M"
    entry.factor = 1
    entry.length_subtotal = round(entry.quantity * entry.factor * pipe_length / 1000, 3)
    entry.weight_output = entry.factor * entry.total_weight
    entry.category = "管路類"

    result.add_entry(entry)
