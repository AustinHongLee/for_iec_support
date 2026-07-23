"""益高子件 golden 批2：CL5(管夾)、DFS4(下支架)、S1(管蹄)、CM1(水泥墩)。"""
from companies import api


def _e(s, **ov):
    return api.analyze(s, company="EKO", overrides=(ov or None))


def _get(r, name):
    return next((e for e in r.entries if e.name == name), None)


def test_cl5_clamp_and_bolts():
    r = _e("CL5-6\"")
    assert not r.error, r.error
    clamp = _get(r, "管夾")
    assert clamp and clamp.material == "A36" and clamp.width == 50   # 帶寬 E
    bolt = _get(r, "螺栓連帽")
    assert bolt and bolt.quantity == 2 and "M16" in bolt.spec


def test_cl5_size_bolt_mapping():
    assert "M10" in _get(_e("CL5-1\""), "螺栓連帽").spec
    assert "M27" in _get(_e("CL5-24\""), "螺栓連帽").spec


def test_dfs4_base_pipe_and_fix():
    r = _e("DFS4E-1-500H")
    assert not r.error, r.error
    base = _get(r, "底板")
    assert base.length == 210 and base.width == 210   # B×B 序號1
    pipe = _get(r, "管路")
    assert pipe.length == 500 and "2\"" in pipe.spec
    assert _get(r, "擴展螺栓") is not None
    # W 焊接無螺栓
    rw = _e("DFS4W-3-800H")
    assert _get(rw, "擴展螺栓") is None and _get(rw, "L型基礎螺栓") is None
    assert _get(rw, "管路").length == 800 and "4\"" in _get(rw, "管路").spec


def test_dfs4_unknown_serial():
    assert _e("DFS4E-9-500H").error


def test_s1_shoe_bands():
    r = _e("S1-6\"-100H")
    assert not r.error, r.error
    assert _get(r, "管蹄柱") and _get(r, "底板")
    assert _get(r, "加強板") is None            # 8" 以下無加強板
    r2 = _e("S1-12\"-120H")
    assert _get(r2, "加強板") is not None        # 10"~24" 有加強板 ×2
    assert _get(r2, "加強板").quantity == 2


def test_s1_sus_reinforcement_optional():
    assert _get(_e("S1-6\"-100H"), "補強板") is None
    r = _e("S1-6\"-100H", sus_pipe=True)
    reinf = _get(r, "補強板")
    assert reinf and reinf.material == "A240-304"


def test_cm1_concrete_and_typeE():
    r = _e("CM1A-")
    pier = _get(r, "水泥墩")
    assert pier and pier.material == "混凝土" and pier.total_weight > 0
    r2 = _e("CM1E-300H-4\"")
    assert _get(r2, "水泥墩") and _get(r2, "L型基礎螺栓") is not None   # E 型加基礎螺栓


def test_cm1_unknown_type():
    assert _e("CM1Z-").error
