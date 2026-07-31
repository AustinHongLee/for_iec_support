"""
主調度器 - 對應 VBA: A_主程序 的 List_to_Analysis + Select Case
支援全域設定 + 單筆覆寫 (per-item overrides)
"""
from typing import List, Optional, Dict
from .models import AnalysisResult
from .issues import apply_issue_gates
from .parser import get_type_code
from .truth import apply_truth_contract, make_evidence
from .config_loader import get_config_version_info
from .source_profiles import (
    CHANGCHUN_DES_M15172,
    CW_E25_24_HP6,
    EKO,
    get_source_profile,
    numeric_calculation_profile,
    normalize_source_profile,
    numeric_type_profile_status,
    source_profile_allows,
)


# 已實作的 Type 對照表
TYPE_HANDLERS = {}

# 全域分析設定 (第一層: Type 常態定義)
_ANALYSIS_SETTINGS = {
    "upper_material": "SUS304",
}

# These calculators inherit the project-level upper-material setting when a
# row does not carry an explicit material override.
_GLOBAL_UPPER_MATERIAL_TYPES = frozenset({"01", "01T", "09", "10", "11"})


def _attach_config_metadata(
    result: AnalysisResult,
    type_id: str,
    source_profile: str | None = None,
    project_source_profile: str | None = None,
) -> AnalysisResult:
    apply_issue_gates(result)
    version, updated = get_config_version_info(type_id)
    if version != "(calculator-only)" or not result.meta.get("config_version"):
        result.meta["config_version"] = version
        result.meta["config_updated"] = updated
    if source_profile is not None:
        profile = get_source_profile(source_profile)
        result.meta["source_profile"] = profile.id
        result.meta["source_profile_label"] = profile.label_zh
        result.meta["source_project"] = profile.project
        result.meta["source_drawing_standard"] = profile.drawing_standard
        if str(type_id)[:1].isdigit():
            result.meta["source_profile_rule_status"] = (
                numeric_type_profile_status(profile.id, type_id)
            )
    if project_source_profile is not None:
        project_profile = get_source_profile(project_source_profile)
        if source_profile is None or project_profile.id != result.meta.get(
            "source_profile"
        ):
            result.meta["project_source_profile"] = project_profile.id
            result.meta["project_source_profile_label"] = project_profile.label_zh
    return result


def set_analysis_setting(key: str, value):
    _ANALYSIS_SETTINGS[key] = value


def get_analysis_setting(key: str, default=None):
    return _ANALYSIS_SETTINGS.get(key, default)


def uses_global_upper_material(fullstring: str) -> bool:
    return get_type_code(fullstring) in _GLOBAL_UPPER_MATERIAL_TYPES


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
                         type_58, type_59, type_60, type_64, type_65, type_80,
                         type_81, type_82, type_82A, type_83, type_84, type_85,
                         type_86, type_87, type_101, type_102, type_103,
                         type_104, type_105, type_108, type_110, type_112,
                         type_115, type_118, type_119, type_120, type_125,
                         type_126, type_127, type_128, type_129,
                         type_109C, type_110C, type_112C, type_113C,
                         type_114C, type_115C, type_116C, type_117C,
                         type_119C, type_120C, type_121C,
                         type_cold_01_26,
                         type_penetration_hole)

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
        "80":  type_80.calculate,
        "81":  type_81.calculate,
        "82":  type_82.calculate,
        "82A": type_82A.calculate,
        "83":  type_83.calculate,
        "84":  type_84.calculate,
        "85":  type_85.calculate,
        "86":  type_86.calculate,
        "87":  type_87.calculate,
        "101": type_101.calculate,
        "102": type_102.calculate,
        "103": type_103.calculate,
        "104": type_104.calculate,
        "105": type_105.calculate,
        "108": type_108.calculate,
        "110": type_110.calculate,
        "112": type_112.calculate,
        "115": type_115.calculate,
        "118": type_118.calculate,
        "119": type_119.calculate,
        "120": type_120.calculate,
        "125": type_125.calculate,
        "126": type_126.calculate,
        "127": type_127.calculate,
        "128": type_128.calculate,
        "129": type_129.calculate,
        "109C": type_109C.calculate,
        "110C": type_110C.calculate,
        "112C": type_112C.calculate,
        "113C": type_113C.calculate,
        "114C": type_114C.calculate,
        "115C": type_115C.calculate,
        "116C": type_116C.calculate,
        "117C": type_117C.calculate,
        "119C": type_119C.calculate,
        "120C": type_120C.calculate,
        "121C": type_121C.calculate,
        "52":  type_52.calculate,
        "53":  type_52.calculate,
        "54":  type_52.calculate,
        "55":  type_52.calculate,
        "66":  type_52.calculate,
        "67":  type_52.calculate,
        "57":  type_57.calculate,
        "58":  type_58.calculate,
        "59":  type_59.calculate,
        "60":  type_60.calculate,
        "64":  type_64.calculate,
        "65":  type_65.calculate,
        "PENETRATION HOLE": type_penetration_hole.calculate,
    })
    TYPE_HANDLERS.update(type_cold_01_26.CALCULATORS)


