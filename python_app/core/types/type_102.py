"""Type 102 D-111 E-plate interface to an existing member."""

from __future__ import annotations

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
    config = load_config("102", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 102: 尚未建立來源 profile {profile_id}"
        return result

    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    figure = (get_part(fullstring, 3) or "").upper()
    row = profile["rows"].get(f"{size:g}")
    if not row:
        result.error = f'Type 102 / {profile_id}: D-111 未表列 {size:g}"'
        return result
    if figure not in {"A", "B"}:
        result.error = "Type 102 格式應為 102-{LINE}B-{A|B}"
        return result

    blocker = (
        "D-111 只給 E-plate 厚度、W weld 與 40/50/60/75/G 等組立 offsets；"
        "E-plate 的完整平面輪廓、分片邊界及與 D-80 shoe 的實際 bearing "
        "layout 未唯一標出，不能由 100/80 外框直接算重量"
    )
    parameters = {
        "line_size_in": size,
        "figure": figure,
        "plate_thickness_E_mm": row["E"],
        "fillet_weld_W_mm": row["W"],
        "typical_gap_mm": 3,
        "d80_bearing_width_mm": 80,
        "overall_bearing_width_mm": 100,
        "right_edge_offset_mm": 60,
        "pipe_side_offset_mm": 40 if figure == "A" else 75,
        "adjacent_offset_mm": 50,
        "G_mm": None if figure == "A" else 50,
        "not_furnished": ["D-80 pipe shoe", "existing member"],
    }
    add_reference(
        result,
        name="E-PLATE INTERFACE SET",
        spec=f'{row["E"]}t; W={row["W"]}; FIG-{figure}',
        material="A36/SS400",
        quantity=1,
        category="鋼板類",
        component_id="D111-E-PLATE-INTERFACE-SET",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="pipe_shoe_interface_plate_set",
        parameters=parameters,
        blocker=blocker,
        manufacturing_type="plate_cut",
    )
    result.warnings.append(blocker)
    result.meta["type_id"] = "102"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker],
        "not_furnished": parameters["not_furnished"],
        "assembly_dimensions": parameters,
    }
    result.evidence.append(
        make_evidence(
            "type102_d111_row",
            parameters,
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
