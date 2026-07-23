"""益高 UB1 — U-BOLT U型螺栓。 UB1-□"  (□=公稱管徑吋)
被眾多 FS/PU/SS/VA 支撐引用(『詳見 UB1』)。可獨立判讀，也供父支撐依管徑解析。
規格/重量集中在 companies/eko/ubolt.py(師傅叫料直觀說法+彎鋼棒重量近似)。
資料來源: companies/eko/configs/ub1.json (依 UB1.pdf 全 21 列)。"""
from core.models import AnalysisResult
from .. import ubolt as _ub


def calculate(parsed, config, overrides=None):
    overrides = overrides or {}
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    pipe = parsed.get("pipe")
    if _ub.lookup(pipe) is None:
        result.error = f"UB1: 管徑 {pipe!r} 不在表內 (3/8\"~24\")"
        return result
    _ub.add_ubolt(result, pipe, qty=int(overrides.get("qty", 1)))
    return result
