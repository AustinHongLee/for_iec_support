"""
Type 01 / 01T 計算器 (Config 驅動)

Elbow 接入 (預設, code=01):
  格式: 01-2B-05A
  上段管: L(查表) + 100mm

Tee 接入 (code=01T):
  格式: 01T-2B-05A
  上段管: 100 + M(ASME B16.9 TEE_DATA, 依主管線尺寸查表)

共通:
  下段管: H×100 - 100mm
  上段管材質: 跟隨主管線 (預設 SUS304, 由 context 傳入)
  下段管材質: A53Gr.B (固定黑鐵)
  M42 底板: 依字母代碼
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..pipe import add_pipe_entry
from ..m42 import perform_action_by_letter
from ..config_loader import get_type_table_as_dict
from data.tee_table import get_tee_M


# ─── 建立查表 (從 JSON config 讀取, 失敗時用 fallback) ───

def _load_table() -> dict:
    """從 configs/type_01.json 載入, 轉為 {line_size: row} dict"""
    table = get_type_table_as_dict("01")
    if table:
        return table
    # fallback: 硬寫值 (與 PDF STM-05.01 一致)
    return {
        2:  {"pipe_size": "1-1/2", "schedule": "SCH.80",  "L": 71},
        3:  {"pipe_size": "2",     "schedule": "SCH.40",  "L": 93},
        4:  {"pipe_size": "3",     "schedule": "SCH.40",  "L": 139},
        6:  {"pipe_size": "4",     "schedule": "SCH.40",  "L": 186},
        8:  {"pipe_size": "6",     "schedule": "SCH.40",  "L": 271},
        10: {"pipe_size": "8",     "schedule": "SCH.40",  "L": 353},
        12: {"pipe_size": "8",     "schedule": "SCH.40",  "L": 370},
        14: {"pipe_size": "10",    "schedule": "SCH.40",  "L": 473},
        16: {"pipe_size": "10",    "schedule": "SCH.40",  "L": 491},
        18: {"pipe_size": "12",    "schedule": "STD.WT",  "L": 572},
        20: {"pipe_size": "12",    "schedule": "STD.WT",  "L": 594},
        24: {"pipe_size": "12",    "schedule": "STD.WT",  "L": 647},
    }


def calculate(fullstring: str, connection: str = "elbow",
              upper_material: str = "SUS304",
              overrides: dict = None) -> AnalysisResult:
    """
    計算 Type 01 (或 01T) 材料清單

    Parameters
    ----------
    fullstring : 編碼字串
    connection : "elbow" 或 "tee"
    upper_material : 上段管材質
    overrides : 單筆覆寫 dict, 可包含:
        pipe_size, schedule, l_value
    """
    overrides = overrides or {}
    result = AnalysisResult(fullstring=fullstring)
    table = _load_table()

    # 解析第二段: 主管線尺寸 (Line Size "A")
    part2 = get_part(fullstring, 2)
    line_size = int(get_lookup_value(part2))

    if line_size not in table:
        result.error = f"Type 01: 不支援管徑 {line_size}\""
        return result

    row = table[line_size]

    # 套用覆寫 (有覆寫值時優先使用)
    support_pipe_size = overrides.get("pipe_size") or row["pipe_size"]
    pipe_thickness = overrides.get("schedule") or row["schedule"]

    # 解析第三段: H高度 + M42字母代碼
    part3 = get_part(fullstring, 3)
    letter = part3[-1]
    h_value = int(part3[:-1]) * 100  # H×100mm

    # ─── 上段管 (材質跟隨主管線) ───
    if connection == "tee":
        tee_m = get_tee_M(line_size)
        upper_pipe_length = 100 + tee_m
    else:
        l_value = overrides.get("l_value") or row["L"]
        if isinstance(l_value, str):
            l_value = int(l_value)
        upper_pipe_length = l_value + 100

    add_pipe_entry(result, support_pipe_size, pipe_thickness,
                   upper_pipe_length, upper_material)

    # ─── 下段管 (固定黑鐵 A53Gr.B) ───
    lower_pipe_length = h_value - 100
    if lower_pipe_length > 0:
        add_pipe_entry(result, support_pipe_size, pipe_thickness,
                       lower_pipe_length, "A53Gr.B")

    # ─── M42 底板 ───
    perform_action_by_letter(result, letter, support_pipe_size)

    return result
