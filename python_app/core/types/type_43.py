"""
Type 43 計算器 — Trunnion 曲面設備全約束支撐 (D-51, D-52)
格式: 43-{line_size}B-{MEMBER}-{H} {A|B}

H = K - √(R² - Q²) - t - E - 30
S/N 依公式表計算

BOM (7 筆): ① 主梁(H+A) ② 斜撐(N) ③ Trunnion ④ LUG PLATE TYPE-C (M-34)
            ⑤ LUG PLATE TYPE-D/E (M-35/36) ⑥ K BOLT ⑦ C/S Shim
"""
from ..models import AnalysisResult
from ..trunnion_engine import (
    parse_inputs,
    add_trunnion,
    add_cs_shim,
    add_bolt_set,
    STRUCTURAL_MATERIAL,
    PLATE_LUG_MATERIAL,
)
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from data.type43_table import (get_type43_data, get_type43_formula,
                                get_type43_pipe, get_type43_h_max)
from data.m34_table import get_m34_by_member
from data.m35_table import get_m35_by_member
from data.m36_table import get_m36_by_member


def calculate(fullstring: str) -> AnalysisResult:
    inputs, err = parse_inputs(
        fullstring,
        type_label="Type 43",
        get_pipe_fn=get_type43_pipe,
        get_member_fn=get_type43_data,
        get_h_max_fn=get_type43_h_max,
    )
    if err:
        return err

    result = AnalysisResult(fullstring=fullstring)
    if inputs._h_warning:
        result.warnings.append(inputs._h_warning)

    # 計算 S/N
    formula = get_type43_formula(inputs.member_code, inputs.fig_type)
    if not formula:
        result.error = f"Type 43: 無 {inputs.member_code} FIG-{inputs.fig_type} 公式"
        return result
    s_val = round(formula["s_coeff"] * inputs.h_mm + formula["s_offset"])
    n_val = round(formula["n_coeff"] * inputs.h_mm + formula["n_offset"])
    b_val = formula["B"]

    trunnion_spec = inputs.pipe_data["trunnion"]
    Q = inputs.pipe_data["Q"]
    main_len = inputs.h_mm + inputs.member_data["A"]

    # ① 主梁 — length = H + A
    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            main_len, material=STRUCTURAL_MATERIAL)
    result.entries[-1].remark = (
        f"主梁, H={inputs.h_mm}+A={inputs.member_data['A']}={main_len}mm"
    )

    # ② 斜撐 — length = N
    add_steel_section_entry(result, inputs.section_type, inputs.section_dim,
                            n_val, material=STRUCTURAL_MATERIAL)
    result.entries[-1].remark = (
        f"斜撐 FIG-{inputs.fig_type}(θ={inputs.theta}°), S={s_val}, N={n_val}"
    )

    # ③ Trunnion
    add_trunnion(result, trunnion_spec,
                 f"Trunnion {trunnion_spec}, Q={Q}mm, 需 D-72/73/74 校核")

    # ④ LUG PLATE TYPE-C (M-34, DETAIL Y — 管線端)
    m34 = get_m34_by_member(inputs.member_code)
    if m34:
        add_plate_entry(result, plate_a=m34["A"], plate_b=m34["B"],
                        plate_thickness=m34["T"], plate_name="LUG PLATE TYPE-C",
                        plate_role="lug_plate", material=PLATE_LUG_MATERIAL,
                        plate_qty=1)
        result.entries[-1].remark = f"DETAIL Y(管線端), {m34['type']}"
    else:
        result.warnings.append(f"M-34 無 {inputs.member_code} 對應的 LUG PLATE")

    # ⑤ LUG PLATE TYPE-D/E (M-35 or M-36, DETAIL Z — Vessel端)
    if inputs.fig_type == "B":
        m_dz = get_m35_by_member(inputs.member_code)
        dz_label = "TYPE-D"
    else:
        m_dz = get_m36_by_member(inputs.member_code)
        dz_label = "TYPE-E"
    if m_dz:
        add_plate_entry(result, plate_a=m_dz["A"], plate_b=m_dz["B"],
                        plate_thickness=m_dz["T"],
                        plate_name=f"LUG PLATE {dz_label}",
                        plate_role="lug_plate", material=PLATE_LUG_MATERIAL,
                        plate_qty=1)
        result.entries[-1].remark = f"DETAIL Z(Vessel端), {dz_label}"

    # ⑥ K BOLT — 3/4"x50, ×2 SET
    add_bolt_set(result, "K BOLT", '3/4"x50', 2)

    # ⑦ C/S Shim
    add_cs_shim(result, inputs.member_data["C"], b_val)

    return result
