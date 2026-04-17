"""
Type 30 計算器  (判讀來源: D-35, E1906-DSP-500-006)
格式: 30-L75-0505A-0401

第二段: 型鋼代碼 (L50, L75, C150)
第三段: LL+HH+FIG
        前2位 = L(水平臂長) ×100mm
        後2位 = H(垂直柱高) ×100mm
        末1位 = FIG 字母 (A 或 B)
第四段: L1L2 (可選, 各2位×100mm, 修改左右分配; 預設 L1=L2=L/2)

結構: 夾持型支撐 — 焊接於既有鋼構之間, 無 M-42
────────────────────────────────────────────────────────────

  FIG-A:                          FIG-B:
       ┌── L ──┐                       ┌── L ──┐
       │L1│ L2 │                       │L1│ L2 │
       ┌───────┐                       ┌───────┐
       │  6V   │                       │  6V   │
   H   │MEMBER │                   H   │MEMBER │
       │ "M"   │                       │ "M"   │  15
       │  6V   │                       │  6V   │──┤
       └───────┘                       └───┬───┘
    EXISTING STEEL                      plate/base
       TYP.

  FIG-A: 直接接 EXISTING STEEL (無板偏移)
         Total_Length = H + L

  FIG-B: 底部有 15mm 板厚偏移
         Total_Length = (H - 15) + L

  ★ 無 M-42 — 直接焊接至既有鋼構, 不落地
  ★ 與 TYPE-27/28 的本質差異: 27/28 落地需 M-42, 30 夾在結構間

DIMENSIONS TABLE (D-35):
  MEMBER "M"    | L MAX | H MAX
  L50×50×6      |  300  |  600
  L75×75×9      |  700  | 1000
  C150×75×9     | 1000  | 2000

NOTE 2: "H" & "L" SHALL BE CUT SUIT IN FIELD.

VBA NOTE: VBA 中 Section_Length_H/L 變量名互換,
          但因加法交換律 (L+H = H+L), 最終結果相同.
          FIG-B 的 15mm 扣除同理: (L-15)+H = L+(H-15).
"""
from ..models import AnalysisResult
from ..parser import get_part
from ..steel import add_steel_section_entry
from data.steel_sections import get_section_details

# ── 15mm 底板偏移 (FIG-B 圖面標示 15) ──
_PLATE_OFFSET = 15

# ── D-35 限制表 ──────────────────────────────────────────
_LIMITS = {
    "L50":  {"L_max":  300, "H_max":  600},
    "L75":  {"L_max":  700, "H_max": 1000},
    "C150": {"L_max": 1000, "H_max": 2000},
}


def calculate(fullstring: str) -> AnalysisResult:
    result = AnalysisResult(fullstring=fullstring)

    # ── 第二段: 型鋼代碼 ──
    part2 = get_part(fullstring, 2)
    details = get_section_details(part2)
    if not details:
        result.error = f"Type 30: 未知型鋼代碼 {part2}"
        return result

    section_type = details["type"]   # "Angle" or "Channel"
    full_size = details["size"]      # "L75*75*9" or "C150*75*9"

    # ── 第三段: LLHH + FIG ──
    part3 = get_part(fullstring, 3)
    if not part3 or len(part3) < 5:
        result.error = f"Type 30: 第三段格式錯誤 '{part3}' (需至少5字元, 如 0505A)"
        return result

    fig = part3[-1].upper()
    if fig not in ("A", "B"):
        result.error = f"Type 30: 不支援的 FIG 型式 '{fig}' (僅支援 A/B)"
        return result

    digits = part3[:-1]  # 去掉末位字母
    try:
        section_L = int(digits[:2]) * 100  # 前兩位 = L (水平臂長)
        section_H = int(digits[2:]) * 100  # 後兩位 = H (垂直柱高)
    except ValueError:
        result.error = f"Type 30: 無法解析 L/H 值 '{part3}'"
        return result

    # ── 第四段: L1/L2 修改尺寸 (可選) ──
    part4 = get_part(fullstring, 4)
    L1 = None
    L2 = None
    if part4 and len(part4) >= 4:
        try:
            L1 = int(part4[:2]) * 100
            L2 = int(part4[2:4]) * 100
        except ValueError:
            pass

    # ── 超限檢查 ──
    limits = _LIMITS.get(part2, {"L_max": 1000, "H_max": 2000})
    if section_L > limits["L_max"]:
        result.warnings.append(
            f"L={section_L}mm 超出 {part2} 標準範圍 (≤ {limits['L_max']}mm)"
        )
    if section_H > limits["H_max"]:
        result.warnings.append(
            f"H={section_H}mm 超出 {part2} 標準範圍 (≤ {limits['H_max']}mm)"
        )

    # ── 備註標籤 ──
    l1l2_tag = ""
    if L1 is not None and L2 is not None:
        l1l2_tag = f", L1={L1}, L2={L2}"

    # ═══════════════════════════════════════════════════════
    # ① MEMBER "M" — 唯一構件
    #    FIG-A: Total = H + L (直接接既有鋼構, 無偏移)
    #    FIG-B: Total = (H - 15) + L (底部板厚偏移 15mm)
    #    ★ 無 M-42 (不落地, 焊接至 EXISTING STEEL)
    # ═══════════════════════════════════════════════════════
    if fig == "A":
        effective_H = section_H
        total_length = section_H + section_L
        h_formula = f"H={section_H}"
    else:  # FIG-B
        effective_H = section_H - _PLATE_OFFSET
        total_length = effective_H + section_L
        h_formula = f"H={section_H}-15={effective_H}"

    section_dim = full_size[1:]  # 去掉前綴字母
    add_steel_section_entry(result, section_type, section_dim, total_length)
    result.entries[-1].remark = (
        f"FIG-{fig}, {h_formula}+L={section_L}={total_length}{l1l2_tag}"
    )

    return result
