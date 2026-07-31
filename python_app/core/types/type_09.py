"""Type 09 source-profile calculator.

Type 09 is an adjustable dummy-leg support.  D-9 itself does not encode
whether the upper leg attaches to a straight run or a long-radius elbow, so
that connection must be selected as a variation axis for a fabrication-safe
result.
"""
from __future__ import annotations

import math
import re

from ..bolt import add_custom_entry
from ..component_roles import ComponentRole
from ..config_loader import load_config
from ..hardware_material import HardwareKind
from ..issues import (
    register_host_m42_variance,
    register_source_envelope,
)
from ..m42 import perform_action_by_letter, source_allows_m42_type
from ..material_specs import (
    HEAVY_HEX_NUT_A307_HDG,
    SUPPORT_PIPE_A53GRB,
    THREADED_ROD_A307_HDG,
    material_spec,
)
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..pipe import add_pipe_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence


_HEIGHT_RE = re.compile(r"^(?P<h>\d+)(?P<letter>[A-Za-z])$")
_STEEL_DENSITY_KG_PER_MM3 = 7.85e-6


def _load_profile(source_profile: str | None) -> tuple[str, dict, dict, dict]:
    config = load_config("09", strict=True)
    if not config:
        raise FileNotFoundError(
            "Type 09 設定檔遺失或損毀 (configs/type_09.json)"
        )
    profile_id = normalize_source_profile(source_profile)
    try:
        profile = config["source_profiles"][profile_id]
    except KeyError as exc:
        raise ValueError(f"Type 09 尚未建立來源 profile: {profile_id}") from exc
    return (
        profile_id,
        profile,
        {int(k): v for k, v in config["line_size_table"].items()},
        config,
    )


def _parse_line_size(fullstring: str) -> int:
    value = float(get_lookup_value(get_part(fullstring, 2)))
    if not value.is_integer():
        raise ValueError("第二段 supported line size 必須是 2/3/4 吋整數")
    return int(value)


def _parse_height_and_letter(fullstring: str) -> tuple[int, str]:
    raw = str(get_part(fullstring, 3) or "").strip()
    match = _HEIGHT_RE.fullmatch(raw)
    if not match:
        raise ValueError("第三段格式應為 HH+M42 字母，例如 05B")
    return int(match.group("h")) * 100, match.group("letter").upper()


def _h_within_profile(h_value: int, profile: dict) -> bool:
    minimum = int(profile["h_min_mm"])
    if profile.get("h_min_inclusive"):
        minimum_ok = h_value >= minimum
    else:
        minimum_ok = h_value > minimum
    return minimum_ok and h_value <= int(profile["h_max_mm"])


def _remove_type09_deleted_plate_a(
    result: AnalysisResult,
    *,
    m42_start: int,
    letter: str,
    profile: dict,
) -> list[str]:
    if letter not in profile["delete_m42_plate_a_for"]:
        return []
    before = result.entries[:m42_start]
    kept = []
    deleted = []
    for entry in result.entries[m42_start:]:
        if entry.name.startswith("Plate_a_"):
            deleted.append(entry.name)
        else:
            kept.append(entry)
    result.entries = before + kept
    for item_no, entry in enumerate(result.entries, start=1):
        entry.item_no = item_no
    return deleted


def _nominal_bolt_blank_weight(diameter_mm: float, length_mm: float) -> float:
    volume = math.pi * diameter_mm**2 / 4 * length_mm
    return round(volume * _STEEL_DENSITY_KG_PER_MM3, 2)


