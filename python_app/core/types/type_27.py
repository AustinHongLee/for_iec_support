"""
Type 27 計算器  (判讀來源: D-30, E1906-DSP-500-006)
格式: 27-L75-0505L-0401

第二段: 型鋼代碼 (L50, L75, L100, H150)
第三段: LL+HH+M42Letter
        前2位 = L(頂部總寬) ×100mm
        後2位 = H(高度, TO GRADE OR FDN) ×100mm
        末1位 = M-42 下部組件型式字母 (NOTE 4: USE TYPE-L & P ONLY)
第四段: L1L2 (可選, 各2位×100mm, 修改左右分配; 預設 L1=L2=L/2)

結構: 立柱式管線支撐 (Column Support)
────────────────────────────────────────────────────────────

★ 角鐵版 (L50 / L75 / L100) — 簡化組構
  角鐵本身沒有封閉中空, 不需要額外補板去形成安裝面.
  圖面左側 ELEV 畫得比較簡單.

  BOM:
    ① MEMBER "M" 主件 (H-15+L 一體) ×1
    ② M-42 lower component ×1 set

★ H150 版 — 完整板件系統
  H型鋼是開口截面, 需要周圍板件把它轉換成可焊、可承載、
  可與 M-42 對接的標準化組件.
  圖面右側視圖 + Section A~A 明確顯示板件系統.

  BOM:
    ① H150×150×10 主件 (H-15+L 一體) ×1
    ② 6t top plate (頂部承載板) ×1
    ③ 6t side plate ×3 (圖面 "3 SIDES TYP." 6V)
    ④ 9t lower side/wing plate ×2 (配合H截面形成下部轉接構造)
    ⑤ M-42 lower component ×1 set

DIMENSIONS TABLE (D-30):
  MEMBER "M"    | L MAX | H MAX | C
  L50×50×6      | 300   | 500   | 30
  L75×75×9      | 500   | 500   | 35
  L100×100×10   | 700   | 1000  | 50
  H150×150×10   | 600   | 2500  | – (C 空白 → 截面配置不同)

NOTE 2: "H" & "L" SHALL BE CUT TO SUIT IN FIELD.
NOTE 3: IF THE FOUNDATION IS NOT USED, "H" = FROM LOWEST POINT OF PAVING.
NOTE 4: THIS TYPE SHALL BE USED WITH M-42. USE TYPE-L & P ONLY.
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from ..plate import add_plate_entry
from ..m42 import perform_action_by_letter
from data.steel_sections import get_section_details

# ── 頂端接合扣除量 (圖面 ELEV 標示 15mm TYP) ──
_TOP_PLATE_DEDUCTION = 15

# ── D-30 限制表 ──────────────────────────────────────────
_LIMITS = {
    "L50":  {"L_max":  300, "H_max":  500, "C": 30},
    "L75":  {"L_max":  500, "H_max":  500, "C": 35},
    "L100": {"L_max":  700, "H_max": 1000, "C": 50},
    "H150": {"L_max":  600, "H_max": 2500, "C": None},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 27: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle" or "H Beam"
    full_size = details["size"]      # "L75*75*9" or "H150*150*10"
    is_hbeam = (section_type == "H Beam")

    # ── 第三段: LLHH + M42Letter ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 5:
        result.error = f"Type 27: 第三段格式錯誤 '{part3}' (需至少5字元, 如 0505L)"
        return result

    m42_letter = part3[-1].upper()
    if m42_letter.isdigit():
        result.error = f"Type 27: 缺少 M-42 型式字母 (末位='{m42_letter}' 不是字母)"
        return result

    # NOTE 4: USE TYPE-L & P ONLY
    if m42_letter not in ("L", "P"):
        result.warnings.append(
            f"M-42 型式 '{m42_letter}' 非標準 (NOTE 4: USE TYPE-L & P ONLY)"
        )

    digits = part3[:-1]  # 去掉末位字母
    try:
        section_L = int(digits[:2]) * 100  # 前兩位 = L (頂部總寬)
        section_H = int(digits[2:]) * 100  # 後兩位 = H (高度)
    except ValueError:
        result.error = f"Type 27: 無法解析 L/H 值 '{part3}'"
        return result

    # ── 第四段: L1/L2 修改尺寸 (可選, 預設 L1=L2=L/2) ──
    part4 = get_part(fullstring, 4)
    L1 = None
    L2 = None
    if part4 and len(part4) >= 4:
        try:
            L1 = int(part4[:2]) * 100
            L2 = int(part4[2:4]) * 100
        except ValueError:
            pass

    # ── 超限檢查 (WARNING, 不阻擋 — 可施工但非標準設計) ──
    limits = _LIMITS.get(part2, {"L_max": 700, "H_max": 2500, "C": None})
    if section_L > limits["L_max"]:
        result.warnings.append(
            f"L={section_L}mm 超出 {part2} 標準範圍 (≤ {limits['L_max']}mm), 非標準設計"
        )
    if section_H > limits["H_max"]:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 標準範圍 (≤ {limits['H_max']}mm), 非標準設計"
        )

    # ── 備註標籤 ──
    l1l2_tag = ""
    if L1 is not None and L2 is not None:
        l1l2_tag = f", L1={L1}, L2={L2}"

    # 去掉型鋼前綴字母 (L75*75*9 → 75*75*9)
    section_dim = full_size[1:]

    # ═══════════════════════════════════════════════════════
    # ① MEMBER "M" — 主立件 (所有 MEMBER 共通)
    #    VBA: Total_Length = (H - 15) + L
    #    15mm = ELEV 圖面標示 15 TYP (頂端焊接接合偏移)
    # ═══════════════════════════════════════════════════════
    effective_H = section_H - _TOP_PLATE_DEDUCTION
    total_length = effective_H + section_L
    add_steel_section_entry(result, section_type, section_dim, total_length)
    result.entries[-1].remark = (
        f"M-42:{m42_letter}, H={section_H}-15={effective_H}+L={section_L}"
        f"={total_length}{l1l2_tag}"
    )

    # ═══════════════════════════════════════════════════════
    # H150 限定 — 板件系統
    #   H型鋼是開口截面, 需要周圍板件補成可焊、可承載、
    #   可與 M-42 對接的標準化組件.
    #   角鐵版不需要這些板件 (簡化結構).
    # ═══════════════════════════════════════════════════════
    if is_hbeam:
        # ② 6t top plate — 頂部承載板 ×1
        #    圖面右側視圖明確標示 "6t PLATE"
        #    管線直接座在此板上
        #    尺寸: L(寬) × 200(深) × 6mm
        add_plate_entry(
            result,
            plate_a=section_L,
            plate_b=200,
            plate_thickness=6,
            plate_name="Plate_6t_Top",
            material="A36/SS400",
            plate_qty=1,
        )
        result.entries[-1].remark = f"頂部承載板 {section_L}×200×6"

        # ③ 6t side plates ×3 — "3 SIDES TYP." 6V
        #    柱-板接合處補強/封邊, 把 H 型鋼頂端轉成承載面
        #    尺寸估值: 150(配合H150高度) × 100 × 6mm
        add_plate_entry(
            result,
            plate_a=150,
            plate_b=100,
            plate_thickness=6,
            plate_name="Plate_6t_Side",
            material="A36/SS400",
            plate_qty=3,
        )
        result.entries[-1].remark = "3 SIDES TYP 上部補板 150×100×6"

        # ④ 9t lower side/wing plates ×2
        #    配合 H150 截面形成下部轉接構造
        #    左右各一片, 焊在 H 型鋼翼緣/腹板周邊
        #    VBA 原寫 200×100×9, 圖面右側尺寸 200/100 對應
        add_plate_entry(
            result,
            plate_a=200,
            plate_b=100,
            plate_thickness=9,
            plate_name="Plate_9t_Wing",
            material="A36/SS400",
            plate_qty=2,
        )
        result.entries[-1].remark = "下部翼側板 200×100×9 ×2"

    # ═══════════════════════════════════════════════════════
    # M-42 下部組件 (底板 + 螺栓) — 所有 MEMBER 共通
    #    NOTE 4: USE TYPE-L & P ONLY
    # ═══════════════════════════════════════════════════════
    perform_action_by_letter(result, m42_letter, full_size)

    return result
