"""
Type 11 查表資料 - 彈簧可變載支撐 (Spring Variable Support)
PDF: 11.pdf

lookup key = line_size (A) in inches
  L: dummy pipe spacing (mm), 基於 long radius elbow
  spring_mark: 彈簧標記 (SPR12 / SPR14)
  spring_wire: 彈簧線徑 (mm)
  spring_id: 彈簧內徑 (mm)
  spring_k: 彈簧常數 (kg/mm)
  spring_free_len: 彈簧自由長 (mm)
  spring_max_defl: 最大建議撓度 (mm)
"""

TYPE11_TABLE = {
    2:  {"L": 71,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    3:  {"L": 81,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    4:  {"L": 97,  "spring_mark": "SPR12", "spring_wire": 12, "spring_id": 46, "spring_k": 25, "spring_free_len": 100, "spring_max_defl": 22},
    6:  {"L": 129, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
    8:  {"L": 162, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
    10: {"L": 195, "spring_mark": "SPR14", "spring_wire": 14, "spring_id": 46, "spring_k": 42, "spring_free_len": 115, "spring_max_defl": 24},
}


TYPE11_HARDWARE_TABLE = {
    "threaded_rod": {
        "name": "M.B.(FULL THREADED)",
        "spec": '1-5/8"*300L',
        "material": "A307Gr.B(HDG)",
        "quantity": 1,
        "unit_weight_kg": 3.2,
        "unit": "EA",
        "category": "螺栓類",
        "length_mm": 300,
        "remark": "legacy Type 11 calculator assumption",
    },
    "hex_nut": {
        "name": "HEAVY HEX NUT",
        "spec": '1-5/8"',
        "material": "A307Gr.B(HDG)",
        "quantity": 2,
        "unit_weight_kg": 0.4,
        "unit": "EA",
        "category": "螺栓類",
        "remark": "legacy Type 11 calculator assumption",
    },
    "washer": {
        "name": "WASHER",
        "spec": "92*9t*50",
        "material": "A36/SS400",
        "quantity": 2,
        "unit_weight_kg": 1.0,
        "unit": "EA",
        "category": "鋼板類",
        "remark": "legacy Type 11 calculator assumption",
    },
}


TYPE11_SPRING_TABLE = {
    "SPR12": {
        "name": "SPRING",
        "material": "ASTM A229",
        "quantity": 2,
        "unit_weight_kg": 1.0,
        "unit": "EA",
        "category": "彈簧類",
        "wire_mm": 12,
        "id_mm": 46,
        "spring_k_kg_per_mm": 25,
        "free_len_mm": 100,
        "max_defl_mm": 22,
        "remark": "legacy Type 11 calculator assumption",
    },
    "SPR14": {
        "name": "SPRING",
        "material": "ASTM A229",
        "quantity": 2,
        "unit_weight_kg": 1.0,
        "unit": "EA",
        "category": "彈簧類",
        "wire_mm": 14,
        "id_mm": 46,
        "spring_k_kg_per_mm": 42,
        "free_len_mm": 115,
        "max_defl_mm": 24,
        "remark": "legacy Type 11 calculator assumption",
    },
}


def get_type11_data(line_size: int) -> dict | None:
    row = TYPE11_TABLE.get(line_size)
    return dict(row) if row else None


def get_type11_hardware_item(item_id: str) -> dict | None:
    row = TYPE11_HARDWARE_TABLE.get(item_id)
    return dict(row) if row else None


def build_type11_spring_item(spring_mark: str) -> dict | None:
    row = TYPE11_SPRING_TABLE.get(spring_mark)
    if not row:
        return None
    item = dict(row)
    item["spring_mark"] = spring_mark
    item["spec"] = f'{spring_mark} ({item["wire_mm"]}W×{item["id_mm"]}ID)'
    return item
