"""益高 EB2 — EXPANSION BOLT 擴展螺栓。 EB2-M□-□L-{U}
被 FS/SS/PU 的 E(擴展螺栓固定)版引用。U=SUS304，否則鍍鋅鋼。
重量以螺桿近似：斷面 π/4·M² × 長度 L。資料來源 configs/eb2.json (M10/12/16/20)。"""
import math
from core.models import AnalysisResult
from core.bolt import add_custom_entry

_DENSITY = 7.85e-6


def bolt_weight(msize, length):
    return round(math.pi / 4 * msize ** 2 * length * _DENSITY, 3)


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    msize = parsed.get("msize")
    table = config.get("table", {})
    if msize is None or str(msize) not in table:
        result.error = f"EB2: 螺栓徑 M{msize} 不在表內 (M10/M12/M16/M20)"
        return result
    row = table[str(msize)]
    length = parsed.get("L") or row["L"]
    is_sus = "U" in parsed.get("flags", [])
    material = "SUS304" if is_sus else "鍍鋅鋼"
    qty = int(overrides.get("qty", 1))
    w = bolt_weight(msize, length)
    add_custom_entry(result, "擴展螺栓", f"EB2-M{msize}x{length}L{'-U' if is_sus else ''}",
                     material, qty, w, unit="PC",
                     remark=(f"鑽孔φ{row['drill_d']}x深{row['drill_depth']}, 最大固定厚{row['max_fix']}, "
                             f"抗拉{row['tensile_kg']}kg/抗剪{row['shear_kg']}kg@混凝土280"),
                     category="螺栓類")
    return result
