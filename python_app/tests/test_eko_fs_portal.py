"""益高 FS 角鋼門架/立柱型 (fs_portal 引擎) golden：FS2/FS3/FS13/FS14/FS15。"""
from core.calculator import analyze_single


def _a(s): return analyze_single(s)
def _n(r, name): return [e for e in r.entries if e.name == name]


def test_fs2_aframe_slant_and_pier():
    r = _a("FS2E-6\"-600H-200H1")
    assert not r.error, r.error
    angs = _n(r, "角鋼")
    top = next(a for a in angs if a.quantity == 1)
    legs = next(a for a in angs if a.quantity == 2)
    assert top.length == 290                      # 上橫段=A
    assert legs.length == 605                      # 斜腳=√(600²+((450-290)/2)²)
    assert _n(r, "水泥墩")[0].quantity == 2         # CM1B ×2 (E)
    assert _n(r, "擴展螺栓")


def test_fs2_welded_no_bolt_pier():
    r = _a("FS2W-2\"-800H")
    assert not _n(r, "擴展螺栓") and not _n(r, "水泥墩")
    assert _n(r, "底板") and _n(r, "U型螺栓")


def test_fs2_bolt_B_no_pier():
    r = _a("FS2B-2\"-600H-200H1")                  # B 非 A/E → 無水泥墩
    assert _n(r, "螺栓連帽") and not _n(r, "水泥墩")


def test_fs14_ubolt_resolved_to_concrete_spec():
    # FS14 自帶 UB1：不再寫「詳 UB1」，而是算出實際規格(幾分/牙/線徑/展開長/重量)
    r = _a("FS14W-1/2\"-575H")
    assert not r.error, r.error
    ub = _n(r, "U型螺栓")
    assert ub, "FS14 應帶 U型螺栓"
    u = ub[0]
    assert "4分" in u.spec and "M10" in u.spec        # 1/2"→4分 M10
    assert "詳 UB1" not in u.spec                       # 不再只是參照
    assert u.unit_weight > 0                            # 具實際重量
    assert "叫料" in (u.remark or "")                   # 師傅叫料說法


def test_fs3_portal_serial():
    r = _a("FS3E-1-1000L-900H-300H1")
    angs = _n(r, "角鋼")
    top = next(a for a in angs if a.quantity == 1)
    legs = next(a for a in angs if a.quantity == 2)
    assert top.length == 1000 and legs.length == 900   # 上橫樑=L, 立柱=H
    assert all(a.spec == "50*50*6" for a in angs)       # 序號1
    assert _n(r, "水泥墩")[0].quantity == 2             # CM1B ×2


def test_fs13_double_column_and_N():
    r = _a("FS13E-1\"-500H-300H1")
    legs = _n(r, "角鋼")
    assert len(legs) == 1 and legs[0].quantity == 2 and legs[0].length == 500  # 立柱×2
    assert _n(r, "水泥墩")[0].quantity == 1            # CM1A ×1
    rn = _a("FS13N-1\"-600H")                          # 不固定
    assert not _n(rn, "擴展螺栓") and not _n(rn, "水泥墩")


def test_fs14_single_column():
    r = _a("FS14A-2\"-600H-300H1")
    assert _n(r, "角鋼")[0].quantity == 1
    assert _n(r, "L型基礎螺栓") and _n(r, "水泥墩")


def test_fs15_type_flag_serial():
    r = _a("FS15E-H-1-600H-300H1")                     # 型式H, 序號1
    assert _n(r, "角鋼")[0].spec == "50*50*6"
    r2 = _a("FS15W-V-2-800H")                          # 型式V, 序號2, 焊接
    assert _n(r2, "角鋼")[0].spec == "75*75*9"
    assert not _n(r2, "水泥墩")


def test_fs15_gamma_two_pieces_no_selfubolt():
    # 角鋼為Γ型 → 逐桿分列2支：立柱(H) + 頂臂(300)
    rh = _a("FS15E-H-1-600H-300H1")                    # 型式H
    angs = _n(rh, "角鋼")
    assert len(angs) == 2 and {a.length for a in angs} == {600, 300}
    # FS15 本體★不自帶 U型螺栓(型式H/V皆然)
    assert not _n(rh, "U型螺栓")
    # 型式V：不自帶 U型螺栓，改提醒「另以 UB1 標註」；帶管徑→附參考規格
    rv = _a("FS15W-V-1\"-2-1500H")
    assert not _n(rv, "U型螺栓")                        # 不自帶
    assert any("UB1" in w for w in rv.warnings)         # 提醒另計
    assert any("M10" in w for w in rv.warnings)         # 帶管徑1"→參考規格
    assert len(_n(rv, "角鋼")) == 2                    # 立柱+頂臂


def test_fs15_serial1_over_h_warns():
    # 序1(L50×50×6) 荷重表 H1500 不可 → 警告
    r = _a("FS15A-H-1-1500H-300H1")
    assert not r.error
    assert any("超出荷重表上限" in w for w in r.warnings)
