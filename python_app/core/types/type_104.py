"""Type 104 spring-wedge support (D-113 referencing M-52)."""

from __future__ import annotations

from data.m52_table import get_m52_by_line_size

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("104", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 104: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    row = profile["rows"].get(f"{size:g}")
    m52 = get_m52_by_line_size(size)
    if not row or not m52:
        result.error = f'Type 104 / {profile_id}: D-113/M-52 未表列 {size:g}"'
        return result

    blocker = (
        "D-113 的 spring wedge 完整構件引用 M-52；M-52 有尺寸與 spring data，"
        "但沒有完整各件展開/finished assembly unit-weight。9x25 flat bar 的"
        "實際供貨邊界亦需 civil/foundation scope 確認"
    )
    parameters = {
        "line_size_in": size,
        **{f"d113_{key}_mm": value for key, value in row.items()},
        "m52_designation": m52["designation"],
        "m52_pipe_size": m52["pipe_size"],
        "m52_dimensions_mm": m52["dimensions_mm"],
        "m52_thread_size_J": m52["thread_size_j"],
        "m52_spring_data": m52["spring_data"],
        "clearance_mm": 6,
        "maximum_deflection_mm": 3,
        "foundation_flat_bar": "FB9x25; SCOPE/CUT LENGTH TBD",
    }
    add_reference(
        result,
        name="M-52 SPRING WEDGE ASSEMBLY",
        spec=f"{m52['designation']}; D-113 B={row['B']} C={row['C']} D={row['D']}",
        material="A53-B / A193 B7 / A229",
        quantity=1,
        category="彈簧類",
        component_id="D113-M52-SPRING-WEDGE-ASSEMBLY",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="spring_wedge_assembly",
        parameters=parameters,
        blocker=blocker,
        manufacturing_type="assembled",
    )
    result.warnings.append(blocker)
    result.meta["type_id"] = "104"
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
            "type104_d113_m52_lookup",
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.98,
        )
    )
    return result
