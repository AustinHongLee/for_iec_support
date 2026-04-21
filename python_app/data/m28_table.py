"""
M-28 Beam Attachment Type-A 資料表
來源: M-28 圖紙

用途:
- Type 65 等 trapeze hanger 的上部 beam attachment

說明:
- 圖面表格以 rod size 為主索引
- TYPE 欄為 BA-A-* 系列
- FIG-2 僅適用於 1 3/4" rod dia. and smaller
"""
from .component_size_utils import normalize_fractional_size

M28_TABLE = {
    '3/8"': {"type": "BA-A-3/8", "rod_size_a": '3/8"', "bolt_size": '1/2" x 70', "load_650f_kg": 270, "load_750f_kg": 240, "takeoff_e_fig1": 48, "takeoff_e_prime_fig2": 51, "B": 51, "H": 14, "R": 22, "S": 32, "T": 6, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.20},
    '1/2"': {"type": "BA-A-1/2", "rod_size_a": '1/2"', "bolt_size": '5/8" x 70', "load_650f_kg": 510, "load_750f_kg": 460, "takeoff_e_fig1": 44, "takeoff_e_prime_fig2": 51, "B": 51, "H": 17, "R": 22, "S": 32, "T": 6, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.25},
    '5/8"': {"type": "BA-A-5/8", "rod_size_a": '5/8"', "bolt_size": '3/4" x 70', "load_650f_kg": 820, "load_750f_kg": 730, "takeoff_e_fig1": 44, "takeoff_e_prime_fig2": 51, "B": 51, "H": 21, "R": 22, "S": 32, "T": 6, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.32},
    '3/4"': {"type": "BA-A-3/4", "rod_size_a": '3/4"', "bolt_size": '7/8" x 80', "load_650f_kg": 1230, "load_750f_kg": 1100, "takeoff_e_fig1": 44, "takeoff_e_prime_fig2": 51, "B": 64, "H": 24, "R": 29, "S": 38, "T": 9, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.45},
    '7/8"': {"type": "BA-A-7/8", "rod_size_a": '7/8"', "bolt_size": '1" x 110', "load_650f_kg": 1710, "load_750f_kg": 1520, "takeoff_e_fig1": 67, "takeoff_e_prime_fig2": 76, "B": 64, "H": 29, "R": 32, "S": 51, "T": 9, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.62},
    '1"': {"type": "BA-A-1", "rod_size_a": '1"', "bolt_size": '1 1/8" x 120', "load_650f_kg": 2250, "load_750f_kg": 2000, "takeoff_e_fig1": 70, "takeoff_e_prime_fig2": 76, "B": 76, "H": 32, "R": 38, "S": 51, "T": 12, "Y": 6, "fig2_allowed": True, "unit_weight_kg": 0.82},
    '1 1/4"': {"type": "BA-A-1 1/4", "rod_size_a": '1 1/4"', "bolt_size": '1 3/8" x 130', "load_650f_kg": 3630, "load_750f_kg": 3240, "takeoff_e_fig1": 73, "takeoff_e_prime_fig2": 76, "B": 102, "H": 38, "R": 51, "S": 64, "T": 16, "Y": 10, "fig2_allowed": True, "unit_weight_kg": 1.10},
    '1 1/2"': {"type": "BA-A-1 1/2", "rod_size_a": '1 1/2"', "bolt_size": '1 5/8" x 150', "load_650f_kg": 5280, "load_750f_kg": 4700, "takeoff_e_fig1": 102, "takeoff_e_prime_fig2": 102, "B": 127, "H": 44, "R": 64, "S": 76, "T": 19, "Y": 10, "fig2_allowed": True, "unit_weight_kg": 1.45},
    '1 3/4"': {"type": "BA-A-1 3/4", "rod_size_a": '1 3/4"', "bolt_size": '1 7/8" x 180', "load_650f_kg": 7120, "load_750f_kg": 6350, "takeoff_e_fig1": 127, "takeoff_e_prime_fig2": 127, "B": 127, "H": 51, "R": 70, "S": 95, "T": 19, "Y": 10, "fig2_allowed": True, "unit_weight_kg": 1.90},
    '2"': {"type": "BA-A-2", "rod_size_a": '2"', "bolt_size": '2 1/4" x 180', "load_650f_kg": 9390, "load_750f_kg": 8370, "takeoff_e_fig1": 133, "takeoff_e_prime_fig2": 127, "B": 152, "H": 60, "R": 83, "S": 95, "T": 19, "Y": 10, "fig2_allowed": False, "unit_weight_kg": 2.45},
    '2 1/4"': {"type": "BA-A-2 1/4", "rod_size_a": '2 1/4"', "bolt_size": '2 1/2" x 190', "load_650f_kg": 12430, "load_750f_kg": 11000, "takeoff_e_fig1": 159, "takeoff_e_prime_fig2": 152, "B": 152, "H": 67, "R": 89, "S": 108, "T": 19, "Y": 16, "fig2_allowed": False, "unit_weight_kg": 3.10},
    '2 1/2"': {"type": "BA-A-2 1/2", "rod_size_a": '2 1/2"', "bolt_size": '2 3/4" x 200', "load_650f_kg": 15200, "load_750f_kg": 13560, "takeoff_e_fig1": 159, "takeoff_e_prime_fig2": 152, "B": 152, "H": 73, "R": 95, "S": 114, "T": 19, "Y": 16, "fig2_allowed": False, "unit_weight_kg": 3.90},
}



def get_m28_by_rod_size(dia: str) -> dict | None:
    """依 rod size 查 beam attachment A 規格。"""
    return M28_TABLE.get(normalize_fractional_size(dia))


def get_m28_takeoff(dia: str, fig: int = 1) -> int | None:
    """依 rod size 與 figure 查 rod takeoff 尺寸。"""
    row = get_m28_by_rod_size(dia)
    if not row:
        return None
    if fig == 2:
        return row["takeoff_e_prime_fig2"] if row["fig2_allowed"] else None
    return row["takeoff_e_fig1"]
