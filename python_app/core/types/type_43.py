"""Type 43 source-aware trunnion/lug vessel support (D-51/D-52)."""
from __future__ import annotations

from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..plate import add_plate_entry
from ..source_profiles import normalize_source_profile
from ..steel import add_steel_section_entry
from ..truth import make_evidence
from ..trunnion_engine import (
    ANCHOR_BOLT_MATERIAL,
    PLATE_LUG_MATERIAL,
    STRUCTURAL_MATERIAL,
    SUPPORT_PIPE_MATERIAL,
    add_cs_shim,
    parse_inputs,
)
from ._lug_plate_common import lug_hole_count
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member
from data.type43_table import get_type43_data, get_type43_formula, get_type43_h_max, get_type43_pipe


def _add_lug(result, lug, label, component_id, drawing, bolt_spec):
    holes = lug_hole_count(lug)
    add_plate_entry(
        result, lug["A"], lug["B"], lug["T"], f"LUG PLATE {label}",
        material=PLATE_LUG_MATERIAL, plate_role="lug_plate",
        bolt_switch=True, bolt_x=2 * lug["E"] + lug["F"],
        bolt_y=2 * (lug.get("G") or 0), bolt_hole=lug["J"],
        bolt_size=bolt_spec,
    )
    entry = result.entries[-1]
    entry.geometry.component_id = component_id
    entry.geometry.source_drawing = drawing
    entry.geometry.source_revision = "1"
    entry.geometry.shape_kind = "standard_lug_plate"
    entry.geometry.shape_spec = (
        f'{lug["type"]}; {lug["A"]}x{lug["B"]}x{lug["T"]}t; '
        f'{holes}-HOLE DIA{lug["J"]}'
    )
    entry.geometry.holes.count = holes
    entry.geometry.parameters.update(
        {
            "lgp_type": lug["type"], "hole_count": holes,
            "E_mm": lug["E"], "F_mm": lug["F"],
            "G_mm": lug.get("G"), "H_mm": lug.get("H"),
        }
    )
    entry.geometry.fabrication_ready = True
    return holes


