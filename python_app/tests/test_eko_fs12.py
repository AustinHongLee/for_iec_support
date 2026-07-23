"""益高 FS12 golden：鎖住編號解析、BOM 構件、關鍵長度/重量、固定方式分支。"""
from companies import api
from companies.eko import parser as eko_parser


def _analyze(s, **ov):
    return api.analyze(s, company="EKO", overrides=(ov or None))


def _entry(result, name):
    return next((e for e in result.entries if e.name == name), None)


def _entries(result, name):
    return [e for e in result.entries if e.name == name]


def test_parse_fs12w():
    p = eko_parser.parse_designation("FS12W-2-1300H-400L")
    assert p["code"] == "FS12"
    assert p["fix"] == "W"
    assert p["serial"] == 2
    assert p["L"] == 400
    assert p["H"] == 1300
    assert p["H1"] is None


def test_parse_order_independent_and_h1():
    p = eko_parser.parse_designation("FS12E-1-500L-500H-300H1")
    assert (p["code"], p["fix"], p["serial"]) == ("FS12", "E", 1)
    assert (p["L"], p["H"], p["H1"]) == (500, 500, 300)


def test_fs12w_bom_and_weight():
    r = _analyze("FS12W-2-1300H-400L")
    assert not r.error, r.error
    names = [e.name for e in r.entries]

    # 冂型 = 3 支獨立下料件：立柱×2(長H=1300) + 上橫樑×1(長L=400)，不可併成單一 3000mm 長料
    angles = _entries(r, "角鋼")
    assert len(angles) == 2                       # 兩種長度各一列
    assert all(a.spec == "75*75*9" for a in angles)  # 序號2 → L75×75×9
    legs = next(a for a in angles if a.quantity == 2)
    top = next(a for a in angles if a.quantity == 1)
    assert legs.length == 1300 and top.length == 400
    assert sum(a.quantity for a in angles) == 3   # 共 3 支
    assert abs(sum(a.total_weight for a in angles) - 29.88) < 0.1

    plate = _entry(r, "底板")
    assert plate is not None
    assert (plate.length, plate.width) == (260, 260)      # 方板 A×A (B=190 為螺栓中心距)
    assert plate.quantity == 2
    assert abs(plate.total_weight - 9.55) < 0.1
    assert plate.geometry.holes is None                   # W 焊接→免鑽孔(無孔)

    # FS12 本體不含 U型螺栓：管線固定由 VA2 系列接手(使用者確認 2026-07-21)
    assert _entry(r, "U型螺栓") is None
    # W 焊接：不得出現任何固定螺栓 / 水泥墩
    assert "L型基礎螺栓" not in names
    assert "擴展螺栓" not in names
    assert "螺栓錨帽" not in names
    assert "水泥墩" not in names
    assert any("焊接固定" in w for w in r.warnings)


def test_fs12_base_plate_holes_when_bolted():
    # 加工繪圖幾何:非焊接(A/B/E)底板 4-∅ 孔,中心距=B、邊距=C
    r = _analyze("FS12A-2-1300H-400L-300H1")
    plate = _entry(r, "底板")
    assert (plate.length, plate.width) == (260, 260)
    h = plate.geometry.holes
    assert h and h.count == 4 and h.diameter == 19 and h.pitch_x == 190


def test_fs12_serial1_uses_l50_and_anchor_bolt():
    r = _analyze("FS12A-1-500H-500L")
    angles = _entries(r, "角鋼")
    assert all(a.spec == "50*50*6" for a in angles)   # 序號1 → L50×50×6
    assert sum(a.quantity for a in angles) == 3       # 立柱×2 + 橫樑×1
    assert abs(sum(a.total_weight for a in angles) - 6.64) < 0.1  # 3×500mm×4.43kg/m
    assert _entry(r, "L型基礎螺栓") is not None         # A → 基礎螺栓


def test_fs12e_with_pier():
    r = _analyze("FS12E-2-1000L-1000H-400H1")
    assert _entry(r, "擴展螺栓") is not None
    pier = _entry(r, "水泥墩")
    assert pier is not None and pier.quantity == 2


def test_fs12_missing_fix_errors():
    r = _analyze("FS12-2-1300H-400L")
    assert r.error and "固定方式" in r.error


def test_fs12b_nut_bolt_no_pier():
    r = _analyze("FS12B-2-800H-600L")
    assert _entry(r, "螺栓錨帽") is not None
    assert _entry(r, "水泥墩") is None       # B 不含水泥墩
