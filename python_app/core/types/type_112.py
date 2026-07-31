"""Type 112 valve support for non-ferrous pipe (D-125)."""

from __future__ import annotations

from ..config_loader import load_config
from ..models import AnalysisResult
from ..parser import get_lookup_value, get_part
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ._source_reference import add_reference


def calculate(
    fullstring: str,
    overrides: dict | None = None,
    source_profile: str | None = None,
) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)
    config = load_config("112", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 112: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    row = profile["rows"].get(f"{size:g}")
    if not row:
        result.error = f'Type 112: D-125 未表列 {size:g}"'
        return result

    base_length = row["L"] + 50
    add_plate_entry(
        result,
        base_length,
        row["W"],
        row["T2"],
        "D-125 BASE PLATE",
        "A36/SS400",
        formula="(L+2*25)*W*T2",
        shape_spec=f"{base_length}x{row['W']}x{row['T2']}t",
        shape_kind="valve_support_base_plate",
    )
    base = result.entries[-1]
    base.geometry.component_id = "D125-BASE-PLATE"
    base.geometry.source_drawing = profile["drawing"]
    base.geometry.source_revision = profile["revision"]
    base.geometry.parameters = {
        "line_size_in": size,
        "table_L_mm": row["L"],
        "end_allowance_each_mm": 25,
        "cut_length_mm": base_length,
        "width_W_mm": row["W"],
        "thickness_T2_mm": row["T2"],
    }
    base.geometry.fabrication_ready = True

    blocker = (
        "D-125 的兩片 T1 valve-flange support plates 需 ANSI 150# "
        "實際 flange OD/bolt circle 與 machine-bolt hole layout；H/W 是組立外框，"
        "不可直接當無孔矩形板算重"
    )
    add_reference(
        result,
        name="VALVE-FLANGE SUPPORT PLATES",
        spec=f"2-PC {row['T1']}t; H={row['H']}; W={row['W']}",
        material="A36/SS400",
        quantity=2,
        category="鋼板類",
        component_id="D125-VALVE-FLANGE-SUPPORT-PLATES",
        drawing=profile["drawing"],
        revision=profile["revision"],
        shape_kind="flange_drilled_support_plate",
        parameters={
            "line_size_in": size,
            "piece_count": 2,
            "thickness_T1_mm": row["T1"],
            "assembly_H_mm": row["H"],
            "envelope_W_mm": row["W"],
            "flange_rating": "ANSI 150#",
            "machine_bolts": '2-3/8"x35 per detail',
        },
        blocker=blocker,
        manufacturing_type="shaped_plate",
    )
    result.warnings.append(blocker)
    result.meta["type_id"] = "112"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": profile["drawing"],
        "source_revision": profile["revision"],
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": [blocker],
        "assembly_dimensions": {
            "line_size_in": size,
            **row,
            "base_cut_length_mm": base_length,
        },
    }
    result.evidence.append(
        make_evidence(
            "type112_d125_row",
            result.meta["fabrication"]["assembly_dimensions"],
            "visual_transcription",
            source=profile["drawing"],
            confidence=0.99,
        )
    )
    return result
