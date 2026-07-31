"""
Type 42 計算器 — Trunnion 曲面設備斜撐支撐 (D-50)
格式: 42-{line_size}B-{MEMBER}-{H} {A|B}

H = F - √(R² - E²)  (圓弧反算)
G = g_coeff × H + g_offset (斜撐長)

BOM (5 筆): ① 主梁(H) ② 斜撐(G) ③ Trunnion ④ C/S Shim ⑤ M.B.
"""
from ..bolt import add_custom_entry
from ..config_loader import load_config
from ..models import AnalysisResult, set_remark
from ..source_profiles import normalize_source_profile
from ..truth import make_evidence
from ..trunnion_engine import (
    parse_inputs,
    add_cs_shim,
    STRUCTURAL_MATERIAL,
    SUPPORT_PIPE_MATERIAL,
    ANCHOR_BOLT_MATERIAL,
)
from ..steel import add_steel_section_entry
from data.type42_table import get_type42_member, get_type42_pipe


def calculate(fullstring: str, overrides=None, source_profile=None) -> AnalysisResult:
    config = load_config("42", strict=True)
    profile_id = normalize_source_profile(source_profile)
    profile = config["source_profiles"].get(profile_id)
    if not profile:
        result = AnalysisResult(fullstring=fullstring)
        result.error = f"Type 42: 尚未建立來源 profile {profile_id}"
        return result
    inputs, err = parse_inputs(
        fullstring,
        type_label="Type 42",
        get_pipe_fn=get_type42_pipe,
        get_member_fn=get_type42_member,
        get_h_max_fn=lambda code: get_type42_member(code)["H_MAX"] if get_type42_member(code) else None,
    )
    if err:
        return err

    result = AnalysisResult(fullstring=fullstring)
    if inputs._h_warning:
        result.error = f"Type 42 / {profile_id}: {inputs._h_warning}"
        return result

    # 計算斜撐長度 G
    fig_formula = inputs.member_data.get(inputs.fig_type)
    if not fig_formula:
        result.error = f"Type 42: FIG-{inputs.fig_type} 無效 (A=30°, B=45°)"
        return result
    g_val = round(fig_formula["g_coeff"] * inputs.h_mm + fig_formula["g_offset"])

    trunnion_spec = inputs.pipe_data["trunnion"]
    E = inputs.pipe_data["E"]

    drawing = profile["drawing"]
    blockers = [
        "Trunnion只指定公稱管徑，材質/管厚(schedule)/切長需依D-72/73/74核定",
        "斜撐兩端切角/貼合輪廓未在D-50完整尺寸化",
    ]
    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            inputs.h_mm, material=STRUCTURAL_MATERIAL)
    main = result.entries[-1]
    main.geometry.component_id = "D50-MAIN-BEAM"
    main.geometry.source_drawing = drawing
    main.geometry.source_revision = profile["revision"]
    main.geometry.shape_kind = "stock_section_cut"
    main.geometry.formula = "H"
    main.geometry.parameters = {"H_mm": inputs.h_mm}
    main.geometry.fabrication_ready = True
    set_remark(main, f"主梁H={inputs.h_mm}mm")

    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            g_val, material=STRUCTURAL_MATERIAL)
    brace = result.entries[-1]
    brace.geometry.component_id = "D50-BRACE"
    brace.geometry.source_drawing = drawing
    brace.geometry.source_revision = profile["revision"]
    brace.geometry.shape_kind = "stock_section_cut"
    brace.geometry.formula = "G(member,H,figure)"
    brace.geometry.parameters = {
        "G_mm": g_val, "H_mm": inputs.h_mm,
        "figure": inputs.fig_type, "theta_deg": inputs.theta,
    }
    brace.geometry.fabrication_ready = False
    brace.geometry.fabrication_blockers = [blockers[1]]
    set_remark(brace, f"斜撐FIG-{inputs.fig_type}，G={g_val}mm")

    add_custom_entry(
        result, name="TRUNNION", spec=trunnion_spec,
        material=SUPPORT_PIPE_MATERIAL, quantity=1, unit_weight=0, unit="PC",
    )
    trunnion = result.entries[-1]
    trunnion.geometry.component_id = "D50-TRUNNION"
    trunnion.geometry.source_drawing = drawing
    trunnion.geometry.source_revision = profile["revision"]
    trunnion.geometry.shape_kind = "partially_specified_pipe"
    trunnion.geometry.parameters = {
        "nominal_pipe_size": trunnion_spec, "E_mm": E,
        "schedule": None, "cut_length_mm": None,
    }
    trunnion.geometry.fabrication_ready = False
    trunnion.geometry.fabrication_blockers = [blockers[0]]

    add_cs_shim(result, inputs.member_data["C"], inputs.member_data["D"])
    shim = result.entries[-1]
    shim.geometry.component_id = "D50-CS-SHIM"
    shim.geometry.source_drawing = drawing
    shim.geometry.source_revision = profile["revision"]
    shim.geometry.shape_kind = "rectangular_plate"
    shim.geometry.fabrication_ready = True

    add_custom_entry(
        result, name="M.BOLT", spec='3/4"x50',
        material=ANCHOR_BOLT_MATERIAL, quantity=2, unit_weight=0, unit="PC",
    )
    bolt = result.entries[-1]
    bolt.geometry.component_id = "D50-M-BOLT"
    bolt.geometry.source_drawing = drawing
    bolt.geometry.source_revision = profile["revision"]
    bolt.geometry.shape_kind = "purchased_fastener"
    bolt.geometry.parameters = {"spec": '3/4"x50', "quantity": 2, "hole_diameter_mm": 22}
    bolt.geometry.fabrication_ready = True

    result.meta["fabrication"] = {
        "source_profile": profile_id,
        "source_drawing": drawing,
        "source_revision": profile["revision"],
        "branch": f"{inputs.member_code}/FIG-{inputs.fig_type}",
        "bom_ready": False,
        "fabrication_ready": False,
        "blockers": blockers,
        "G_mm": g_val,
        "trunnion_nominal_size": trunnion_spec,
    }
    result.warnings.extend(blockers)
    result.evidence.extend(
        [
            make_evidence("type42_member_row", inputs.member_data, "visual_transcription", source=drawing, confidence=0.99),
            make_evidence("type42_pipe_row", inputs.pipe_data, "visual_transcription", source=drawing, confidence=0.99),
        ]
    )
    return result
