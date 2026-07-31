"""Type 115 continuous support for small non-ferrous pipe (D-128)."""

from __future__ import annotations

import math

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("115", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 115: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    length_token = get_part(fullstring, 3) or ""
    if not length_token.isdigit():
        result.error = "Type 115 格式應為 115-{LINE}B-{L/100}"
        return result
    length = int(length_token) * 100
    row = profile["rows"].get(f"{size:g}")
    if not row:
        result.error = f'Type 115: D-128 未表列 {size:g}"'
        return result
    if length <= 0 or length > row["L_max"]:
        result.error = (
            f"Type 115 / {size:g}\": L 必須 0 < L <= {row['L_max']} mm"
        )
        return result

    add_steel_section_entry(
        result,
        "Angle",
        row["member_m_spec"],
        length,
        1,
        "A36/SS400",
    )
    member = result.entries[-1]
    member.geometry.component_id = "D128-MEMBER-M"
    member.geometry.source_drawing = profile["drawing"]
    member.geometry.source_revision = profile["revision"]
    member.geometry.shape_kind = "continuous_angle_support"
    member.geometry.parameters = {
        "line_size_in": size,
        "cut_length_L_mm": length,
        "section": f"L{row['member_m_spec'].replace('*', 'x')}",
        "weld_mm": 6,
        "support_on_existing_steel": True,
    }
    member.geometry.fabrication_ready = True

    plate_qty = math.ceil(length / row["N_max"]) + 1
    spacing = length / (plate_qty - 1)
    positions = [round(index * spacing, 3) for index in range(plate_qty)]
    add_plate_entry(
        result,
        row["plate_size"],
        row["plate_size"],
        row["plate_thickness"],
        "PLATE P",
        "A36/SS400",
        plate_qty=plate_qty,
        shape_spec=(
            f"{row['plate_size']}x{row['plate_size']}x"
            f"{row['plate_thickness']}t; QTY{plate_qty}"
        ),
        shape_kind="continuous_support_side_plate",
    )
    plate = result.entries[-1]
    plate.geometry.component_id = "D128-PLATE-P"
    plate.geometry.source_drawing = profile["drawing"]
    plate.geometry.source_revision = profile["revision"]
    plate.geometry.parameters = {
        "line_size_in": size,
        "piece_count": plate_qty,
        "plate_size_mm": row["plate_size"],
        "thickness_mm": row["plate_thickness"],
        "maximum_spacing_N_mm": row["N_max"],
        "actual_equal_spacing_mm": spacing,
        "positions_from_start_mm": positions,
        "pipe_side_clearance_mm": 3,
    }
    plate.geometry.fabrication_ready = True

    site_blocker = (
        "Member M 與 Plate P 下料/間距已可發圖；但 D-128 未指定下方 existing "
        "steel support 的 project positions，整體安裝圖仍需現場/結構配置"
    )
    result.warnings.append(site_blocker)
    result.meta["type_id"] = "115"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": True,
        "fabrication_ready": False,
        "blockers": [site_blocker],
        "assembly_dimensions": {
            "line_size_in": size,
            "L_mm": length,
            "N_max_mm": row["N_max"],
            "plate_count": plate_qty,
            "actual_plate_spacing_mm": spacing,
            "plate_positions_mm": positions,
        },
    }
    result.evidence.append(
        make_evidence(
            "type115_d128_cut_and_spacing",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
