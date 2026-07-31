"""Type 126 I-Rod cross-beam pad (D-136)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def _normalize_schedule(value: object) -> str:
    schedule = str(value or "").strip().upper().replace(" ", "")
    aliases = {
        "STD": "STD",
        "STD.WT": "STD",
        "SCH.40": "SCH40",
        "SCH40": "SCH40",
        "40": "SCH40",
        "40S": "SCH40",
        "XS": "XS",
        "SCH.80": "SCH80",
        "SCH80": "SCH80",
        "80": "SCH80",
        "80S": "SCH80",
    }
    return aliases.get(schedule, "")


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("126", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 126: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    row = profile["rows"].get(f"{size:g}")
    if not row:
        result.error = f'Type 126: D-136 未表列 {size:g}"'
        return result

    count_raw = overrides.get("i_rod_count")
    count = None
    if count_raw not in (None, ""):
        try:
            count = int(count_raw)
        except (TypeError, ValueError):
            count = 0
        if count not in {1, 2, 3}:
            result.error = "Type 126: i_rod_count 必須為 1、2 或 3"
            return result

    temperature_class = str(
        overrides.get("i_rod_temperature_class") or ""
    ).strip().lower()
    if temperature_class and temperature_class not in profile["temperature_classes"]:
        result.error = (
            "Type 126: i_rod_temperature_class 必須為 "
            f"{sorted(profile['temperature_classes'])}"
        )
        return result

    schedule_raw = overrides.get("pipe_schedule")
    schedule = _normalize_schedule(schedule_raw)
    if schedule_raw not in (None, "") and not schedule:
        result.error = "Type 126: pipe_schedule 必須為 STD、SCH.40、XS 或 SCH.80"
        return result
    maximum_spacing = (
        row["maximum_spacing_m"].get(schedule)
        if schedule
        else None
    )
    if schedule and maximum_spacing is None:
        result.error = (
            f'Type 126 / {size:g}" / {schedule}: '
            "D-136 未提供 I-Rod cross-beam 最大間距"
        )
        return result

    blockers: list[str] = []
    if count is None:
        blockers.append(
            "D-136 allows one to three parallel I-Rods with evenly shared "
            "load；designation does not encode i_rod_count"
        )
    if not temperature_class:
        blockers.append(
            "D-136 lists Regular/High Temp/PEEK temperature limits，"
            "designation does not select the I-Rod material class"
        )
    if not schedule:
        blockers.append(
            "D-136 cross-beam maximum spacing depends on pipe schedule；"
            "需以 pipe_schedule 明選 STD/SCH.40/XS/SCH.80"
        )
    if not any(value is not None for value in row["maximum_spacing_m"].values()):
        blockers.append(
            f'D-136 has no tabulated spacing for {size:g}"；'
            "cross-beam layout requires project structural calculation"
        )
    irod_blocker = (
        "I-Rod is a proprietary toothed thermoplastic extrusion；D-136 "
        "provides L/C/D but not net profile/density or supplier unit-weight"
    )
    blockers.append(irod_blocker)
    adhesive_blocker = (
        "D-136 permits 3M double-sided tape or manufacturer adhesive，"
        "but product/coverage/quantity is project-selected"
    )
    blockers.append(adhesive_blocker)
    quantity = count if count is not None else 1
    rod_class = (
        profile["temperature_classes"][temperature_class]
        if temperature_class
        else {
            "label": "THERMOPLASTIC I-ROD; CLASS TBD",
            "maximum_temperature_C": None,
        }
    )
    single_point_load_limit_kg = (
        profile["single_point_load_limits_kg"]["1.5"]
        if row["width_C_mm"] == 38.1
        else profile["single_point_load_limits_kg"]["1"]
    )
    add_reference(
        result,
        name="D-136 I-ROD CROSS-BEAM PAD SET",
        spec=(
            f"L={row['length_L_mm']} x C={row['width_C_mm']} x "
            f"D={row['height_D_mm']}; "
            f"QTY={count if count is not None else 'TBD'}"
        ),
        material=rod_class["label"],
        quantity=quantity,
        category="墊片類",
        component_id="D136-I-ROD-PAD",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="purchased_toothed_thermoplastic_i_rod_pad",
        parameters={
            "line_size_in": size,
            "pipe_od_mm": row["pipe_od_mm"],
            "piece_count": count,
            "temperature_class": temperature_class or None,
            "maximum_temperature_C": rod_class["maximum_temperature_C"],
            "single_point_load_limit_kg": single_point_load_limit_kg,
            "length_L_mm": row["length_L_mm"],
            "width_C_mm": row["width_C_mm"],
            "height_D_mm": row["height_D_mm"],
            "pipe_schedule": schedule or None,
            "maximum_cross_beam_spacing_m": maximum_spacing,
            "maximum_spacing_options_m": row["maximum_spacing_m"],
            "attachment_options": [
                "3M DOUBLE-SIDED TAPE",
                "I-ROD MANUFACTURER ADHESIVE",
            ],
        },
        blocker="；".join(blockers),
        manufacturing_type="purchased",
    )

    parameters = {
        "line_size_in": size,
        "pipe_schedule": schedule or None,
        "i_rod_count": count,
        "temperature_class": temperature_class or None,
        "maximum_temperature_C": rod_class["maximum_temperature_C"],
        "single_point_load_limit_kg": single_point_load_limit_kg,
        "maximum_cross_beam_spacing_m": maximum_spacing,
        **row,
    }
    result.warnings.extend(blockers)
    result.meta["type_id"] = "126"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": parameters,
        "not_furnished": ["cross beam", "pipe"],
    }
    result.evidence.append(
        make_evidence(
            "type126_d136_row",
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
