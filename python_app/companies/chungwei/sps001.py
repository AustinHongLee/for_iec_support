"""E25-24 special-support list SPS-001 (E2524-SPS-001 Rev.0)."""

from __future__ import annotations

from companies.changchun.calculators import _hardware, _plate, _section
from core.component_roles import ComponentRole
from core.models import AnalysisResult
from core.truth import apply_truth_contract, make_evidence


def calculate(parsed: dict, config: dict, overrides: dict) -> AnalysisResult:
    result = AnalysisResult(fullstring=parsed["raw"])
    row = config["members"][parsed["member"]]
    nominal_h = int(parsed["H"])
    nominal_l = int(parsed["L"])
    if nominal_h <= 0 or nominal_h > row["H_max_mm"]:
        result.error = (
            f"SPS-001 {parsed['member']}: H必須 0 < H <= {row['H_max_mm']} mm"
        )
        return result
    if nominal_l <= 0 or nominal_l > row["L_max_mm"]:
        result.error = (
            f"SPS-001 {parsed['member']}: L必須 0 < L <= {row['L_max_mm']} mm"
        )
        return result

    final_h = overrides.get("final_h_mm")
    final_l = overrides.get("final_l_mm")
    cut_h = float(final_h) if final_h not in (None, "") else nominal_h
    cut_l = float(final_l) if final_l not in (None, "") else nominal_l
    field_blockers = []
    if final_h in (None, ""):
        field_blockers.append(
            "SPS-001註記H須現場配切；正式加工圖需回填 final_h_mm"
        )
    if final_l in (None, ""):
        field_blockers.append(
            "SPS-001註記FIELD TO CUT LENGTH AS REQUIRED；正式加工圖需回填 final_l_mm"
        )
    drawing = config["drawing"]
    revision = config["revision"]
    approved_weight = overrides.get("member_weight_kg_m")
    standard_weight = row.get("weight_kg_m")
    weight = (
        float(approved_weight)
        if approved_weight not in (None, "")
        else standard_weight
    )
    _section(
        result,
        section_type=row["section_type"],
        spec=row["lookup_spec"],
        length=cut_h,
        quantity=1,
        material="A36",
        name="垂直構件 M",
        component_id="E2524-SPS-001-VERTICAL-M",
        drawing=drawing,
        revision=revision,
        parameters={
            "source_spec": row["source_spec"],
            "nominal_H_mm": nominal_h,
            "field_cut_confirmed": final_h not in (None, ""),
        },
        ready=final_h not in (None, ""),
        blockers=[] if final_h not in (None, "") else field_blockers[:1],
        weight_kg_m=weight,
    )
    _section(
        result,
        section_type=row["section_type"],
        spec=row["lookup_spec"],
        length=cut_l,
        quantity=1,
        material="A36",
        name="水平構件 M",
        component_id="E2524-SPS-001-HORIZONTAL-M",
        drawing=drawing,
        revision=revision,
        parameters={
            "source_spec": row["source_spec"],
            "nominal_L_mm": nominal_l,
            "field_cut_confirmed": final_l not in (None, ""),
            "pipe_center_from_end_mm": 100,
        },
        ready=final_l not in (None, ""),
        blockers=[] if final_l not in (None, "") else field_blockers[-1:],
        weight_kg_m=weight,
    )
    if parsed["fix"] == "B":
        _plate(
            result,
            name="固定板",
            a=265,
            b=175,
            thickness=12,
            quantity=1,
            material="A283 Gr.C",
            component_id="E2524-SPS-001-FIXING-PLATE",
            drawing=drawing,
            revision=revision,
            hole={
                "count": 4,
                "diameter": 19,
                "pitch_x": 195,
                "pitch_y": 105,
                "fastener": "M16x50L",
            },
            role=ComponentRole.BASE_PLATE.value,
        )
        _hardware(
            result,
            name="螺栓連帽",
            spec="M16x50L",
            material="A307 Gr.B",
            quantity=4,
            role=ComponentRole.MACHINE_BOLT.value,
            component_id="E2524-SPS-001-BOLTS",
            drawing=drawing,
            revision=revision,
        )

    weight_blockers = []
    if weight is None:
        weight_blockers.append(
            f"{row['source_spec']}圖面未給可核定每米重；請以member_weight_kg_m覆寫後再作總重"
        )
    if parsed["fix"] == "B":
        weight_blockers.append(
            "M16x50螺栓連帽已列理論估重；供應商成品重量待確認"
        )
    warnings = [*field_blockers, *weight_blockers]
    result.warnings.extend(warnings)
    assembly = {
        "member": parsed["member"],
        "source_spec": row["source_spec"],
        "nominal_H_mm": nominal_h,
        "nominal_L_mm": nominal_l,
        "cut_H_mm": cut_h,
        "cut_L_mm": cut_l,
        "fix": parsed["fix"],
        "H_max_mm": row["H_max_mm"],
        "L_max_mm": row["L_max_mm"],
        "plate_mm": [265, 175, 12] if parsed["fix"] == "B" else None,
    }
    result.meta["fabrication"] = {
        "source_profile": "cw_e25_24_hp6",
        "source_drawing": drawing,
        "source_file": config["source_file"],
        "source_revision": revision,
        "branch": parsed["fix"],
        "bom_ready": True,
        "weight_complete": not weight_blockers,
        "fabrication_ready": not field_blockers,
        "blockers": field_blockers,
        "weight_blockers": weight_blockers,
        "assembly_dimensions": assembly,
    }
    result.meta["config_version"] = str(config.get("version") or "?")
    result.meta["config_updated"] = str(config.get("data_updated_at") or "")
    result.evidence.append(
        make_evidence(
            "sps001_e2524",
            assembly,
            "visual_transcription",
            source=f"{drawing} / {config['source_file']}",
            confidence=0.99,
            note="E25-24 Rev.0 FOR CONSTRUCTION逐頁渲染轉錄",
        )
    )
    apply_truth_contract(
        result,
        type_id="SPS-001",
        review_reasons=warnings,
    )
    return result
