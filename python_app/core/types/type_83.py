"""Type 83 source-aware axial-stop pipe shoe (D-101/D-102)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import extract_parts, get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from . import type_80
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("83", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 83: 尚未建立來源 profile {profile_id}"
        return result

    token, _ = extract_parts(get_part(fullstring, 2) or "")
    size = get_lookup_value(token)
    base = type_80.calculate(
        fullstring,
        overrides=overrides,
        source_profile=profile_id,
    )
    if base.error:
        result.error = f"Type 83 / D-80 shoe subassembly: {base.error}"
        return result
    for entry in base.entries:
        entry.geometry.parameters["parent_type"] = "83"
        result.add_entry(entry)
    result.warnings.extend(base.warnings)
    result.evidence.extend(base.evidence)

    if size <= 24:
        drawing = profile["small_drawing"]
        detail_no = profile["small_detail_no"]
        stop_spec = profile["small_stop_spec"]
        blocker = (
            f"{drawing} 的 axial-stop 依管徑使用 L40/L50 與 9t plate；"
            "圖面未唯一標出每件沿管方向 cut length、完整片數及 fireproofing "
            "beam 選配尺寸，暫不把 TYP. 外框轉成重量"
        )
    else:
        drawing = profile["large_drawing"]
        detail_no = profile["large_detail_no"]
        stop_spec = profile["large_stop_spec"]
        blocker = (
            f"{drawing} 的 No.1~No.4 axial-stop/guide pieces 雖有部分規格與數量，"
            "仍缺依 resting-beam/fireproofing 尺寸決定的 plate 平面尺寸與 cut length；"
            "在 piece recipe 完成前維持零重量"
        )
    add_reference(
        result,
        name="AXIAL STOP ASSEMBLY",
        spec=stop_spec,
        material=profile["stop_material"],
        quantity=1,
        category="鋼板類",
        component_id=f"D{detail_no}-AXIAL-STOP-ASSEMBLY",
        drawing=drawing,
        revision=profile["revision"],
        shape_kind="multi_piece_axial_stop_assembly",
        parameters={
            "line_size_in": size,
            "source_detail": f"D-{detail_no}",
            "fireproofing_option": profile["fireproofing_option"],
        },
        blocker=blocker,
        manufacturing_type="plate_cut",
    )

    blockers = list(base.meta.get("fabrication", {}).get("blockers", []))
    blockers.append(blocker)
    result.warnings.append(blocker)
    result.meta["type_id"] = "83"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"D-{detail_no}",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "base_pipe_shoe": base.meta.get("fabrication", {}),
        "assembly_dimensions": {"line_size_in": size},
    }
    result.evidence.append(
        make_evidence(
            "type83_axial_stop_branch",
            {"line_size_in": size, "detail": f"D-{detail_no}"},
            "visual_transcription",
            source=drawing,
            confidence=0.98,
        )
    )
    return result
