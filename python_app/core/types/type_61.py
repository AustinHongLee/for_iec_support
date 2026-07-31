"""Type 61 trunnion support — D-72/D-73/D-74.

The designation fixes the nominal trunnion size, T1/T2 quantity and nominal
length H.  It does *not* contain the main-line size/schedule, design moment or
temperature needed to select/check the reinforcing pad and moment capacity.
Those omissions are preserved as explicit blockers instead of being replaced
with a guessed square pad.
"""
from __future__ import annotations

import math

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, HolePattern, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.pipe_table import calculate_pipe_weight, get_pipe_details, get_pipe_od


def _pipe_row(config: dict, size: float) -> dict | None:
    return config["trunnion_pipe_table"].get(f"{size:g}")


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    overrides = overrides or {}
    config = load_config("61", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 61: 尚未建立來源 profile {profile_id}"
        return result

    part2 = get_part(fullstring, 2)
    part3 = (get_part(fullstring, 3) or "").upper()
    part4 = get_part(fullstring, 4)
    if not part2 or part3 not in {"T1", "T2"} or not part4:
        result.error = "Type 61 格式應為 61-{TRUNNION}B-T{1|2}-{H/100}[(P)]"
        return result

    trunnion_size = get_lookup_value(part2)
    pipe_rule = _pipe_row(config, trunnion_size)
    if not pipe_rule:
        result.error = (
            f'Type 61: D-73/D-74 未表列 {trunnion_size:g}" trunnion；'
            '允許 2", 3", 4", 6", 8", 10", 12", 14"'
        )
        return result

    h_token, pad_token = extract_parts(part4)
    try:
        h_mm = int(h_token) * 100
    except (TypeError, ValueError):
        result.error = f"Type 61: 無法解析 trunnion 長度 {part4!r}"
        return result
    if h_mm <= 0:
        result.error = "Type 61: trunnion 長度 H 必須大於 0"
        return result

    quantity = 1 if part3 == "T1" else 2
    has_pad = pad_token.upper() == "(P)"
    material = str(overrides.get("trunnion_material") or profile["default_material"])
    schedule = pipe_rule.get("schedule")
    if schedule:
        details = get_pipe_details(trunnion_size, schedule, material)
        wall_mm = details["thickness_mm"]
        weight_per_m = details["weight_per_m"]
        pipe_spec = f'{trunnion_size:g}" SCH.{schedule.removesuffix("S")}'
    else:
        wall_mm = float(pipe_rule["minimum_wall_mm"])
        od_mm = get_pipe_od(trunnion_size)
        weight_per_m = calculate_pipe_weight(od_mm, wall_mm)
        pipe_spec = f'{trunnion_size:g}" {wall_mm:g}t MIN.'

    # H is a drawing take-off dimension.  Its straight-pipe stock weight is
    # useful for procurement, but the main-line saddle cut still needs a
    # template based on the actual main pipe.
    add_custom_entry(
        result,
        "TRUNNION PIPE",
        pipe_spec,
        material,
        quantity,
        round(weight_per_m * h_mm / 1000, 2),
        "PC",
        category="管路類",
        item_class="primary_structure",
        manufacturing_type="raw_cut",
    )
    trunnion = result.entries[-1]
    trunnion.length = h_mm
    trunnion.geometry.component_id = "D72-TRUNNION-PIPE"
    trunnion.geometry.source_drawing = profile["geometry_drawing"]
    trunnion.geometry.source_revision = profile["revision"]
    trunnion.geometry.shape_kind = "pipe_with_main_line_saddle_cut"
    trunnion.geometry.shape_spec = (
        f'{pipe_spec}; H={h_mm}; QTY={quantity}; MAIN-LINE CONTACT CUT'
    )
    trunnion.geometry.parameters = {
        "nominal_size_in": trunnion_size,
        "wall_thickness_mm": wall_mm,
        "nominal_length_H_mm": h_mm,
        "quantity": quantity,
        "type": part3,
        "weep_hole_diameter_mm": 6,
        "end_bevel_mm": 12,
    }
    main_size = overrides.get("main_line_size")
    contact_blocker = (
        "D-72 trunnion 與 main line 的貼合切口需 main_line_size/實際 OD "
        "及切割基準；目前只可列直管備料長度 H"
    )
    if main_size not in (None, ""):
        trunnion.geometry.parameters["main_line_size_in"] = get_lookup_value(str(main_size))
        contact_blocker = (
            "已提供 main_line_size，但 D-72 貼合切口尚未建立可輸出的展開模板/座標"
        )
    trunnion.geometry.fabrication_ready = False
    trunnion.geometry.fabrication_blockers = [contact_blocker]
    set_remark(trunnion, f"{part3}，H={h_mm} mm；{contact_blocker}")

    pad_blockers: list[str] = []
    if has_pad:
        pad_length = overrides.get("pad_developed_length_mm")
        pad_width = overrides.get("pad_width_mm")
        pad_thickness = overrides.get("pad_thickness_mm")
        if all(value not in (None, "") for value in (pad_length, pad_width, pad_thickness)):
            pad_length = float(pad_length)
            pad_width = float(pad_width)
            pad_thickness = float(pad_thickness)
            hole_area = math.pi * 3**2
            add_plate_entry(
                result,
                pad_length,
                pad_width,
                pad_thickness,
                "REINFORCING PAD",
                material=str(overrides.get("pad_material") or material),
                plate_qty=quantity,
                plate_role="reinforcement_pad",
                formula=f"{pad_length:g}*{pad_width:g}-PI*3^2",
                gross_area_mm2=pad_length * pad_width,
                cutout_area_mm2=hole_area,
                net_area_mm2=pad_length * pad_width - hole_area,
                shape_kind="rolled_rectangular_pad",
            )
            pad = result.entries[-1]
            pad.geometry.component_id = "D72-REINFORCING-PAD"
            pad.geometry.source_drawing = profile["geometry_drawing"]
            pad.geometry.source_revision = profile["revision"]
            pad.geometry.shape_spec = (
                f"DEVELOPED {pad_length:g}x{pad_width:g}x{pad_thickness:g}t; "
                "ROLL TO MAIN LINE; 1-DIA6 WEEP HOLE"
            )
            pad.geometry.holes = HolePattern(
                pattern="single",
                diameter=6,
                count=1,
            )
            pad.geometry.parameters.update(
                {
                    "developed_length_mm": pad_length,
                    "width_mm": pad_width,
                    "thickness_mm": pad_thickness,
                    "quantity": quantity,
                    "weep_hole_diameter_mm": 6,
                }
            )
            pad.geometry.fabrication_ready = True
            set_remark(pad, "尺寸由本筆 override 明確提供；D-73/D-74 capacity 仍須另行核對")
        else:
            pad_blocker = (
                "編號含(P)，但 designation 未含 main-line size/schedule；"
                "D-73/D-74 的 pad 厚度 E、尺寸 D 與展開長度無法由本編號唯一決定，"
                "禁止沿用舊版 OD+50 方板"
            )
            add_custom_entry(
                result,
                "REINFORCING PAD",
                "SEE D-73 / D-74 PAD REQUIREMENTS",
                str(overrides.get("pad_material") or material),
                quantity,
                0,
                "PC",
                remark=pad_blocker,
                category="鋼板類",
                item_class="reference_only",
                manufacturing_type="not_furnished",
            )
            pad = result.entries[-1]
            pad.geometry.component_id = "D72-REINFORCING-PAD-REFERENCE"
            pad.geometry.source_drawing = profile["capacity_drawings"]
            pad.geometry.source_revision = profile["revision"]
            pad.geometry.shape_kind = "rolled_main_line_reinforcing_pad"
            pad.geometry.parameters = {
                "quantity": quantity,
                "weep_hole_diameter_mm": 6,
                "carbon_steel_fillet_F_mm": 9,
                "alloy_or_stainless_fillet_F_mm": 6,
            }
            pad.geometry.fabrication_ready = False
            pad.geometry.fabrication_blockers = [pad_blocker]
            pad_blockers.append(pad_blocker)

    capacity_blocker = (
        f"{profile['capacity_drawings']} moment-capacity matrix 尚需 main-line size/schedule、"
        "材質、設計溫度與設計 moment；T2 容量為 one-trunnion 表值的 2 倍"
    )
    blockers = [contact_blocker, capacity_blocker, *pad_blockers]
    result.warnings.extend(blockers)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["geometry_drawing"],
        "source_revision": profile["revision"],
        "capacity_drawings": profile["capacity_drawings"],
        "bom_ready": not pad_blockers,
        "fabrication_ready": False,
        "capacity_verified": False,
        "blockers": blockers,
        "designation_parameters": {
            "trunnion_size_in": trunnion_size,
            "type": part3,
            "quantity": quantity,
            "H_mm": h_mm,
            "pad_required": has_pad,
        },
    }
    result.evidence.extend(
        [
            make_evidence(
                "trunnion_geometry",
                result.meta["fabrication"]["designation_parameters"],
                "visual_transcription",
                source=profile["geometry_drawing"],
                confidence=0.98,
            ),
            make_evidence(
                "trunnion_pipe_rule",
                pipe_rule,
                "visual_transcription",
                source=profile["capacity_drawings"],
                confidence=0.98,
            ),
        ]
    )
    return result
