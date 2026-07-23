"""益高 通用元件清單引擎 — 涵蓋導架/錨定/管蹄/托撐/虛設管等單段家族。

以 config 的 components[] 逐件組裝，容錯優先（缺尺寸→警告略過，不硬錯）。
元件種類：
  steel(型鋼,逐桿分列) · plate(鋼板) · pipe(管) · bolt_by_fix(依固定字母出螺栓)
  · ubolt(引用UB1) · ref(引用他件,重量另計) · pier(水泥墩)
查表 table_key=pipe(依管徑列, 各列含 max)/serial(依序號 dict)/null(固定尺寸圖)。
值來源：數字=固定; 大寫維度(H/L/L1/L2/A/H1/H2)=從編號取; "pipe"=管徑; 其餘字串=查 row 欄位。
逐桿分列見 [[feedback-cutting-members]]。資料來源 各 config 的 data_update_note。
"""
from core.models import AnalysisResult, set_remark
from core.steel import add_steel_section_entry
from core.plate import add_plate_entry
from core.pipe import add_pipe_entry
from core.bolt import add_custom_entry
from core.material_specs import SUPPORT_PIPE_A53GRB
from .. import ubolt as _ubolt
from .. import plating as _plating

_DIMS = ("H", "L", "L1", "L2", "A", "H1", "H2")


def _hole(c, parsed, row):
    """解析元件孔位設定(literal 或 *_field 取 row)。無 hole→None。"""
    h = c.get("hole")
    if not h:
        return None
    out = {}
    for k in ("n", "dia", "px", "py", "edge", "pattern", "bolt"):
        if k in h:
            out[k] = h[k]
        elif k + "_field" in h:
            out[k] = (row or {}).get(h[k + "_field"])
    return out
_SECTION_ZH = {"Angle": "角鋼", "Channel": "槽鐵", "H Beam": "H型鋼", "I Beam": "I型鋼"}


def _v(val, parsed, row):
    """解析值：數字→原值；大寫維度→編號段；'pipe'→管徑；其餘→ row 欄位。"""
    if isinstance(val, (int, float)):
        return val
    if val in _DIMS:
        return parsed.get(val)
    if val == "pipe":
        return parsed.get("pipe")
    return (row or {}).get(val)


def _row(config, parsed, result):
    """回傳 row（dict）。容錯：序號缺→首序號；管徑超限→最大列；null→{}。"""
    tk, tbl = config.get("table_key"), config.get("table")
    if tk == "serial":
        s = parsed.get("serial")
        if s is not None and str(s) in tbl:
            return tbl[str(s)]
        first = sorted(tbl)[0]
        result.warnings.append(f"缺/未知序號 {s!r}，預設序號 {first}")
        return tbl[first]
    if tk == "pipe":
        p = parsed.get("pipe")
        if p is None:
            result.warnings.append("缺配管管徑，採表列首列近似")
            return tbl[0]
        for r in tbl:
            if p <= r["max"] + 1e-6:
                return r
        result.warnings.append(f"管徑 {p}\" 超出表列上限，採最大列近似")
        return tbl[-1]
    return {}


def _sec_of(c, parsed, row, result):
    """型鋼斷面：sec 固定 / sec_field 查 row / sec_bands 依管徑帶。回傳 (stype, dim)。"""
    if c.get("sec_field"):
        return c.get("stype", "Angle"), row.get(c["sec_field"])
    if c.get("sec_bands"):
        p = parsed.get("pipe")
        bands = c["sec_bands"]
        if p is None:
            result.warnings.append(f"{c.get('name','型鋼')} 缺管徑，採首帶斷面")
            b = bands[0]
        else:
            b = next((x for x in bands if p <= x["max"] + 1e-6), bands[-1])
        return b["sec"][0], b["sec"][1]
    sec = c["sec"]
    return sec[0], sec[1]


