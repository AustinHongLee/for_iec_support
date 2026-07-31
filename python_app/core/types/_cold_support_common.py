"""Shared source-safe helpers for the DSP-500-006 cold-support family."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def load_cold_profile(
    result: AnalysisResult,
    type_id: str,
    source_profile: str | None,
) -> tuple[str, dict] | tuple[None, None]:
    config = load_config(type_id, strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type {type_id}: 尚未建立來源 profile {profile_id}"
        return None, None
    return profile_id, profile


def parse_positive_mm(token: object) -> int | None:
    value = str(token or "").strip()
    if not value.isdigit():
        return None
    parsed = int(value)
    return parsed if parsed > 0 else None


def parse_pipe_size(token: object) -> float | None:
    raw = str(token or "").strip().upper()
    if not raw.endswith("B"):
        return None
    size = get_lookup_value(raw[:-1])
    return size if size > 0 else None


def add_cold_reference(
    result: AnalysisResult,
    *,
    name: str,
    component_id: str,
    profile: dict,
    parameters: dict,
    blockers: list[str],
    spec: str = "PER SOURCE DRAWING AND REFERENCED C/N SHEETS",
) -> None:
    add_reference(
        result,
        name=name,
        spec=spec,
        material="MULTI-MATERIAL COLD-SUPPORT ASSEMBLY",
        quantity=1,
        category="冷保溫支撐類",
        component_id=component_id,
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="cold_support_assembly_reference",
        parameters=parameters,
        blocker="；".join(blockers),
        manufacturing_type="assembly",
    )


def finalize_cold_result(
    result: AnalysisResult,
    *,
    type_id: str,
    profile_id: str,
    profile: dict,
    parameters: dict,
    blockers: list[str],
    evidence_key: str,
    bom_ready: bool = False,
) -> AnalysisResult:
    result.warnings.extend(blockers)
    result.meta["type_id"] = type_id
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "drawing_standard": profile["drawing_standard"],
        "bom_ready": bom_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": parameters,
    }
    result.evidence.append(
        make_evidence(
            evidence_key,
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
