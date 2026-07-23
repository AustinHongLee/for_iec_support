"""益高 S1 — PIPE SHOE 管蹄。 S1-□"-□H  (H=保溫厚+25)
件:①管蹄柱(t×L長×H高) ②底板(t×L長×A寬) ③加強板(10\"~24\",t12×W×H,×2) ④補強板(不銹鋼管線,A240-304)。
資料來源 configs/s1.json (4段)。被 VA1/VG1/VG2 引用。"""
from core.models import AnalysisResult
from core.plate import add_plate_entry


def _band(bands, pipe):
    if pipe is None:
        return None
    for b in bands:
        if pipe <= b["max_size"] + 1e-6:
            return b
    return None


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    pipe = parsed.get("pipe")
    H = parsed.get("H")
    b = _band(config.get("bands", []), pipe)
    if b is None:
        result.error = f"S1: 管徑 {pipe!r} 不在範圍 (1/2\"~24\")"
        return result
    mat = config["material"]
    # ① 管蹄柱 (立板) t × L(沿管) × H(高)；容錯：缺 H 則略過需高度之件，仍出底板
    if H is None:
        result.warnings.append("S1: 缺 H(管蹄高=保溫厚+25)，管蹄柱/加強板略過，僅出底板")
    else:
        add_plate_entry(result, plate_a=b["stem_L"], plate_b=H, plate_thickness=b["stem_t"],
                        plate_name="管蹄柱", material=mat, plate_qty=1,
                        notes_zh=f"{b['stem_t']}t × {b['stem_L']}L × {H}H")
    # ② 底板 t × L × A(寬)
    add_plate_entry(result, plate_a=b["base_L"], plate_b=b["base_W"], plate_thickness=b["base_t"],
                    plate_name="底板", material=mat, plate_qty=1,
                    notes_zh=f"{b['base_t']}t × {b['base_L']}L × {b['base_W']}W")
    # ③ 加強板 (10"~24") t12 × W × H ×2
    if b.get("stiff_t") and H is not None:
        add_plate_entry(result, plate_a=b["stiff_W"], plate_b=H, plate_thickness=b["stiff_t"],
                        plate_name="加強板", material=mat, plate_qty=2,
                        notes_zh=f"{b['stiff_t']}t × {b['stiff_W']}W × {H}H ×2 (10\"~24\")")
    # ④ 補強板 (不銹鋼管線, 需 override sus_pipe)
    if overrides.get("sus_pipe"):
        add_plate_entry(result, plate_a=b["reinf_L"], plate_b=round(3.14159 * (pipe * 25.4) / 3, 1),
                        plate_thickness=b["reinf_t"], plate_name="補強板",
                        material=config.get("sus_reinf_material", "A240-304"), plate_qty=1,
                        notes_zh=f"不銹鋼管底補強 {b['reinf_t']}t × {b['reinf_L']}L × 弧寬≈πOD/3")
    else:
        result.warnings.append("不銹鋼管線需另加補強板 A240-304 (以 sus_pipe override 啟用)")
    return result
