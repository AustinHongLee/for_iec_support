"""
Type 80 — Pipe Shoe detail (D-95 / D-96)

D-95 covers pipe size 3/4"~24".
D-96 covers pipe size 26"~42" and refers missing dimensions to D-80B.
"""

TYPE80_SMALL_TABLE = {
    0.75: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    1.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    1.5: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    2.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    2.5: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    3.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    4.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    5.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    6.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    8.0: {"A": 100, "B": 100, "member_c": ("H Beam", "200*100*5.5"), "D": None, "E": None},
    10.0: {"A": 200, "B": 200, "member_c": ("H Beam", "200*200*8"), "D": 70, "E": None},
    12.0: {"A": 200, "B": 200, "member_c": ("H Beam", "200*200*8"), "D": 70, "E": None},
    14.0: {"A": 200, "B": 200, "member_c": ("H Beam", "200*200*8"), "D": 70, "E": None},
    16.0: {"A": 300, "B": 250, "member_c": ("Plate", "12"), "D": 100, "E": 12},
    18.0: {"A": 300, "B": 250, "member_c": ("Plate", "12"), "D": 100, "E": 12},
    20.0: {"A": 300, "B": 250, "member_c": ("Plate", "12"), "D": 100, "E": 12},
    24.0: {"A": 350, "B": 250, "member_c": ("Plate", "12"), "D": 100, "E": 12},
}


TYPE80_BIG_TABLE = {
    26.0: {"foot_a": 148, "foot_b": 198, "b": 430, "c": 230, "a_a": 222, "a_b": 272, "e_a": 150, "e_b": 200, "h_a": 480, "h_b": 530, "L": 540, "m": 35, "n": 75},
    28.0: {"foot_a": 148, "foot_b": 198, "b": 440, "c": 240, "a_a": 230, "a_b": 280, "e_a": 150, "e_b": 200, "h_a": 506, "h_b": 556, "L": 540, "m": 35, "n": 75},
    30.0: {"foot_a": 148, "foot_b": 198, "b": 450, "c": 250, "a_a": 237, "a_b": 287, "e_a": 150, "e_b": 200, "h_a": 531, "h_b": 581, "L": 540, "m": 35, "n": 75},
    32.0: {"foot_a": 148, "foot_b": 198, "b": 460, "c": 260, "a_a": 244, "a_b": 294, "e_a": 150, "e_b": 200, "h_a": 556, "h_b": 606, "L": 740, "m": 40, "n": 75},
    36.0: {"foot_a": 152, "foot_b": 202, "b": 500, "c": 300, "a_a": 259, "a_b": 309, "e_a": 150, "e_b": 200, "h_a": 607, "h_b": 657, "L": 740, "m": 40, "n": 75},
    40.0: {"foot_a": 156, "foot_b": 206, "b": 535, "c": 335, "a_a": 274, "a_b": 324, "e_a": 150, "e_b": 200, "h_a": 658, "h_b": 708, "L": 740, "m": 40, "n": 75},
    42.0: {"foot_a": 156, "foot_b": 206, "b": 550, "c": 350, "a_a": 281, "a_b": 331, "e_a": 150, "e_b": 200, "h_a": 683, "h_b": 733, "L": 740, "m": 40, "n": 75},
}


def get_type80_small_row(pipe_size: float) -> dict | None:
    return TYPE80_SMALL_TABLE.get(float(pipe_size))


def get_type80_big_row(pipe_size: float) -> dict | None:
    return TYPE80_BIG_TABLE.get(float(pipe_size))
