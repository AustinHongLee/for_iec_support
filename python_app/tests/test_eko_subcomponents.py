"""益高子件 golden：UB1(U型螺栓)、EB2(擴展螺栓) 及泛用 parser。"""
from companies import api
from companies.eko import parser as p


def _e(s, **ov):
    return api.analyze(s, company="EKO", overrides=(ov or None))


def test_parser_generic_classification():
    d = p.parse_designation("EB2-M20-140L-U")
    assert d["code"] == "EB2" and d["msize"] == 20 and d["L"] == 140 and "U" in d["flags"]
    d = p.parse_designation("CM1E-300H-4\"")
    assert d["code"] == "CM1" and d["mods"] == "E" and d["H"] == 300 and d["pipe"] == 4.0
    d = p.parse_designation("S1-6\"-100H")
    assert d["code"] == "S1" and d["pipe"] == 6.0 and d["H"] == 100
    d = p.parse_designation("DFS4E-1-500H")
    assert d["code"] == "DFS4" and d["mods"] == "E" and d["serial"] == 1 and d["H"] == 500


def test_parser_fs12_backward_compatible():
    d = p.parse_designation("FS12W-2-1300H-400L", code="FS12")
    assert d["code"] == "FS12" and d["fix"] == "W" and d["serial"] == 2
    assert d["H"] == 1300 and d["L"] == 400
    assert d["parse_warnings"] == []          # 有字母→不觸發位置備援


def test_parser_fs12_suffix_order_independent():
    d = p.parse_designation("FS12W-2-400L-1300H", code="FS12")   # 順序對調
    assert d["L"] == 400 and d["H"] == 1300 and not d["parse_warnings"]


def test_parser_fs12_positional_fallback():
    # 無字母純位置：序號→L→H→H1(依文法圖)，並警告
    d = p.parse_designation("FS12W-2-1300-400-300", code="FS12")
    assert d["serial"] == 2 and d["L"] == 1300 and d["H"] == 400 and d["H1"] == 300
    assert d["parse_warnings"] and "位置推定" in d["parse_warnings"][0]


def test_parser_fs12_mixed_suffix_and_bare():
    # 混用：H 有字母(=1300)，裸數字 400 補到剩下未設的 L
    d = p.parse_designation("FS12W-2-1300H-400", code="FS12")
    assert d["H"] == 1300 and d["L"] == 400 and d["parse_warnings"]


def test_ub1_6inch():
    r = _e("UB1-6\"")
    assert not r.error, r.error
    e = r.entries[0]
    assert e.name == "U型螺栓"
    assert "M16" in e.spec
    assert e.material == "A307-B 鍍鋅"
    assert abs(e.unit_weight - 1.039) < 0.03


def test_ub1_1inch_is_m10():
    r = _e("UB1-1\"")
    assert "M10" in r.entries[0].spec


def test_ub1_qty_override():
    r = _e("UB1-6\"", qty=4)
    assert r.entries[0].quantity == 4


def test_ub1_unknown_size_errors():
    r = _e("UB1-99\"")
    assert r.error


def test_eb2_galvanized_vs_sus():
    r = _e("EB2-M16-125L")
    assert r.entries[0].material == "鍍鋅鋼"
    assert "M16" in r.entries[0].spec
    r2 = _e("EB2-M20-140L-U")
    assert r2.entries[0].material == "SUS304"


def test_eb2_unknown_size_errors():
    r = _e("EB2-M14-100L")
    assert r.error
