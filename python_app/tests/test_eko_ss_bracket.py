"""益高 SS 結構撐托架共用引擎 golden：SS24/25/26/27/28/37。
驗證逐桿分列(立柱/水平桿各長度分列)、B型加底板+螺栓、W型焊接無、SS28 無L段。"""
from core.calculator import analyze_single


def _a(s):
    return analyze_single(s)


def _named(r, name):
    return [e for e in r.entries if e.name == name]


def test_ss24_angle_members_and_base():
    r = _a("SS24B-1000H-800L")
    assert not r.error, r.error
    angles = _named(r, "角鋼")
    assert len(angles) == 2                       # 立柱(長H) 與 水平桿(長L) 分列
    legs = next(a for a in angles if a.quantity == 2)
    horiz = next(a for a in angles if a.quantity == 1)
    assert legs.length == 1000 and horiz.length == 800
    base = _named(r, "底板")
    assert base and base[0].quantity == 2 and base[0].material == "A283 Gr.C"
    assert _named(r, "螺栓連帽")[0].quantity == 8


def test_ss25_hbeam_welded_no_base():
    r = _a("SS25W-1200H-2000L")
    assert _named(r, "H型鋼")                      # H 型鋼構件
    assert not _named(r, "底板")                   # W 焊接無底板
    assert not _named(r, "螺栓連帽")
    assert any("焊接" in w for w in r.warnings)


def test_ss27_hbeam_125():
    r = _a("SS27B-800H-600L")
    hb = _named(r, "H型鋼")
    assert all(e.spec == "125*125*6.5" for e in hb)


def test_ss28_no_L_segment_fixed_base():
    r = _a("SS28B-1000H")                          # 無 L 段
    assert not r.error, r.error
    angles = _named(r, "角鋼")
    assert sum(a.quantity for a in angles) == 2    # 立柱×1 + 水平底座×1
    assert any(a.length == 500 for a in angles)    # 水平底座固定 500
    assert _named(r, "底板")[0].quantity == 1
    assert _named(r, "螺栓連帽")[0].quantity == 4


def test_ss_missing_dims_and_fix():
    # 缺尺寸或未知固定方式會改變鋼構/底板，必須阻擋而非部分計算。
    r = _a("SS24B-1000H")                          # 缺 L
    assert r.error and "L" in r.error
    r2 = _a("SS24X-1000H-800L")
    assert r2.error and "固定方式" in r2.error


def test_ss37_side_mount():
    r = _a("SS37B-500H-1800L")
    assert not r.error
    assert len(_named(r, "H型鋼")) == 2            # 立柱(H) + 水平懸臂(L)
