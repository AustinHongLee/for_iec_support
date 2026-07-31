"""益高判讀分派：解析編號 → 依 code 找計算器 → 載入設定 → 產出 BOM。"""
from core.models import AnalysisResult
from . import parser as _parser
from .config_loader import load_eko_config
from .validation import validate_designation
from .types import fs12, ub1, eb2, cl5, dfs4, s1, cm1
from .engines import ss_bracket, fs_portal, fs_pipe, eko_generic

HANDLERS = {
    "FS12": fs12.calculate,
    # FS 角鋼門架/立柱型（共用引擎 fs_portal）
    "FS2": fs_portal.calculate,
    "FS3": fs_portal.calculate,
    "FS13": fs_portal.calculate,
    "FS14": fs_portal.calculate,
    "FS15": fs_portal.calculate,
    # FS 鋼管立柱型（共用引擎 fs_pipe）
    "FS4": fs_pipe.calculate,
    "FS5": fs_pipe.calculate,
    "FS8": fs_pipe.calculate,
    "FS9": fs_pipe.calculate,
    "FS11": fs_pipe.calculate,
    "FS19": fs_pipe.calculate,
    "FS22": fs_pipe.calculate,
    "FS23": fs_pipe.calculate,
    "FS31": fs_pipe.calculate,
    "FS33": fs_pipe.calculate,
    "UB1": ub1.calculate,
    "EB2": eb2.calculate,
    "CL5": cl5.calculate,
    "DFS4": dfs4.calculate,
    "S1": s1.calculate,
    "CM1": cm1.calculate,
    # SS 結構撐家族（全 17 張共用引擎 ss_bracket）
    "SS1": ss_bracket.calculate,
    "SS6": ss_bracket.calculate,
    "SS8": ss_bracket.calculate,
    "SS11": ss_bracket.calculate,
    "SS12": ss_bracket.calculate,
    "SS13": ss_bracket.calculate,
    "SS15": ss_bracket.calculate,
    "SS21": ss_bracket.calculate,
    "SS22": ss_bracket.calculate,
    "SS24": ss_bracket.calculate,
    "SS25": ss_bracket.calculate,
    "SS26": ss_bracket.calculate,
    "SS27": ss_bracket.calculate,
    "SS28": ss_bracket.calculate,
    "SS33": ss_bracket.calculate,
    "SS34": ss_bracket.calculate,
    "SS37": ss_bracket.calculate,
    # 單段家族（導架/錨定/管蹄/托撐/虛設管/落地管架）共用引擎 eko_generic
    "G1": eko_generic.calculate,
    "G2": eko_generic.calculate,
    "A3": eko_generic.calculate,
    "VA1": eko_generic.calculate,
    "VA2": eko_generic.calculate,
    "VG5": eko_generic.calculate,
    "DS3": eko_generic.calculate,
    "ST3": eko_generic.calculate,
    "FS1": eko_generic.calculate,
    "PU4": eko_generic.calculate,
    "PU9": eko_generic.calculate,
    "PU11": eko_generic.calculate,
    "PU12": eko_generic.calculate,
    "PU23": eko_generic.calculate,
}

# 有圖但本階段未建，或無圖面：給明確訊息而非崩潰
_NO_DRAWING = {
    "FS24": "益高(EKO): FS24 無對應圖面(未提供)，暫無法建表；請補圖或確認編號",
    "PU22": "益高(EKO): PU22 無對應圖面(未提供)，暫無法建表；文法近似 PU23(□L-□L1)，請補圖確認",
}
# 已確認屬於益高、但計算規則尚未匯入主系統的型號。
# 保留在分派器中，讓主程式能正確標示公司，同時明確拒絕套用其他 Type 猜測。
_NOT_IMPORTED = {
    "PU1", "PU5", "PU21",
    "VG1", "VG2",
    "CS1", "CS2", "SUB1", "SUB2",
    "DS1", "ST",
}
# 特殊委派碼（無獨立 config，借用核心計算器）
_DELEGATES = {"OPEN"}


def _open(fullstring, overrides):
    """OPEN-□"：委派核心 PENETRATION HOLE 計算器（管徑經 overrides 傳入）。"""
    from core.types import type_penetration_hole
    ov = dict(overrides or {})
    if "-" in fullstring:
        tok = fullstring.split("-", 1)[1].replace('"', "").strip()
        if tok:
            ov.setdefault("nominal_size", tok)
    result = type_penetration_hole.calculate(fullstring, ov)
    for e in result.entries:      # 益高側品名整理：規格勿混進品名
        if e.name and e.name.startswith("FB50×6"):
            e.name = "開孔補強扁鐵"
    return result


def analyze(fullstring, overrides=None):
    parsed = _parser.parse_designation(fullstring)
    code = parsed.get("code", "")
    if code == "OPEN":
        return _open(fullstring, overrides)
    if code in _NOT_IMPORTED:
        r = AnalysisResult(fullstring=fullstring)
        r.error = (
            f"益高型號 {code} 已識別，但計算規則尚未匯入；"
            "本筆不計算，也不會套用其他 Type 猜測。"
        )
        return r
    if code in _NO_DRAWING:
        r = AnalysisResult(fullstring=fullstring)
        r.error = _NO_DRAWING[code]
        return r
    handler = HANDLERS.get(code)
    if handler is not None:
        # 已知 code：用該 code 重解析，精準切出修飾字母(固定方式/型式)
        parsed = _parser.parse_designation(fullstring, code=code)
    if handler is None:
        r = AnalysisResult(fullstring=fullstring)
        r.error = f"益高(EKO): 代碼 {code!r} 尚未實作 (已支援: {sorted(HANDLERS)})"
        return r
    config = load_eko_config(code)
    if config is None:
        r = AnalysisResult(fullstring=fullstring)
        r.error = f"益高(EKO): 找不到設定檔 {code}.json"
        return r
    validation_error = validate_designation(parsed, config)
    if validation_error is not None:
        return validation_error
    result = handler(parsed, config, overrides)
    # 解析階段的提醒(如無字母數字→位置推定)前置到警告，讓使用者看得到
    for w in reversed(parsed.get("parse_warnings", [])):
        if not result.error:
            result.warnings.insert(0, w)
    return result


def can_handle(fullstring):
    """本 fullstring 是否為已知益高代碼（含尚未匯入/委派/無圖佔位）。"""
    try:
        code = _parser.parse_designation(fullstring).get("code", "")
        return (
            code in HANDLERS
            or code in _NOT_IMPORTED
            or code in _NO_DRAWING
            or code in _DELEGATES
        )
    except Exception:
        return False


def supported_codes():
    return sorted(HANDLERS)
