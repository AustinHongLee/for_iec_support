"""益高 SS 全家族（通用引擎）golden：涵蓋序號型鋼/雙高度/雙字母/焊接/耳板/選型橫樑等變體。"""
from core.calculator import analyze_single


def _a(s):
    return analyze_single(s)


def _named(r, name):
    return [e for e in r.entries if e.name == name]


def test_ss_base_plate_holes_stored():
    # 加工繪圖幾何:SS 底板孔位(∅/中心距/邊距)已結構化
    r = _a("SS24B-356H-800L")
    bp = _named(r, "底板")[0]
    h = bp.geometry.holes
    assert h and h.count == 4 and h.diameter == 15 and h.pitch_x and h.pitch_y
    # SS33 耳板為五邊形 lug
    r2 = _a('SS33-1.1/2"-150L')
    lug = _named(r2, "耳板")[0]
    assert lug.geometry.shape_kind == "lug"


def test_ss13_double_height_three_members():
    r = _a("SS13W-2-500H1-600H2-600L")
    assert not r.error, r.error
    angles = _named(r, "角鋼")
    assert len(angles) == 3                       # 立柱H1 + 立柱H2 + 水平L 各自分列
    lengths = sorted(a.length for a in angles)
    assert lengths == [500, 600, 600]
    assert all(a.spec == "75*75*9" for a in angles)   # 序號2


def test_ss1_welded_channel_serial():
    r = _a("SS1S-1-500L")
    assert not r.error
    ch = _named(r, "槽鐵")
    assert ch and ch[0].length == 500
    assert not _named(r, "底板") and not _named(r, "螺栓連帽")   # 焊接無底板螺栓


def test_ss8_no_base_plate_direct_bolt():
    r = _a("SS8B-400H")
    assert not _named(r, "底板")                   # 角鋼直鎖,無底板
    assert _named(r, "螺栓連帽")[0].quantity == 2
    angs = _named(r, "角鋼")
    assert any(a.length == 250 for a in angs)      # 底邊固定250


def test_ss6_fix_branches():
    assert _named(_a("SS6E-2-500H-600L"), "擴展螺栓")   # E→擴展螺栓
    assert _named(_a("SS6B-2-500H-600L"), "螺栓連帽")   # B→螺栓連帽
    rw = _a("SS6W-2-500H-600L")
    assert not _named(rw, "底板") and not _named(rw, "螺栓連帽")  # W焊接


def test_ss21_double_letter_fix():
    rb = _a("SS21SB-700L")
    assert _named(rb, "底板") and _named(rb, "螺栓連帽")[0].quantity == 4
    assert _named(rb, "鋼板(擋板)")
    rw = _a("SS21VW-700L")
    assert not _named(rw, "底板")                  # W 無底板
    assert _named(rw, "鋼板(擋板)")                # 擋板恆有


def test_ss33_lug_channel_ubolt():
    r = _a("SS33-1\"-200L")
    assert _named(r, "槽鐵")[0].length == 200
    assert _named(r, "耳板")
    assert _named(r, "U型螺栓連帽")                # 引用 UB1


def test_ss34_crossbeam_sum_lengths():
    r = _a("SS34-2-750L-750L")
    beam = _named(r, "槽鐵")
    assert beam and beam[0].length == 1500         # A+B = 750+750


def test_ss15_column_hbeam():
    r = _a("SS15-3-2000H")
    assert _named(r, "H型鋼")[0].length == 2000
