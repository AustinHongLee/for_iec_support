"""Type 119 guide support for non-ferrous pipe (D-132)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._nonferrous_support_common import (
    add_m57_saddle,
    add_m58_ubolt,
    add_m59_uband,
    add_small_guide_plate,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("119", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 119: 尚未建立來源 profile {profile_id}"
        return result
    try:
        size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
        pipe_od = float(get_part(fullstring, 3) or 0)
    except ValueError:
        result.error = "Type 119 格式應為 119-{LINE}B-{ACTUAL PIPE OD mm}"
        return result
    if pipe_od <= 0:
        result.error = "Type 119: actual non-ferrous pipe OD 必須大於 0 mm"
        return result
    if size not in [float(value) for value in profile["allowed_sizes"]]:
        result.error = f'Type 119: D-132 未表列 {size:g}"'
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    blockers: list[str] = []
    try:
        _, saddle_blockers = add_m57_saddle(
            result,
            line_size=size,
            pipe_od_mm=pipe_od,
            drawing=drawing,
            revision=revision,
            component_prefix="D132",
        )
        blockers.extend(saddle_blockers)
        if size <= 8:
            m58, ubolt_blockers = add_m58_ubolt(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                drawing=drawing,
                revision=revision,
                component_prefix="D132",
            )
            blockers.extend(ubolt_blockers)
            guide_row = profile["small_rows"][f"{size:g}"]
            add_small_guide_plate(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                row=guide_row,
                drawing=drawing,
                revision=revision,
                component_prefix="D132",
            )
            branch = "M-58 U-BOLT / TWO-HOLE PLATE"
            guide_component = m58["component_id"]
        else:
            m59, uband_blockers = add_m59_uband(
                result,
                line_size=size,
                pipe_od_mm=pipe_od,
                drawing=drawing,
                revision=revision,
                component_prefix="D132",
            )
            blockers.extend(uband_blockers)
            branch = "M-59 U-BAND"
            guide_component = m59["component_id"]
    except (KeyError, ValueError) as exc:
        result.error = f"Type 119: {exc}"
        return result

    result.warnings.extend(blockers)
    result.meta["type_id"] = "119"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "branch": branch,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_in": size,
            "actual_pipe_od_mm": pipe_od,
            "guide_component": guide_component,
            "gap_mm": 3,
        },
    }
    result.evidence.append(
        make_evidence(
            "type119_d132_branch",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
