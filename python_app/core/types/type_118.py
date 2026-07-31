"""Type 118 under-support saddle for non-ferrous pipe (D-131/M-57)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._nonferrous_support_common import add_m57_saddle


def _parse(fullstring: str) -> tuple[float, float]:
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    pipe_od = float(get_part(fullstring, 3) or 0)
    return size, pipe_od


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("118", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 118: 尚未建立來源 profile {profile_id}"
        return result
    try:
        size, pipe_od = _parse(fullstring)
    except ValueError:
        result.error = "Type 118 格式應為 118-{LINE}B-{ACTUAL PIPE OD mm}"
        return result
    if pipe_od <= 0:
        result.error = "Type 118: actual non-ferrous pipe OD 必須大於 0 mm"
        return result
    try:
        row, blockers = add_m57_saddle(
            result,
            line_size=size,
            pipe_od_mm=pipe_od,
            drawing=profile["drawing"],
            revision=profile["revision"],
            component_prefix="D131",
        )
    except ValueError as exc:
        result.error = f"Type 118: {exc}"
        return result

    result.warnings.extend(blockers)
    dims = row["dimensions_mm"]
    result.meta["type_id"] = "118"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": {
            "line_size_in": size,
            "actual_pipe_od_mm": pipe_od,
            "T_mm": dims["T"],
            "G_mm": profile["groups"][f"{size:g}"]["G"],
            "W_mm": dims["W"],
        },
    }
    result.evidence.append(
        make_evidence(
            "type118_d131_m57",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
