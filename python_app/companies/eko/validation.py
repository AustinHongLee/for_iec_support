"""Config-driven strict designation validation for EKO drawings.

Only configs with a ``validation`` block opt in.  Legacy EKO calculators keep
their existing tolerant behavior until their drawing grammar has been checked.
"""
from core.models import AnalysisResult


_DIMENSIONS = ("L", "L1", "H", "H1", "H2")
_FIELD_LABELS = {
    "fix": "固定方式",
    "serial": "序號",
    "pipe": "配管管徑",
    "L": "L",
    "L1": "L1",
    "H": "H",
    "H1": "H1",
    "H2": "H2",
    "flags": "型式",
    "cold": "保冷厚度C",
    "msize": "螺栓尺寸M",
    "tcount": "T數量",
}


def _present(parsed, field):
    if field == "fix":
        return bool(parsed.get("fix"))
    if field == "flags":
        return bool(parsed.get("flags"))
    return parsed.get(field) is not None


def _allowed_serials(config, validation):
    explicit = validation.get("serials")
    if explicit is not None:
        return {str(v) for v in explicit}
    for key in ("table", "serial_sections", "serial_limits"):
        values = config.get(key)
        if isinstance(values, dict):
            return {str(v) for v in values}
    return set()


def _fail(parsed, message):
    result = AnalysisResult(fullstring=parsed.get("raw", ""))
    result.error = f"{parsed.get('code', 'EKO')}: {message}"
    return result


def validate_designation(parsed, config):
    """Return an error ``AnalysisResult`` or ``None`` when validation passes."""
    validation = config.get("validation")
    if not validation:
        return None

    if validation.get("block_reason"):
        return _fail(parsed, validation["block_reason"])

    required = validation.get("required", [])
    missing = [field for field in required if not _present(parsed, field)]
    if missing:
        labels = "、".join(_FIELD_LABELS.get(field, field) for field in missing)
        return _fail(parsed, f"缺少必要欄位：{labels}；本筆不計算")

    allowed = set(validation.get("allowed", required))
    active = []
    if parsed.get("fix"):
        active.append("fix")
    if parsed.get("serial") is not None:
        active.append("serial")
    if parsed.get("pipe") is not None:
        active.append("pipe")
    active.extend(field for field in _DIMENSIONS if parsed.get(field) is not None)
    if parsed.get("flags"):
        active.append("flags")
    active.extend(
        field for field in ("cold", "msize", "tcount")
        if parsed.get(field) is not None
    )

    unexpected = [field for field in active if field not in allowed]
    if parsed.get("duplicates"):
        duplicate_labels = "、".join(
            _FIELD_LABELS.get(field, field) for field in parsed["duplicates"]
        )
        return _fail(parsed, f"同一欄位重複出現：{duplicate_labels}；無法判定應採用哪個值")
    if parsed.get("extra"):
        unexpected.append("未識別段落 " + "/".join(map(str, parsed["extra"])))
    if unexpected:
        labels = "、".join(_FIELD_LABELS.get(field, field) for field in unexpected)
        return _fail(parsed, f"包含圖面格式沒有的欄位：{labels}；請依標準稱呼代號修正")

    fixes = validation.get("fixes")
    if fixes is not None and parsed.get("fix") not in fixes:
        return _fail(
            parsed,
            f"固定方式 {parsed.get('fix')!r} 不在圖面允許值 "
            f"({', '.join(map(str, fixes))})",
        )

    serials = _allowed_serials(config, validation)
    if parsed.get("serial") is not None and serials:
        serial = str(parsed["serial"])
        if serial not in serials:
            return _fail(
                parsed,
                f"未知序號 {serial}（應填 {', '.join(sorted(serials))}），"
                "無法決定型鋼或支撐規格",
            )

    allowed_flags = validation.get("allowed_flags")
    if parsed.get("flags") and allowed_flags is not None:
        bad_flags = [flag for flag in parsed["flags"] if flag not in allowed_flags]
        if bad_flags:
            return _fail(
                parsed,
                f"未知型式 {'/'.join(bad_flags)}（應填 {', '.join(allowed_flags)}）",
            )

    pipe_rule = validation.get("pipe") or {}
    pipe = parsed.get("pipe")
    if pipe is not None:
        minimum = pipe_rule.get("min")
        maximum = pipe_rule.get("max")
        if minimum is not None and pipe < minimum:
            return _fail(parsed, f"配管管徑 {pipe:g}\" 小於圖面適用下限 {minimum:g}\"")
        if maximum is not None and pipe > maximum:
            return _fail(parsed, f"配管管徑 {pipe:g}\" 超出圖面適用上限 {maximum:g}\"")

    for field, rule in (validation.get("dimensions") or {}).items():
        value = parsed.get(field)
        if value is None:
            continue
        minimum = rule.get("min")
        maximum = rule.get("max")
        if minimum is not None:
            inclusive = rule.get("min_inclusive", True)
            invalid = value < minimum if inclusive else value <= minimum
            if invalid:
                if rule.get("message"):
                    return _fail(parsed, rule["message"].format(field=field, value=value))
                op = "至少" if inclusive else "必須大於"
                return _fail(parsed, f"{field}={value}mm 不合圖面限制（{op} {minimum}mm）")
        if maximum is not None:
            inclusive = rule.get("max_inclusive", True)
            invalid = value > maximum if inclusive else value >= maximum
            if invalid:
                if rule.get("message"):
                    return _fail(parsed, rule["message"].format(field=field, value=value))
                op = "不得超過" if inclusive else "必須小於"
                return _fail(parsed, f"{field}={value}mm 不合圖面限制（{op} {maximum}mm）")

    serial_max = validation.get("serial_dimension_max") or {}
    if serial_max:
        field = serial_max.get("field")
        values = serial_max.get("values") or config.get(serial_max.get("config_key", ""), {})
        serial = str(parsed.get("serial"))
        value = parsed.get(field)
        maximum = values.get(serial) if isinstance(values, dict) else None
        if value is not None and maximum is not None and value > maximum:
            return _fail(
                parsed,
                f"{field}={value}mm 超出序號 {serial} 圖面上限 {maximum}mm",
            )

    return None
