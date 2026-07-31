"""Type 125 I-Rod clamp support (D-135)."""

from __future__ import annotations

import math

from ..config_loader import load_config
from ..fastener_weight import (
    STEEL_DENSITY_KG_PER_MM3,
    estimate_u_bolt_assembly,
)
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
    overrides = overrides or {}
    config = load_config("125", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result.error = f"Type 125: 尚未建立來源 profile {profile_id}"
        return result
    size = get_lookup_value((get_part(fullstring, 2) or "").replace("B", ""))
    row = profile["rows"].get(f"{size:g}")
    if not row:
        result.error = f'Type 125: D-135 未表列 {size:g}"'
        return result

    count_raw = overrides.get("i_rod_count")
    count = None
    if count_raw not in (None, ""):
        try:
            count = int(count_raw)
        except (TypeError, ValueError):
            count = 0
        if count not in {1, 2, 3}:
            result.error = "Type 125: i_rod_count 必須為 1、2 或 3"
            return result
    temperature_class = str(
        overrides.get("i_rod_temperature_class") or ""
    ).strip().lower()
    if temperature_class and temperature_class not in profile["temperature_classes"]:
        result.error = (
            "Type 125: i_rod_temperature_class 必須為 "
            f"{sorted(profile['temperature_classes'])}"
        )
        return result

    drawing = profile["drawing"]
    revision = profile["revision"]
    count_blocker = (
        "D-135 allows one to three parallel I-Rods with evenly shared load；"
        "designation does not encode piece count，需以 i_rod_count 明選"
        if count is None
        else ""
    )
    class_blocker = (
        "D-135 lists Regular/High Temp/PEEK temperature limits，"
        "designation does not select the I-Rod material class"
        if not temperature_class
        else ""
    )
    ubolt_blocker = (
        "D-135 provides d1/L/P/thread-length A and tightening torque；"
        "U-bolt rod and the two nuts visibly shown are included by theoretical "
        "carbon-steel estimate，but finished U-bolt material, nut grade and "
        "supplier unit-weight remain high-risk procurement confirmations"
    )
    common_blockers = [
        item for item in (count_blocker, class_blocker) if item
    ]
    ubolt_blockers = [
        item for item in (count_blocker, ubolt_blocker) if item
    ]
    piece_count = count if count is not None else 1
    ubolt = add_reference(
        result,
        name="D-135 U-BOLT / NUT ASSEMBLY",
        spec=(
            f"d1={row['bolt_diameter']}; L={row['bolt_leg_L_mm']}; "
            f"P={row['span_P_mm']}; A={row['thread_A_mm']}; "
            f"QTY={count if count is not None else 'TBD'}"
        ),
        material="NOT SPECIFIED IN D-135",
        quantity=piece_count,
        category="螺栓類",
        component_id="D135-U-BOLT-ASSEMBLY",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_u_bolt_i_rod_clamp",
        parameters={
            "line_size_in": size,
            "pipe_od_D_mm": row["pipe_od_D_mm"],
            "bolt_diameter_d1": row["bolt_diameter"],
            "bolt_leg_L_mm": row["bolt_leg_L_mm"],
            "span_P_mm": row["span_P_mm"],
            "thread_length_A_mm": row["thread_A_mm"],
            "tightening_torque_Nm": row["tightening_torque_Nm"],
            "piece_count": count,
        },
        blocker="；".join(ubolt_blockers),
        manufacturing_type="purchased",
    )
    rod_diameter_mm = (
        get_lookup_value(str(row["bolt_diameter"]).replace("in", ""))
        * 25.4
    )
    # D-135 dimensions L from the rod crown outside to the cut end and P
    # between leg centre-lines.  Centre-line development therefore removes
    # half P plus half d1 from each overall leg before adding the 180deg arc.
    straight_leg_mm = (
        row["bolt_leg_L_mm"]
        - row["span_P_mm"] / 2
        - rod_diameter_mm / 2
    )
    developed_length_mm = (
        math.pi * row["span_P_mm"] / 2
        + 2 * straight_leg_mm
    )
    ubolt_estimate = estimate_u_bolt_assembly(
        rod_diameter_mm,
        developed_length_mm,
        nut_count=2,
        density_kg_per_mm3=STEEL_DENSITY_KG_PER_MM3,
    )
    ubolt.unit_weight = ubolt_estimate["unit_weight_kg"]
    ubolt.total_weight = round(ubolt.unit_weight * ubolt.quantity, 2)
    ubolt.weight_output = round(ubolt.factor * ubolt.total_weight, 2)
    ubolt.length = developed_length_mm
    ubolt.density_g_cm3 = STEEL_DENSITY_KG_PER_MM3 * 1e6
    ubolt.density_source = (
        "core.fastener_weight.source_derived_u_bolt_estimate"
    )
    ubolt.density_requires_review = True
    ubolt.geometry.parameters.update(
        {
            "rod_diameter_d1_mm": rod_diameter_mm,
            "span_P_basis": "leg centre-line spacing",
            "overall_L_basis": "rod crown outside to cut end",
            "straight_leg_centerline_mm": straight_leg_mm,
            "developed_length_formula": (
                "PI*P/2 + 2*(L - P/2 - d1/2)"
            ),
            "developed_length_mm": developed_length_mm,
            "nut_quantity_visibly_shown": 2,
            "weight_estimate": ubolt_estimate,
        }
    )

    rod_class = (
        profile["temperature_classes"][temperature_class]
        if temperature_class
        else {
            "label": "THERMOPLASTIC CLASS TBD",
            "maximum_temperature_C": None,
        }
    )
    irod_blocker = (
        "D-135 gives I-Rod F/H/I and hole diameter G，but not the "
        "two hole-center offsets, toothed extrusion net profile/density, "
        "or supplier unit-weight；尺寸可採購，不能自算重量/加工孔位"
    )
    irod_blockers = [*common_blockers, irod_blocker]
    add_reference(
        result,
        name="D-135 I-ROD SUPPORT",
        spec=(
            f"{row['i_rod_H_in']}in I-ROD; "
            f"F={row['i_rod_F_mm']}; I={row['i_rod_I_mm']}; "
            f"2-G={row['hole_G']}; QTY={count if count is not None else 'TBD'}"
        ),
        material=rod_class["label"],
        quantity=piece_count,
        category="墊片類",
        component_id="D135-I-ROD",
        drawing=drawing,
        revision=revision,
        shape_kind="purchased_toothed_thermoplastic_i_rod",
        parameters={
            "line_size_in": size,
            "piece_count": count,
            "length_F_mm": row["i_rod_F_mm"],
            "nominal_width_H_in": row["i_rod_H_in"],
            "nominal_width_H_mm": row["i_rod_H_in"] * 25.4,
            "height_I_mm": row["i_rod_I_mm"],
            "hole_diameter_G": row["hole_G"],
            "hole_count": 2,
            "hole_center_offsets_mm": None,
            "temperature_class": temperature_class or None,
            "maximum_temperature_C": rod_class["maximum_temperature_C"],
            "single_point_load_limit_kg": row["single_point_load_limit_kg"],
        },
        blocker="；".join(irod_blockers),
        manufacturing_type="purchased",
    )

    blockers = [*common_blockers, ubolt_blocker, irod_blocker]
    result.warnings.extend(blockers)
    parameters = {
        "line_size_in": size,
        "pipe_od_D_mm": row["pipe_od_D_mm"],
        "i_rod_count": count,
        "temperature_class": temperature_class or None,
        "maximum_parallel_i_rods": 3,
        "equal_load_sharing_required": True,
        **row,
    }
    result.meta["type_id"] = "125"
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": revision,
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "assembly_dimensions": parameters,
        "u_bolt_theoretical_weight_ready": True,
        "not_furnished": ["existing support steel/plate"],
    }
    result.evidence.append(
        make_evidence(
            "type125_d135_row",
            parameters,
            "visual_transcription",
            source=drawing,
            confidence=0.99,
        )
    )
    return result
