"""
Type 42 計算器 — Trunnion 曲面設備斜撐支撐 (D-50)
格式: 42-{line_size}B-{MEMBER}-{H} {A|B}

H = F - √(R² - E²)  (圓弧反算)
G = g_coeff × H + g_offset (斜撐長)

BOM (5 筆): ① 主梁(H) ② 斜撐(G) ③ Trunnion ④ C/S Shim ⑤ M.B.
"""
from ..models import AnalysisResult
from ..trunnion_engine import (
    parse_inputs,
    add_trunnion,
    add_cs_shim,
    add_bolt_set,
    STRUCTURAL_MATERIAL,
)
from ..steel import add_steel_section_entry
from data.type42_table import get_type42_member, get_type42_pipe


def calculate(fullstring: str) -> AnalysisResult:
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
        result.warnings.append(inputs._h_warning)

    # 計算斜撐長度 G
    fig_formula = inputs.member_data.get(inputs.fig_type)
    if not fig_formula:
        result.error = f"Type 42: FIG-{inputs.fig_type} 無效 (A=30°, B=45°)"
        return result
    g_val = round(fig_formula["g_coeff"] * inputs.h_mm + fig_formula["g_offset"])

    trunnion_spec = inputs.pipe_data["trunnion"]
    E = inputs.pipe_data["E"]

    # ① 主梁 — length = H
    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            inputs.h_mm, material=STRUCTURAL_MATERIAL)
    result.entries[-1].remark = f"主梁 (立柱), H={inputs.h_mm}mm"

    # ② 斜撐 — length = G
    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            g_val, material=STRUCTURAL_MATERIAL)
    result.entries[-1].remark = f"斜撐 FIG-{inputs.fig_type}(θ={inputs.theta}°), G={g_val}mm"

    # ③ Trunnion
    add_trunnion(result, trunnion_spec,
                 f"Trunnion {trunnion_spec}, E={E}mm, 需 D-72/73/74 校核")

    # ④ C/S Shim
    add_cs_shim(result, inputs.member_data["C"], inputs.member_data["D"])

    # ⑤ M.B. (3/4"×50)
    add_bolt_set(result, "M.BOLT", '3/4"x50', 2, remark="Ø22 孔固定")

    return result
