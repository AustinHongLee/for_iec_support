"""益高 FS12 — FIELD SUPPORT 管架 (E-KO ENGINEERING)

編號: FS12{固定方式}-{序號}-{L}L-{H}H[-{H1}H1]
  例 FS12W-2-1300H-400L / FS12E-1-500L-500H-300H1

結構: 冂型角鋼門架
  ① 角鋼 (序號1=L50*50*6 / 序號2=L75*75*9, A36), 冂型, 長度 = L + 2H, ×1
  ② 底板 9t (A36), ×2  (W 焊接免鑽孔)
  ※ FS12 本體不含 U型螺栓：管線固定另由 VA2 系列接手(使用者確認 2026-07-21)。
固定方式:
  A 基礎螺栓(③, 含水泥墩⑦) / B 螺栓錨帽(⑥) / E 擴展螺栓(④, 含水泥墩⑦) / W 焊接(免螺栓、免水泥墩)
水泥墩詳見 CM1A；未指定 H1 依規則不製作。
資料來源: companies/eko/configs/fs12.json
"""
from core.models import AnalysisResult, set_remark
from core.steel import add_steel_section_entry
from core.plate import add_plate_entry
from core.bolt import add_custom_entry, add_estimated_fastener_entry
from core.material_specs import (
    STRUCTURAL_A36_SS400,
    SUPPORT_PLATE_A36_SS400,
)

_VALID_FIX = {"A", "B", "E", "W"}


def _bolt_spec_material(bolts, key, default_material=""):
    """回傳 (spec, material)；相容 config 中的 dict 或純字串。"""
    entry = bolts.get(key, {})
    if isinstance(entry, dict):
        return entry.get("spec", ""), entry.get("material", "") or default_material
    return entry, default_material


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))

    serial = parsed.get("serial")
    fix = (parsed.get("fix") or "").upper()
    L = parsed.get("L")
    H = parsed.get("H")
    H1 = parsed.get("H1")

    serials = config.get("serials", {})
    if serial is None or str(serial) not in serials:
        result.error = f"FS12: 未知或缺少序號 {serial!r} (應為 {sorted(serials)})"
        return result
    if fix not in _VALID_FIX:
        result.error = f"FS12: 未知或缺少固定方式 {fix!r} (應為 A/B/E/W)"
        return result
    if L is None or H is None:
        result.error = "FS12: 缺少 L(長度) 或 H(高度) 尺寸"
        return result

    sdef = serials[str(serial)]
    angle_dim = sdef["angle"]

    h_limit = config.get("h_limit_mm", 1500)
    if H >= h_limit:
        result.warnings.append(f"H={H}mm 超出 FS12 適用範圍 (H<{h_limit}mm)")
    h_max = sdef.get("h_max_mm")
    if h_max and H > h_max:
        result.warnings.append(
            f"H={H}mm 超出序號{serial} ({angle_dim}) 負荷表最大 H={h_max}mm"
        )

    # ① 角鋼 冂型門架 = 3 支獨立下料件（焊接組立，非彎折單一長料）：
    #    立柱 ×2(長=H) + 上橫樑 ×1(長=L)。各自長度分開列出，下料/裁切才能正確套排；
    #    切勿併成單一 L+2H 長料，否則材料合計/下料明細失真。(依使用者回饋 2026-07-21)
    add_steel_section_entry(result, "Angle", angle_dim, H, steel_qty=2,
                            material=STRUCTURAL_A36_SS400)
    set_remark(result.entries[-1], f"立柱 ×2, 長={H}mm (冂型門架, 焊接組立)")
    add_steel_section_entry(result, "Angle", angle_dim, L, steel_qty=1,
                            material=STRUCTURAL_A36_SS400)
    set_remark(result.entries[-1], f"上橫樑 ×1, 長={L}mm (冂型門架, 焊接組立)")

    # ② 底板 9t, ×2 (方板 A×A；B=螺栓中心距、C=孔邊距)
    bp = sdef["base_plate"]
    hole_note = "焊接免鑽孔" if fix == "W" else f"鑽∅{bp.get('hole_dia', '?')}孔配固定螺栓"
    add_plate_entry(result, plate_a=bp["A"], plate_b=bp["A"], plate_thickness=9,
                    plate_name="底板", material=SUPPORT_PLATE_A36_SS400, plate_qty=2,
                    notes_zh=f"{bp['A']}×{bp['A']}×9t 方板, ×2, {hole_note}")
    if fix != "W":     # 加工繪圖:4-∅ 孔,中心距 B,邊距 C
        from .. import plating as _plating
        _plating.attach_geom(result.entries[-1],
                             hole={"n": 4, "dia": bp["hole_dia"], "px": bp["B"], "py": bp["B"], "edge": bp["C"]})

    # 固定五金 / 水泥墩（依固定方式）
    bolts = config.get("bolts", {}).get(str(serial), {})
    pier_needed = False
    if fix == "A":
        spec, mat = _bolt_spec_material(bolts, "anchor_bolt", "A307-B")
        add_estimated_fastener_entry(
            result,
            name="L型基礎螺栓",
            spec=spec,
            material=mat,
            quantity=8,
            kind="foundation_bolt",
            unit="SET",
            remark="適用 FS12A, ×8",
        )
        pier_needed = True
    elif fix == "E":
        spec, mat = _bolt_spec_material(bolts, "exp_bolt", "碳鋼(鍍鋅)")
        add_estimated_fastener_entry(
            result,
            name="擴展螺栓",
            spec=spec,
            material=mat,
            quantity=8,
            kind="expansion_bolt",
            unit="SET",
            remark="適用 FS12E, ×8",
        )
        pier_needed = True
    elif fix == "B":
        spec, mat = _bolt_spec_material(bolts, "nut_bolt", "A307-B 鍍鋅")
        add_estimated_fastener_entry(
            result,
            name="螺栓錨帽",
            spec=spec,
            material=mat,
            quantity=8,
            unit="SET",
            remark="適用 FS12B, ×8",
        )
    elif fix == "W":
        result.warnings.append("FS12W 焊接固定：底板免鑽孔、不含固定螺栓與水泥墩")

    # ※ FS12 不含 U型螺栓：管線固定由 VA2 系列接手(使用者確認 2026-07-21)

    # ⑦ 水泥墩（A/E 且指定 H1）
    if pier_needed:
        if H1:
            add_custom_entry(result, "水泥墩", f"H1={H1}", "混凝土", 2, 0.0,
                             unit="PC", remark="詳見 CM1A, ×2 (另計)", category="其他")
        else:
            result.warnings.append(
                f"FS12{fix} 需水泥墩，但未指定 H1，依規則不製作 (詳見 CM1A)"
            )

    return result
