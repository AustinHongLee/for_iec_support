"""公司模板註冊表：company_id -> analyze(fullstring, overrides) -> AnalysisResult。"""
from functools import lru_cache
import re

from .eko import dispatch as _eko_dispatch


def _iec_analyze(fullstring, overrides=None):
    # 沿用原始核心的數字型 Type 判讀，未修改 core。
    from core.calculator import analyze_single
    return analyze_single(fullstring, overrides)


COMPANIES = {
    "EKO": _eko_dispatch.analyze,
    "IEC": _iec_analyze,
}

COMPANY_NAMES = {
    "EKO": "益高工程有限公司 (E-KO ENGINEERING)",
    "IEC": "IEC 案 (數字型 Type 01/51…)",
}

# 使用者面的設計公司短標籤（顯示用）。IEC 數字型 Type＝長春案；EKO＝益高工程。
# 這是「把既有的代碼分流判斷顯示成公司名」的唯一對照表，改名只改這裡。
COMPANY_DISPLAY = {
    "EKO": "益高",
    "IEC": "長春",
}


def get_analyzer(company):
    return COMPANIES.get((company or "").upper())


@lru_cache(maxsize=8192)
def design_company_id(designation: str) -> str | None:
    """Return a company only when the designation has a defensible match."""
    try:
        if _eko_dispatch.can_handle(designation or ""):
            return "EKO"
    except Exception:
        pass

    type_code = str(designation or "").strip().split("-", 1)[0].upper()
    if re.fullmatch(r"\d+(?:T)?", type_code) or type_code == "PENETRATION HOLE":
        return "IEC"
    return None


@lru_cache(maxsize=8192)
def design_company_label(designation: str) -> str:
    """Return a display label without guessing an unmatched company."""
    company_id = design_company_id(designation)
    return COMPANY_DISPLAY.get(company_id, "待判定")
