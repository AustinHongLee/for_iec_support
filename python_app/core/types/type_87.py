"""Type 87 adjustable support post — source-aware D-108/D-109."""

from __future__ import annotations

import math

from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def _parse(fullstring: str, result: AnalysisResult) -> tuple[str, int, str] | None:
    rod = (get_part(fullstring, 2) or "").upper()
    token = (get_part(fullstring, 3) or "").upper()
    if not rod or len(token) < 2 or not token[-1].isalpha() or not token[:-1].isdigit():
        result.error = "Type 87 格式應為 87-{ROD}-{H/100}{G|J|T|R}"
        return None
    return rod, int(token[:-1]) * 100, token[-1]


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("87", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 87: 尚未建立來源 profile {profile_id}"
        return result
    parsed = _parse(fullstring, result)
    if parsed is None:
        return result
    rod_token, h_mm, lower_type = parsed
    rod_key = profile.get("rod_aliases", {}).get(rod_token, rod_token)
    try:
        rod_size = get_lookup_value(rod_key)
    except (TypeError, ValueError):
        result.error = f"Type 87: 無法辨識 rod size {rod_token}"
        return result
    row = profile["rows"].get(f"{rod_size:g}")
    if not row:
        result.error = f'Type 87 / {profile_id}: 未表列 rod {rod_size:g}"'
        return result
    if lower_type not in profile["lower_component_types"]:
        result.error = (
            f"Type 87 / {profile_id}: lower component 只允許 "
            f"{'/'.join(profile['lower_component_types'])}"
        )
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    blockers: list[str] = []
    common_parameters = {
        "rod_size_in": rod_size,
        "assembly_H_mm": h_mm,
        "thread_E_mm": row["E"],
        "lower_component_type": lower_type,
    }

    pipe_blocker = (
        "D-108/D-109 NOTE 1 指定 H/pipe length 現場切配；H 是 ground-to-load "
        "組立高度，不是 A53-B pipe finished cut。需 pipe_cut_length_mm"
    )
    add_reference(
        result,
        name="A53-B SUPPORT PIPE",
        spec=f'{row["B"]}; CUT LENGTH TBD',
        material="A53 Gr.B",
        quantity=1,
        category="管路類",
        component_id=f"D{profile['detail_no']}-SUPPORT-PIPE",
        drawing=drawing,
        revision=revision,
        shape_kind="field_cut_support_pipe",
        parameters={**common_parameters, "pipe_cut_length_mm": None},
        blocker=pipe_blocker,
        manufacturing_type="raw_cut",
    )
    blockers.append(pipe_blocker)

    rod_blocker = (
        "Special machine-threaded rod M-2 的 finished length、端部加工與來源單重"
        "未由 designation/H 唯一決定"
    )
    add_reference(
        result,
        name="SPECIAL MACHINE THREADED ROD",
        spec=f'ROD {rod_token}; THREAD E={row["E"]}',
        material="PROJECT-SPEC ROD MATERIAL",
        quantity=1,
        category="螺栓類",
        component_id=f"D{profile['detail_no']}-M2-THREADED-ROD",
        drawing=drawing,
        revision=revision,
        shape_kind="special_machine_threaded_rod",
        parameters=common_parameters,
        blocker=rod_blocker,
        manufacturing_type="raw_cut",
    )
    blockers.append(rod_blocker)

    for plate_name, plate_data, component in (
        ("PLATE C", row["C"], "PLATE-C"),
        (profile["top_plate_name"], row["top_plate"], "TOP-PLATE"),
    ):
        blocker = (
            f"{plate_name} 外形尺寸已知，但中心 rod hole/fit tolerance 未標；"
            "在孔徑確認前保留零重量加工 reference"
        )
        add_reference(
            result,
            name=plate_name,
            spec=plate_data,
            material="A36/SS400",
            quantity=1,
            category="鋼板類",
            component_id=f"D{profile['detail_no']}-{component}",
            drawing=drawing,
            revision=revision,
            shape_kind="square_plate_with_unresolved_center_hole",
            parameters={**common_parameters, "source_size": plate_data},
            blocker=blocker,
            manufacturing_type="plate_cut",
        )
        blockers.append(blocker)

    if row.get("internal_disc"):
        disc = row["internal_disc"]
        diameter = disc["diameter_mm"]
        thickness = disc["thickness_mm"]
        area = math.pi * diameter**2 / 4
        add_plate_entry(
            result,
            diameter,
            diameter,
            thickness,
            "ROUND PLATE D",
            "A36/SS400",
            formula="PI*D^2/4",
            shape_spec=f"ROUND DIA{diameter}x{thickness}t",
            shape_kind="round_disc",
            gross_area_mm2=area,
            net_area_mm2=area,
        )
        disc_entry = result.entries[-1]
        disc_entry.geometry.component_id = f"D{profile['detail_no']}-ROUND-PLATE-D"
        disc_entry.geometry.source_drawing = drawing
        disc_entry.geometry.source_revision = revision
        disc_entry.geometry.fabrication_ready = True
        disc_entry.geometry.parameters = {
            **common_parameters,
            "diameter_mm": diameter,
            "thickness_mm": thickness,
        }
        set_remark(disc_entry, "D-109 exact solid round plate D")

    accessory_blocker = (
        "Lock nut、adjust nut 與 M-42 lower component 的完整採購規格/重量"
        "需對應 M-2/M-42；本圖只限制 lower type 與組立位置"
    )
    add_reference(
        result,
        name="ADJUSTING HARDWARE / LOWER COMPONENT",
        spec=f"LOCK+ADJUST NUT; M-42 TYPE-{lower_type}",
        material="PROJECT SPECIFICATION",
        quantity=1,
        category="螺栓類",
        component_id=f"D{profile['detail_no']}-ADJUSTING-HARDWARE",
        drawing=drawing,
        revision=revision,
        shape_kind="adjustable_support_hardware_set",
        parameters=common_parameters,
        blocker=accessory_blocker,
        manufacturing_type="purchased",
    )
    blockers.append(accessory_blocker)

    result.warnings.extend(blockers)
    result.meta["type_id"] = "87"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": common_parameters,
    }
    result.evidence.append(
        make_evidence(
            "type87_dimension_row",
            {**common_parameters, **row},
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
