"""
Type 25 計算器  (判讀來源: D-27/M.DWG, E1906-DSP-500-006)
格式: 25-L50-0505A  或  25-L50-0505C-0401

第二段: 型鋼代碼 (L50, L65, L75)
第三段: LL+HH+Fig
        前2位 = L(水平/懸臂) ×100mm
        中間   = H(垂直)       ×100mm
        末1位 = Fig 字母 (A / B / C)
第四段: L1L2 (可選, 各2位×100mm, FIG-A 修改尺寸, 供建模使用)

結構: 懸臂式角鋼支撐
────────────────────────────────────────────
FIG-A  簡易懸臂型
  ├ Member "M" 角鋼: H段(垂直) + L段(水平)
  └ 第四段 L1, L2 → 修改尺寸 (不影響重量, 供建模)

FIG-B  附 U-bolt / Down Stopper 型
  ├ Member "M" 角鋼: H段 + L段 (同 FIG-A)
  ├ DOWN STOPPER (D-70) — NOT FURNISHED
  └ STANDARD U-BOLT (D-68) — NOT FURNISHED

FIG-C  附連接板型
  ├ Member "M" 角鋼: H段 + L段 (同 FIG-A)
  ├ LUG PLATE TYPE C (SEE M-34) — 連接板 ×1
  └ K BOLT — 連接螺栓 ×4
────────────────────────────────────────────

DIMENSIONS TABLE (from drawing D-27):
  MEMBER "M"  | A   | C  | D  | E  | F  | ØJ | K        | L MAX | H MAX
  L50×50×6    | 150 | 50 | 30 | 30 | 60 | 19 | 5/8"×40  | 1000  | 500
  L65×65×6    | 160 | 65 | 35 | 30 | 70 | 22 | 3/4"×50  | 1000  | 500
  L75×75×9    | 160 | 75 | 40 | 30 | 70 | 22 | 3/4"×50  | 1000  | 2000

NOTE: "H" & "L" SHALL BE CUT TO SUIT IN FIELD.
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..bolt import add_custom_entry
from data.steel_sections import get_section_details

# ── D-27 尺寸表 ──────────────────────────────────────────
_TABLE = {
    #              A    C   D   E   F   ØJ  K bolt 規格    角鋼板厚
    "L50": {"A": 150, "C": 50, "D": 30, "E": 30, "F": 60,
            "OJ": 19, "K": '5/8"X40', "angle_t": 6},
    "L65": {"A": 160, "C": 65, "D": 35, "E": 30, "F": 70,
            "OJ": 22, "K": '3/4"X50', "angle_t": 6},
    "L75": {"A": 160, "C": 75, "D": 40, "E": 30, "F": 70,
            "OJ": 22, "K": '3/4"X50', "angle_t": 9},
}

_LIMITS = {
    "L50": {"L_max": 1000, "H_max": 500},
    "L65": {"L_max": 1000, "H_max": 500},
    "L75": {"L_max": 1000, "H_max": 2000},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 25: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle"
    full_size = details["size"]      # "L50*50*6"

    # ── 第三段: LLHH + Fig ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 5:
        result.error = f"Type 25: 第三段格式錯誤 '{part3}' (需至少5字元, 如 0505A)"
        return result

    fig = part3[-1].upper()
    if fig.isdigit():
        result.error = f"Type 25: 缺少 Fig 字母 (末位='{fig}' 不是字母)"
        return result

    try:
        section_L = int(part3[:2]) * 100   # 前兩位 = L (水平/懸臂)
        section_H = int(part3[2:-1]) * 100  # 中間   = H (垂直)
    except ValueError:
        result.error = f"Type 25: 無法解析 L/H 值 '{part3}'"
        return result

    # ── 第四段: L1/L2 (可選, FIG-A 修改尺寸, 供建模使用) ──
    part4 = get_part(fullstring, 4)
    L1 = None
    L2 = None
    if part4 and len(part4) >= 4:
        try:
            L1 = int(part4[:2]) * 100
            L2 = int(part4[2:4]) * 100
        except ValueError:
            pass  # 第四段可選, 解析失敗不報錯

    # ── 超限檢查 ──
    limits = _LIMITS.get(part2, {"L_max": 1000, "H_max": 2000})
    if section_L > limits["L_max"]:
        result.warnings.append(
            f"L={section_L}mm 超出 {part2} 適用範圍 (≤ {limits['L_max']}mm)"
        )
    if section_H > limits["H_max"]:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 適用範圍 (≤ {limits['H_max']}mm)"
        )

    # ── 建構備註資訊 ──
    fig_tag = f"Fig-{fig}"
    l1l2_tag = ""
    if L1 is not None and L2 is not None:
        l1l2_tag = f", L1={L1}, L2={L2}"

    # 去掉型鋼前綴字母 (L50*50*6 -> 50*50*6)
    section_dim = full_size[1:]

    # ═══════════════════════════════════════
    # 共通: H段 + L段 角鐵 (所有 Fig 皆有)
    # ═══════════════════════════════════════

    # 1. H 段 (垂直)
    add_steel_section_entry(result, section_type, section_dim, section_H)
    result.entries[-1].remark = f"{fig_tag}, H段{l1l2_tag}"

    # 2. L 段 (水平/懸臂)
    add_steel_section_entry(result, section_type, section_dim, section_L)
    result.entries[-1].remark = f"{fig_tag}, L段{l1l2_tag}"

    # ═══════════════════════════════════════
    # FIG-C 額外: 連接板 (LUG PLATE TYPE C) + K bolt
    # ═══════════════════════════════════════
    if fig == "C":
        table = _TABLE.get(part2, {})
        k_spec = table.get("K", "")
        plate_a = table.get("A", 0)
        plate_c = table.get("C", 0)
        plate_d = table.get("D", 0)
        angle_t = table.get("angle_t", 6)

        # DETAIL "Z" — LUG PLATE TYPE C (M-34)
        # 板寬 = A, 板高 ≈ C + D (角鋼腿寬 + 延伸), 板厚 ≈ 角鋼厚度
        # 實際尺寸以 M-34 為準, 此處為估值
        if plate_a > 0:
            plate_height = plate_c + plate_d
            add_plate_entry(
                result,
                plate_a=plate_a,
                plate_b=plate_height,
                plate_thickness=angle_t,
                plate_name="LUG_PLATE_C",
                material="A36/SS400",
                plate_qty=1,
                bolt_switch=True,
                bolt_x=2 * table.get("E", 0) + table.get("F", 0),
                bolt_y=0,
                bolt_hole=table.get("OJ", 0),
                bolt_size=k_spec,
                plate_role="lug_plate",
            )
            result.entries[-1].remark = f"SEE M-34, {fig_tag}"

        # K BOLT ×4 (依 M-34 TYPE-C 四孔)
        if k_spec:
            add_custom_entry(
                result,
                name="BOLT",
                spec=k_spec,
                material="SS400",
                quantity=4,
                unit_weight=0.1,  # 估值, 實際依 K bolt 規格
                unit="PC",
            )
            result.entries[-1].remark = f"M-34 K bolt, {fig_tag}"

    return result
