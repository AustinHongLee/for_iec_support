"""益高 SS 結構撐 — 通用引擎（涵蓋 SS 全家族 17 張）。

以 config 的「成員清單 members」驅動，逐桿分列(每桿各自長度)；固定方式決定底板/螺栓：
  B=螺栓連帽(+底板) / E=擴展螺栓(+底板) / W=焊接(無底板螺栓)。
支援：序號→型鋼(serial_sections)、雙字母固定(fix_scheme=double, 方向S/V + B/W)、
     恆焊接型(always_welded, 無固定字母)、耳板等額外板(extra_plates)、U型螺栓引用(ubolt_ref)。
成員長度來源(len)：H / L / H1 / H2 / sumL(所有□L相加, 用於 SS34 兩側懸挑) / 固定整數。
逐桿分列規則見 [[feedback-cutting-members]]。資料來源：各 ss*.json（依各圖普查/轉錄）。
"""
import math

from core.models import AnalysisResult, set_remark
from core.steel import add_steel_section_entry
from core.plate import add_plate_entry
from core.bolt import add_custom_entry, add_estimated_fastener_entry
from .. import ubolt as _ubolt
from .. import plating as _plating


# 與 core/steel.py _SECTION_NAME_ZH 對齊，確保材料合計同名彙總
_SECTION_ZH = {"Angle": "角鋼", "Channel": "槽鐵", "H Beam": "H型鋼", "I Beam": "I型鋼"}


def _add_member(result, stype, sdim, length, qty, mat, config):
    """加型鋼成員；斷面若不在核心鋼表，改用 config['section_weights'] 的每米重(kg/m)後援，
    並設好 length 供下料。避免修改核心 data/steel_sections。"""
    override = (config.get("section_weights") or {}).get(sdim)
    if override is None:
        add_steel_section_entry(result, stype, sdim, length, steel_qty=qty, material=mat)
        return
    unit_w = round(length / 1000 * override, 2)
    add_custom_entry(result, _SECTION_ZH.get(stype, stype), sdim, mat, qty, unit_w,
                     unit="M", remark=f"每米重 {override} kg/m (核心鋼表無此斷面)", category="型鋼類")
    e = result.entries[-1]
    e.length = length
    e.weight_per_unit = override


def _length(lv, parsed):
    if isinstance(lv, int):
        return lv
    if isinstance(lv, dict) and lv.get("formula") == "diagonal":
        base = parsed.get(lv.get("base", "L"))
        if base is None:
            return None
        run = base - lv.get("end_offset", 0)
        angle = lv.get("angle_deg", 0)
        if run <= 0 or not 0 < angle < 90:
            return None
        return round(run / math.cos(math.radians(angle)))
    if lv == "sumL":
        return sum(parsed.get("L_list") or []) or None
    return {"H": parsed.get("H"), "L": parsed.get("L"),
            "H1": parsed.get("H1"), "H2": parsed.get("H2"),
            "L1": parsed.get("L1")}.get(lv)


