"""
Type 41 查表資料 — 牆面錨定支撐 (Wall-Mounted Anchor Support, D-49)
固定規格表, 9 種支撐型號 (41-1 ~ 41-9)
FIG-A (41-1~41-4): 單懸臂, FIG-B (41-5~41-9): 含斜撐
"""

TYPE41_TABLE = {
    "41-1": {
        "support_no": "41-1", "L": 230,
        "member1": "L50*50*6", "member2": None,
        "base_plate_t": 16, "exp_bolt_dia": '1/2"',
        "bolt_dist": 150, "weld_size": 5, "b": 25, "fig": "A",
    },
    "41-2": {
        "support_no": "41-2", "L": 460,
        "member1": "L75*75*9", "member2": None,
        "base_plate_t": 16, "exp_bolt_dia": '5/8"',
        "bolt_dist": 200, "weld_size": 6, "b": 30, "fig": "A",
    },
    "41-3": {
        "support_no": "41-3", "L": 610,
        "member1": "L100*100*10", "member2": None,
        "base_plate_t": 19, "exp_bolt_dia": '3/4"',
        "bolt_dist": 230, "weld_size": 6, "b": 35, "fig": "A",
    },
    "41-4": {
        "support_no": "41-4", "L": 915,
        "member1": "H150*150*7", "member2": None,
        "base_plate_t": 19, "exp_bolt_dia": '3/4"',
        "bolt_dist": 250, "weld_size": 6, "b": 35, "fig": "A",
    },
    "41-5": {
        "support_no": "41-5", "L": 610,
        "member1": "L75*75*9", "member2": "L75*75*9",
        "base_plate_t": 16, "exp_bolt_dia": '5/8"',
        "bolt_dist": 200, "weld_size": 6, "b": 30, "fig": "B",
    },
    "41-6": {
        "support_no": "41-6", "L": 915,
        "member1": "L75*75*9", "member2": "L75*75*9",
        "base_plate_t": 16, "exp_bolt_dia": '5/8"',
        "bolt_dist": 200, "weld_size": 6, "b": 30, "fig": "B",
    },
    "41-7": {
        "support_no": "41-7", "L": 1220,
        "member1": "L75*75*9", "member2": "L100*100*10",
        "base_plate_t": 19, "exp_bolt_dia": '3/4"',
        "bolt_dist": 230, "weld_size": 6, "b": 35, "fig": "B",
    },
    "41-8": {
        "support_no": "41-8", "L": 915,
        "member1": "H150*150*7", "member2": "L100*100*10",
        "base_plate_t": 19, "exp_bolt_dia": '3/4"',
        "bolt_dist": 250, "weld_size": 6, "b": 35, "fig": "B",
    },
    "41-9": {
        "support_no": "41-9", "L": 1220,
        "member1": "H150*150*7", "member2": "L100*100*10",
        "base_plate_t": 19, "exp_bolt_dia": '3/4"',
        "bolt_dist": 250, "weld_size": 6, "b": 35, "fig": "B",
    },
}


def get_type41_data(support_no: str) -> dict | None:
    """依支撐型號查詢, 如 '41-1' 或 '1'"""
    if not support_no.startswith("41-"):
        support_no = f"41-{support_no}"
    return TYPE41_TABLE.get(support_no)