def _add_steel(result, stype, dim, length, qty, mat, config, name, structure):
    sw = (config.get("section_weights") or {}).get(dim)
    if sw is None:
        add_steel_section_entry(result, stype, dim, length, steel_qty=qty, material=mat)
    else:
        uw = round(length / 1000 * sw, 2)
        add_custom_entry(result, _SECTION_ZH.get(stype, stype), dim, mat, qty, uw,
                         unit="M", remark=f"每米重 {sw} kg/m (核心鋼表無此斷面)", category="型鋼類")
        result.entries[-1].length = length
        result.entries[-1].weight_per_unit = sw
    set_remark(result.entries[-1], f"{name} ×{qty}, 長={length}mm ({structure})")


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    code = config.get("code", "EKO")
    structure = config.get("structure", "")
    mat_def = config.get("material", "A36")

    fixm = (parsed.get("fix") or "").upper()
    fixes = config.get("fix_letters")
    if fixes is not None and fixm and fixm not in fixes:
        result.warnings.append(
            f"{code}: 非標準固定方式 {fixm!r} (標準 {fixes})，暫視為不固定/免螺栓")
        fixm = "N"

    row = _row(config, parsed, result)

    def _active(c):
        w = c.get("when")
        return (w is None) or (fixm in w)

    for c in config.get("components", []):
        if not _active(c):
            continue
        kind = c["kind"]

        if kind == "steel":
            stype, dim = _sec_of(c, parsed, row, result)
            length = _v(c.get("len"), parsed, row)
            if dim is None or length is None:
                result.warnings.append(f"{code}: {c.get('name','型鋼')} 缺規格/長度，略過"); continue
            _add_steel(result, stype, dim, length, c.get("qty", 1),
                       c.get("material", mat_def), config, c.get("name", ""), structure)

        elif kind == "plate":
            t = _v(c.get("t"), parsed, row); w = _v(c.get("w"), parsed, row); ll = _v(c.get("l"), parsed, row)
            if None in (t, w, ll):
                result.warnings.append(f"{code}: {c.get('name','鋼板')} 缺尺寸，略過"); continue
            hole_note = "; 免鑽孔" if (c.get("name") == "底板" and fixm in ("W", "N")) else ""
            tri = c.get("tri")   # 直角三角形肋板：淨面積取外接矩形一半
            kw = {"net_area_mm2": round(0.5 * w * ll, 1)} if tri else {}
            sfx = "三角" if tri else ""
            add_plate_entry(result, plate_a=w, plate_b=ll, plate_thickness=t,
                            plate_name=c.get("name", "鋼板"), material=c.get("material", mat_def),
                            plate_qty=c.get("qty", 1),
                            notes_zh=f"{w}×{ll}×{t}t{sfx} ×{c.get('qty',1)}"
                                     + hole_note + ("; 尺寸近似" if c.get("approx") else ""), **kw)
            # 加工繪圖幾何：孔位/輪廓(免鑽孔者不掛孔)
            _hl = None if fixm in ("W", "N") else _hole(c, parsed, row)
            if _hl or c.get("shape"):
                _plating.attach_geom(result.entries[-1], hole=_hl, shape=c.get("shape"),
                                     bolt_spec=(c.get("hole") or {}).get("bolt", ""))

        elif kind == "pipe":
            size = _v(c.get("size"), parsed, row)
            length = _v(c.get("len"), parsed, row)
            if size is None or length is None:
                result.warnings.append(f"{code}: {c.get('name','管')} 缺尺寸/長度，略過"); continue
            add_pipe_entry(result, str(size), c.get("sch", "SCH.40"), length, SUPPORT_PIPE_A53GRB)
            if c.get("name"):        # 品名用元件名(撐管/支撐套管)取代核心預設「管路」
                result.entries[-1].name = c["name"]
            set_remark(result.entries[-1],
                       f"{c.get('name','管')} {size}\"{c.get('sch','SCH.40')}, 長={length}mm"
                       + ("; 長度現場配合" if c.get("field_fit") else "")
                       + ("; ⚠材質須同母材(預設碳鋼A53 Gr.B)" if config.get("material_reminder") else ""))

        elif kind == "bolt_by_fix":
            bf = c.get("by_fix", {})
            if fixm in bf:
                b = bf[fixm]
                add_custom_entry(result, b["name"], b.get("spec", ""), b.get("mat", "A307-B"),
                                 b.get("qty", 4), 0.0, unit="SET",
                                 remark=f"適用 {code}{fixm} (重量另計)", category="螺栓類")
            elif fixm == "W":
                result.warnings.append(f"{code}W 焊接固定：免鑽孔、不含固定螺栓")
            elif fixm == "N":
                result.warnings.append(f"{code}N 不固定：免鑽孔、無螺栓")

        elif kind == "ubolt":
            if c.get("qty") == "site":
                uq = int(overrides.get("ubolt_qty", 1)); note = "數量配合現場需要"
            else:
                uq = c.get("qty", 1); note = ""
            _ubolt.add_ubolt(result, parsed.get("pipe"), qty=uq, extra_note=note)

        elif kind == "ref":
            add_custom_entry(result, c["name"], c.get("spec", ""), c.get("material", ""),
                             c.get("qty", 1), 0.0, unit=c.get("unit", "PC"),
                             remark=c.get("note", ""), category=c.get("category", "其他"))

        elif kind == "pier":
            H1 = parsed.get("H1")
            if c.get("needs_h1"):
                if H1:
                    add_custom_entry(result, "水泥墩", f"{c['type']} H1={H1}", "混凝土",
                                     c.get("qty", 1), 0.0, unit="PC",
                                     remark=f"詳見 {c['type']} (另計)", category="其他")
                else:
                    result.warnings.append(f"{code}: 需水泥墩但未指定 H1，不製作 (詳見 {c['type']})")
            else:
                add_custom_entry(result, "水泥墩", c["type"], "混凝土", c.get("qty", 1), 0.0,
                                 unit="PC", remark=f"詳見 {c['type']} (另計)", category="其他")

    for w in config.get("extra_warnings", []):
        result.warnings.append(w)
    return result
