"""益高 FS 鋼管立柱型 (fs_pipe 引擎) golden：FS4/5/8/9/11/19/22/23。"""
from core.calculator import analyze_single


def _a(s): return analyze_single(s)
def _n(r, name): return [e for e in r.entries if e.name == name]
def _has(r, name): return bool(_n(r, name))


def test_fs5_column_base_bolt_pier():
    r = _a("FS5A-1\"-500H-300H1")
    assert not r.error, r.error
    assert _n(r, "管路")[0].length == 500          # 立柱=H
    assert _has(r, "底板") and _has(r, "L型基礎螺栓") and _has(r, "水泥墩")
    rn = _a("FS5N-4\"-600H")                        # 不固定/焊接類→無螺栓無墩
    assert not _has(rn, "L型基礎螺栓") and not _has(rn, "水泥墩")


def test_fs8_clamp_ref():
    r = _a("FS8B-2\"-600H-300H1")
    assert _has(r, "管夾") and _has(r, "管路") and _has(r, "螺栓連帽")


def test_fs4_expands_dfs4_and_toppipe():
    r = _a("FS4E-2-400L-3000H-300H1")
    pipes = _n(r, "管路")
    assert any(p.length == 3000 for p in pipes)     # DFS4 立柱=H
    assert any(p.length == 400 for p in pipes)       # 上頂管=L
    assert _has(r, "封板") and _has(r, "補強板")      # 來自 DFS4 展開
    assert _has(r, "水泥墩")


def test_fs9_dfs4_channel_ubolt():
    r = _a("FS9E-2-400L-3000H-300H1")
    assert _has(r, "槽鐵") and _has(r, "U型螺栓")
    assert any(p.length == 3000 for p in _n(r, "管路"))   # DFS4 立柱


def test_fs11_dfs4_serial_from_side():
    r = _a("FS11E-4\"-500L-800H-300H1")               # 4"→撐2"→DFS4序1
    assert _has(r, "補強板")                           # DFS4 展開
    assert any(p.length == 800 for p in _n(r, "管路"))  # DFS4 立柱=H
    assert any(p.length == 500 for p in _n(r, "管路"))  # 側支撐管=L
    assert _has(r, "側支撐板")


def test_fs19_no_fix_always_nut_and_conditional_plate():
    r = _a("FS19-4\"-600H-300H1")
    assert _has(r, "螺栓連帽") and _has(r, "水泥墩")
    assert not _has(r, "補強角板")                     # 4" 無補強角板
    r2 = _a("FS19-8\"-800H")
    assert _has(r2, "補強角板")                         # 8-10" 有補強角板


def test_fs22_no_pier_no_bolt():
    r = _a("FS22-4\"-1000H")
    assert _has(r, "管路") and _n(r, "底板")[0].material == "A283 Gr.C"
    assert not _has(r, "水泥墩") and not _has(r, "螺栓連帽") and not _has(r, "U型螺栓")


def test_fs23_gusset_and_fix():
    r = _a("FS23E-6\"-1500H-50H1")
    assert _n(r, "補強角板")[0].quantity == 4          # 4 片 gusset
    assert _has(r, "頂板") and _has(r, "擴展螺栓") and _has(r, "水泥墩")
    rw = _a("FS23W-12\"-2000H")
    assert not _has(rw, "擴展螺栓") and not _has(rw, "水泥墩")   # W 焊接


def test_fs33_cold_best_effort():
    r = _a("FS33E-1\"-500H-300H1")
    assert not r.error, r.error
    assert any(p.length == 500 for p in _n(r, "管路"))     # 1.1/2"SCH80 立柱=H
    assert _has(r, "不鏽鋼夾板") and _has(r, "柱頭螺栓")
    assert any("FS32" in w for w in r.warnings)            # 明確標 FS32 缺


def test_fs5_square_base_plate_and_holes():
    # 底板為方板 B×B(原誤存 A×B),孔 ∅d 中心距=A
    r = _a('FS5A-1"-500H-300H1')
    bp = _n(r, "底板")[0]
    assert bp.length == bp.width == 160                # 方板 160×160
    h = bp.geometry.holes
    assert h and h.count == 4 and h.diameter == 14 and h.pitch_x == 120


def test_fs23_gusset_shape_and_base_holes():
    r = _a("FS23E-6\"-1500H-50H1")
    gusset = _n(r, "補強角板")[0]
    assert gusset.geometry.shape_kind == "triangle"     # 三角補強板
    bp = _n(r, "底板")[0]
    assert bp.length == bp.width and bp.geometry.holes.count == 4   # 方板+4孔


def test_fs31_full_table():
    r = _a("FS31E-4\"-800H-300H1")                          # 使用者補入尺寸表後正式可建
    assert not r.error
    assert any(p.length == 800 for p in _n(r, "管路"))      # 支撐管(4"→撐3")=H
    assert _has(r, "間隔板") and _has(r, "底板")
    assert _n(r, "柱頭螺栓")[0].quantity == 4
    assert _n(r, "夾持塊")[0].quantity == 3                 # BLOCK N=3 (4")
    assert _has(r, "擴展螺栓") and _has(r, "水泥墩")         # E→擴展螺栓+墩
    rn = _a("FS31N-2\"-600H")                               # 不固定→無螺栓無墩
    assert not _has(rn, "擴展螺栓") and not _has(rn, "水泥墩")