def _add_adjusting_hardware(
    result: AnalysisResult,
    *,
    profile: dict,
    config: dict,
) -> tuple[int, int]:
    bolt_index = len(result.entries)
    diameter = float(profile["adjusting_bolt_diameter_mm"])
    length = float(config["fabrication_contract"]["adjusting_bolt_length_mm"])
    bolt_weight = _nominal_bolt_blank_weight(diameter, length)
    add_custom_entry(
        result,
        name="M.B.(FULL THREADED)",
        spec=profile["adjusting_bolt_spec"],
        material=THREADED_ROD_A307_HDG,
        quantity=1,
        unit_weight=bolt_weight,
        unit="EA",
        role=ComponentRole.MACHINE_BOLT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    bolt = result.entries[-1]
    bolt.length = length
    bolt.geometry.component_id = "D9-ADJUSTING-BOLT"
    bolt.geometry.shape_kind = "purchased_full_thread_machine_bolt"
    bolt.geometry.shape_spec = profile["adjusting_bolt_spec"]
    bolt.geometry.fabrication_ready = True
    bolt.geometry.parameters = {
        "nominal_diameter_mm": diameter,
        "overall_length_mm": length,
        "thread": "full length",
        "material": "A307-B galvanized",
        "weight_basis": config["fabrication_contract"]["bolt_weight_basis"],
    }

    nut_index = len(result.entries)
    add_custom_entry(
        result,
        name="HEAVY HEX NUT",
        spec=profile["heavy_hex_nut_spec"],
        material=HEAVY_HEX_NUT_A307_HDG,
        quantity=int(profile["heavy_hex_nut_quantity"]),
        unit_weight=0,
        unit="EA",
        role=ComponentRole.NUT.value,
        item_class="accessory",
        manufacturing_type="purchased",
    )
    nut = result.entries[-1]
    nut.geometry.component_id = "D9-HEAVY-HEX-NUT"
    nut.geometry.shape_kind = "purchased_heavy_hex_nut"
    nut.geometry.shape_spec = profile["heavy_hex_nut_spec"]
    nut.geometry.fabrication_ready = True
    nut.geometry.parameters = {
        "spec": profile["heavy_hex_nut_spec"],
        "quantity": nut.quantity,
        "one_nut_welded_to_dummy_leg": True,
    }
    result.warnings.append(
        "D-9 僅給 HEAVY HEX NUT 規格/數量，未給單重；螺帽重量未計入"
    )
    result.warnings.append(
        "D-9 調整螺栓重量以 nominal solid-cylinder blank 概算；"
        "採購全牙成品實重需由供應商確認"
    )
    return bolt_index, nut_index


def _decorate_pipe_entry(
    entry,
    *,
    component_id: str,
    drawing: str,
    revision: str,
    shape_kind: str,
    shape_spec: str,
    parameters: dict,
    fabrication_ready: bool,
    blockers: list[str] | None = None,
) -> None:
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = revision
    entry.geometry.shape_kind = shape_kind
    entry.geometry.shape_spec = shape_spec
    entry.geometry.fabrication_ready = fabrication_ready
    entry.geometry.fabrication_blockers = list(blockers or [])
    entry.geometry.parameters = dict(parameters)


def _decorate_m42_entries(
    entries,
    *,
    profile: dict,
    letter: str,
) -> None:
    for entry in entries:
        entry.geometry.source_drawing = profile["m42_drawing"]
        entry.geometry.source_revision = profile["m42_revision"]
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
                    "type09_resting_surface": True,
                }
            )
            if letter == "C" and profile.get("type_c_note"):
                entry.geometry.notes_zh = profile["type_c_note"]
                entry.geometry.parameters["weld_per_type09_detail"] = True
        elif entry.category == "螺栓類":
            entry.geometry.component_id = "M42-FASTENER"
            entry.geometry.shape_kind = "purchased_fastener"
            entry.geometry.parameters.update(
                {"spec": entry.spec, "quantity": entry.quantity}
            )
        elif entry.category == "型鋼類":
            entry.geometry.component_id = "M42-ANGLE-RETAINER"
            entry.geometry.shape_kind = "stock_section_cut"


