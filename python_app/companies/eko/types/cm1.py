"""益高 CM1 — 管支撐水泥墩。 CM1{A/B/C/D/E}-□H-□"
混凝土墩(1:2:4)。體積=平面積×高(高由 H 或預設)。TYPE E=籃式過濾器基礎(M×N)+L型基礎螺栓×2。
資料來源 configs/cm1.json。被眾多 FS 引用(『詳見 CM1x』);多數情況高度由父支撐 H1 帶入。"""
from core.models import AnalysisResult
from core.bolt import add_custom_entry


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    t = (parsed.get("mods") or "").upper()
    types = config.get("types", {})
    if t not in types:
        result.error = f"CM1: 未知型式 {t!r} (應為 {sorted(types)})"
        return result

    if t == "E":
        pipe = parsed.get("pipe")
        rows = [r for r in config.get("type_e_mnp", []) if abs(r["pipe"] - (pipe or -1)) < 1e-6]
        if not rows:
            result.error = f"CM1E: 出入口管徑 {pipe!r} 不在表 (2/3/4/6\")"
            return result
        w, d = rows[0]["M"], rows[0]["N"]
    else:
        w, d = types[t]["plan_w"], types[t]["plan_d"]

    height = overrides.get("height") or parsed.get("H") or config.get("default_height_mm", 300)
    vol_m3 = w * d * height / 1e9
    weight = round(vol_m3 * config.get("concrete_density_kg_m3", 2400), 1)
    add_custom_entry(result, "水泥墩", f"TYPE {t} {w}×{d}×H{height}", "混凝土", 1, weight,
                     unit="PC", remark=f"混凝土{config.get('concrete_ratio','1:2:4')}; 體積≈{round(vol_m3,3)}m³; 埋深≥{config.get('embed_min_mm',200)}",
                     category="其他")
    if height == config.get("default_height_mm", 300) and not (parsed.get("H") or overrides.get("height")):
        result.warnings.append(f"未指定高度,以預設 {height}mm 概算(實務由 H1/現場決定)")
    if t == "E":
        a = config.get("type_e_anchor", {})
        add_custom_entry(result, "L型基礎螺栓", a.get("spec", "M12x200L"), a.get("material", "A307-B"),
                         a.get("qty", 2), 0.0, unit="SET", remark="籃式過濾器基礎 (重量另計)", category="螺栓類")
    return result
