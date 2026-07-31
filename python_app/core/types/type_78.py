"""Type 78 M-54 Fig.1 strap — D-93."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from data.m54_table import build_m54_item


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("78", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 78: 尚未建立來源 profile {profile_id}"
        return result

    token, anchor = extract_parts(get_part(fullstring, 2) or "")
    part3 = get_part(fullstring, 3)
    if part3 and part3.startswith("("):
        anchor = part3
    if not token:
        result.error = "Type 78 格式應為 78-{line_size}B[(A)]"
        return result
    line_size = get_lookup_value(token)
    strap = build_m54_item(line_size, fig_no=1)
    if not strap:
        result.error = f'Type 78: M-54 未表列 {line_size:g}"；範圍 3/4"~4"'
        return result

    dims = strap["dimensions_mm"]
    blocker = (
        "M-54 的 B 是成形後外側跨距；缺 flat development/bend allowance，"
        "禁止再以 B×C×T 當 STRAP 淨重"
    )
    add_custom_entry(
        result,
        "STRAP",
        strap["spec"],
        strap["material"],
        1,
        0,
        "PC",
        remark=blocker,
        category="鋼板類",
        item_class="reference_only",
        manufacturing_type="shaped_plate",
    )
    entry = result.entries[-1]
    entry.geometry.component_id = "D93-M54-FIG1-STRAP"
    entry.geometry.source_drawing = "TYPE-78_D-93.pdf / STRAP_M-54.pdf"
    entry.geometry.source_revision = profile["revision"]
    entry.geometry.shape_kind = "formed_pipe_strap"
    entry.geometry.shape_spec = (
        f'M-54 FIG.1; A={dims["A"]}; B={dims["B"]}; C={dims["C"]}; '
        f'T={dims["T"]}; H={dims["H"]}; R={dims["R"]}; D={dims["D"]}'
    )
    entry.geometry.parameters = {
        "line_size_in": line_size,
        "figure": 1,
        **dims,
        "anchor_option": bool(anchor),
        "anchor_weld_mm": 6 if anchor else None,
    }
    entry.geometry.fabrication_ready = False
    entry.geometry.fabrication_blockers = [blocker]
    set_remark(
        entry,
        blocker
        + ("；(A) 僅增加 D-93 6 mm anchor weld note，不增加另一零件" if anchor else ""),
    )

    result.warnings.append(blocker)
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker],
        "assembly_dimensions": entry.geometry.parameters,
    }
    result.evidence.append(
        make_evidence(
            "type78_d93_m54_dimensions",
            entry.geometry.parameters,
            "visual_transcription",
            source="TYPE-78_D-93.pdf / STRAP_M-54.pdf",
            confidence=0.99,
        )
    )
    return result
