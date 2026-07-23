"""益高 加工件(板)繪圖幾何附掛：把孔位/輪廓填進 entry.geometry，供日後拉圖取用。

用法：呼叫 add_plate_entry 後，若 config 元件帶 hole/shape，呼叫 attach_geom() 補上：
  hole  = {"n":4, "dia":19, "px":190, "py":190, "edge":35}  # px/py=孔中心距(mm)
  shape = {"kind":"triangle"/"lug"/"wing", "spec":"直角三角 底75×高45×9t", "net_area":<mm²>}
孔位存進 geometry.holes(HolePattern)；輪廓存 shape_spec/shape_kind；異形板自動歸類 shaped_plate。
"""
from core.models import HolePattern
from core.component_roles import manufacturing_type_for


def resolve_hole(spec, row=None):
    """解析孔位設定(literal 或 *_field 取 row)。無→None。"""
    if not spec:
        return None
    row = row or {}
    out = {}
    for k in ("n", "dia", "px", "py", "edge", "pattern", "bolt"):
        if k in spec:
            out[k] = spec[k]
        elif k + "_field" in spec:
            out[k] = row.get(spec[k + "_field"])
    return out


def attach_geom(entry, hole=None, shape=None, bolt_spec=""):
    g = entry.geometry
    if g is None:
        return entry
    if hole:
        g.holes = HolePattern(
            pattern=hole.get("pattern", "rect"),
            pitch_x=hole.get("px", 0) or 0,
            pitch_y=hole.get("py", 0) or 0,
            diameter=hole.get("dia", 0) or 0,
            fastener_spec=bolt_spec or hole.get("bolt", ""),
            count=hole.get("n", 4),
        )
        if hole.get("edge") is not None:
            g.notes_zh = (g.notes_zh + "; " if g.notes_zh else "") + f"孔邊距{hole['edge']}"
    if shape:
        if shape.get("spec"):
            g.shape_spec = shape["spec"]
        if shape.get("kind"):
            g.shape_kind = shape["kind"]
        if shape.get("net_area"):
            g.net_area_mm2 = shape["net_area"]
        entry.manufacturing_type = manufacturing_type_for(
            "", category=entry.category, shape_kind=g.shape_kind)
    return entry
