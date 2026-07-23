"""益高 單段家族 (eko_generic 引擎) golden：導架/錨定/管蹄/托撐/虛設管/落地管架/開孔/委派。"""
from core.calculator import analyze_single


def _a(s): return analyze_single(s)
def _n(r, name): return [e for e in r.entries if e.name == name]
def _has(r, name): return bool(_n(r, name))


# ── 托撐 PU ──
def test_pu4_single_angle_ubolt():
    r = _a('PU4W-1"-500L')
    assert not r.error, r.error
    assert _n(r, "角鋼")[0].length == 500          # 臂長=L, 逐桿分列
    assert _has(r, "支撐塊") and _has(r, "U型螺栓")
    # W 焊接→無底板/固定螺栓
    assert not _has(r, "底板") and not _has(r, "擴展螺栓")


def test_pu9_two_angles_h_and_l_and_base_bolt():
    r = _a('PU9E-1"-300L-438H')
    assert not r.error, r.error
    angs = _n(r, "角鋼")
    assert {a.length for a in angs} == {300, 438}   # 立柱=H、橫臂=L 各一支
    assert _has(r, "底板") and _has(r, "擴展螺栓")   # E→底板+擴展螺栓


def test_pu23_no_pipe_channels_l_l1():
    r = _a("PU23B-500L-350L1")
    assert not r.error, r.error
    ch = _n(r, "槽鐵")
    assert any(c.length == 500 and c.quantity == 2 for c in ch)   # 縱×2=L
    assert any(c.length == 350 and c.quantity == 1 for c in ch)   # 橫×1=L1
    assert _n(r, "底板")[0].material == "A283 Gr.C"                # 僅B有底板
    rw = _a("PU23W-500L-350L1")
    assert not _has(rw, "底板")                                     # W 焊接無底板


# ── 導架 G ──
def test_g1_angle_by_pipe_band():
    assert _n(_a('G1-3"'), "角鋼")[0].spec == "25*25*3"    # ≤4"
    assert _n(_a('G1-8"'), "角鋼")[0].spec == "50*50*6"    # ≥6"
    assert _n(_a('G1-3"'), "角鋼")[0].quantity == 2         # 兩側逐桿


def test_g2_shoe_stanchion_and_guides():
    r = _a('G2-4"-100H')
    assert not r.error, r.error
    assert _has(r, "管蹄柱") and _has(r, "底板") and _has(r, "角鋼")


# ── 支撐座 / 錨定 ──
def test_a3_four_plates_two_each():
    r = _a('A3-3"')
    assert not r.error, r.error
    ribs = _n(r, "三角肋板"); seats = _n(r, "水平座板")
    assert ribs and ribs[0].quantity == 2          # 三角肋板 B1/B2 ×2
    assert seats and seats[0].quantity == 2        # 水平座板 A1/A2 ×2
    assert ribs[0].spec == "9"                      # 2~8" → t9
    # 三角肋板淨重 = 矩形一半
    assert ribs[0].total_weight < seats[0].total_weight


def test_va1_lug_angles_ref_shoe():
    r = _a('VA1-1.1/2"')
    assert _n(r, "錨定鋼板")[0].material == "A283 Gr.C"
    assert _n(r, "角鋼")[0].quantity == 2
    assert _has(r, "管蹄")                          # 引用 S1(另計)


def test_va2_lug_and_ubolt():
    r = _a('VA2-1"')
    assert _has(r, "錨定鋼板") and _has(r, "U型螺栓")


# ── 虛設管 / 套管 ──
def test_ds3_dummy_pipe_len_l():
    r = _a('DS3-1"-450L')
    assert not r.error, r.error
    assert _n(r, "撐管")[0].length == 450            # 品名=撐管(非核心「管路」), 長=L


def test_st3_trunnion_size_from_table():
    r = _a('ST3-4"')                                # 4"→套管3"
    assert not r.error, r.error
    assert _n(r, "支撐套管")[0].spec.startswith("3")  # 品名=支撐套管, 尺寸查表
    assert _has(r, "托架")


# ── 落地管架 FS1（序號+L+H, 無管徑）──
def test_fs1_serial_channel_and_fix():
    r = _a("FS1E-1-500L-300H")
    assert not r.error, r.error
    assert _n(r, "槽鐵")[0].spec == "100*50*5" and _n(r, "槽鐵")[0].length == 500
    assert _has(r, "擴展螺栓") and not _has(r, "水泥墩")   # E 無墩
    ra = _a("FS1A-3-800L-300H")
    assert _has(ra, "水泥墩")                             # A→CM1C 墩
    rn = _a("FS1E-200H-400L")                             # 缺序號→預設1
    assert not rn.error and _n(rn, "槽鐵")[0].spec == "100*50*5"


# ── OPEN 委派核心開孔補強 ──
def test_open_delegates_penetration_hole():
    r = _a('OPEN-2"')
    assert not r.error, r.error
    assert _has(r, "開孔補強扁鐵")                   # 益高側整理品名(規格FB50×6在spec)


# ── 無圖面：明確訊息而非崩潰 ──
def test_no_drawing_graceful():
    assert "無對應圖面" in _a('FS24W-1/2"-800H').error
    assert "無對應圖面" in _a("PU22W-500L-350L1").error


# ── VG5 第2頁缺：best-effort 且明確標註 ──
def test_vg5_best_effort_warns():
    r = _a('VG5W-1"-200H-200L')
    assert not r.error, r.error
    assert any("第2頁" in w for w in r.warnings)
