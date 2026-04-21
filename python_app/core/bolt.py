"""
螺栓處理模組 - 對應 VBA: D_螺栓處理 + X_M42底板程序 的 AddBoltEntry
"""
from .models import AnalysisEntry, AnalysisResult
from data.m42_table import get_m42_data
from .parser import get_lookup_value


def add_bolt_entry(result: AnalysisResult, pipe_size, quantity: int):
    """
    新增螺栓項目到結果
    對應 VBA: AddBoltEntry
    pipe_size 可以是數字(管徑)或含"*"的型鋼字串
    """
    s = str(pipe_size)
    if "*" in s or "x" in s:
        m42 = get_m42_data(s)
    else:
        size_val = get_lookup_value(pipe_size)
        m42 = get_m42_data(size_val)
    bolt_size = m42["exp_bolt_spec"]

    entry = AnalysisEntry()
    entry.name = "EXP.BOLT"
    entry.spec = bolt_size
    entry.material = "SUS304"
    entry.quantity = quantity
    entry.unit_weight = 1  # 預設每組重量 1 kg
    entry.total_weight = entry.unit_weight * quantity
    entry.unit = "SET"
    entry.factor = 1
    entry.qty_subtotal = entry.factor * quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = "螺栓類"

    result.add_entry(entry)


def add_custom_entry(result: AnalysisResult, name: str, spec: str,
                     material: str, quantity: int, unit_weight: float,
                     unit: str = "SET", remark: str = "", category: str = "螺栓類"):
    """新增自訂項目 (Machine Bolt, Washer, Spring 等)"""
    entry = AnalysisEntry()
    entry.name = name
    entry.spec = spec
    entry.material = material
    entry.quantity = quantity
    entry.unit_weight = unit_weight
    entry.total_weight = round(unit_weight * quantity, 2)
    entry.unit = unit
    entry.factor = 1
    entry.qty_subtotal = entry.factor * quantity
    entry.weight_output = round(entry.factor * entry.total_weight, 2)
    entry.category = category
    entry.remark = remark

    result.add_entry(entry)