def calculate(
    fullstring: str,
    connection: str = "elbow",
    upper_material: str = "SUS304",
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    connection = str(connection or "").strip().lower()

    try:
        profile_id, profile, table, config = _load_profile(source_profile)
        line_size = _parse_line_size(fullstring)
        h_value, letter = _parse_height_and_letter(fullstring)
    except (FileNotFoundError, TypeError, ValueError) as exc:
        result.error = f"Type 09: {exc}"
        return result

    if connection not in {"elbow", "straight"}:
        result.error = (
            f"Type 09: connection={connection!r} 不支援；僅 elbow/straight"
        )
        return result
    if line_size not in table:
        result.error = (
            f'Type 09 / {profile_id}: supported line {line_size}" '
            "不在 D-9 表列 2/3/4 吋範圍"
        )
        return result
    minimum = int(profile["h_min_mm"])
    minimum_ok = (
        h_value >= minimum
        if profile.get("h_min_inclusive")
        else h_value > minimum
    )
    if not minimum_ok:
        relation = "≤" if profile.get("h_min_inclusive") else "<"
        result.error = (
            f"Type 09 / {profile_id}: H={h_value}mm 超出來源限制 "
            f'{profile["h_min_mm"]}{relation}H≤{profile["h_max_mm"]}mm'
        )
        return result
    if not register_source_envelope(
        result,
        type_label=f"Type 09 / {profile_id}",
        source_ref="D-9 H上限",
        checks=(("H", h_value, int(profile["h_max_mm"]), True),),
    ):
        return result
    if letter not in profile["allowed_lower_components"]:
        if not source_allows_m42_type(profile_id, letter):
            result.error = (
                f"Type 09 / {profile_id}: M-42 {letter} 不存在於此來源 M-42 圖"
            )
            return result
        register_host_m42_variance(
            result,
            type_label=f"Type 09 / {profile_id}",
            source_ref="D-9",
            letter=letter,
            host_allowed=profile["allowed_lower_components"],
        )

    if profile["b_height_from_lowest_paving"] and letter == "B":
        result.warnings.append(
            "M-42 Type B：H 應從鋪面最低點標高起算"
        )

    fab = config["fabrication_contract"]
    connection_explicit = "connection" in overrides
    if not connection_explicit:
        result.warnings.append(
            "Type 09 編碼未包含 straight/elbow；本筆沿用 elbow 預設，"
            "出加工圖前必須明確選擇主管接點"
        )

    upper_length = float(fab["special_upper_straight_length_mm"])
    if connection == "elbow":
        upper_length += float(table[line_size]["L"])
    lower_length = (
        h_value
        - float(fab["special_upper_straight_length_mm"])
        - float(fab["adjusting_clearance_mm"])
    )
    if lower_length <= 0:
        result.error = (
            f"Type 09 / {profile_id}: H={h_value}mm 導致下段 Supporting "
            f"Pipe 切長 {lower_length:g}mm，無法製作"
        )
        return result

    upper_material_spec = material_spec(
        HardwareKind.SUPPORT_PIPE,
        upper_material,
    )
    support_size = fab["supporting_pipe_size_in"]
    support_schedule = fab["supporting_pipe_schedule"]
    add_pipe_entry(
        result,
        support_size,
        support_schedule,
        upper_length,
        upper_material_spec,
    )
    add_pipe_entry(
        result,
        support_size,
        support_schedule,
        lower_length,
        SUPPORT_PIPE_A53GRB,
    )

    m42_start = len(result.entries)
    perform_action_by_letter(
        result,
        letter,
        support_size,
        source_profile=profile_id,
    )
    if result.error:
        result.entries.clear()
        return result
    deleted_m42 = _remove_type09_deleted_plate_a(
        result,
        m42_start=m42_start,
        letter=letter,
        profile=profile,
    )
    m42_end = len(result.entries)

    _add_adjusting_hardware(result, profile=profile, config=config)

    cope_blocker = (
        f'2" SCH.40 upper dummy leg 的 {connection} 相貫 cope/fishmouth '
        "輪廓未由 D-9 尺寸化"
    )
    upper_blockers = [cope_blocker]
    if not connection_explicit:
        upper_blockers.append(
            "connection 使用預設 elbow，而非由編碼或專案列明確指定"
        )
    _decorate_pipe_entry(
        result.entries[0],
        component_id="D9-UPPER-DUMMY-LEG",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind=f"dummy_leg_to_{connection}",
        shape_spec=(
            f'2"*SCH.40; CUT L={upper_length:g}; TOP COPE TO '
            f"{connection.upper()}"
        ),
        parameters={
            "supported_line_size_in": line_size,
            "connection": connection,
            "L_elbow_mm": table[line_size]["L"] if connection == "elbow" else 0,
            "straight_tail_mm": fab["special_upper_straight_length_mm"],
            "cut_length_mm": upper_length,
            "material_same_as_main": True,
            "field_weld_mm": fab["field_weld_mm"],
        },
        fabrication_ready=False,
        blockers=upper_blockers,
    )
    _decorate_pipe_entry(
        result.entries[1],
        component_id="D9-LOWER-SUPPORTING-PIPE",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="square_cut_support_pipe_with_welded_nut",
        shape_spec=(
            f'2"*SCH.40; CUT L={lower_length:g}; WELD HEAVY HEX NUT '
            f"{profile['heavy_hex_nut_spec']} AT BOTTOM"
        ),
        parameters={
            "H_mm": h_value,
            "upper_special_tail_mm": fab["special_upper_straight_length_mm"],
            "adjusting_clearance_mm": fab["adjusting_clearance_mm"],
            "cut_formula": "H - 100 - 100",
            "cut_length_mm": lower_length,
            "top_joint": "square butt joint to upper dummy leg",
            "bottom_nut_weld_mm": fab["field_weld_mm"],
        },
        fabrication_ready=True,
    )
    _decorate_m42_entries(
        result.entries[m42_start:m42_end],
        profile=profile,
        letter=letter,
    )

    blockers = [cope_blocker]
    if not connection_explicit:
        blockers.append(
            "designation does not encode straight/elbow; connection must be confirmed"
        )
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "branch": f"D-9/{connection}/M42-{letter}",
        "bom_ready": connection_explicit,
        "fabrication_ready": False,
        "blockers": blockers,
        "omitted_by_type09_m43_note": deleted_m42,
        "dimensions": {
            "H_mm": h_value,
            "elbow_L_mm": table[line_size]["L"] if connection == "elbow" else 0,
            "upper_dummy_leg_cut_length_mm": upper_length,
            "lower_supporting_pipe_cut_length_mm": lower_length,
            "adjusting_clearance_mm": fab["adjusting_clearance_mm"],
            "adjusting_bolt_spec": profile["adjusting_bolt_spec"],
        },
    }

    result.warnings.append(
        "Type 09 下料已依 D-9/M-43 修正；上端相貫 cope 輪廓仍需工程確認"
    )
    result.evidence.extend(
        [
            make_evidence(
                "type09_source_profile",
                {
                    "allowed_lower_components": profile[
                        "allowed_lower_components"
                    ],
                    "adjusting_bolt_spec": profile["adjusting_bolt_spec"],
                    "delete_m42_plate_a_for": profile[
                        "delete_m42_plate_a_for"
                    ],
                },
                "visual_transcription",
                source=profile["drawing"],
                confidence=0.95,
                note=f"{profile_id} D-9 and M-43 notes",
            ),
            make_evidence(
                "upper_dummy_leg_cut_length_mm",
                upper_length,
                "formula",
                source=profile["drawing"],
                confidence=0.9,
                note="straight=100; elbow=L+100",
            ),
            make_evidence(
                "lower_supporting_pipe_cut_length_mm",
                lower_length,
                "formula",
                source=profile["drawing"],
                confidence=0.9,
                note="H - 100 upper special tail - 100 adjusting clearance",
            ),
        ]
    )
    return result
