"""Type 85 source-aware D-80/D-80B pipe shoe.

D-105/D-106 add no separate insulation saddle.  They explicitly delegate the
pipe-shoe construction to the selected source's D-80/D-80B, so Type 85 reuses
the Type 66 fabrication engine and blocks only the unhardened branches.
"""

from __future__ import annotations

from .. import pipe_shoe_engine
from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("85", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 85: 尚未建立來源 profile {profile_id}"
        return result

    token, _ = extract_parts(get_part(fullstring, 2) or "")
    size = get_lookup_value(token)
    small = size in [float(value) for value in profile["small_sizes"]]
    large = size in [float(value) for value in profile["large_sizes"]]
    if not (small or large):
        result.error = f'Type 85 / {profile_id}: D-105/D-106 未表列 {size:g}"'
        return result

    drawing = profile["small_drawing"] if small else profile["large_drawing"]
    detail = "D-80" if small else "D-80B"
    try:
        base = pipe_shoe_engine.calculate(
            fullstring,
            "66",
            source_profile=profile_id,
        )
    except ValueError as exc:
        base = AnalysisResult(fullstring=fullstring, error=str(exc))

    if base.error:
        blocker = (
            f"{drawing} 明確引用 {detail}，但此來源/管徑的 {detail} 多片輪廓"
            f"尚未達加工 recipe：{base.error}"
        )
        add_reference(
            result,
            name=f"{detail} PIPE SHOE ASSEMBLY",
            spec=f'SEE {detail}; SIZE={size:g}"',
            material="PER D-80 TABLE A / PIPE MATERIAL",
            quantity=1,
            category="鋼板類",
            component_id=f"D{profile['large_detail_no' if large else 'small_detail_no']}-{detail.replace('-', '')}-ASSEMBLY-REFERENCE",
            drawing=drawing,
            revision=profile["revision"],
            shape_kind="pipe_shoe_assembly_reference",
            parameters={"line_size_in": size, "source_detail": detail},
            blocker=blocker,
        )
        blockers = [blocker]
    else:
        for entry in base.entries:
            entry.geometry.parameters["parent_type"] = "85"
            entry.geometry.parameters["parent_drawing"] = drawing
            result.add_entry(entry)
        result.warnings.extend(base.warnings)
        result.evidence.extend(base.evidence)
        blockers = list(base.meta.get("fabrication", {}).get("blockers", []))

    result.warnings.extend(item for item in blockers if item not in result.warnings)
    result.meta["type_id"] = "85"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": detail,
        "bom_ready": not blockers and not base.error,
        "fabrication_ready": not blockers and not base.error,
        "blockers": blockers,
        "assembly_dimensions": {"line_size_in": size, "source_detail": detail},
    }
    result.evidence.append(
        make_evidence(
            "type85_delegated_pipe_shoe",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
