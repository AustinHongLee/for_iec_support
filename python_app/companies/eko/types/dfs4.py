"""益高 DFS4 — FS LOWER SUPPORT FS下支架。 DFS4{A/B/E/W}-序號-□H
序號1/2/3→支撐管2"/3"/4"。件:①底板9t B×B ②補強板6t×4(三角肋近似) ③支撐管A53-B 長=H ④固定螺栓(依固定方式,×4)。
資料來源 configs/dfs4.json。被 FS4/FS9/FS11 引用。"""
from core.models import AnalysisResult, set_remark
from core.plate import add_plate_entry
from core.pipe import add_pipe_entry
from core.bolt import add_estimated_fastener_entry
from core.material_specs import SUPPORT_PIPE_A53GRB

_VALID_FIX = {"A", "B", "E", "W"}


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    serial = parsed.get("serial")
    fix = (parsed.get("fix") or "").upper()
    H = parsed.get("H")
    serials = config.get("serials", {})
    if serial is None or str(serial) not in serials:
        result.error = f"DFS4: 未知序號 {serial!r} (應為 {sorted(serials)})"
        return result
    if fix not in _VALID_FIX:
        result.error = f"DFS4: 未知固定方式 {fix!r} (A/B/E/W)"
        return result
    if H is None:
        result.error = "DFS4: 缺少 H(支架高度)"
        return result
    sdef = serials[str(serial)]
    B = sdef["B"]

    # ① 底板 9t B×B
    add_plate_entry(result, plate_a=B, plate_b=B, plate_thickness=9, plate_name="底板",
                    material=config["plate_material"], plate_qty=1,
                    notes_zh=f"{B}×{B}×9t; 孔距{sdef['hole_pitch']}(4-∅22){'; W焊接免鑽孔' if fix=='W' else ''}")
    # ② 補強板 6t ×4 (三角肋, 75×75 近似)
    add_plate_entry(result, plate_a=75, plate_b=75, plate_thickness=6, plate_name="補強板",
                    material=config["plate_material"], plate_qty=4,
                    net_area_mm2=0.5 * 75 * 75,
                    notes_zh="三角肋 ×4 (75×75×6t 近似; 圖以60°/reach75幾何)")
    # ③ 支撐管 A53-B 長=H
    add_pipe_entry(result, sdef["pipe"], config.get("pipe_schedule", "SCH.40"), H, SUPPORT_PIPE_A53GRB)
    set_remark(result.entries[-1], f"支撐管 {sdef['pipe']}\" A53-B, 長={H}mm")
    # ④ 固定螺栓 (依固定方式) ×4
    b = config.get("bolts", {})
    qty = config.get("bolt_qty", 4)
    if fix == "A":
        add_estimated_fastener_entry(
            result,
            name="L型基礎螺栓",
            spec=b["anchor_bolt"]["spec"],
            material=b["anchor_bolt"]["material"],
            quantity=qty,
            kind="foundation_bolt",
            unit="SET",
            remark="適用 DFS4A",
        )
    elif fix == "B":
        add_estimated_fastener_entry(
            result,
            name="螺栓連帽",
            spec=b["nut_bolt"]["spec"],
            material=b["nut_bolt"]["material"],
            quantity=qty,
            unit="SET",
            remark="適用 DFS4B",
        )
    elif fix == "E":
        add_estimated_fastener_entry(
            result,
            name="擴展螺栓",
            spec=b["exp_bolt"]["spec"],
            material=b["exp_bolt"]["material"],
            quantity=qty,
            kind="expansion_bolt",
            unit="SET",
            remark="適用 DFS4E",
        )
    else:
        result.warnings.append("DFS4W 焊接固定：底板免鑽孔、不含固定螺栓")
    return result
