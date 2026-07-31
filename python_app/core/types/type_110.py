"""Type 110 site-fit ditch support (20E D-123)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("110", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 110: 尚未建立來源 profile {profile_id}"
        return result
    token = (get_part(fullstring, 2) or "").upper()
    if len(token) < 2 or token[-1] not in {"A", "B"} or not token[:-1].isdigit():
        result.error = "Type 110 格式應為 110-{L/100}{A|B}"
        return result
    length = int(token[:-1]) * 100
    figure = token[-1]
    if length <= 0:
        result.error = "Type 110: L 必須大於 0"
        return result

    spec = (
        "CUT FROM H200x200x8x12 + EMBEDDED L25/L40"
        if figure == "A"
        else "L50x50x6 + EMBEDDED STEEL PLATES"
    )
    blocker = (
        "D-123 NOTE 2 明定 assembly dimensions suit by site；ditch opening、"
        "embedded angle/plate scope、T-section piece count、bearing/end embedment "
        "與 civil interface 未由 designation L 唯一決定，不能把 L 直接當完整下料組"
    )
    parameters = {
        "figure": figure,
        "ditch_clear_span_L_mm": length,
        "source_member_spec": spec,
        "section_A_cut_from": (
            "H200x200x8x12" if figure == "A" else None
        ),
        "figure_B_angle": "L50x50x6" if figure == "B" else None,
        "embedded_angle_options": ["L25", "L40"],
        "site_fit": True,
    }
    add_reference(
        result,
        name="DITCH SUPPORT SITE-FIT ASSEMBLY",
        spec=spec,
        material="A36/SS400",
        quantity=1,
        category="型鋼類",
        component_id=f"D123-FIG-{figure}-DITCH-SUPPORT",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="site_fit_ditch_support",
        parameters=parameters,
        blocker=blocker,
        manufacturing_type="assembled",
    )
    result.warnings.append(blocker)
    result.meta["type_id"] = "110"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker],
        "assembly_dimensions": parameters,
    }
    result.evidence.append(
        make_evidence(
            "type110_d123_site_branch",
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