def _resolve_fix(parsed, config):
    """回傳 (fixm, orient, warn)。容錯：資訊不足→暫視為焊接並警告。"""
    mods = (parsed.get("mods") or "").upper()
    if config.get("always_welded"):
        return "W", None, None
    if config.get("fix_scheme") == "double":
        if len(mods) < 2:
            return "W", None, f"{config.get('code')}: 需方向+固定字母(如 SB/VW)，收到 {mods!r}，暫視為焊接"
        return mods[1], mods[0], None
    return (mods[0] if mods else ""), None, None


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    code = config.get("code", "SS")

    fixm, orient, warn = _resolve_fix(parsed, config)
    if warn:
        result.warnings.append(warn)
    fixes = config.get("fix_methods", {})
    if not config.get("always_welded") and fixm not in fixes:
        result.warnings.append(
            f"{code}: 非標準或缺固定方式 {fixm!r} (標準為 {sorted(fixes)})，暫視為焊接/免螺栓")
        fixm = "W"

    serial = parsed.get("serial")
    ss = config.get("serial_sections")
    if ss is not None and (serial is None or str(serial) not in ss):
        first = sorted(ss)[0]
        result.warnings.append(f"{code}: 缺/未知序號 {serial!r}，預設序號 {first}")
        serial = first

    lim = config.get("limits", {})
    lmax = lim.get("Lmax")
    sl = config.get("serial_limits")
    if sl and serial is not None and str(serial) in sl:
        lmax = sl[str(serial)]
    if lim.get("Hmax") and parsed.get("H") and parsed["H"] > lim["Hmax"]:
        result.warnings.append(f"H={parsed['H']}mm 超出 {code} 上限 {lim['Hmax']}mm")
    if lmax and parsed.get("L") and parsed["L"] > lmax:
        result.warnings.append(f"L={parsed['L']}mm 超出 {code}{('序'+str(serial)) if sl else ''} 上限 {lmax}mm")
    for w in config.get("extra_warnings", []):
        result.warnings.append(w)

    mat = config.get("material", "A36")

    # ── 成員（逐桿分列）──
    for m in config.get("members", []):
        sec = m["sec"]
        if sec == "serial":
            stype, sdim = ss[str(serial)]
        else:
            stype, sdim = sec[0], sec[1]
        length = _length(m["len"], parsed)
        if length is None:
            result.warnings.append(f"{code}: 成員 {m.get('role','?')} 缺尺寸 {m['len']}，略過")
            continue
        _add_member(result, stype, sdim, length, m.get("qty", 1), mat, config)
        set_remark(result.entries[-1],
                   f"{m.get('role','')} ×{m.get('qty',1)}, 長={length}mm ({config.get('structure','')})")

    # ── 額外板（恆有；如擋板、耳板）──
    for p in config.get("extra_plates", []):
        kw = {}
        if p.get("net_area_mm2"):
            kw["net_area_mm2"] = p["net_area_mm2"]
        add_plate_entry(result, plate_a=p["a"], plate_b=p["b"], plate_thickness=p["t"],
                        plate_name=p.get("name", "鋼板"),
                        material=p.get("material", "A283 Gr.C"), plate_qty=p.get("qty", 1),
                        notes_zh=p.get("note", ""), **kw)
        if p.get("hole") or p.get("shape"):
            _plating.attach_geom(result.entries[-1],
                                 hole=_plating.resolve_hole(p.get("hole")), shape=p.get("shape"))

    welded = config.get("always_welded") or fixm == "W"
    if not welded:
        # 底板（B/E 依 plate_fixes）
        if fixm in config.get("plate_fixes", []) and config.get("base_plate"):
            bp = config["base_plate"]
            # 底板尺寸可為固定或依序號
            if bp.get("by_serial"):
                bs = bp["by_serial"]
                a, b = bs.get(str(serial), bs[sorted(bs)[0]])
            else:
                a, b = bp["a"], bp["b"]
            add_plate_entry(result, plate_a=a, plate_b=b, plate_thickness=bp["t"],
                            plate_name="底板", material=bp.get("material", "A283 Gr.C"),
                            plate_qty=bp.get("qty", 2),
                            notes_zh=f"{a}×{b}×{bp['t']}t ×{bp.get('qty',2)}"
                                     + (" (尺寸近似)" if bp.get("approx") else ""))
            hspec = bp.get("by_serial_hole", {}).get(str(serial)) if bp.get("by_serial_hole") else bp.get("hole")
            if hspec:
                _plating.attach_geom(result.entries[-1], hole=_plating.resolve_hole(hspec))
        # 螺栓：B→螺栓連帽 / E→擴展螺栓
        sb = config.get("serial_bolts", {})
        if fixm == "B" and config.get("nut_bolt"):
            nb = config["nut_bolt"]
            spec = sb.get(str(serial), {}).get("B") if nb.get("spec") == "serial" else nb["spec"]
            add_estimated_fastener_entry(
                result,
                name="螺栓連帽",
                spec=spec,
                material="A307-B 鍍鋅",
                quantity=nb.get("qty", 4),
                unit="SET",
                remark=f"適用 {code}B, ×{nb.get('qty',4)}",
            )
        elif fixm == "E" and config.get("exp_bolt"):
            eb = config["exp_bolt"]
            spec = sb.get(str(serial), {}).get("E") if eb.get("spec") == "serial" else eb["spec"]
            add_estimated_fastener_entry(
                result,
                name="擴展螺栓",
                spec=spec,
                material="碳鋼(鍍鋅)",
                quantity=eb.get("qty", 4),
                unit="SET",
                remark=f"適用 {code}E, ×{eb.get('qty',4)}",
            )
    else:
        result.warnings.append(f"{code}{'' if config.get('always_welded') else fixm} 焊接固定：不含底板與螺栓")

    # ── U型螺栓引用（SS33，依管徑給實際規格＋師傅叫料說法）──
    if config.get("ubolt_ref") and parsed.get("pipe"):
        _ubolt.add_ubolt(result, parsed.get("pipe"), qty=1,
                         extra_note="含連帽(另計)；見 DWG UB1", name="U型螺栓連帽")

    if lim.get("max_load_kg"):
        result.warnings.append(f"參考：最大支撐重量 {lim['max_load_kg']} kg")
    if config.get("length_formula"):
        result.warnings.append(f"長度依公式 {config['length_formula']}")
    return result
