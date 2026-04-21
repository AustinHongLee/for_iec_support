"""
主調度器 - 對應 VBA: A_主程序 的 List_to_Analysis + Select Case
支援全域設定 + 單筆覆寫 (per-item overrides)
"""
from typing import List, Optional, Dict
from .models import AnalysisResult
from .parser import get_type_code
from .truth import apply_truth_contract


# 已實作的 Type 對照表
TYPE_HANDLERS = {}

# 全域分析設定 (第一層: Type 常態定義)
_ANALYSIS_SETTINGS = {
    "upper_material": "SUS304",
}


def set_analysis_setting(key: str, value):
    _ANALYSIS_SETTINGS[key] = value


def get_analysis_setting(key: str, default=None):
    return _ANALYSIS_SETTINGS.get(key, default)


def _register_types():
    from .types import (type_01, type_03, type_05, type_06, type_07, type_08,
                         type_09, type_10, type_11, type_12, type_13, type_14,
                         type_15, type_16, type_19, type_20, type_21, type_22,
                         type_23, type_24, type_25, type_26, type_27, type_28,
                         type_30, type_31, type_32, type_33, type_34, type_35,
                         type_36, type_37, type_39,
                         type_41, type_42, type_43, type_44, type_45,
                         type_46, type_47, type_48, type_49, type_51, type_56, type_61, type_62,
                         type_72, type_73, type_76, type_77, type_78, type_79,
                         type_52, type_57,
                         type_58, type_59, type_60, type_64, type_65)

    TYPE_HANDLERS.update({
        "01":  type_01.calculate,
        "01T": type_01.calculate,
        "03":  type_03.calculate,
        "05":  type_05.calculate,
        "06":  type_06.calculate,
        "07":  type_07.calculate,
        "08":  type_08.calculate,
        "09":  type_09.calculate,
        "10":  type_10.calculate,
        "11":  type_11.calculate,
        "12":  type_12.calculate,
        "13":  type_13.calculate,
        "14":  type_14.calculate,
        "15":  type_15.calculate,
        "16":  type_16.calculate,
        "19":  type_19.calculate,
        "20":  type_20.calculate,
        "21":  type_21.calculate,
        "22":  type_22.calculate,
        "23":  type_23.calculate,
        "24":  type_24.calculate,
        "25":  type_25.calculate,
        "26":  type_26.calculate,
        "27":  type_27.calculate,
        "28":  type_28.calculate,
        "30":  type_30.calculate,
        "31":  type_31.calculate,
        "32":  type_32.calculate,
        "33":  type_33.calculate,
        "34":  type_34.calculate,
        "35":  type_35.calculate,
        "36":  type_36.calculate,
        "37":  type_37.calculate,
        "39":  type_39.calculate,
        "41":  type_41.calculate,
        "42":  type_42.calculate,
        "43":  type_43.calculate,
        "44":  type_44.calculate,
        "45":  type_45.calculate,
        "46":  type_46.calculate,
        "47":  type_47.calculate,
        "48":  type_48.calculate,
        "49":  type_49.calculate,
        "51":  type_51.calculate,
        "56":  type_56.calculate,
        "61":  type_61.calculate,
        "62":  type_62.calculate,
        "72":  type_72.calculate,
        "73":  type_73.calculate,
        "76":  type_76.calculate,
        "77":  type_77.calculate,
        "78":  type_78.calculate,
        "79":  type_79.calculate,
        "52":  type_52.calculate,
        "53":  type_52.calculate,
        "54":  type_52.calculate,
        "55":  type_52.calculate,
        "66":  type_52.calculate,
        "67":  type_52.calculate,
        "85":  type_52.calculate,
        "57":  type_57.calculate,
        "58":  type_58.calculate,
        "59":  type_59.calculate,
        "60":  type_60.calculate,
        "64":  type_64.calculate,
        "65":  type_65.calculate,
    })


def analyze_single(fullstring: str, overrides: dict = None) -> AnalysisResult:
    """
    分析單一支撐編碼
    overrides: 第二層單筆覆寫 dict, e.g.
        {"connection": "tee", "upper_material": "SUS316",
         "pipe_size": "2", "schedule": "SCH.40", "l_value": 100}
    """
    if not TYPE_HANDLERS:
        _register_types()

    overrides = overrides or {}

    # 決定有效 type_code (覆寫可切換 elbow/tee)
    raw_type = get_type_code(fullstring)
    conn_override = overrides.get("connection")
    if raw_type in ("01", "01T") and conn_override:
        type_code = "01T" if conn_override == "tee" else "01"
    else:
        type_code = raw_type

    handler = TYPE_HANDLERS.get(type_code)
    if not handler:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"Type {type_code} 尚未實作"
        apply_truth_contract(
            result,
            type_id=type_code,
            review_reasons=["Type 尚未實作，無可信度 evidence"],
        )
        return result

    try:
        import inspect
        sig = inspect.signature(handler)
        kwargs = {}

        # 決定 connection
        if "connection" in sig.parameters:
            if conn_override:
                kwargs["connection"] = conn_override
            elif raw_type == "01T":
                kwargs["connection"] = "tee"
            else:
                kwargs["connection"] = "elbow"

        # 決定 upper_material (覆寫 > 全域設定)
        if "upper_material" in sig.parameters:
            kwargs["upper_material"] = (
                overrides.get("upper_material")
                or _ANALYSIS_SETTINGS["upper_material"]
            )

        # 傳遞 overrides 給支援的計算器
        if "overrides" in sig.parameters:
            kwargs["overrides"] = overrides

        result = handler(fullstring, **kwargs)
        if not result.meta.get("type_id"):
            apply_truth_contract(
                result,
                type_id=type_code,
                review_reasons=["此 Type 尚未補齊中文化 evidence；預設需審核"],
            )
        return result
    except Exception as e:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"計算錯誤: {str(e)}"
        apply_truth_contract(
            result,
            type_id=type_code,
            review_reasons=["calculator runtime error，無可信度 evidence"],
        )
        return result


def analyze_batch(items: List[str],
                  overrides_map: Dict[int, dict] = None) -> List[AnalysisResult]:
    """
    批次分析多筆
    overrides_map: {index: overrides_dict}
    """
    overrides_map = overrides_map or {}
    results = []
    for i, item in enumerate(items):
        item = item.strip()
        if item:
            results.append(analyze_single(item, overrides_map.get(i)))
    return results


def get_supported_types() -> List[str]:
    if not TYPE_HANDLERS:
        _register_types()
    return sorted(set(TYPE_HANDLERS.keys()))
