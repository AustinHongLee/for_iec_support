"""Declarative DSP-500-006 Type 01C~26C cold-support calculators.

These sheets are assembly standards with many dimensions delegated to C/N/M
reference sheets.  This engine validates the designation, selects only
explicit source rows/branches, and emits structured zero-weight references.
It deliberately does not turn assembly envelopes into finished stock cuts.
"""

from __future__ import annotations

import re
from typing import Callable

from ..models import AnalysisResult
from ..parser import get_lookup_value
from ._cold_support_common import (
    add_cold_reference,
    finalize_cold_result,
    load_cold_profile,
    parse_pipe_size,
    parse_positive_mm,
)
from ._cold_component_resolution import resolve_generic_component_bindings


TYPE_IDS = tuple(f"{number:02d}C" for number in range(1, 27))


def _lookup_key(value: object) -> str:
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def _parse_field(field: dict, token: str) -> object | None:
    kind = field["kind"]
    raw = str(token or "").strip()
    if kind == "pipe_size":
        return parse_pipe_size(raw)
    if kind == "positive_mm":
        return parse_positive_mm(raw)
    if kind == "positive_number":
        value = get_lookup_value(raw)
        return value if value > 0 else None
    if kind == "height_100mm":
        if not raw.isdigit() or int(raw) <= 0:
            return None
        return {
            field.get("code_name", "height_code"): raw,
            field.get("name", "H_mm"): int(raw) * 100,
        }
    if kind == "height_lower":
        match = re.fullmatch(
            r"(?P<height>\d+)(?P<lower>[A-Z])(?:\((?P<material>[AS])\))?",
            raw.upper(),
        )
        if not match or int(match.group("height")) <= 0:
            return None
        return {
            "height_code": match.group("height"),
            "H_mm": int(match.group("height")) * 100,
            "lower_component": match.group("lower"),
            "plate_material_symbol": match.group("material") or "NONE",
        }

    value = raw.upper() if field.get("uppercase", True) else raw
    if kind == "choice":
        return value if value in field["values"] else None
    if kind == "code":
        return value if re.fullmatch(field["pattern"], value) else None
    if kind == "text":
        return value or None
    raise ValueError(f"unsupported cold designation field kind: {kind}")


def _parse_designation(
    fullstring: str,
    type_id: str,
    profile: dict,
) -> tuple[dict | None, str | None]:
    tokens = fullstring.split("-")
    if not tokens or tokens[0].upper() != type_id:
        return None, f"Type {type_id}: designation type prefix 不一致"

    payload = tokens[1:]
    for variant in profile["designation_variants"]:
        fields = variant["fields"]
        if len(payload) != len(fields):
            continue
        parameters = dict(variant.get("defaults", {}))
        valid = True
        for definition, token in zip(fields, payload):
            parsed = _parse_field(definition, token)
            if parsed is None:
                valid = False
                break
            if isinstance(parsed, dict):
                parameters.update(parsed)
            else:
                parameters[definition["name"]] = parsed
        if valid:
            return parameters, None
    return None, profile["designation_error"]


def _apply_allowed_values(
    parameters: dict,
    profile: dict,
    type_id: str,
) -> str | None:
    for field, allowed in profile.get("allowed_values", {}).items():
        if parameters.get(field) not in allowed:
            return (
                f"Type {type_id}: {field}={parameters.get(field)!r} "
                "不在原圖列值內"
            )
    return None


def _attach_source_lookups(
    parameters: dict,
    profile: dict,
    type_id: str,
) -> str | None:
    source_rows = {}
    for lookup in profile.get("lookups", []):
        value = parameters.get(lookup["field"])
        row_data = lookup["rows"].get(_lookup_key(value))
        if row_data is None:
            return (
                f"Type {type_id}: "
                f"{lookup['field']}={value!r} 無原圖表列資料"
            )
        candidates = row_data if isinstance(row_data, list) else [row_data]
        row = None
        for candidate in candidates:
            if all(
                parameters.get(parameter_name) == candidate.get(row_name)
                for parameter_name, row_name in lookup.get(
                    "match_fields", {}
                ).items()
            ):
                row = candidate
                break
        if row is None:
            expected = [
                {
                    parameter_name: candidate.get(row_name)
                    for parameter_name, row_name in lookup.get(
                        "match_fields", {}
                    ).items()
                }
                for candidate in candidates
            ]
            return (
                f"Type {type_id}: {lookup['field']}={value!r} "
                f"應搭配 {expected}"
            )
        for parameter_name, row_name in lookup.get(
            "match_fields", {}
        ).items():
            if parameters.get(parameter_name) != row.get(row_name):
                return (
                    f"Type {type_id}: {lookup['field']}={value!r} "
                    f"應搭配 {parameter_name}={row.get(row_name)!r}"
                )
        source_rows[lookup["name"]] = row
    if source_rows:
        parameters["source_rows"] = source_rows

    for selection in profile.get("branch_selections", []):
        value = parameters.get(selection["field"])
        selected_name = None
        selected = None
        for name, branch in selection["branches"].items():
            if value in branch["values"]:
                selected_name = name
                selected = branch
                break
        if selected is None:
            return (
                f"Type {type_id}: "
                f"{selection['field']}={value!r} 無原圖 branch"
            )
        parameters[selection["name"]] = selected_name
        parameters[f"{selection['name']}_data"] = {
            key: item
            for key, item in selected.items()
            if key != "values"
        }
    return None


def calculate_type(
    type_id: str,
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    loaded = load_cold_profile(result, type_id, source_profile)
    if loaded == (None, None):
        return result
    profile_id, profile = loaded
    parameters, error = _parse_designation(fullstring, type_id, profile)
    if error:
        result.error = error
        return result
    assert parameters is not None

    error = _apply_allowed_values(parameters, profile, type_id)
    if error:
        result.error = error
        return result
    error = _attach_source_lookups(parameters, profile, type_id)
    if error:
        result.error = error
        return result

    parameters.update(profile.get("static_parameters", {}))
    try:
        component_blockers = resolve_generic_component_bindings(
            result,
            type_id=type_id,
            profile=profile,
            parameters=parameters,
            overrides=overrides,
        )
    except ValueError as exc:
        result.error = f"Type {type_id}: {exc}"
        result.entries.clear()
        return result
    parameters["references"] = profile["references"]
    parameters["source_pages"] = profile["source_pages"]
    blockers = [*profile["blockers"], *component_blockers]
    add_cold_reference(
        result,
        name=profile["title"],
        component_id=profile["component_id"],
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        spec=profile["source_spec"],
    )
    return finalize_cold_result(
        result,
        type_id=type_id,
        profile_id=profile_id,
        profile=profile,
        parameters=parameters,
        blockers=blockers,
        evidence_key=f"type{type_id.lower()}_source_assembly",
    )


def _make_calculator(type_id: str) -> Callable[..., AnalysisResult]:
    def calculate(
        fullstring: str,
        overrides: dict | None = None,
        source_profile: str | None = None,
    ) -> AnalysisResult:
        return calculate_type(
            type_id,
            fullstring,
            overrides=overrides,
            source_profile=source_profile,
        )

    calculate.__name__ = f"calculate_{type_id}"
    return calculate


CALCULATORS = {
    type_id: _make_calculator(type_id)
    for type_id in TYPE_IDS
}