def analyze_single(
    fullstring: str,
    overrides: dict = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    """
    分析單一支撐編碼
    overrides: 第二層單筆覆寫 dict, e.g.
        {"connection": "tee", "upper_material": "SUS316",
         "pipe_size": "2", "schedule": "SCH.40", "l_value": 100}
    """
    if not TYPE_HANDLERS:
        _register_types()

    overrides = overrides or {}
    normalized_profile = (
        normalize_source_profile(source_profile)
        if source_profile is not None
        else None
    )

    # 決定有效 type_code (覆寫可切換 elbow/tee)
    raw_type = get_type_code(fullstring)
    conn_override = overrides.get("connection")
    if raw_type in ("01", "01T") and conn_override:
        type_code = "01T" if conn_override == "tee" else "01"
    else:
        type_code = raw_type

    numeric_profile = (
        numeric_calculation_profile(normalized_profile)
        if normalized_profile is not None
        and str(type_code)[:1].isdigit()
        else normalized_profile
    )

    if (
        numeric_profile is not None
        and str(type_code)[:1].isdigit()
        and numeric_type_profile_status(
            numeric_profile, type_code
        ) == "unsupported"
    ):
        profile = get_source_profile(numeric_profile)
        result = AnalysisResult(fullstring=fullstring)
        result.error = (
            f"Type {type_code} 尚未完成「{profile.label_zh}」圖面規則；"
            "為避免誤套中威基準，本筆暫不計算。"
        )
        apply_truth_contract(
            result,
            type_id=type_code,
            review_reasons=[
                f"{profile.label_zh} / Type {type_code} 尚未逐圖核定"
            ],
        )
        return _attach_config_metadata(
            result,
            type_code,
            numeric_profile,
            normalized_profile,
        )

    handler = TYPE_HANDLERS.get(type_code)
    if not handler:
        extension_specs = []
        if normalized_profile is None:
            # Legacy API compatibility: historical non-Type calls were EKO.
            extension_specs = [
                ("eko", EKO, "益高(EKO)"),
                ("chungwei_special", CW_E25_24_HP6, "中威特殊支撐"),
            ]
        else:
            extension_specs = [
                ("changchun", CHANGCHUN_DES_M15172, "長春 DES-M15172"),
                ("chungwei_special", CW_E25_24_HP6, "中威特殊支撐"),
                ("eko", EKO, "益高(EKO)"),
            ]

        recognized_elsewhere = []
        for family, actual_profile, label in extension_specs:
            try:
                if family == "changchun":
                    from companies.changchun import dispatch as extension
                elif family == "chungwei_special":
                    from companies.chungwei import dispatch as extension
                else:
                    from companies.eko import dispatch as extension
            except Exception:
                continue

            if not extension.can_handle(fullstring):
                continue
            if (
                normalized_profile is not None
                and not source_profile_allows(normalized_profile, family)
            ):
                recognized_elsewhere.append(label)
                continue
            try:
                result = extension.analyze(fullstring, overrides)
            except Exception as exc:  # noqa: BLE001
                result = AnalysisResult(fullstring=fullstring)
                result.error = f"{label}計算錯誤: {exc}"
            if not result.meta.get("type_id"):
                apply_truth_contract(
                    result,
                    type_id=type_code,
                    review_reasons=[f"{label}延展判讀"],
                )
            return _attach_config_metadata(
                result,
                type_code,
                actual_profile,
                normalized_profile,
            )

        result = AnalysisResult(fullstring=fullstring)
        if recognized_elsewhere and normalized_profile is not None:
            selected = get_source_profile(normalized_profile)
            result.error = (
                f"型號 {type_code!r} 屬於{'／'.join(recognized_elsewhere)}，"
                f"但本列目前選用「{selected.label_zh}」；"
                "請切換專案來源或使用本列圖面來源覆寫。"
            )
        elif type_code and not type_code[:1].isdigit():
            result.error = (
                f"找不到型號 {type_code!r} 的可驗證計算規則；"
                "為避免無依據判斷，本筆不計算。請確認型號，或提供圖面後匯入規則。"
            )
        else:
            result.error = f"Type {type_code} not implemented"
        apply_truth_contract(
            result,
            type_id=type_code,
            review_reasons=["Type 尚未實作，無可信度 evidence"],
        )
        return _attach_config_metadata(
            result,
            type_code,
            normalized_profile,
            normalized_profile,
        )

    try:
        import inspect
        sig = inspect.signature(handler)
        kwargs = {}
        assumed_upper_material = (
            _ANALYSIS_SETTINGS["upper_material"]
            if overrides.get("upper_material_unknown")
            and uses_global_upper_material(fullstring)
            else None
        )

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
            if assumed_upper_material is not None:
                kwargs["upper_material"] = assumed_upper_material
            else:
                kwargs["upper_material"] = (
                    overrides.get("upper_material")
                    or _ANALYSIS_SETTINGS["upper_material"]
                )

        # 傳遞 overrides 給支援的計算器
        if "overrides" in sig.parameters:
            kwargs["overrides"] = overrides
        if "source_profile" in sig.parameters:
            kwargs["source_profile"] = numeric_profile

        result = handler(fullstring, **kwargs)
        if (
            numeric_profile is not None
            and numeric_type_profile_status(
                numeric_profile, type_code
            ) == "partial"
        ):
            profile = get_source_profile(numeric_profile)
            result.warnings.append(
                f"{profile.label_zh} / Type {type_code} "
                "目前僅開放已逐圖建檔的來源別尺寸與可證實構件；"
                "圖面未標完整尺寸的構件仍保留警告並需複核。"
            )
        if assumed_upper_material is not None:
            result.evidence.append(
                make_evidence(
                    field="upper_material",
                    value=assumed_upper_material,
                    basis="assumption",
                    confidence=0.5,
                    note="材質未確認,以預設值概算",
                )
            )
            existing_meta = result.meta if result.meta.get("type_id") else {}
            review_reasons = list(existing_meta.get("review_reasons", []))
            review_reasons.append("材質未確認，以預設值概算")
            apply_truth_contract(
                result,
                type_id=type_code,
                invariant_errors=existing_meta.get("invariant_errors", []),
                review_reasons=review_reasons,
            )
        elif not result.meta.get("type_id"):
            apply_truth_contract(
                result,
                type_id=type_code,
                review_reasons=["此 Type 尚未補齊中文化 evidence；預設需審核"],
            )
        return _attach_config_metadata(
            result,
            type_code,
            numeric_profile,
            normalized_profile,
        )
    except Exception as e:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"計算錯誤: {str(e)}"
        apply_truth_contract(
            result,
            type_id=type_code,
            review_reasons=["calculator runtime error，無可信度 evidence"],
        )
        return _attach_config_metadata(
            result,
            type_code,
            numeric_profile,
            normalized_profile,
        )


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
