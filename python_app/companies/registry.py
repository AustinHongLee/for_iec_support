"""公司模板註冊表：company_id -> analyze(fullstring, overrides) -> AnalysisResult。"""
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


def get_analyzer(company):
    return COMPANIES.get((company or "").upper())