def calculate(fullstring, overrides=None, source_profile=None):
    config = load_config("43", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"Type 43: 尚未建立來源 profile {profile_id}"
        return result
    inputs, err = parse_inputs(
        fullstring, type_label="Type 43",
        get_pipe_fn=get_type43_pipe, get_member_fn=get_type43_data,
        get_h_max_fn=get_type43_h_max,
    )
    if err:
        return err
    result = AnalysisResult(fullstring=fullstring)
    if inputs._h_warning:
        result.error = f"Type 43 / {profile_id}: {inputs._h_warning}"
        return result
    formula = get_type43_formula(inputs.member_code, inputs.fig_type)
    if not formula:
        result.error = f"Type 43: 無 {inputs.member_code} FIG-{inputs.fig_type} 公式"
        return result
    m34 = get_m34_by_member(inputs.member_code)
    mz = (
        get_m36_by_member(inputs.member_code)
        if inputs.fig_type == "A"
        else get_m35_by_member(inputs.member_code)
    )
    if not m34 or not mz:
        result.error = f"Type 43: M-34/M-35/36缺少 {inputs.member_code}"
        return result
    s_mm = round(formula["s_coeff"] * inputs.h_mm + formula["s_offset"])
    n_mm = round(formula["n_coeff"] * inputs.h_mm + formula["n_offset"])
    main_len = inputs.h_mm + inputs.member_data["A"]
    drawing = " / ".join(profile["drawings"])
    blockers = ["斜撐兩端切角/貼合輪廓未在D-51/D-52完整尺寸化"]
    if profile["trunnion_furnished"]:
        blockers.append("Trunnion材質/管厚(schedule)/切長需依D-72/73/74核定")

    for cid, role, length, formula_text in (
        ("D51-MAIN-BEAM", "主梁", main_len, "H + A"),
        ("D51-BRACE", "斜撐", n_mm, "N(member,H,figure)"),
    ):
        add_steel_section_entry(
            result, inputs.section_type, inputs.section_dim, length,
            material=STRUCTURAL_MATERIAL,
        )
        entry = result.entries[-1]
        entry.geometry.component_id = cid
        entry.geometry.source_drawing = drawing
        entry.geometry.source_revision = profile["revision"]
        entry.geometry.shape_kind = "stock_section_cut"
        entry.geometry.formula = formula_text
        entry.geometry.parameters = {
            "H_mm": inputs.h_mm, "S_mm": s_mm, "N_mm": n_mm,
            "figure": inputs.fig_type, "theta_deg": inputs.theta,
        }
        entry.geometry.fabrication_ready = cid == "D51-MAIN-BEAM"
        if cid == "D51-BRACE":
            entry.geometry.fabrication_blockers = [blockers[0]]
        set_remark(entry, f"{role}，下料長度{length}mm")

    if profile["trunnion_furnished"]:
        add_custom_entry(
            result, name="TRUNNION", spec=inputs.pipe_data["trunnion"],
            material=SUPPORT_PIPE_MATERIAL, quantity=1, unit_weight=0, unit="PC",
        )
        trunnion = result.entries[-1]
        trunnion.geometry.component_id = "D51-TRUNNION"
        trunnion.geometry.source_drawing = drawing
        trunnion.geometry.source_revision = profile["revision"]
        trunnion.geometry.shape_kind = "partially_specified_pipe"
        trunnion.geometry.parameters = {
            "nominal_pipe_size": inputs.pipe_data["trunnion"],
            "schedule": None, "cut_length_mm": None,
        }
        trunnion.geometry.fabrication_ready = False
        trunnion.geometry.fabrication_blockers = [blockers[-1]]

    y_holes = _add_lug(
        result, m34, "TYPE-C", f'M34-{m34["type"]}',
        "LUG-PLATE_TYPE-C_M-34.pdf", profile["bolt_spec"],
    )
    z_label = "TYPE-E" if inputs.fig_type == "A" else "TYPE-D"
    z_ref = "M36" if inputs.fig_type == "A" else "M35"
    z_holes = _add_lug(
        result, mz, z_label, f'{z_ref}-{mz["type"]}',
        f"LUG-PLATE_{z_label}_{z_ref}.pdf", profile["bolt_spec"],
    )
    bolt_qty = y_holes + z_holes
    add_custom_entry(
        result, name="K BOLT", spec=profile["bolt_spec"],
        material=ANCHOR_BOLT_MATERIAL, quantity=bolt_qty,
        unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D51-K-BOLT"
    bolt.geometry.source_drawing = drawing
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": profile["bolt_spec"], "quantity": bolt_qty}
    bolt.geometry.fabrication_ready = True

    add_cs_shim(result, inputs.member_data["C"], formula["B"])
    shim = result.entries[-1]
    shim.geometry.component_id = "D51-CS-SHIM"
    shim.geometry.source_drawing = drawing
    shim.geometry.source_revision = profile["revision"]
    shim.geometry.shape_kind = "rectangular_plate"
    shim.geometry.fabrication_ready = True

    bom_ready = not profile["trunnion_furnished"]
    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"{inputs.member_code}/FIG-{inputs.fig_type}",
        "bom_ready": bom_ready,
        "fabrication_ready": False,
        "blockers": blockers,
        "not_furnished": [] if profile["trunnion_furnished"] else ["TRUNNION PIPE"],
        "S_mm": s_mm,
        "N_mm": n_mm,
        "bolt_quantity": bolt_qty,
    }
    if not profile["trunnion_furnished"]:
        result.warnings.append("20E D-51明註TRUNNION PIPE NOT FURNISHED，已排除BOM")
    result.warnings.extend(blockers)
    result.evidence.extend(
        [
            make_evidence("type43_member_row", inputs.member_data, "visual_transcription", source=drawing, confidence=0.99),
            make_evidence("type43_formula", formula, "visual_transcription", source=drawing, confidence=0.99),
        ]
    )
    return result
