"""Conservative sanity checks for editable Type config values."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class SanityIssue:
    code: str
    message: str
    severity: str
    path: str = ""


def existing_schedule_values(config_dir: Path | None = None) -> set[str]:
    root = config_dir or (Path(__file__).resolve().parents[1] / "configs")
    values = set()
    for path in sorted(root.glob("type_[0-9][0-9].json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        for row in config.get("table", []):
            if isinstance(row, dict) and row.get("schedule") not in (None, ""):
                values.add(str(row["schedule"]))
    return values


def _number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def check_config_sanity(
    config: dict,
    *,
    original: dict | None = None,
    allowed_schedules: set[str] | None = None,
) -> list[SanityIssue]:
    issues = []
    table = config.get("table", [])
    if not isinstance(table, list):
        return issues

    l_rows = [
        (index, row.get("line_size"), row.get("L"))
        for index, row in enumerate(table)
        if isinstance(row, dict)
        and _number(row.get("line_size"))
        and _number(row.get("L"))
    ]
    ordered = sorted(l_rows, key=lambda item: item[1])
    for previous, current in zip(ordered, ordered[1:]):
        if current[2] < previous[2]:
            issues.append(
                SanityIssue(
                    "L_NOT_MONOTONIC",
                    f"L 值未隨 line_size 非遞減：{previous[1]}→{current[1]} 時 {previous[2]}→{current[2]}",
                    "error",
                    f"table[{current[0]}].L",
                )
            )

    for row_index, row in enumerate(table):
        if not isinstance(row, dict):
            continue
        for field, value in row.items():
            if _number(value) and value <= 0:
                issues.append(
                    SanityIssue(
                        "NON_POSITIVE_NUMBER",
                        f"數值必須大於 0：{field}={value}",
                        "error",
                        f"table[{row_index}].{field}",
                    )
                )

    for field in ("h_limit", "h_unit_mm"):
        value = config.get(field)
        if _number(value) and value <= 0:
            issues.append(
                SanityIssue(
                    "NON_POSITIVE_NUMBER",
                    f"數值必須大於 0：{field}={value}",
                    "error",
                    field,
                )
            )

    allowed = allowed_schedules if allowed_schedules is not None else existing_schedule_values()
    if allowed:
        for row_index, row in enumerate(table):
            if not isinstance(row, dict) or row.get("schedule") in (None, ""):
                continue
            schedule = str(row["schedule"])
            if schedule not in allowed:
                issues.append(
                    SanityIssue(
                        "UNKNOWN_SCHEDULE",
                        f"Schedule 不在既有集合：{schedule}（允許：{', '.join(sorted(allowed))}）",
                        "error",
                        f"table[{row_index}].schedule",
                    )
                )

    if original is not None:
        original_rows = original.get("table", [])
        for row_index, row in enumerate(table):
            if not isinstance(row, dict) or row_index >= len(original_rows):
                continue
            before_row = original_rows[row_index]
            if not isinstance(before_row, dict):
                continue
            for field, after in row.items():
                before = before_row.get(field)
                if not (_number(before) and _number(after)) or before == 0:
                    continue
                percent = (float(after) - float(before)) / abs(float(before)) * 100
                if abs(percent) > 30:
                    issues.append(
                        SanityIssue(
                            "LARGE_CHANGE",
                            f"單格變動超過 30%：{field} {before}→{after} ({percent:+.1f}%)",
                            "warning",
                            f"table[{row_index}].{field}",
                        )
                    )
    return issues
