"""益高 FS 鋼管立柱型 — 元件清單式共用引擎（FS4/5/8/9/11/19/22/23）。

以 config 的 components[] 逐件組裝，元件種類：
  pipe_col/pipe(add_pipe_entry) · steel(型鋼) · plate(板) · bolt_by_fix(A→L型基礎螺栓/B→螺栓連帽/E→擴展螺栓)
  · bolt_fixed(恆有螺栓,如FS19) · ubolt(UB1引用) · pier(水泥墩CM1x) · subref(就地展開子件,如FS4/9/11 的 DFS4)。
查表 table_key=pipe(依管徑)/serial(依序號)；元件尺寸/規格可引用 row 欄位或固定值；長度來源 H/L/固定。
固定方式 A/B/E/W/N(部分圖無固定字母)。逐桿分列見 [[feedback-cutting-members]]。資料來源 各 fs*.json。
"""
import copy
from core.models import AnalysisResult, set_remark
from core.steel import add_steel_section_entry
from core.plate import add_plate_entry
from core.pipe import add_pipe_entry
from core.bolt import add_custom_entry, add_estimated_fastener_entry
from core.material_specs import SUPPORT_PIPE_A53GRB
from .. import ubolt as _ubolt
from .. import plating as _plating

_FIXBOLT = {"A": ("L型基礎螺栓", "A307-B", "anchor"),
            "B": ("螺栓連帽", "A307-B 鍍鋅", "nut"),
            "E": ("擴展螺栓", "碳鋼(鍍鋅)", "exp")}


def _row(config, parsed):
    """回傳 (row, err, warn)。容錯：序號缺/未知 → 預設首序號並警告。"""
    tk, tbl = config.get("table_key"), config.get("table")
    if tk == "serial":
        s = parsed.get("serial")
        if s is not None and str(s) in tbl:
            return tbl[str(s)], None, None
        first = sorted(tbl)[0]
        return tbl[first], None, f"缺/未知序號 {s!r}，預設序號 {first}"
    if tk == "pipe":
        p = parsed.get("pipe")
        if p is None:
            return None, "缺少配管管徑", None
        for r in tbl:
            if p <= r["max"] + 1e-6:
                return r, None, None
        return tbl[-1], None, f"管徑 {p}\" 超出表列上限，採最大列近似"
    return {}, None, None    # 無表(固定尺寸圖)


def _val(spec, key, row, default=None):
    """取值：優先 spec[key+'_field'] 指到 row 欄位，否則 spec[key]，否則 default。"""
    if key + "_field" in spec:
        return row.get(spec[key + "_field"], default)
    return spec.get(key, default)


