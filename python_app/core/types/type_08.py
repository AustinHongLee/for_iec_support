"""Type 08 source-profile calculator.

The three numeric drawing sets reuse D-8 but do not define the same support:

* CW E25-24: 2"~4", L<=1000, H<=1500, M-42 G/J, two end stoppers.
* CTCI 22A: table-listed 3"~4", source-specific L/H limits, M-42 G/R/T,
  two end stoppers.
* CTCI 20E4588 Rev.1B: table-listed 3"~4", M-42 G/R/T, optional L1/L2
  placement suffix.  The revised elevation no longer depicts the end stoppers.

All dimensions and source switches are stored in configs/type_08.json.
"""
from __future__ import annotations

import re

from ..config_loader import load_config
from ..issues import (
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..material_specs import (
    STRUCTURAL_A36_SS400,
    SUPPORT_PIPE_A53GRB,
    SUPPORT_PLATE_A36_SS400,
)
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from data.m42_table import resolve_m42_data


_CODE_RE = re.compile(r"^(?P<l>\d{2})(?P<h>\d{2})(?P<letter>[A-Za-z])$")
_PLACEMENT_RE = re.compile(r"^(?P<l1>\d{2})(?P<l2>\d{2})$")

_SUPPORT_PIPE_MATERIAL = SUPPORT_PIPE_A53GRB
_STRUCTURAL_MATERIAL = STRUCTURAL_A36_SS400
_SUPPORT_PLATE_MATERIAL = SUPPORT_PLATE_A36_SS400


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("08", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 08 設定檔遺失或損毀 (configs/type_08.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
        rows = config["source_tables"][profile["table_source"]]
    except KeyError as exc:
        raise ValueError(f"Type 08 尚未建立來源 profile: {profile_id}") from exc
    return profile_id, profile, {int(k): v for k, v in rows.items()}, config


def _parse_support_pipe_size(fullstring: str) -> int:
    value = float(get_lookup_value(get_part(fullstring, 2)))
    if not value.is_integer():
        raise ValueError("第二段 supporting pipe size 必須是圖面表列整數管徑")
    return int(value)


def _parse_dimensions(fullstring: str) -> tuple[int, int, str]:
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _CODE_RE.fullmatch(raw)
    if not match:
        raise ValueError(
            "第三段格式應為 LLHH+M42 字母，例如 1005G 或 0515T"
        )
    return (
        int(match.group("l")) * 100,
        int(match.group("h")) * 100,
        match.group("letter").upper(),
    )


def _parse_placement(
    fullstring: str,
    *,
    profile_id: str,
    supports_modifier: bool,
    overall_l: int,
) -> tuple[float, float, bool]:
    raw = str(get_part(fullstring, 4) or "").strip()
    if not supports_modifier:
        if raw:
            raise ValueError(
                f"Type 08 / {profile_id}: 此來源 D-8 未定義 L1/L2 第四段"
            )
        return overall_l / 2, overall_l / 2, False
    if not raw:
        return overall_l / 2, overall_l / 2, False
    match = _PLACEMENT_RE.fullmatch(raw)
    if not match:
        raise ValueError(
            "Type 08 / 20E4588 第四段應為 L1L2 四碼，例如 0208"
        )
    l1 = int(match.group("l1")) * 100
    l2 = int(match.group("l2")) * 100
    if l1 + l2 != overall_l:
        raise ValueError(
            f"Type 08 / 20E4588: L1+L2={l1 + l2}mm "
            f"必須等於 L={overall_l}mm"
        )
    return l1, l2, True


def _decorate_m42_entries(
    entries,
    *,
    source_drawing: str,
    source_revision: str,
) -> None:
    for entry in entries:
        entry.geometry.source_drawing = source_drawing
        entry.geometry.source_revision = source_revision
        entry.geometry.fabrication_ready = True
        if entry.category == "鋼板類":
            plate_code = entry.name.split("_")[1].upper()
            entry.geometry.component_id = f"M42-PLATE-{plate_code}"
            entry.geometry.shape_kind = "rectangular_base_plate"
            entry.geometry.shape_spec = (
                entry.geometry.shape_spec
                or f"{entry.length:g}x{entry.width:g}x{entry.spec}t"
            )
            entry.geometry.parameters.update(
                {
                    "length_mm": entry.length,
                    "width_mm": entry.width,
                    "thickness_mm": float(entry.spec),
                }
            )
        elif entry.category == "螺栓類":
            entry.geometry.component_id = "M42-FASTENER"
            entry.geometry.shape_kind = "purchased_fastener"
            entry.geometry.parameters.update(
                {"spec": entry.spec, "quantity": entry.quantity}
            )
        elif entry.category == "型鋼類":
            entry.geometry.component_id = "M42-ANGLE-RETAINER"
            entry.geometry.shape_kind = "stock_section_cut"
            entry.geometry.parameters.update(
                {"cut_length_mm": entry.length, "quantity": entry.quantity}
            )


def _decorate_type08_entries(
    result: AnalysisResult,
    *,
    profile_id: str,
    profile: dict,
    row: dict,
    config: dict,
    pipe_size: int,
    l_value: int,
    h_value: int,
    l1: float,
    l2: float,
    placement_modified: bool,
    pipe_length: float,
    channel_length: float,
    lower_component: str,
    high_height_unverified: bool,
    m42_start: int,
    m42_end: int,
) -> None:
    fab = config["fabrication_contract"]
    drawing = profile["drawing"]
    revision = profile["revision"]

    pipe_blockers = [fab["known_blocker"]]
    if high_height_unverified:
        pipe_blockers.append(
            "H>1500mm 的 NOTE 4 條件需要 supported line size，編碼本身未攜帶該欄位"
        )

    pipe_entry = result.entries[0]
    pipe_entry.geometry.component_id = "D8-SUPPORTING-PIPE-A"
    pipe_entry.geometry.source_drawing = drawing
    pipe_entry.geometry.source_revision = revision
    pipe_entry.geometry.shape_kind = "square_cut_support_pipe"
    pipe_entry.geometry.shape_spec = (
        f'{pipe_size}"*{row["pipe_sch"]}; CUT L={pipe_length:g}; '
        f'WEEP HOLE DIA{fab["weep_hole_diameter_mm"]}'
    )
    pipe_entry.geometry.fabrication_ready = False
    pipe_entry.geometry.fabrication_blockers = list(pipe_blockers)
    pipe_entry.geometry.parameters = {
        "supporting_pipe_size_in": pipe_size,
        "schedule": row["pipe_sch"],
        "H_to_member_centerline_mm": h_value,
        "cut_length_mm": pipe_length,
        "end_cut": "square",
        "weep_hole_diameter_mm": fab["weep_hole_diameter_mm"],
        "weep_hole_location": "low point shown schematically; center offset not dimensioned",
        "top_weld_mm": fab["field_weld_mm"],
        "base_weld_mm": fab["field_weld_mm"],
        "lower_component": lower_component,
    }

    channel_entry = result.entries[1]
    channel_entry.geometry.component_id = "D8-MEMBER-N"
    channel_entry.geometry.source_drawing = drawing
    channel_entry.geometry.source_revision = revision
    channel_entry.geometry.shape_kind = "stock_channel_cut"
    channel_entry.geometry.shape_spec = (
        f'{row["member_n"]}; CUT L={channel_length:g}'
    )
    channel_entry.geometry.fabrication_ready = True
    channel_entry.geometry.parameters = {
        "overall_L_mm": l_value,
        "cut_length_mm": channel_length,
        "cut_formula": profile["channel_cut_formula"],
        "left_end_cut": "square",
        "right_end_cut": "square",
        "support_axis_from_overall_left_mm": l1,
        "support_axis_from_channel_left_mm": (
            l1 - fab["stopper_thickness_mm"]
            if profile["has_end_stoppers"]
            else l1
        ),
        "right_span_mm": l2,
        "placement_modified": placement_modified,
    }

    _decorate_m42_entries(
        result.entries[m42_start:m42_end],
        source_drawing=profile["m42_drawing"],
        source_revision=profile["m42_revision"],
    )

    for entry in result.entries[m42_end:]:
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = revision
        entry.geometry.fabrication_ready = True
        if entry.name == "Plate_STOPPER":
            entry.geometry.component_id = "D8-STOPPER"
            entry.geometry.shape_kind = "four_corner_chamfered_plate"
            entry.geometry.parameters.update(
                {
                    "overall_width_K_mm": row["K"],
                    "overall_height_M_mm": row["M"],
                    "thickness_mm": fab["stopper_thickness_mm"],
                    "corner_chamfer_mm": fab["stopper_corner_chamfer_mm"],
                    "corner_count": 4,
                    "quantity": 2,
                    "placement": "one at each channel end",
                    "weld_mm": fab["field_weld_mm"],
                }
            )
        elif entry.name == "Plate_TOP":
            entry.geometry.component_id = "D8-TOP-PLATE-B"
            entry.geometry.shape_kind = "square_plate"
            entry.geometry.parameters.update(
                {
                    "side_B_mm": row["B"],
                    "thickness_mm": fab["top_plate_thickness_mm"],
                    "center_from_overall_left_mm": l1,
                    "weld_to_channel_mm": fab["field_weld_mm"],
                    "weld_to_pipe_mm": fab["field_weld_mm"],
                }
            )

    blockers = list(pipe_blockers)
    if profile.get("drawing_ambiguity"):
        blockers.append(profile["drawing_ambiguity"])

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "branch": (
            "D-8/two-end-stopper"
            if profile["has_end_stoppers"]
            else "D-8/rev-1B-multi-line"
        ),
        "bom_ready": not bool(profile.get("drawing_ambiguity")),
        "fabrication_ready": False,
        "blockers": blockers,
        "dimensions": {
            "L_overall_mm": l_value,
            "H_to_member_centerline_mm": h_value,
            "L1_mm": l1,
            "L2_mm": l2,
            "supporting_pipe_cut_length_mm": pipe_length,
            "member_n_cut_length_mm": channel_length,
            "top_plate_B_mm": row["B"],
            "stopper_K_mm": row["K"] if profile["has_end_stoppers"] else None,
            "stopper_M_mm": row["M"] if profile["has_end_stoppers"] else None,
        },
    }


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}

    try:
        profile_id, profile, table, config = _load_profile(source_profile)
        pipe_size = _parse_support_pipe_size(fullstring)
        l_value, h_value, letter = _parse_dimensions(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 08: {exc}"
        return result

    row = table.get(pipe_size)
    if row is None:
        result.error = (
            f"Type 08 / {profile_id}: 來源 D-8 未表列 "
            f'{pipe_size}" supporting pipe'
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 08 / {profile_id}",
        source_ref=f'D-8 {pipe_size}" L/H上限',
        checks=(
            ("L", l_value, int(row["L_max"]), True),
            ("H", h_value, int(row["H_max"]), True),
        ),
    ):
        return result
    if letter not in profile["allowed_lower_components"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 08 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 08 / {profile_id}",
            source_ref="D-8",
            letter=letter,
            host_allowed=profile["allowed_lower_components"],
        )

    try:
        l1, l2, placement_modified = _parse_placement(
            fullstring,
            profile_id=profile_id,
            supports_modifier=profile["supports_l1_l2_modifier"],
            overall_l=l_value,
        )
    except ValueError as exc:
        result.error = str(exc)
        return result

    high_height_unverified = False
    unconditional_h = row.get("H_unconditional_max")
    if unconditional_h is not None and h_value > int(unconditional_h):
        required_max = float(row["H_high_requires_supported_line_lte"])
        supported_line_size = overrides.get("supported_line_size")
        if supported_line_size in (None, ""):
            high_height_unverified = True
            result.warnings.append(
                f"Type 08 / {profile_id}: H={h_value}mm 僅適用於 "
                f'{required_max:g}" 以下 single line；尚未提供 supported line size'
            )
        else:
            try:
                supported_line_size = float(
                    get_lookup_value(supported_line_size)
                )
            except (TypeError, ValueError):
                result.error = "Type 08: supported_line_size 覆寫值無法解析"
                return result
            if supported_line_size > required_max:
                result.error = (
                    f"Type 08 / {profile_id}: H={h_value}mm 僅適用於 "
                    f'{required_max:g}" 以下 single line，'
                    f'目前為 {supported_line_size:g}"'
                )
                return result

    if profile["g_height_from_lowest_paving"] and letter == "G":
        result.warnings.append(
            "M-42 Type G：H 應從鋪面最低點標高起算"
        )

    fab = config["fabrication_contract"]
    channel_height = float(row["member_n"][1:].split("*")[0])
    m42_data, m42_warning = resolve_m42_data(pipe_size)
    if m42_warning and m42_warning not in result.warnings:
        result.warnings.append(m42_warning)
    pipe_length = (
        h_value
        - float(fab["top_plate_thickness_mm"])
        - channel_height / 2
        - float(m42_data["plate_thickness"])
    )
    if pipe_length <= 0:
        result.error = (
            f"Type 08 / {profile_id}: H={h_value}mm 導致立管切長 "
            f"{pipe_length:g}mm，無法製作"
        )
        return result

    if profile["has_end_stoppers"]:
        channel_length = (
            l_value - 2 * float(fab["stopper_thickness_mm"])
        )
    else:
        channel_length = float(l_value)
    if channel_length <= 0:
        result.error = "Type 08: L 導致 MEMBER N 切長小於或等於 0"
        return result

    add_pipe_entry(
        result,
        str(pipe_size),
        row["pipe_sch"],
        pipe_length,
        _SUPPORT_PIPE_MATERIAL,
    )
    add_steel_section_entry(
        result,
        "Channel",
        row["member_n"][1:],
        channel_length,
        material=_STRUCTURAL_MATERIAL,
    )

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        pipe_size,
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    m42_end = len(result.entries)

    if profile["has_end_stoppers"]:
        chamfer = float(fab["stopper_corner_chamfer_mm"])
        net_area = row["K"] * row["M"] - 4 * chamfer * chamfer / 2
        add_plate_entry(
            result,
            row["K"],
            row["M"],
            fab["stopper_thickness_mm"],
            "Plate_STOPPER",
            material=_SUPPORT_PLATE_MATERIAL,
            plate_qty=2,
            plate_role="stopper_plate",
            shape_spec=(
                f'{row["K"]}x{row["M"]}x{fab["stopper_thickness_mm"]}t; '
                f'4-C{fab["stopper_corner_chamfer_mm"]}'
            ),
            shape_kind="four_corner_chamfered_plate",
            gross_area_mm2=row["K"] * row["M"],
            cutout_area_mm2=4 * chamfer * chamfer / 2,
            net_area_mm2=net_area,
            notes_zh=(
                "兩端止擋各1片；四角 10C chamfer / 10mm 折角；"
                "與 MEMBER N 以 6mm fillet weld 接合"
            ),
        )
    elif profile.get("drawing_ambiguity"):
        result.warnings.append(profile["drawing_ambiguity"])

    add_plate_entry(
        result,
        row["B"],
        row["B"],
        fab["top_plate_thickness_mm"],
        "Plate_TOP",
        material=_SUPPORT_PLATE_MATERIAL,
        plate_role="top_plate",
        shape_spec=(
            f'{row["B"]}x{row["B"]}x{fab["top_plate_thickness_mm"]}t'
        ),
        shape_kind="square_plate",
        notes_zh="置中於 supporting pipe；與槽鐵及立管採 6mm fillet weld",
    )

    _decorate_type08_entries(
        result,
        profile_id=profile_id,
        profile=profile,
        row=row,
        config=config,
        pipe_size=pipe_size,
        l_value=l_value,
        h_value=h_value,
        l1=l1,
        l2=l2,
        placement_modified=placement_modified,
        pipe_length=pipe_length,
        channel_length=channel_length,
        lower_component=letter,
        high_height_unverified=high_height_unverified,
        m42_start=m42_start,
        m42_end=m42_end,
    )

    result.warnings.append(
        "Type 08 主構件下料已依來源圖核對；weep hole 孔中心離底板尺寸仍需工程確認"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type08_source_row",
                row,
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.95,
                note=f"{profile_id} D-8 dimensions table",
            ),
            make_evidence(
                "member_n_cut_length_mm",
                channel_length,
                "formula",
                source=profile["drawing"],
                confidence=0.95,
                note=profile["channel_cut_formula"],
            ),
            make_evidence(
                "supporting_pipe_cut_length_mm",
                pipe_length,
                "formula",
                source=profile["drawing"],
                confidence=0.9,
                note="H - top plate t - member N depth/2 - M42 plate t",
            ),
        ]
    )
    return result
