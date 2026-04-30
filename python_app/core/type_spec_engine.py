"""Declarative TypeSpec runner for small table-driven calculators."""

from __future__ import annotations

from typing import Any

from .config_loader import load_config
from .material_specs import SUPPORT_PLATE_A36_SS400, U_BOLT_A36_SS400
from .models import AnalysisResult
from .parser import get_lookup_value, get_part, parse_pipe_size
from .plate import add_plate_entry
from .bolt import add_custom_entry


_MATERIALS = {
    "support_plate_a36_ss400": SUPPORT_PLATE_A36_SS400,
    "u_bolt_a36_ss400": U_BOLT_A36_SS400,
}


def _field(row: dict[str, Any], name: str) -> Any:
    if name not in row:
        raise KeyError(f"TypeSpec row missing field '{name}'")
    return row[name]


def _component_enabled(component: dict[str, Any], row: dict[str, Any]) -> bool:
    field = component.get("when_field_not_null")
    if field:
        return row.get(field) is not None
    return True


def _material(key: str):
    try:
        return _MATERIALS[key]
    except KeyError as exc:
        raise KeyError(f"Unknown TypeSpec material key '{key}'") from exc


def _add_plate_component(
    result: AnalysisResult,
    component: dict[str, Any],
    row: dict[str, Any],
) -> None:
    add_plate_entry(
        result,
        plate_a=_field(row, component["plate_a_field"]),
        plate_b=_field(row, component["plate_b_field"]),
        plate_thickness=_field(row, component["plate_thickness_field"]),
        plate_name=component["name"],
        material=_material(component["material"]),
        plate_qty=component.get("quantity", 1),
        plate_role=component.get("plate_role", ""),
    )
    remark_template = component.get("remark")
    if remark_template:
        result.entries[-1].remark = remark_template.format(**row)


def _unit_weight(component: dict[str, Any], row: dict[str, Any]) -> float:
    if "unit_weight" in component:
        return component["unit_weight"]
    mapping = component.get("unit_weight_map")
    if mapping:
        key = row.get(mapping["field"])
        return mapping.get("values", {}).get(key, mapping.get("default", 0))
    return 0


def _add_custom_component(
    result: AnalysisResult,
    component: dict[str, Any],
    row: dict[str, Any],
) -> None:
    add_custom_entry(
        result,
        name=component["name"],
        spec=component["spec"].format(**row),
        material=_material(component["material"]),
        quantity=component.get("quantity", 1),
        unit_weight=_unit_weight(component, row),
        unit=component.get("unit", "PC"),
        remark=component.get("remark", "").format(**row),
        category=component.get("category", "螺栓類"),
    )


def _size_key(pipe_token: str, designation: dict[str, Any]) -> str:
    if designation.get("size_key") == "parse_pipe_size":
        return parse_pipe_size(pipe_token)
    return pipe_token.replace("B", "").strip()


def _row_key(type_id: str, designation: dict[str, Any], pipe_token: str, fig: str) -> str:
    return designation["support_no_template"].format(
        type_id=type_id,
        pipe_token=pipe_token.strip(),
        size_key=_size_key(pipe_token, designation),
        figure=fig,
    )


def _warning_enabled(warning: dict[str, Any], fig: str) -> bool:
    when_figure = warning.get("when_figure")
    if when_figure:
        return fig == when_figure
    return True


def calculate_table_plate_spec(fullstring: str, type_id: str) -> AnalysisResult:
    config = load_config(type_id)
    result = AnalysisResult(fullstring=fullstring)
    if not config:
        result.error = f"Type {type_id}: missing config"
        return result

    spec = config.get("TYPE_SPEC")
    if not spec:
        result.error = f"Type {type_id}: missing TYPE_SPEC"
        return result
    if spec.get("engine") not in ("table_plate_v1", "table_parts_v1"):
        result.error = f"Type {type_id}: unsupported TypeSpec engine {spec.get('engine')}"
        return result

    designation = spec["designation"]
    pipe_token = get_part(fullstring, designation.get("pipe_size_part", 2))
    fig_token = get_part(fullstring, designation.get("figure_part", 3))

    if not pipe_token:
        result.error = spec.get("missing_pipe_error", "缺少管徑欄位")
        return result

    size_str = pipe_token.replace("B", "").strip()
    pipe_size = get_lookup_value(size_str)
    min_size, max_size = designation["pipe_size_range"]
    if pipe_size < min_size or pipe_size > max_size:
        result.error = spec["range_error"].format(size=size_str)
        return result

    fig = designation.get("default_figure", "A")
    allowed_figures = set(designation.get("allowed_figures", []))
    if fig_token and fig_token.strip().upper() in allowed_figures:
        fig = fig_token.strip().upper()

    table = config[spec["table_key"]]
    support_no = _row_key(type_id, designation, pipe_token, fig)
    row = table.get(support_no)
    if not row:
        result.error = spec["missing_row_error"].format(support_no=support_no)
        return result

    for component in spec["components"]:
        if not _component_enabled(component, row):
            continue
        kind = component.get("kind")
        if kind == "plate":
            _add_plate_component(result, component, row)
            continue
        if kind == "custom":
            _add_custom_component(result, component, row)
            continue
        else:
            result.error = f"Type {type_id}: unsupported component kind {kind}"
            return result

    context = dict(row)
    context.update({"figure": fig, "support_no": support_no, "type_id": type_id})
    for warning in spec.get("warnings", []):
        if not _warning_enabled(warning, fig):
            continue
        result.warnings.append(warning["template"].format(**context))

    return result
