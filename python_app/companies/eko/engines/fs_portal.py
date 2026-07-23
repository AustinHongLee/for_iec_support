"""益高 FS 角鋼門架/立柱型 — 共用引擎（FS2/FS3/FS13/FS14/FS15；FS12 暫用專用版）。

結構：角鋼成員(立柱/斜腳/橫樑，逐桿分列) + 底板9t(恆有) + 固定五金 + U型螺栓 + 水泥墩。
固定方式：A=基礎螺栓 / B=螺栓連帽 / E=擴展螺栓 / W=焊接(免鑽免螺栓) / N=不固定(免鑽免墩)。
底板恆為結構件(A/B/E 鑽孔、W/N 免鑽)；螺栓僅 A/B/E 出；水泥墩僅 A/E 且有 H1 才出。
查表：table_key=pipe(依管徑取列) 或 serial(依序號)。成員長度來源 H/L/A(頂寬)/slant(A字斜腳幾何)。
逐桿分列見 [[feedback-cutting-members]]。資料來源：各 fs*.json（依各圖轉錄）。
"""
import math
from core.models import AnalysisResult, set_remark
from core.steel import add_steel_section_entry
from core.plate import add_plate_entry
from core.bolt import add_custom_entry
from .. import ubolt as _ubolt
from .. import plating as _plating

_BOLT = {  # fixm -> (件名, 材質, row欄位)
    "A": ("L型基礎螺栓", "A307-B", "anchor"),
    "B": ("螺栓連帽", "A307-B 鍍鋅", "nut"),
    "E": ("擴展螺栓", "碳鋼(鍍鋅)", "exp"),
}


def _row(config, parsed):
    """回傳 (row, err, warn)。容錯：缺/未知序號→預設首序號；管徑超限→採最大列近似。"""
    tk = config.get("table_key")
    tbl = config.get("table")
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
        for r in tbl:                       # rows sorted by max
            if p <= r["max"] + 1e-6:
                return r, None, None
        return tbl[-1], None, f"管徑 {p}\" 超出表列上限，採最大列近似"
    return None, "config table_key 未設定", None


