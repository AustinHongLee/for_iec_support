"""益高延展與主程式整合 golden：EKO 編號走與 Type 同一條 analyze_single/analyze_project_rows。
鎖住主程式 GUI 免改即可判讀益高，且不影響既有 IEC Type。"""
from core.calculator import analyze_single
from core.project_aggregation import ProjectInputRow, analyze_project_rows


def test_analyze_single_routes_eko():
    r = analyze_single("FS12W-2-1300H-400L")
    assert not r.error, r.error
    assert any(e.name == "角鋼" for e in r.entries)
    assert abs(r.total_weight - 39.43) < 0.1        # 底板修正為方板260×260後


def test_analyze_single_routes_eko_subcomponent():
    r = analyze_single("UB1-6\"")
    assert not r.error and r.entries[0].name == "U型螺栓"


def test_analyze_single_iec_type_unaffected():
    r = analyze_single("01-2B-05B-A")          # IEC Type 01
    assert not r.error
    assert any(e.name == "管路" for e in r.entries)


def test_unknown_code_still_not_implemented():
    r = analyze_single("ZZ9-1-500H")           # 既非 IEC 也非 EKO
    assert r.error and "not implemented" in r.error


def test_mixed_iec_eko_project():
    rows = [
        ProjectInputRow(designation="FS12W-2-1300H-400L", quantity=2),
        ProjectInputRow(designation="UB1-6\"", quantity=5),
        ProjectInputRow(designation="01-2B-05B-A", quantity=1),
    ]
    proj = analyze_project_rows(rows)          # 預設 calculate_type=analyze_single (GUI 用)
    assert proj.errors == []
    assert proj.total_support_count == 8
    assert proj.total_weight > 0
