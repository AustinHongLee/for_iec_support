"""Type 127 field-cut C150 cross-channel support (D-137)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._field_channel_support_common import (
    add_field_channel_support,
    parse_hundred_mm_token,
)


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("127", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 127: 尚未建立來源 profile {profile_id}"
        return result
    length = parse_hundred_mm_token(get_part(fullstring, 2) or "", "L")
    if length is None:
        result.error = "Type 127 格式應為 127-{L/100}L"
        return result
    if length <= 0 or length > profile["L_max_mm"]:
        result.error = f"Type 127: L 必須 0 < L <= {profile['L_max_mm']} mm"
        return result

    blockers = add_field_channel_support(
        result,
        type_id="127",
        length_mm=length,
        profile=profile,
    )
    parameters = {
        "L_mm": length,
        "L_max_mm": profile["L_max_mm"],
        "overall_support_envelope_mm": length + 100,
        "member_section": profile["member"]["source_spec"],
        "base_plate": profile["base_plate"],
    }
    result.warnings.extend(blockers)
    result.meta["type_id"] = "127"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": parameters,
    }
    result.evidence.append(
        make_evidence(
            "type127_d137_field_support",
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
