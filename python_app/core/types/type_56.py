"""
Type 56 計算器 — 結構式管線檔止 (D-67, D-67A)
格式: 56-{line_size}B
  例: 56-2B, 56-10B, 56-36B

自成一體的結構鋼檔止, 不引用 D-80/D-81
四種結構:
  ≤2-1/2": PL 100×100×6
  3"~4": FAB FROM 6t PLATE
  5"~14": H型鋼切割
  16"~24": FAB FROM 12t PLATE
  26"~42": 大型結構 + 120° 鞍座 + D-91

BOM:
  小管 (≤2-1/2"): PLATE 100×100×6 ×2
  3"~4": MEMBER C (A×B×6t) ×2 + SIDE PLATE (D×B×E) ×2
  5"~14": MEMBER C ×2 (H型鋼切割)
  16"~24": MEMBER C (A×B×12t) ×4 + SIDE PLATE ((D-2E)×B×12t) ×2
  超大管 (26"~42"): ① MEMBER C + 鞍座 + D-91
"""
from ..models import AnalysisResult
from ..parser import get_part, get_lookup_value
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..trunnion_engine import SUPPORT_PLATE_MATERIAL as _SUPPORT_PLATE_MATERIAL
from data.type56_table import get_type56_data


def _h_spec_from_table_desc(desc: str) -> str:
    """將 'CUT FROM H200*100*5.5*8' 轉成型鋼重量表使用的 '200*100*5.5'。"""
    token = str(desc).replace("CUT FROM H", "").strip()
    parts = token.split("*")
    return "*".join(parts[:3])


def _add_gross_plate_warning(result: AnalysisResult) -> None:
    warning = (
        "Type 56: B值依圖表只到管底；與管線相切/放樣弧形目前採外接矩形重量估算，"
        "不扣圓弧、倒角，也不另加未標尺寸的接觸延伸"
    )
    if warning not in result.warnings:
        result.warnings.append(warning)


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # 第二段: 管徑
    part2 = get_part(fullstring, 2)
    if not part2:
        result.error = "Type 56: 缺少管徑"
        return result
    line_size = get_lookup_value(part2)

    data = get_type56_data(line_size)
    if not data:
        result.error = f"Type 56: 管徑 {part2} ({line_size}\") 不在範圍 (3/4\"~42\")"
        return result

    R = data["R"]

    if line_size <= 2.5:
        # 小管: PL 100×100×6 ×2
        add_plate_entry(result, plate_a=100, plate_b=100,
                        plate_thickness=6, plate_name="PLATE",
                            plate_role="generic_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = "管線檔止, PL 100×100×6, ×2"

    elif line_size <= 4:
        # 3"~4": A×B×6t ×2 + D×B×E ×2
        A = data["A"]
        B = data["B"]
        D = data["D"]
        E = data["E"]
        _add_gross_plate_warning(result)
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=6, plate_name="MEMBER C",
                            plate_role="generic_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"FAB FROM 6t PLATE, {A}x{B}x6t, ×2, R={R}mm; gross rectangle"

        add_plate_entry(result, plate_a=D, plate_b=B,
                        plate_thickness=E, plate_name="SIDE PLATE",
                            plate_role="side_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"側板, {D}x{B}x{E}t, ×2; gross rectangle"

    elif line_size <= 14:
        # 5"~14": MEMBER C ×2, CUT FROM H型鋼
        C_desc = data["C"]  # "CUT FROM H200*100*5.5*8" etc.
        D = data["D"]
        h_spec = _h_spec_from_table_desc(C_desc)
        _add_gross_plate_warning(result)
        add_steel_section_entry(result, "H Beam", h_spec, D, 2)
        result.entries[-1].name = "MEMBER C"
        if line_size == 5:
            split_note = "D=100；依圖面概念為 H200x100x5.5x8 剖半後左右各一"
        elif line_size <= 8:
            split_note = "D=100；H194x150x6x9 切出左右件，餘料/可用性需人工評估"
        else:
            split_note = "左右各一，不做剖半折減"
        result.entries[-1].remark = f"{C_desc}, L={D}, ×2, R={R}mm; {split_note}"

    elif line_size <= 24:
        # 16"~24": A×B×12t ×4 + (D-2E)×B×12t ×2
        A = data["A"]
        B = data["B"]
        E = data["E"]
        D = data["D"]
        side_len = D - 2 * E
        _add_gross_plate_warning(result)
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=E, plate_name="MEMBER C",
                            plate_role="generic_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=4)
        result.entries[-1].remark = f"FAB FROM {E}t PLATE, {A}x{B}x{E}t, ×4, R={R}mm; gross rectangle"

        add_plate_entry(result, plate_a=side_len, plate_b=B,
                        plate_thickness=E, plate_name="SIDE PLATE",
                            plate_role="side_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"側板, (D-2E)={side_len}x{B}x{E}t, ×2; gross rectangle"

    else:
        # 26"~42": 大型結構 + 120° 鞍座
        A = data["A"]
        B = data["B"]
        C = data["C"]
        D = data["D"]
        E = data["E"]
        add_plate_entry(result, plate_a=A, plate_b=B,
                        plate_thickness=E, plate_name="MEMBER C",
                            plate_role="channel",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"主承載框, A={A}, B={B}, C={C}, R={R}mm"

        add_plate_entry(result, plate_a=D, plate_b=B,
                        plate_thickness=E, plate_name="SIDE PLATE",
                            plate_role="side_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=2)
        result.entries[-1].remark = f"側板, {D}x{B}x{E}t, ×2"

        # 120° 鞍座
        add_plate_entry(result, plate_a=C, plate_b=C,
                        plate_thickness=E, plate_name="SADDLE (120°)",
                            plate_role="saddle_plate",
                        material=_SUPPORT_PLATE_MATERIAL, plate_qty=1)
        result.entries[-1].remark = f"120° 鞍座, 含 D-91 REIN. PAD"

        result.warnings.append(
            f"大管 ({line_size}\") 需 D-91 Reinforcing Pad, 尺寸另查"
        )

    return result