def _mlen(lv, parsed, row):
    if isinstance(lv, int):
        return lv
    if lv in ("H", "L", "H1", "H2"):
        return parsed.get(lv)
    if lv == "A":
        return row.get("A")
    if lv == "slant":                        # A字斜腳：√(H² + ((B-A)/2)²)
        H, A, B = parsed.get("H"), row.get("A"), row.get("B")
        if None in (H, A, B):
            return None
        return round(math.sqrt(H ** 2 + ((B - A) / 2) ** 2))
    return None


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    code = config.get("code", "FS")
    fixm = (parsed.get("fix") or "").upper()
    fixes = config.get("fix_letters", ["A", "B", "E", "W"])
    if fixm not in fixes:
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
    # 序號-高度荷重上限(如 FS15 序1 不可用於 H1500)
    shmax = config.get("serial_hmax", {})
    _s = parsed.get("serial")
    if _s is not None and str(_s) in shmax and H and H > shmax[str(_s)]:
        result.warnings.append(
            f"{code}: 序號{_s} 於 H={H}mm 超出荷重表上限(H≤{shmax[str(_s)]}mm)，建議改用較大序號")

    mat = config.get("material", "A36")
    angle_dim = row.get("angle")

    # ── 角鋼成員（逐桿分列）──
    for m in config.get("members", []):
        if m.get("sec") == "row":
            stype, sdim = "Angle", angle_dim
        else:
            stype, sdim = m["sec"][0], m["sec"][1]
        length = _mlen(m["len"], parsed, row)
        if length is None:
            result.error = f"{code}: 成員 {m.get('role','?')} 缺尺寸 {m['len']}"
            return result
        add_steel_section_entry(result, stype, sdim, length,
                                steel_qty=m.get("qty", 1), material=mat)
        set_remark(result.entries[-1],
                   f"{m.get('role','')} ×{m.get('qty',1)}, 長={length}mm ({config.get('structure','')})")

    # ── 底板 9t（恆有結構件）──
    bp = config.get("base", {})
    bw, bl = row.get("base_w", bp.get("w")), row.get("base_l", bp.get("l"))
    hole_note = "免鑽孔" if fixm in ("W", "N") else f"鑽∅{row.get('d','?')}孔"
    add_plate_entry(result, plate_a=bw, plate_b=bl, plate_thickness=bp.get("t", 9),
                    plate_name="底板", material=bp.get("material", "A36"),
                    plate_qty=bp.get("qty", 2),
                    notes_zh=f"{bw}×{bl}×{bp.get('t',9)}t ×{bp.get('qty',2)}, {hole_note}"
                             + ("; 尺寸近似" if bp.get("approx") else ""))
    if fixm not in ("W", "N") and bp.get("hole"):   # 加工繪圖:底板孔位
        _plating.attach_geom(result.entries[-1],
                             hole=_plating.resolve_hole(bp["hole"], row),
                             bolt_spec=row.get(_BOLT.get(fixm, ("", "", ""))[2], "") if fixm in _BOLT else "")

    # ── 固定螺栓（僅 A/B/E）──
    if fixm in _BOLT:
        name, bmat, field = _BOLT[fixm]
        add_custom_entry(result, name, row.get(field, ""), bmat,
                         config.get("bolt_qty", 4), 0.0, unit="SET",
                         remark=f"適用 {code}{fixm}, ×{config.get('bolt_qty',4)} (重量另計)", category="螺栓類")
    elif fixm == "W":
        result.warnings.append(f"{code}W 焊接固定：底板免鑽孔、不含固定螺栓")
    elif fixm == "N":
        result.warnings.append(f"{code}N 不固定：底板免鑽孔、無螺栓、不做水泥墩")

    # ── U型螺栓 ──
    # (a) ubolt_separate：本體不自帶(如 FS15)，特定型式僅提醒「另以 UB1 標註計算」。
    # (b) ubolt：本體自帶(如 FS2/13/14)，依管徑給實際規格＋師傅叫料說法。
    ubsep = config.get("ubolt_separate")
    ub = config.get("ubolt", {})
    if ubsep:
        flags = parsed.get("flags") or []
        variant = "V" if "V" in flags else ("H" if "H" in flags else None)
        if variant == ubsep.get("variant"):
            hint = ""
            sp = _ubolt.lookup(parsed.get("pipe")) if parsed.get("pipe") is not None else None
            if sp:
                hint = f"；若採 {sp['label']}管 → {_ubolt.spec_text(sp)}"
            result.warnings.append(
                ubsep.get("note", f"{code} 型式{ubsep.get('variant')}之U型螺栓請另以 UB1 標註") + hint)
    elif ub:
        if ub.get("qty") == "site":
            uq = int(overrides.get("ubolt_qty", 1)); unote = "數量配合現場需要"
        else:
            uq = ub.get("qty", 1); unote = ""
        _ubolt.add_ubolt(result, parsed.get("pipe"), qty=uq, extra_note=unote)

    # ── 水泥墩（僅 A/E 且有 H1）──
    pier = config.get("pier")
    if pier and fixm in ("A", "E"):
        H1 = parsed.get("H1")
        if H1:
            add_custom_entry(result, "水泥墩", f"{pier['type']} H1={H1}", "混凝土",
                             pier.get("qty", 1), 0.0, unit="PC",
                             remark=f"詳見 {pier['type']}, ×{pier.get('qty',1)} (另計)", category="其他")
        else:
            result.warnings.append(f"{code}{fixm} 需水泥墩，但未指定 H1，依規則不製作 (詳見 {pier['type']})")

    for w in config.get("extra_warnings", []):
        result.warnings.append(w)
    return result