def _len(lv, parsed, row):
    if isinstance(lv, (int, float)):
        return lv
    if lv in ("H", "L", "H1", "H2"):
        return parsed.get(lv)
    return row.get(lv)   # row 欄位名


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    code = config.get("code", "FS")
    fixm = (parsed.get("fix") or "").upper()
    fixes = config.get("fix_letters")
    if fixes is not None and fixm not in fixes:
        # 容錯：非標準/缺固定字母 → 警告並視為「不固定」(免螺栓/免墩)，不硬錯
        result.warnings.append(
            f"{code}: 非標準或缺固定方式 {fixm!r} (標準為 {fixes})，暫視為不固定/免螺栓")
        fixm = "N"

    row, err, warn = _row(config, parsed)
    if err:
        result.error = f"{code}: {err}"
        return result
    if warn:
        result.warnings.append(f"{code}: {warn}")

    H = parsed.get("H")
    lim = config.get("limits", {})
    if lim.get("Hmax") and H and H > lim["Hmax"]:
        result.warnings.append(f"H={H}mm 超出 {code} 適用範圍 (≤{lim['Hmax']}mm)")
    mat_def = config.get("material", "A36")

    for c in config.get("components", []):
        kind = c["kind"]
        if kind in ("pipe_col", "pipe"):
            size = _val(c, "size", row)
            sch = _val(c, "sch", row, "SCH.40")
            length = _len(c.get("len"), parsed, row)
            if size is None or length is None:
                result.warnings.append(f"{code}: {c.get('name','管')} 缺尺寸/長度，略過")
                continue
            add_pipe_entry(result, str(size), sch, length, SUPPORT_PIPE_A53GRB)
            set_remark(result.entries[-1], f"{c.get('name','管支撐')} {size}\"{sch}, 長={length}mm")

        elif kind == "steel":
            stype = c.get("type", "Channel")
            dim = _val(c, "dim", row)
            length = _len(c.get("len"), parsed, row)
            if dim is None or length is None:
                result.warnings.append(f"{code}: {c.get('name','型鋼')} 缺規格/長度，略過"); continue
            sw = (config.get("section_weights") or {}).get(dim)
            if sw is not None:      # 核心鋼表無此斷面，用 config 每米重後援
                uw = round(length / 1000 * sw, 2)
                zh = {"Angle": "角鋼", "Channel": "槽鐵", "H Beam": "H型鋼"}.get(stype, stype)
                add_custom_entry(result, zh, dim, c.get("material", mat_def), c.get("qty", 1), uw,
                                 unit="M", remark=f"每米重 {sw} kg/m", category="型鋼類")
                result.entries[-1].length = length
            else:
                add_steel_section_entry(result, stype, dim, length, steel_qty=c.get("qty", 1),
                                        material=c.get("material", mat_def))
            set_remark(result.entries[-1], f"{c.get('name','')} ×{c.get('qty',1)}, 長={length}mm")

        elif kind == "ref":
            rq = row.get(c["qty_field"], 1) if c.get("qty_field") else c.get("qty", 1)
            add_custom_entry(result, c["name"], c.get("spec", c.get("note", "")), "", rq, 0.0,
                             unit="PC", remark=c.get("note", ""), category="其他")

        elif kind == "plate":
            t = _val(c, "t", row); w = _val(c, "w", row); ll = _val(c, "l", row)
            if None in (t, w, ll):
                result.warnings.append(f"{code}: {c.get('name','板')} 缺尺寸，略過"); continue
            hole = "免鑽孔" if fixm in ("W", "N") else ""
            add_plate_entry(result, plate_a=w, plate_b=ll, plate_thickness=t,
                            plate_name=c.get("name", "鋼板"), material=c.get("material", mat_def),
                            plate_qty=c.get("qty", 1),
                            notes_zh=f"{w}×{ll}×{t}t ×{c.get('qty',1)}"
                                     + (f", {hole}" if hole and c.get("name") == "底板" else "")
                                     + ("; 尺寸近似" if c.get("approx") else ""))
            _hl = None if (c.get("name") == "底板" and fixm in ("W", "N")) else _plating.resolve_hole(c.get("hole"), row)
            if _hl or c.get("shape"):
                _plating.attach_geom(result.entries[-1], hole=_hl, shape=c.get("shape"))

        elif kind == "bolt_by_fix":
            if fixm in _FIXBOLT:
                name, bmat, fld = _FIXBOLT[fixm]
                add_estimated_fastener_entry(
                    result,
                    name=name,
                    spec=row.get(fld, ""),
                    material=bmat,
                    quantity=c.get("qty", 4),
                    unit="SET",
                    remark=f"適用 {code}{fixm}",
                )
            elif fixm == "W":
                result.warnings.append(f"{code}W 焊接固定：底板免鑽孔、不含固定螺栓")
            elif fixm == "N":
                result.warnings.append(f"{code}N 不固定：免鑽孔、無螺栓、不做水泥墩")

        elif kind == "bolt_fixed":
            spec = _val(c, "spec", row)
            add_estimated_fastener_entry(
                result,
                name=c.get("name", "螺栓連帽"),
                spec=spec or "",
                material=c.get("material", "A307-B 鍍鋅"),
                quantity=c.get("qty", 1),
                unit="SET",
            )

        elif kind == "ubolt":
            if c.get("qty") == "site":
                uq = int(overrides.get("ubolt_qty", 1)); note = "數量配合現場需要"
            else:
                uq = c.get("qty", 1); note = ""
            _ubolt.add_ubolt(result, parsed.get("pipe"), qty=uq, extra_note=note)

        elif kind == "pier":
            when = c.get("when", ["A", "E"])
            active = (when == "always") or (fixm in when)
            if active:
                H1 = parsed.get("H1")
                if H1:
                    add_custom_entry(result, "水泥墩", f"{c['type']} H1={H1}", "混凝土",
                                     c.get("qty", 1), 0.0, unit="PC",
                                     remark=f"詳見 {c['type']} (另計)", category="其他")
                elif fixm in ("A", "E") or when == "always":
                    result.warnings.append(f"{code}: 需水泥墩但未指定 H1，不製作 (詳見 {c['type']})")

        elif kind == "subref":
            _subref(result, c, parsed, fixm, H, row)

    if config.get("no_pier"):
        pass
    for w in config.get("extra_warnings", []):
        result.warnings.append(w)
    return result


def _subref(result, c, parsed, fixm, H, row):
    """就地展開子件 BOM（如 FS4/9/11 的 DFS4 下支架）。
    序號來源：serial_field(從 row 取,如 FS11 依側管徑對應) 否則沿用 parsed.serial。"""
    from ..config_loader import load_eko_config
    scode = c["code"]
    serial = row.get(c["serial_field"]) if c.get("serial_field") else parsed.get("serial")
    if serial is None:
        serial = 1
        result.warnings.append(f"子件 {scode}: 缺序號，預設序號 1")
    sub_parsed = {"raw": parsed.get("raw", ""), "serial": serial,
                  "fix": fixm, "H": _len(c.get("len", "H"), parsed, row), "mods": fixm}
    cfg = load_eko_config(scode)
    if cfg is None:
        result.warnings.append(f"子件 {scode} 設定缺失"); return
    if scode == "DFS4":
        from ..types import dfs4
        sub = dfs4.calculate(sub_parsed, cfg)
    else:
        result.warnings.append(f"子件 {scode} 未支援展開"); return
    if sub.error:
        result.warnings.append(f"子件 {scode}: {sub.error}"); return
    for e in sub.entries:
        result.add_entry(copy.deepcopy(e))
    result.warnings.extend(f"[{scode}] {w}" for w in sub.warnings)
