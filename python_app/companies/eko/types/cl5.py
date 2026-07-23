"""益高 CL5 — PIPE CLAMP 管夾。 CL5-□"
2 半片鋼帶(A36) + 螺栓連帽(A307-B鍍鋅)×2。管夾重量以彎板近似:展開長 π(A+t) × 帶寬E × 帶厚t。
資料來源 configs/cl5.json (全16列)。被 FS8 引用。"""
import math
from core.models import AnalysisResult
from core.plate import add_plate_entry
from core.bolt import add_custom_entry


def _row(table, pipe):
    if pipe is None:
        return None
    ge = [r for r in table if r["size"] >= pipe - 1e-6]
    return min(ge, key=lambda r: r["size"]) if ge else None


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    row = _row(config.get("table", []), parsed.get("pipe"))
    if row is None:
        result.error = f"CL5: 管徑 {parsed.get('pipe')!r} 不在表內 (1\"~24\")"
        return result
    dev_len = round(math.pi * (row["A"] + row["t"]), 1)   # 全圈展開長近似
    add_plate_entry(result, plate_a=dev_len, plate_b=row["E"], plate_thickness=row["t"],
                    plate_name="管夾", material=config.get("clamp_material", "A36"), plate_qty=1,
                    notes_zh=f"2半片彎板;帶寬{row['E']}x厚{row['t']};展開≈π(A{row['A']}+t)={dev_len}")
    add_custom_entry(result, "螺栓連帽", row["bolt"], config.get("bolt_material", "A307-B 鍍鋅"),
                     2, 0.0, unit="SET", remark="管夾兩側鎖固 ×2 (重量另計)", category="螺栓類")
    return result
